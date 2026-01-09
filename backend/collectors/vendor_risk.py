"""
Vendor Risk Collector for Azure Security Platform V2

Collects third-party and vendor risk data.
"""
from datetime import datetime, timedelta
from typing import Optional
import structlog

from ..services.graph_client import GraphClient
from ..services.cache_service import CacheService

logger = structlog.get_logger(__name__)


class VendorRiskCollector:
    """
    Collects third-party/vendor risk data.
    
    Features:
    - Guest user inventory
    - Third-party app permissions
    - External sharing statistics
    - OAuth app consent tracking
    """
    
    def __init__(
        self,
        graph_client: GraphClient,
        cache_service: Optional[CacheService] = None,
    ):
        self._graph = graph_client
        self._cache = cache_service
        self._tenant_id = graph_client.tenant_id
        
        logger.info("vendor_risk_collector_initialized", tenant_id=self._tenant_id)
    
    async def get_guest_user_inventory(self, force_refresh: bool = False) -> list[dict]:
        """
        Get all guest/external users with access levels.
        """
        # Check cache
        if not force_refresh and self._cache:
            cached = await self._cache.get(self._tenant_id, "guest_users")
            if cached:
                return cached
        
        # Fetch guest users
        guests = await self._graph.get_guest_users()
        
        inventory = []
        for guest in guests:
            created_at = guest.get("created_at")
            last_sign_in = guest.get("last_sign_in")
            
            # Calculate days since last sign-in
            days_inactive = None
            if last_sign_in:
                try:
                    sign_in_time = datetime.fromisoformat(str(last_sign_in).replace("Z", ""))
                    days_inactive = (datetime.utcnow() - sign_in_time).days
                except:
                    pass
            
            inventory.append({
                "user_id": guest.get("id"),
                "display_name": guest.get("display_name"),
                "email": guest.get("email"),
                "user_type": guest.get("user_type"),
                "created_at": created_at,
                "last_sign_in": last_sign_in,
                "days_inactive": days_inactive,
                "is_stale": days_inactive is not None and days_inactive > 90,
                "source": "Azure AD B2B",
                "access_level": "Guest",  # Would need to query group memberships
            })
        
        # Cache result
        if self._cache:
            await self._cache.set(self._tenant_id, "guest_users", inventory, ttl_seconds=86400)
        
        logger.info(
            "guest_users_collected",
            tenant_id=self._tenant_id,
            count=len(inventory),
            stale_count=len([g for g in inventory if g.get("is_stale")]),
        )
        
        return inventory
    
    async def get_guest_user_summary(self) -> dict:
        """
        Get guest user summary statistics.
        """
        guests = await self.get_guest_user_inventory()
        
        total = len(guests)
        stale = len([g for g in guests if g.get("is_stale")])
        never_signed_in = len([g for g in guests if g.get("last_sign_in") is None])
        
        # Group by domain
        domains = {}
        for guest in guests:
            email = guest.get("email", "")
            if "@" in email:
                domain = email.split("@")[1].lower()
                domains[domain] = domains.get(domain, 0) + 1
        
        return {
            "total_guests": total,
            "stale_guests": stale,
            "never_signed_in": never_signed_in,
            "active_guests": total - stale - never_signed_in,
            "top_domains": sorted(domains.items(), key=lambda x: x[1], reverse=True)[:10],
        }
    
    async def get_third_party_apps(self, force_refresh: bool = False) -> list[dict]:
        """
        Get third-party apps with admin consent.
        
        Note: Requires ServicePrincipal and OAuth2PermissionGrant access.
        In production, would query:
        - /servicePrincipals
        - /oauth2PermissionGrants
        """
        # Check cache
        if not force_refresh and self._cache:
            cached = await self._cache.get(self._tenant_id, "third_party_apps")
            if cached:
                return cached
        
        # In production, would query Graph API for service principals
        # and OAuth2 permission grants
        
        # For demo, return structured placeholder
        apps = [
            {
                "app_id": "app-slack",
                "display_name": "Slack",
                "publisher": "Slack Technologies",
                "permissions": ["User.Read", "Calendars.Read", "Mail.Send"],
                "permission_count": 3,
                "consent_type": "admin",
                "consented_by": "IT Admin",
                "consented_at": (datetime.utcnow() - timedelta(days=180)).isoformat(),
                "risk_level": "low",
            },
            {
                "app_id": "app-zoom",
                "display_name": "Zoom",
                "publisher": "Zoom Video Communications",
                "permissions": ["User.Read", "OnlineMeetings.ReadWrite", "Calendars.ReadWrite"],
                "permission_count": 3,
                "consent_type": "admin",
                "consented_by": "IT Admin",
                "consented_at": (datetime.utcnow() - timedelta(days=90)).isoformat(),
                "risk_level": "low",
            },
            {
                "app_id": "app-salesforce",
                "display_name": "Salesforce",
                "publisher": "Salesforce.com",
                "permissions": ["User.Read.All", "Directory.Read.All", "Mail.Read"],
                "permission_count": 3,
                "consent_type": "admin",
                "consented_by": "IT Admin",
                "consented_at": (datetime.utcnow() - timedelta(days=365)).isoformat(),
                "risk_level": "medium",
            },
        ]
        
        # Cache result
        if self._cache:
            await self._cache.set(self._tenant_id, "third_party_apps", apps, ttl_seconds=86400)
        
        return apps
    
    async def get_high_risk_apps(self) -> list[dict]:
        """
        Get apps with high-risk permissions.
        
        High-risk permissions include:
        - Mail.ReadWrite, Mail.Send
        - Files.ReadWrite.All
        - Directory.ReadWrite.All
        - User.ReadWrite.All
        """
        high_risk_permissions = {
            "Mail.ReadWrite", "Mail.Send", "Mail.ReadWrite.All",
            "Files.ReadWrite.All", "Sites.ReadWrite.All",
            "Directory.ReadWrite.All", "User.ReadWrite.All",
            "RoleManagement.ReadWrite.Directory",
        }
        
        apps = await self.get_third_party_apps()
        
        high_risk = []
        for app in apps:
            app_permissions = set(app.get("permissions", []))
            risky_perms = app_permissions & high_risk_permissions
            
            if risky_perms:
                app_copy = app.copy()
                app_copy["high_risk_permissions"] = list(risky_perms)
                app_copy["risk_level"] = "high"
                high_risk.append(app_copy)
        
        return high_risk
    
    async def get_external_sharing_stats(self) -> dict:
        """
        Get external sharing statistics.
        
        Note: Requires SharePoint/OneDrive admin access.
        In production, would query SharePoint API.
        """
        # In production, would query:
        # - SharePoint site collection sharing settings
        # - OneDrive sharing links
        # - External access grants
        
        # For demo, return structured placeholder
        return {
            "total_external_shares": 156,
            "files_shared_externally": 89,
            "folders_shared_externally": 23,
            "sites_with_external_access": 5,
            "shares_without_expiry": 34,
            "shares_older_than_90_days": 45,
            "anonymous_links": 12,
            "top_external_domains": [
                {"domain": "partner.com", "count": 45},
                {"domain": "vendor.com", "count": 32},
                {"domain": "contractor.net", "count": 18},
            ],
            "sharing_trend": "stable",
            "last_updated": datetime.utcnow().isoformat(),
        }
    
    async def get_vendor_risk_summary(self) -> dict:
        """
        Get comprehensive vendor risk summary for executive dashboard.
        """
        guest_summary = await self.get_guest_user_summary()
        apps = await self.get_third_party_apps()
        high_risk_apps = await self.get_high_risk_apps()
        sharing_stats = await self.get_external_sharing_stats()
        
        return {
            "guest_users": guest_summary,
            "third_party_apps": {
                "total": len(apps),
                "high_risk": len(high_risk_apps),
                "admin_consented": len([a for a in apps if a.get("consent_type") == "admin"]),
            },
            "external_sharing": sharing_stats,
            "risk_score": self._calculate_vendor_risk_score(
                guest_summary, apps, high_risk_apps, sharing_stats
            ),
            "last_updated": datetime.utcnow().isoformat(),
        }
    
    def _calculate_vendor_risk_score(
        self,
        guest_summary: dict,
        apps: list,
        high_risk_apps: list,
        sharing_stats: dict,
    ) -> dict:
        """
        Calculate overall vendor risk score.
        """
        score = 100  # Start at 100, deduct for risks
        
        # Deduct for stale guests
        stale_ratio = guest_summary.get("stale_guests", 0) / max(guest_summary.get("total_guests", 1), 1)
        score -= min(stale_ratio * 20, 20)
        
        # Deduct for high-risk apps
        score -= len(high_risk_apps) * 5
        
        # Deduct for anonymous sharing
        score -= min(sharing_stats.get("anonymous_links", 0) * 2, 15)
        
        # Deduct for shares without expiry
        score -= min(sharing_stats.get("shares_without_expiry", 0) * 0.5, 10)
        
        score = max(score, 0)
        
        if score >= 80:
            risk_level = "low"
        elif score >= 60:
            risk_level = "medium"
        else:
            risk_level = "high"
        
        return {
            "score": round(score, 1),
            "risk_level": risk_level,
            "max_score": 100,
        }
