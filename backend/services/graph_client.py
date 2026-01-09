"""
Microsoft Graph API Client for Azure Security Platform V2

Handles all Graph API interactions for security data collection.
"""
import asyncio
from datetime import datetime, timedelta
from typing import Optional, Any
import structlog

from azure.identity import ClientSecretCredential
from msgraph import GraphServiceClient
from msgraph.generated.models.o_data_errors.o_data_error import ODataError

logger = structlog.get_logger(__name__)


class GraphClient:
    """
    Microsoft Graph API client for security data collection.
    
    Handles authentication and provides methods for all required Graph endpoints:
    - Secure Score
    - Identity Protection (MFA, Risky Users)
    - Conditional Access
    - Role Management (PIM)
    - Device Management (Intune)
    - Security Alerts
    - Audit Logs
    """
    
    def __init__(
        self,
        tenant_id: str,
        client_id: str,
        client_secret: str,
    ):
        """
        Initialize Graph client with service principal credentials.
        
        Args:
            tenant_id: Azure AD tenant ID
            client_id: App registration client ID
            client_secret: App registration client secret
        """
        self.tenant_id = tenant_id
        self.client_id = client_id
        
        # Create credential
        self._credential = ClientSecretCredential(
            tenant_id=tenant_id,
            client_id=client_id,
            client_secret=client_secret,
        )
        
        # Create Graph client with required scopes
        scopes = ["https://graph.microsoft.com/.default"]
        self._client = GraphServiceClient(
            credentials=self._credential,
            scopes=scopes,
        )
        
        logger.info("graph_client_initialized", tenant_id=tenant_id)
    
    # ========================================================================
    # Secure Score
    # ========================================================================
    
    async def get_secure_score(self) -> dict:
        """
        Get current Microsoft Secure Score.
        
        Returns:
            dict with current_score, max_score, and control details
        """
        try:
            result = await self._client.security.secure_scores.get()
            
            if not result or not result.value:
                logger.warning("no_secure_score_data", tenant_id=self.tenant_id)
                return {"current_score": 0, "max_score": 100, "controls": []}
            
            # Get most recent score
            latest = result.value[0]
            
            return {
                "current_score": latest.current_score or 0,
                "max_score": latest.max_score or 100,
                "created_date": latest.created_date_time,
                "control_scores": [
                    {
                        "name": cs.control_name,
                        "score": cs.score,
                        "max_score": cs.max_score,
                        "description": cs.description,
                    }
                    for cs in (latest.control_scores or [])
                ],
            }
        except ODataError as e:
            logger.error("secure_score_error", error=str(e))
            raise
    
    # ========================================================================
    # Identity Protection
    # ========================================================================
    
    async def get_mfa_registration_details(self) -> list[dict]:
        """
        Get MFA registration details for all users.
        
        Endpoint: /reports/authenticationMethods/userRegistrationDetails
        """
        try:
            result = await self._client.reports.authentication_methods.user_registration_details.get()
            
            users = []
            for user in (result.value or []):
                users.append({
                    "user_id": user.id,
                    "display_name": user.user_display_name,
                    "email": user.user_principal_name,
                    "is_mfa_registered": user.is_mfa_registered or False,
                    "is_admin": user.is_admin or False,
                    "methods_registered": user.methods_registered or [],
                })
            
            return users
        except ODataError as e:
            logger.error("mfa_registration_error", error=str(e))
            raise
    
    async def get_risky_users(self) -> list[dict]:
        """
        Get users flagged as risky by Identity Protection.
        
        Endpoint: /identityProtection/riskyUsers
        """
        try:
            result = await self._client.identity_protection.risky_users.get()
            
            users = []
            for user in (result.value or []):
                users.append({
                    "user_id": user.id,
                    "display_name": user.user_display_name,
                    "email": user.user_principal_name,
                    "risk_level": str(user.risk_level) if user.risk_level else "none",
                    "risk_state": str(user.risk_state) if user.risk_state else "none",
                    "risk_detail": str(user.risk_detail) if user.risk_detail else "",
                    "risk_last_updated": user.risk_last_updated_date_time,
                })
            
            return users
        except ODataError as e:
            logger.error("risky_users_error", error=str(e))
            raise
    
    async def get_risky_sign_ins(self, days: int = 7) -> list[dict]:
        """
        Get risky sign-in events.
        
        Args:
            days: Number of days to look back
        """
        try:
            result = await self._client.identity_protection.risky_service_principal_histories.get()
            # Note: For sign-ins, use auditLogs/signIns with risk filter
            
            sign_ins = []
            # Implementation would filter by risk and date
            return sign_ins
        except ODataError as e:
            logger.error("risky_sign_ins_error", error=str(e))
            raise
    
    # ========================================================================
    # Conditional Access
    # ========================================================================
    
    async def get_conditional_access_policies(self) -> list[dict]:
        """
        Get all Conditional Access policies.
        
        Endpoint: /identity/conditionalAccess/policies
        """
        try:
            result = await self._client.identity.conditional_access.policies.get()
            
            policies = []
            for policy in (result.value or []):
                policies.append({
                    "id": policy.id,
                    "name": policy.display_name,
                    "state": str(policy.state) if policy.state else "disabled",
                    "created_at": policy.created_date_time,
                    "modified_at": policy.modified_date_time,
                    "conditions": {
                        "users": self._serialize_ca_users(policy.conditions.users) if policy.conditions else {},
                        "applications": self._serialize_ca_apps(policy.conditions.applications) if policy.conditions else {},
                        "locations": self._serialize_ca_locations(policy.conditions.locations) if policy.conditions else {},
                    },
                    "grant_controls": self._serialize_grant_controls(policy.grant_controls),
                })
            
            return policies
        except ODataError as e:
            logger.error("conditional_access_error", error=str(e))
            raise
    
    def _serialize_ca_users(self, users) -> dict:
        """Serialize CA user conditions."""
        if not users:
            return {}
        return {
            "include_users": users.include_users or [],
            "exclude_users": users.exclude_users or [],
            "include_groups": users.include_groups or [],
            "exclude_groups": users.exclude_groups or [],
        }
    
    def _serialize_ca_apps(self, apps) -> dict:
        """Serialize CA application conditions."""
        if not apps:
            return {}
        return {
            "include_applications": apps.include_applications or [],
            "exclude_applications": apps.exclude_applications or [],
        }
    
    def _serialize_ca_locations(self, locations) -> dict:
        """Serialize CA location conditions."""
        if not locations:
            return {}
        return {
            "include_locations": locations.include_locations or [],
            "exclude_locations": locations.exclude_locations or [],
        }
    
    def _serialize_grant_controls(self, controls) -> list[str]:
        """Serialize grant controls."""
        if not controls:
            return []
        return controls.built_in_controls or []
    
    # ========================================================================
    # Role Management (PIM)
    # ========================================================================
    
    async def get_directory_role_assignments(self) -> list[dict]:
        """
        Get all directory role assignments (active and eligible).
        
        Endpoint: /roleManagement/directory/roleAssignments
        """
        try:
            result = await self._client.role_management.directory.role_assignments.get()
            
            assignments = []
            for assignment in (result.value or []):
                assignments.append({
                    "id": assignment.id,
                    "principal_id": assignment.principal_id,
                    "role_definition_id": assignment.role_definition_id,
                    "directory_scope_id": assignment.directory_scope_id,
                })
            
            return assignments
        except ODataError as e:
            logger.error("role_assignments_error", error=str(e))
            raise
    
    async def get_directory_roles(self) -> list[dict]:
        """
        Get all directory role definitions.
        """
        try:
            result = await self._client.role_management.directory.role_definitions.get()
            
            roles = []
            for role in (result.value or []):
                roles.append({
                    "id": role.id,
                    "display_name": role.display_name,
                    "description": role.description,
                    "is_built_in": role.is_built_in,
                    "is_enabled": role.is_enabled,
                })
            
            return roles
        except ODataError as e:
            logger.error("directory_roles_error", error=str(e))
            raise
    
    # ========================================================================
    # Device Management (Intune)
    # ========================================================================
    
    async def get_managed_devices(self) -> list[dict]:
        """
        Get all Intune managed devices.
        
        Endpoint: /deviceManagement/managedDevices
        """
        try:
            result = await self._client.device_management.managed_devices.get()
            
            devices = []
            for device in (result.value or []):
                devices.append({
                    "id": device.id,
                    "device_name": device.device_name,
                    "user_display_name": device.user_display_name,
                    "user_principal_name": device.user_principal_name,
                    "os_version": device.os_version,
                    "operating_system": device.operating_system,
                    "compliance_state": str(device.compliance_state) if device.compliance_state else "unknown",
                    "is_encrypted": device.is_encrypted or False,
                    "last_sync": device.last_sync_date_time,
                    "enrolled_at": device.enrolled_date_time,
                })
            
            return devices
        except ODataError as e:
            logger.error("managed_devices_error", error=str(e))
            raise
    
    # ========================================================================
    # Security Alerts
    # ========================================================================
    
    async def get_security_alerts(self, top: int = 100) -> list[dict]:
        """
        Get security alerts (v2 API).
        
        Endpoint: /security/alerts_v2
        """
        try:
            result = await self._client.security.alerts_v2.get()
            
            alerts = []
            for alert in (result.value or [])[:top]:
                alerts.append({
                    "id": alert.id,
                    "title": alert.title,
                    "description": alert.description,
                    "severity": str(alert.severity) if alert.severity else "informational",
                    "status": str(alert.status) if alert.status else "unknown",
                    "category": alert.category,
                    "service_source": str(alert.service_source) if alert.service_source else "",
                    "created_at": alert.created_date_time,
                    "last_updated": alert.last_update_date_time,
                })
            
            return alerts
        except ODataError as e:
            logger.error("security_alerts_error", error=str(e))
            raise
    
    # ========================================================================
    # Audit Logs
    # ========================================================================
    
    async def get_directory_audit_logs(self, days: int = 7) -> list[dict]:
        """
        Get directory audit logs.
        
        Endpoint: /auditLogs/directoryAudits
        """
        try:
            filter_date = datetime.utcnow() - timedelta(days=days)
            filter_str = f"activityDateTime ge {filter_date.isoformat()}Z"
            
            result = await self._client.audit_logs.directory_audits.get()
            
            logs = []
            for log in (result.value or []):
                logs.append({
                    "id": log.id,
                    "activity": log.activity_display_name,
                    "category": log.category,
                    "result": str(log.result) if log.result else "unknown",
                    "initiated_by": self._get_initiated_by(log.initiated_by),
                    "target_resources": [
                        {"type": t.type, "display_name": t.display_name}
                        for t in (log.target_resources or [])
                    ],
                    "timestamp": log.activity_date_time,
                })
            
            return logs
        except ODataError as e:
            logger.error("audit_logs_error", error=str(e))
            raise
    
    def _get_initiated_by(self, initiated_by) -> str:
        """Extract who initiated an action."""
        if not initiated_by:
            return "Unknown"
        if initiated_by.user:
            return initiated_by.user.display_name or initiated_by.user.user_principal_name or "User"
        if initiated_by.app:
            return initiated_by.app.display_name or "Application"
        return "Unknown"
    
    # ========================================================================
    # Users
    # ========================================================================
    
    async def get_guest_users(self) -> list[dict]:
        """
        Get all guest/external users.
        
        Endpoint: /users?$filter=userType eq 'Guest'
        """
        try:
            result = await self._client.users.get()
            
            guests = []
            for user in (result.value or []):
                if user.user_type == "Guest":
                    guests.append({
                        "id": user.id,
                        "display_name": user.display_name,
                        "email": user.mail or user.user_principal_name,
                        "user_type": user.user_type,
                        "created_at": user.created_date_time,
                        "last_sign_in": getattr(user, 'sign_in_activity', {}).get('lastSignInDateTime') if hasattr(user, 'sign_in_activity') else None,
                    })
            
            return guests
        except ODataError as e:
            logger.error("guest_users_error", error=str(e))
            raise
    
    async def get_all_users(self) -> list[dict]:
        """
        Get all users (for MFA analysis).
        """
        try:
            result = await self._client.users.get()
            
            users = []
            for user in (result.value or []):
                users.append({
                    "id": user.id,
                    "display_name": user.display_name,
                    "email": user.mail or user.user_principal_name,
                    "user_type": user.user_type,
                    "account_enabled": user.account_enabled,
                    "department": user.department,
                    "job_title": user.job_title,
                })
            
            return users
        except ODataError as e:
            logger.error("all_users_error", error=str(e))
            raise
