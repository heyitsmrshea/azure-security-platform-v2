"""
Identity Collector for Azure Security Platform V2

Collects identity and access management data:
- MFA coverage
- Privileged accounts
- Risky users
- Conditional Access status
"""
from datetime import datetime
from typing import Optional
import structlog

from ..services.graph_client import GraphClient
from ..services.cache_service import CacheService
from ..models.schemas import (
    MFACoverage,
    PrivilegedAccounts,
    RiskyUsers,
    MetricTrend,
    TrendDirection,
)

logger = structlog.get_logger(__name__)


class IdentityCollector:
    """
    Collects identity and access management metrics.
    """
    
    # Privileged role IDs (Azure AD built-in roles)
    PRIVILEGED_ROLES = {
        "62e90394-69f5-4237-9190-012177145e10": "Global Administrator",
        "e8611ab8-c189-46e8-94e1-60213ab1f814": "Privileged Role Administrator",
        "194ae4cb-b126-40b2-bd5b-6091b380977d": "Security Administrator",
        "f28a1f50-f6e7-4571-818b-6a12f2af6b6c": "SharePoint Administrator",
        "29232cdf-9323-42fd-ade2-1d097af3e4de": "Exchange Administrator",
        "fe930be7-5e62-47db-91af-98c3a49a38b1": "User Administrator",
        "9b895d92-2cd3-44c7-9d02-a6ac2d5ea5c3": "Application Administrator",
        "158c047a-c907-4556-b7ef-446551a6b5f7": "Cloud Application Administrator",
        "b0f54661-2d74-4c50-afa3-1ec803f12efe": "Billing Administrator",
        "729827e3-9c14-49f7-bb1b-9608f156bbb8": "Helpdesk Administrator",
    }
    
    GLOBAL_ADMIN_ROLE_ID = "62e90394-69f5-4237-9190-012177145e10"
    
    def __init__(
        self,
        graph_client: GraphClient,
        cache_service: Optional[CacheService] = None,
    ):
        self._graph = graph_client
        self._cache = cache_service
        self._tenant_id = graph_client.tenant_id
        
        logger.info("identity_collector_initialized", tenant_id=self._tenant_id)
    
    # ========================================================================
    # MFA Coverage
    # ========================================================================
    
    async def collect_mfa_coverage(self, force_refresh: bool = False) -> MFACoverage:
        """
        Collect MFA coverage metrics.
        
        Calculates coverage for both admins and all users.
        """
        # Check cache
        if not force_refresh and self._cache:
            cached = await self._cache.get(self._tenant_id, "mfa_coverage")
            if cached:
                return MFACoverage(**cached)
        
        # Fetch MFA registration details
        mfa_details = await self._graph.get_mfa_registration_details()
        
        # Calculate metrics
        total_users = len(mfa_details)
        users_with_mfa = len([u for u in mfa_details if u.get("is_mfa_registered")])
        
        admins = [u for u in mfa_details if u.get("is_admin")]
        total_admins = len(admins)
        admins_with_mfa = len([u for u in admins if u.get("is_mfa_registered")])
        
        coverage = MFACoverage(
            admin_coverage_percent=round((admins_with_mfa / total_admins * 100) if total_admins > 0 else 100, 1),
            user_coverage_percent=round((users_with_mfa / total_users * 100) if total_users > 0 else 0, 1),
            total_admins=total_admins,
            admins_with_mfa=admins_with_mfa,
            total_users=total_users,
            users_with_mfa=users_with_mfa,
            last_updated=datetime.utcnow(),
        )
        
        # Cache result
        if self._cache:
            await self._cache.set(self._tenant_id, "mfa_coverage", coverage.model_dump())
        
        logger.info(
            "mfa_coverage_collected",
            tenant_id=self._tenant_id,
            admin_coverage=coverage.admin_coverage_percent,
            user_coverage=coverage.user_coverage_percent,
        )
        
        return coverage
    
    async def get_users_without_mfa(self) -> list[dict]:
        """
        Get list of users without MFA enabled.
        
        Useful for IT staff dashboard.
        """
        mfa_details = await self._graph.get_mfa_registration_details()
        
        return [
            {
                "user_id": u.get("user_id"),
                "display_name": u.get("display_name"),
                "email": u.get("email"),
                "is_admin": u.get("is_admin"),
            }
            for u in mfa_details
            if not u.get("is_mfa_registered")
        ]
    
    # ========================================================================
    # Privileged Accounts
    # ========================================================================
    
    async def collect_privileged_accounts(self, force_refresh: bool = False) -> PrivilegedAccounts:
        """
        Collect privileged account metrics.
        
        Includes Global Admin count, all privileged roles, and PIM status.
        """
        # Check cache
        if not force_refresh and self._cache:
            cached = await self._cache.get(self._tenant_id, "privileged_accounts")
            if cached:
                return PrivilegedAccounts(**cached)
        
        # Fetch role assignments
        assignments = await self._graph.get_directory_role_assignments()
        roles = await self._graph.get_directory_roles()
        
        # Create role lookup
        role_lookup = {r["id"]: r["display_name"] for r in roles}
        
        # Count Global Admins
        global_admin_count = len([
            a for a in assignments
            if a.get("role_definition_id") == self.GLOBAL_ADMIN_ROLE_ID
        ])
        
        # Count all privileged role assignments
        privileged_assignments = [
            a for a in assignments
            if a.get("role_definition_id") in self.PRIVILEGED_ROLES
        ]
        
        # Get unique users with privileged roles
        privileged_users = set(a.get("principal_id") for a in privileged_assignments)
        
        # Note: PIM eligible/active would require additional Graph calls
        # For now, estimate based on assignment types
        
        accounts = PrivilegedAccounts(
            global_admin_count=global_admin_count,
            privileged_role_count=len(privileged_users),
            pim_eligible_count=0,  # Would need PIM-specific API
            pim_active_count=len(privileged_users),
            last_updated=datetime.utcnow(),
        )
        
        # Cache result
        if self._cache:
            await self._cache.set(self._tenant_id, "privileged_accounts", accounts.model_dump())
        
        logger.info(
            "privileged_accounts_collected",
            tenant_id=self._tenant_id,
            global_admins=accounts.global_admin_count,
            total_privileged=accounts.privileged_role_count,
        )
        
        return accounts
    
    async def get_privileged_users_detail(self) -> list[dict]:
        """
        Get detailed list of all privileged users.
        
        Useful for IT staff dashboard.
        """
        assignments = await self._graph.get_directory_role_assignments()
        roles = await self._graph.get_directory_roles()
        users = await self._graph.get_all_users()
        mfa_details = await self._graph.get_mfa_registration_details()
        
        # Create lookups
        role_lookup = {r["id"]: r["display_name"] for r in roles}
        user_lookup = {u["id"]: u for u in users}
        mfa_lookup = {m["user_id"]: m.get("is_mfa_registered", False) for m in mfa_details}
        
        # Group assignments by user
        user_roles: dict[str, list[str]] = {}
        for assignment in assignments:
            role_id = assignment.get("role_definition_id")
            if role_id in self.PRIVILEGED_ROLES:
                user_id = assignment.get("principal_id")
                role_name = role_lookup.get(role_id, role_id)
                
                if user_id not in user_roles:
                    user_roles[user_id] = []
                user_roles[user_id].append(role_name)
        
        # Build response
        result = []
        for user_id, roles_list in user_roles.items():
            user = user_lookup.get(user_id, {})
            result.append({
                "user_id": user_id,
                "display_name": user.get("display_name", "Unknown"),
                "email": user.get("email", ""),
                "roles": roles_list,
                "mfa_enabled": mfa_lookup.get(user_id, False),
            })
        
        return result
    
    # ========================================================================
    # Risky Users
    # ========================================================================
    
    async def collect_risky_users(self, force_refresh: bool = False) -> RiskyUsers:
        """
        Collect risky user metrics from Identity Protection.
        """
        # Check cache
        if not force_refresh and self._cache:
            cached = await self._cache.get(self._tenant_id, "risky_users")
            if cached:
                return RiskyUsers(**cached)
        
        # Fetch risky users
        risky = await self._graph.get_risky_users()
        
        # Count by risk level
        high = len([u for u in risky if u.get("risk_level") == "high"])
        medium = len([u for u in risky if u.get("risk_level") == "medium"])
        low = len([u for u in risky if u.get("risk_level") == "low"])
        
        # Users requiring investigation (at risk and not dismissed)
        requires_investigation = len([
            u for u in risky
            if u.get("risk_state") not in ["dismissed", "remediated", "confirmedSafe"]
        ])
        
        users = RiskyUsers(
            high_risk_count=high,
            medium_risk_count=medium,
            low_risk_count=low,
            requires_investigation=requires_investigation,
            last_updated=datetime.utcnow(),
        )
        
        # Cache result
        if self._cache:
            await self._cache.set(self._tenant_id, "risky_users", users.model_dump())
        
        logger.info(
            "risky_users_collected",
            tenant_id=self._tenant_id,
            high=high,
            medium=medium,
            low=low,
        )
        
        return users
    
    async def get_risky_users_detail(self) -> list[dict]:
        """
        Get detailed list of risky users.
        
        Useful for IT staff dashboard.
        """
        return await self._graph.get_risky_users()
    
    # ========================================================================
    # Conditional Access
    # ========================================================================
    
    async def collect_conditional_access_policies(self) -> list[dict]:
        """
        Collect Conditional Access policy status.
        """
        policies = await self._graph.get_conditional_access_policies()
        
        logger.info(
            "conditional_access_collected",
            tenant_id=self._tenant_id,
            policy_count=len(policies),
            enabled_count=len([p for p in policies if p.get("state") == "enabled"]),
        )
        
        return policies
