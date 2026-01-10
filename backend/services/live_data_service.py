"""
Live Data Service - Fetches real-time data from Azure tenant.

This service connects to Microsoft Graph API using your service principal
credentials and returns real security metrics for the dashboard.
"""
import os
from datetime import datetime, timedelta
from typing import Optional
import structlog

# Load environment variables from .env file (must be before reading any env vars)
from dotenv import load_dotenv
load_dotenv()

from .graph_client import GraphClient

logger = structlog.get_logger(__name__)


class LiveDataService:
    """
    Service to fetch live security data from Azure/M365.
    
    Uses environment variables for credentials:
    - AZURE_CLIENT_ID
    - AZURE_CLIENT_SECRET
    - AZURE_TENANT_ID
    """
    
    _instance: Optional["LiveDataService"] = None
    _graph_client: Optional[GraphClient] = None
    
    def __init__(self):
        self.client_id = os.getenv("AZURE_CLIENT_ID", "")
        self.client_secret = os.getenv("AZURE_CLIENT_SECRET", "")
        self.tenant_id = os.getenv("AZURE_TENANT_ID", "")
        
        if self.client_id and self.client_secret and self.tenant_id:
            try:
                self._graph_client = GraphClient(
                    tenant_id=self.tenant_id,
                    client_id=self.client_id,
                    client_secret=self.client_secret,
                )
                logger.info("live_data_service_initialized", tenant_id=self.tenant_id)
            except Exception as e:
                logger.error("graph_client_init_failed", error=str(e))
                self._graph_client = None
        else:
            logger.warning("missing_azure_credentials", 
                          has_client_id=bool(self.client_id),
                          has_secret=bool(self.client_secret),
                          has_tenant=bool(self.tenant_id))
    
    @classmethod
    def get_instance(cls) -> "LiveDataService":
        """Get singleton instance."""
        if cls._instance is None:
            cls._instance = LiveDataService()
        return cls._instance
    
    def is_connected(self) -> bool:
        """Check if we have a valid Graph client."""
        return self._graph_client is not None

    async def test_connection(self) -> dict:
        """
        Test connection to Microsoft Graph and return detailed status.
        
        Returns:
            Dictionary with connection status and details.
        """
        if not self.is_connected():
            return {
                "status": "error",
                "message": "Graph client not initialized. Check Azure credentials."
            }
            
        try:
            # Try a simple call to get organization details
            # We don't have a direct method for this in GraphClient, 
            # so we'll use get_secure_score as a proxy for connectivity
            await self._graph_client.get_secure_score()
            
            return {
                "status": "success",
                "message": "Successfully connected to Microsoft Graph API",
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error("connection_test_failed", error=str(e))
            return {
                "status": "error",
                "message": f"Connection failed: {str(e)}",
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def get_secure_score(self) -> dict:
        """Get Microsoft Secure Score with industry comparisons."""
        if not self._graph_client:
            return self._mock_secure_score()
        
        try:
            data = await self._graph_client.get_secure_score()
            current = data.get("current_score", 0)
            max_score = data.get("max_score", 100)
            
            # Calculate percentage (0-100 scale)
            score_percent = round((current / max_score) * 100, 1) if max_score > 0 else 0
            
            # Process comparison data from Microsoft
            comparisons = data.get("comparisons", [])
            benchmark_data = {
                "your_score_percent": score_percent,
                "all_tenants": None,
                "similar_size": None,
                "industry": None,
                "organization_size": data.get("licensed_user_count"),
            }
            
            for comp in comparisons:
                basis = comp.get("basis", "").lower()
                avg = comp.get("average_score", 0)
                avg_percent = round((avg / max_score) * 100, 1) if max_score > 0 else 0
                
                if "alltenants" in basis or basis == "all":
                    benchmark_data["all_tenants"] = {
                        "average_score": avg,
                        "average_percent": avg_percent,
                        "comparison": "above" if current > avg else "below" if current < avg else "equal",
                        "difference": round(score_percent - avg_percent, 1),
                    }
                elif "seat" in basis or "size" in basis:
                    benchmark_data["similar_size"] = {
                        "average_score": avg,
                        "average_percent": avg_percent,
                        "comparison": "above" if current > avg else "below" if current < avg else "equal",
                        "difference": round(score_percent - avg_percent, 1),
                        "size_category": self._get_size_category(data.get("licensed_user_count", 0)),
                    }
                elif "industry" in basis:
                    benchmark_data["industry"] = {
                        "average_score": avg,
                        "average_percent": avg_percent,
                        "comparison": "above" if current > avg else "below" if current < avg else "equal",
                        "difference": round(score_percent - avg_percent, 1),
                    }
            
            return {
                "current_score": current,
                "max_score": max_score,
                "score_percent": score_percent,
                "percentile": 0,
                "controls": data.get("control_scores", []),
                "benchmarks": benchmark_data,
                "is_live": True,
            }
        except Exception as e:
            logger.error("secure_score_fetch_failed", error=str(e))
            return self._mock_secure_score()
    
    def _get_size_category(self, user_count: int) -> str:
        """Categorize organization size based on user count."""
        if user_count == 0:
            return "Unknown"
        elif user_count <= 50:
            return "Small (1-50)"
        elif user_count <= 250:
            return "Medium (51-250)"
        elif user_count <= 1000:
            return "Large (251-1000)"
        else:
            return "Enterprise (1000+)"
    
    def _mock_secure_score(self) -> dict:
        """Return mock data when live data unavailable."""
        return {
            "current_score": 0,
            "max_score": 100,
            "score_percent": 0,
            "percentile": 0,
            "controls": [],
            "benchmarks": {
                "your_score_percent": 0,
                "all_tenants": None,
                "similar_size": None,
                "industry": None,
            },
            "is_live": False,
            "error": "Unable to fetch live data",
        }
    
    async def get_mfa_coverage(self) -> dict:
        """Get MFA coverage statistics."""
        if not self._graph_client:
            return self._mock_mfa_coverage()
        
        try:
            users = await self._graph_client.get_mfa_registration_details()
            
            total_users = len(users)
            admins = [u for u in users if u.get("is_admin")]
            total_admins = len(admins)
            
            users_with_mfa = len([u for u in users if u.get("is_mfa_registered")])
            admins_with_mfa = len([u for u in admins if u.get("is_mfa_registered")])
            
            return {
                "total_users": total_users,
                "users_with_mfa": users_with_mfa,
                "user_coverage_percent": round((users_with_mfa / total_users * 100), 1) if total_users > 0 else 0,
                "total_admins": total_admins,
                "admins_with_mfa": admins_with_mfa,
                "admin_coverage_percent": round((admins_with_mfa / total_admins * 100), 1) if total_admins > 0 else 100,
                "is_live": True,
            }
        except Exception as e:
            logger.error("mfa_coverage_fetch_failed", error=str(e))
            return self._mock_mfa_coverage()
    
    def _mock_mfa_coverage(self) -> dict:
        return {
            "total_users": 0,
            "users_with_mfa": 0,
            "user_coverage_percent": 0,
            "total_admins": 0,
            "admins_with_mfa": 0,
            "admin_coverage_percent": 0,
            "is_live": False,
        }
    
    async def get_risky_users(self) -> dict:
        """Get risky users from Identity Protection."""
        if not self._graph_client:
            return self._mock_risky_users()
        
        try:
            users = await self._graph_client.get_risky_users()
            
            high_risk = len([u for u in users if "high" in u.get("risk_level", "").lower()])
            medium_risk = len([u for u in users if "medium" in u.get("risk_level", "").lower()])
            low_risk = len([u for u in users if "low" in u.get("risk_level", "").lower()])
            
            return {
                "high_risk_count": high_risk,
                "medium_risk_count": medium_risk,
                "low_risk_count": low_risk,
                "total_risky": len(users),
                "users": users[:10],  # Top 10 for display
                "is_live": True,
            }
        except Exception as e:
            logger.error("risky_users_fetch_failed", error=str(e))
            return self._mock_risky_users()
    
    def _mock_risky_users(self) -> dict:
        return {
            "high_risk_count": 0,
            "medium_risk_count": 0,
            "low_risk_count": 0,
            "total_risky": 0,
            "users": [],
            "is_live": False,
        }
    
    async def get_privileged_accounts(self) -> dict:
        """Get privileged account statistics."""
        if not self._graph_client:
            return self._mock_privileged_accounts()
        
        try:
            assignments = await self._graph_client.get_directory_role_assignments()
            roles = await self._graph_client.get_directory_roles()
            
            # Find Global Admin role ID
            global_admin_role = next(
                (r for r in roles if "Global Administrator" in r.get("display_name", "")),
                None
            )
            
            global_admin_count = 0
            if global_admin_role:
                global_admin_count = len([
                    a for a in assignments 
                    if a.get("role_definition_id") == global_admin_role.get("id")
                ])
            
            # Count unique principals with privileged roles
            privileged_principals = set(a.get("principal_id") for a in assignments)
            
            return {
                "global_admin_count": global_admin_count,
                "privileged_role_count": len(privileged_principals),
                "total_role_assignments": len(assignments),
                "roles": roles,
                "is_live": True,
            }
        except Exception as e:
            logger.error("privileged_accounts_fetch_failed", error=str(e))
            return self._mock_privileged_accounts()
    
    def _mock_privileged_accounts(self) -> dict:
        return {
            "global_admin_count": 0,
            "privileged_role_count": 0,
            "total_role_assignments": 0,
            "roles": [],
            "is_live": False,
        }
    
    async def get_conditional_access_policies(self) -> dict:
        """Get Conditional Access policy summary."""
        if not self._graph_client:
            return self._mock_ca_policies()
        
        try:
            policies = await self._graph_client.get_conditional_access_policies()
            
            enabled_count = len([p for p in policies if p.get("state") == "enabled"])
            report_only = len([p for p in policies if p.get("state") == "enabledForReportingButNotEnforced"])
            disabled_count = len([p for p in policies if p.get("state") == "disabled"])
            
            return {
                "total_policies": len(policies),
                "enabled_count": enabled_count,
                "report_only_count": report_only,
                "disabled_count": disabled_count,
                "policies": policies,
                "is_live": True,
            }
        except Exception as e:
            logger.error("ca_policies_fetch_failed", error=str(e))
            return self._mock_ca_policies()
    
    def _mock_ca_policies(self) -> dict:
        return {
            "total_policies": 0,
            "enabled_count": 0,
            "report_only_count": 0,
            "disabled_count": 0,
            "policies": [],
            "is_live": False,
        }
    
    async def get_device_compliance(self) -> dict:
        """Get device compliance from Intune."""
        if not self._graph_client:
            return self._mock_device_compliance()
        
        try:
            devices = await self._graph_client.get_managed_devices()
            
            compliant = len([d for d in devices if d.get("compliance_state") == "compliant"])
            non_compliant = len([d for d in devices if d.get("compliance_state") == "noncompliant"])
            unknown = len([d for d in devices if d.get("compliance_state") not in ["compliant", "noncompliant"]])
            total = len(devices)
            
            return {
                "total_devices": total,
                "compliant_count": compliant,
                "non_compliant_count": non_compliant,
                "unknown_count": unknown,
                "compliance_percent": round((compliant / total * 100), 1) if total > 0 else 0,
                "devices": devices[:20],  # Sample for display
                "is_live": True,
            }
        except Exception as e:
            logger.error("device_compliance_fetch_failed", error=str(e))
            return self._mock_device_compliance()
    
    def _mock_device_compliance(self) -> dict:
        return {
            "total_devices": 0,
            "compliant_count": 0,
            "non_compliant_count": 0,
            "unknown_count": 0,
            "compliance_percent": 0,
            "devices": [],
            "is_live": False,
        }
    
    async def get_security_alerts(self) -> dict:
        """Get security alerts from Defender."""
        if not self._graph_client:
            return self._mock_security_alerts()
        
        try:
            alerts = await self._graph_client.get_security_alerts()
            
            # Helper to normalize severity string (handles enum-like strings)
            def normalize_severity(sev: str) -> str:
                sev_lower = sev.lower()
                # Handle both plain strings and enum-like strings (e.g., "AlertSeverity.High")
                if "critical" in sev_lower:
                    return "critical"
                elif "high" in sev_lower:
                    return "high"
                elif "medium" in sev_lower:
                    return "medium"
                elif "low" in sev_lower:
                    return "low"
                else:
                    return "informational"
            
            # Count by severity
            critical = len([a for a in alerts if normalize_severity(a.get("severity", "")) == "critical"])
            high = len([a for a in alerts if normalize_severity(a.get("severity", "")) == "high"])
            medium = len([a for a in alerts if normalize_severity(a.get("severity", "")) == "medium"])
            low = len([a for a in alerts if normalize_severity(a.get("severity", "")) == "low"])
            informational = len([a for a in alerts if normalize_severity(a.get("severity", "")) == "informational"])
            
            # Filter active alerts (not resolved or dismissed)
            def is_active(status: str) -> bool:
                status_lower = status.lower()
                return "resolved" not in status_lower and "dismissed" not in status_lower
            
            active_alerts = [a for a in alerts if is_active(a.get("status", "active"))]
            
            return {
                "total_alerts": len(alerts),
                "active_alerts": len(active_alerts),
                "critical_count": critical,
                "high_count": high,
                "medium_count": medium,
                "low_count": low + informational,  # Combine low and informational
                "alerts": alerts[:20],  # Recent alerts
                "is_live": True,
            }
        except Exception as e:
            logger.error("security_alerts_fetch_failed", error=str(e))
            return self._mock_security_alerts()
    
    def _mock_security_alerts(self) -> dict:
        return {
            "total_alerts": 0,
            "active_alerts": 0,
            "critical_count": 0,
            "high_count": 0,
            "medium_count": 0,
            "low_count": 0,
            "alerts": [],
            "is_live": False,
        }
    
    async def get_all_users_summary(self) -> dict:
        """Get user summary stats."""
        if not self._graph_client:
            return {"total_users": 0, "guest_users": 0, "is_live": False}
        
        try:
            users = await self._graph_client.get_all_users()
            guests = [u for u in users if u.get("user_type") == "Guest"]
            enabled = [u for u in users if u.get("account_enabled")]
            
            return {
                "total_users": len(users),
                "enabled_users": len(enabled),
                "disabled_users": len(users) - len(enabled),
                "guest_users": len(guests),
                "member_users": len(users) - len(guests),
                "is_live": True,
            }
        except Exception as e:
            logger.error("users_summary_fetch_failed", error=str(e))
            return {" total_users": 0, "guest_users": 0, "is_live": False}
    
    async def get_risky_sign_ins_data(self, days: int = 7) -> dict:
        """Get risky sign-in detections from Identity Protection."""
        if not self._graph_client:
            return self._mock_risky_sign_ins_data()
        
        try:
            detections = await self._graph_client.get_risky_sign_ins(days)
            
            # Categorize by risk level
            high_risk = [d for d in detections if "high" in d.get("risk_level", "").lower()]
            medium_risk = [d for d in detections if "medium" in d.get("risk_level", "").lower()]
            low_risk = [d for d in detections if "low" in d.get("risk_level", "").lower()]
            
            return {
                "total": len(detections),
                "high_risk_count": len(high_risk),
                "medium_risk_count": len(medium_risk),
                "low_risk_count": len(low_risk),
                "detections": detections[:50],  # Limit for display
                "is_live": True,
            }
        except Exception as e:
            logger.error("risky_sign_ins_data_fetch_failed", error=str(e))
            return self._mock_risky_sign_ins_data()
    
    def _mock_risky_sign_ins_data(self) -> dict:
        return {
            "total": 0,
            "high_risk_count": 0,
            "medium_risk_count": 0,
            "low_risk_count": 0,
            "detections": [],
            "is_live": False,
        }
    
    async def get_third_party_apps_data(self) -> dict:
        """Get third-party applications with OAuth consent details."""
        if not self._graph_client:
            return self._mock_third_party_apps()
        
        try:
            apps = await self._graph_client.get_third_party_applications()
            
            # Categorize by consent type
            admin_consent = [a for a in apps if a.get("consent_type") == "admin"]
            user_consent = [a for a in apps if a.get("consent_type") == "user"]
            
            return {
                "total": len(apps),
                "admin_consent_count": len(admin_consent),
                "user_consent_count": len(user_consent),
                "apps": apps,
                "is_live": True,
            }
        except Exception as e:
            logger.error("third_party_apps_fetch_failed", error=str(e))
            return self._mock_third_party_apps()
    
    def _mock_third_party_apps(self) -> dict:
        return {
            "total": 0,
            "admin_consent_count": 0,
            "user_consent_count": 0,
            "apps": [],
            "is_live": False,
        }
    
    async def get_high_risk_operations(self, days: int = 7) -> dict:
        """Get high-risk operations from audit logs."""
        if not self._graph_client:
            return self._mock_high_risk_ops()
        
        try:
            audit_logs = await self._graph_client.get_directory_audit_logs(days)
            
            # Define high-risk categories and activities
            high_risk_categories = {
                "RoleManagement",
                "Policy",
                "ApplicationManagement",
                "UserManagement",
            }
            
            high_risk_activities = {
                "add member to role",
                "update conditional access policy",
                "delete conditional access policy",
                "disable conditional access policy",
                "consent to application",
                "add service principal",
                "delete user",
                "reset user password",
                "update application",
            }
            
            # Filter for high-risk operations
            risky_ops = []
            for log in audit_logs:
                category = log.get("category", "")
                activity = log.get("activity", "").lower()
                
                if category in high_risk_categories or any(risk_activity in activity for risk_activity in high_risk_activities):
                    risky_ops.append(log)
            
            return {
                "total": len(risky_ops),
                "operations": risky_ops[:20],  # Recent 20
                "is_live": True,
            }
        except Exception as e:
            logger.error("high_risk_ops_fetch_failed", error=str(e))
            return self._mock_high_risk_ops()
    
    def _mock_high_risk_ops(self) -> dict:
        return {
            "total": 0,
            "operations": [],
            "is_live": False,
        }
    
    async def get_full_dashboard_data(self) -> dict:
        """
        Get all dashboard data in one call.
        
        Returns comprehensive security posture data with permission status flags
        to indicate which data sources are available.
        """
        import asyncio
        
        # Fetch all data concurrently
        results = await asyncio.gather(
            self.get_secure_score(),
            self.get_mfa_coverage(),
            self.get_risky_users(),
            self.get_privileged_accounts(),
            self.get_conditional_access_policies(),
            self.get_device_compliance(),
            self.get_security_alerts(),
            self.get_all_users_summary(),
            return_exceptions=True,
        )
        
        # Unpack results
        secure_score, mfa, risky_users, priv_accounts, ca_policies, devices, alerts, users = results
        
        # Track permission status for each API
        permission_status = {
            "secure_score": False,
            "mfa_registration": False,
            "identity_protection": False,
            "directory_roles": False,
            "conditional_access": False,
            "intune_devices": False,
            "security_alerts": False,
            "users": False,
        }
        
        # Handle any exceptions and track permission status
        def safe_get(result, default, permission_key: str):
            if isinstance(result, Exception):
                error_str = str(result).lower()
                # Log specific permission errors
                if "authorization" in error_str or "forbidden" in error_str or "403" in error_str:
                    logger.warning("permission_denied", permission=permission_key, error=str(result))
                else:
                    logger.error("dashboard_data_error", permission=permission_key, error=str(result))
                return default
            
            # Check if result indicates live data
            if isinstance(result, dict) and result.get("is_live"):
                permission_status[permission_key] = True
            
            return result
        
        # Process results with permission tracking
        secure_score_data = safe_get(secure_score, self._mock_secure_score(), "secure_score")
        mfa_data = safe_get(mfa, self._mock_mfa_coverage(), "mfa_registration")
        risky_users_data = safe_get(risky_users, self._mock_risky_users(), "identity_protection")
        priv_accounts_data = safe_get(priv_accounts, self._mock_privileged_accounts(), "directory_roles")
        ca_policies_data = safe_get(ca_policies, self._mock_ca_policies(), "conditional_access")
        devices_data = safe_get(devices, self._mock_device_compliance(), "intune_devices")
        alerts_data = safe_get(alerts, self._mock_security_alerts(), "security_alerts")
        users_data = safe_get(users, {"total_users": 0, "guest_users": 0, "is_live": False}, "users")
        
        # Update users permission status
        if isinstance(users_data, dict) and users_data.get("is_live"):
            permission_status["users"] = True
        
        return {
            "tenant_id": self.tenant_id,
            "tenant_name": "Your Organization",  # Could fetch from Graph
            "is_live_data": self.is_connected(),
            "last_updated": datetime.utcnow().isoformat(),
            
            "secure_score": secure_score_data,
            "mfa_coverage": mfa_data,
            "risky_users": risky_users_data,
            "privileged_accounts": priv_accounts_data,
            "conditional_access": ca_policies_data,
            "device_compliance": devices_data,
            "security_alerts": alerts_data,
            "users_summary": users_data,
            
            # Permission status indicates which APIs are accessible
            "permission_status": permission_status,
            
            # Summary of configuration status
            "configuration_status": {
                "graph_connected": self.is_connected(),
                "has_secure_score": permission_status["secure_score"],
                "has_identity_data": permission_status["mfa_registration"] or permission_status["identity_protection"],
                "has_device_data": permission_status["intune_devices"],
                "has_alert_data": permission_status["security_alerts"],
            },
        }
    async def get_department_analytics(self) -> dict:
        """
        Aggregate security metrics by department.
        
        Correlates Users (Dept) with MFA status and Devices.
        """
        if not self._graph_client:
            return {"mfa_by_department": [], "devices_by_department": [], "is_live": False}

        try:
            # Fetch base data
            users = await self._graph_client.get_all_users()
            mfa_details = await self._graph_client.get_mfa_registration_details()
            devices = await self._graph_client.get_managed_devices()

            # Create User Map: UPN -> Department
            user_dept_map = {}
            dept_stats = {}

            for u in users:
                upn = u.get("email", "").lower()
                dept = u.get("department") or "Unknown"
                user_dept_map[upn] = dept
                
                if dept not in dept_stats:
                    dept_stats[dept] = {
                        "users_total": 0,
                        "users_mfa_registered": 0,
                        "devices_total": 0,
                        "devices_compliant": 0,
                        "devices_non_compliant": 0
                    }
                
                dept_stats[dept]["users_total"] += 1

            # 1. MFA Correlation
            # MFA details uses 'userPrincipalName' which maps to our 'email'
            for m in mfa_details:
                upn = m.get("email", "").lower()
                dept = user_dept_map.get(upn, "Unknown")
                
                # If we found a user with this UPN, update their dept stats
                # Note: mfa_details might contain users not in get_all_users if scope differs, but usually they match
                if dept not in dept_stats:
                     dept_stats[dept] = {
                        "users_total": 0, # Increment only if we missed them in main list
                        "users_mfa_registered": 0,
                        "devices_total": 0,
                        "devices_compliant": 0,
                        "devices_non_compliant": 0
                    }
                
                if m.get("is_mfa_registered"):
                    dept_stats[dept]["users_mfa_registered"] += 1

            # 2. Device Correlation
            for d in devices:
                upn = d.get("user_principal_name", "").lower()
                dept = user_dept_map.get(upn, "Unknown")
                
                if dept not in dept_stats:
                     dept_stats[dept] = {
                        "users_total": 0,
                        "users_mfa_registered": 0,
                        "devices_total": 0,
                        "devices_compliant": 0,
                        "devices_non_compliant": 0
                    }
                
                dept_stats[dept]["devices_total"] += 1
                if d.get("compliance_state") == "compliant":
                    dept_stats[dept]["devices_compliant"] += 1
                elif d.get("compliance_state") == "noncompliant":
                    dept_stats[dept]["devices_non_compliant"] += 1
            
            # 3. Format Output
            mfa_output = []
            device_output = []
            
            for dept, stats in dept_stats.items():
                if dept == "Unknown" and stats["users_total"] == 0 and stats["devices_total"] == 0:
                    continue # Skip empty unknown buckets
                
                # MFA Entry
                if stats["users_total"] > 0:
                    mfa_output.append({
                        "department": dept,
                        "total": stats["users_total"],
                        "compliant": stats["users_mfa_registered"],
                        "nonCompliant": stats["users_total"] - stats["users_mfa_registered"],
                        "percentage": round((stats["users_mfa_registered"] / stats["users_total"]) * 100, 1)
                    })

                # Device Entry
                if stats["devices_total"] > 0:
                    device_output.append({
                        "department": dept,
                        "total": stats["devices_total"],
                        "compliant": stats["devices_compliant"],
                        "nonCompliant": stats["devices_non_compliant"],
                        "percentage": round((stats["devices_compliant"] / stats["devices_total"]) * 100, 1)
                    })
            
            # Sort by risk (percentage ascending)
            mfa_output.sort(key=lambda x: x["percentage"])
            device_output.sort(key=lambda x: x["percentage"])

            return {
                "mfa_by_department": mfa_output,
                "devices_by_department": device_output,
                "is_live": True
            }

        except Exception as e:
            logger.error("department_analytics_failed", error=str(e))
            return {"mfa_by_department": [], "devices_by_department": [], "is_live": False}

# Singleton accessor
def get_live_data_service() -> LiveDataService:
    """Get the live data service instance."""
    return LiveDataService.get_instance()
