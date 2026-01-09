"""
Backup Collector for Azure Security Platform V2

Collects backup and recovery data - CRITICAL FOR RANSOMWARE READINESS.
"""
from datetime import datetime, timedelta
from typing import Optional
import structlog

from ..services.azure_client import AzureClient
from ..services.cache_service import CacheService
from ..models.schemas import (
    BackupHealth,
    RecoveryReadiness,
    BackupStatus,
)

logger = structlog.get_logger(__name__)


class BackupCollector:
    """
    Collects Azure Backup health metrics.
    
    This is CRITICAL for post-ransomware visibility.
    """
    
    # Default RTO/RPO targets (configurable per tenant)
    DEFAULT_RTO_HOURS = 24
    DEFAULT_RPO_HOURS = 4
    
    def __init__(
        self,
        azure_client: AzureClient,
        cache_service: Optional[CacheService] = None,
    ):
        self._azure = azure_client
        self._cache = cache_service
        self._tenant_id = azure_client.tenant_id
        
        logger.info("backup_collector_initialized", tenant_id=self._tenant_id)
    
    async def collect_backup_health(self, force_refresh: bool = False) -> BackupHealth:
        """
        Collect backup health metrics.
        
        Returns:
            BackupHealth with protection %, last backup time, and status
        """
        # Check cache
        if not force_refresh and self._cache:
            cached = await self._cache.get(self._tenant_id, "backup_health")
            if cached:
                return BackupHealth(**cached)
        
        # Fetch all backup data
        backup_data = await self._azure.get_all_backup_data()
        summary = backup_data.get("summary", {})
        
        # Calculate protected percentage
        # In production, we'd compare protected items against a critical systems inventory
        total_protected = summary.get("total_protected_items", 0)
        
        # Estimate total critical systems (would be configured per tenant)
        # For now, assume 90-100% of protected items are critical
        estimated_critical = max(total_protected, int(total_protected * 1.1))
        
        protected_percent = (total_protected / estimated_critical * 100) if estimated_critical > 0 else 0
        
        # Get last successful backup time
        last_backup = summary.get("last_successful_backup")
        hours_since = summary.get("hours_since_backup")
        
        # Determine overall status
        status = self._determine_backup_status(
            protected_percent=protected_percent,
            hours_since_backup=hours_since,
            job_success_rate=summary.get("job_success_rate", 0),
        )
        
        health = BackupHealth(
            protected_percent=round(protected_percent, 1),
            total_protected_items=total_protected,
            total_critical_systems=estimated_critical,
            last_successful_backup=last_backup,
            hours_since_backup=hours_since,
            status=status,
            last_updated=datetime.utcnow(),
        )
        
        # Cache result
        if self._cache:
            await self._cache.set(self._tenant_id, "backup_health", health.model_dump())
        
        logger.info(
            "backup_health_collected",
            tenant_id=self._tenant_id,
            protected_percent=health.protected_percent,
            hours_since_backup=hours_since,
            status=status.value,
        )
        
        return health
    
    async def collect_recovery_readiness(
        self,
        rto_target_hours: int = DEFAULT_RTO_HOURS,
        rpo_target_hours: int = DEFAULT_RPO_HOURS,
        force_refresh: bool = False,
    ) -> RecoveryReadiness:
        """
        Assess recovery readiness (RTO/RPO status).
        
        Args:
            rto_target_hours: Recovery Time Objective target
            rpo_target_hours: Recovery Point Objective target
            
        Returns:
            RecoveryReadiness with RTO/RPO status indicators
        """
        # Check cache
        if not force_refresh and self._cache:
            cached = await self._cache.get(self._tenant_id, "recovery_readiness")
            if cached:
                return RecoveryReadiness(**cached)
        
        # Fetch backup data
        backup_data = await self._azure.get_all_backup_data()
        summary = backup_data.get("summary", {})
        
        # Calculate RPO actual (hours since last backup)
        hours_since = summary.get("hours_since_backup")
        rpo_actual = hours_since if hours_since is not None else None
        
        # Estimate RTO based on backup size and historical recovery times
        # In production, this would use actual recovery test data
        rto_actual = self._estimate_rto(backup_data.get("protected_items", []))
        
        # Determine status
        rto_status = self._determine_rto_status(rto_actual, rto_target_hours)
        rpo_status = self._determine_rpo_status(rpo_actual, rpo_target_hours)
        
        # Overall status is worst of RTO/RPO
        if rto_status == BackupStatus.CRITICAL or rpo_status == BackupStatus.CRITICAL:
            overall = BackupStatus.CRITICAL
        elif rto_status == BackupStatus.WARNING or rpo_status == BackupStatus.WARNING:
            overall = BackupStatus.WARNING
        else:
            overall = BackupStatus.HEALTHY
        
        readiness = RecoveryReadiness(
            rto_status=rto_status,
            rpo_status=rpo_status,
            rto_target_hours=rto_target_hours,
            rpo_target_hours=rpo_target_hours,
            rto_actual_hours=rto_actual,
            rpo_actual_hours=rpo_actual,
            overall_status=overall,
            last_updated=datetime.utcnow(),
        )
        
        # Cache result
        if self._cache:
            await self._cache.set(self._tenant_id, "recovery_readiness", readiness.model_dump())
        
        logger.info(
            "recovery_readiness_collected",
            tenant_id=self._tenant_id,
            rto_status=rto_status.value,
            rpo_status=rpo_status.value,
            overall=overall.value,
        )
        
        return readiness
    
    async def get_backup_jobs(self, days: int = 7) -> list[dict]:
        """
        Get recent backup job details.
        
        Useful for IT staff dashboard.
        """
        backup_data = await self._azure.get_all_backup_data()
        return backup_data.get("jobs", [])
    
    async def get_protected_items(self) -> list[dict]:
        """
        Get all protected items.
        
        Useful for IT staff dashboard.
        """
        backup_data = await self._azure.get_all_backup_data()
        return backup_data.get("protected_items", [])
    
    async def get_unprotected_critical_systems(self) -> list[dict]:
        """
        Identify critical systems without backup protection.
        
        This would compare against a configured critical systems inventory.
        """
        # In production, this would:
        # 1. Get list of critical systems from config/cosmos
        # 2. Compare against protected items
        # 3. Return unprotected items
        
        # For now, return empty (would need critical systems inventory)
        return []
    
    async def get_failed_jobs(self, days: int = 7) -> list[dict]:
        """
        Get failed backup jobs.
        
        Critical for identifying backup issues.
        """
        jobs = await self.get_backup_jobs(days)
        return [j for j in jobs if j.get("status") == "Failed"]
    
    def _determine_backup_status(
        self,
        protected_percent: float,
        hours_since_backup: Optional[int],
        job_success_rate: float,
    ) -> BackupStatus:
        """
        Determine overall backup health status.
        """
        # Critical conditions
        if protected_percent < 80:
            return BackupStatus.CRITICAL
        if hours_since_backup is not None and hours_since_backup > 48:
            return BackupStatus.CRITICAL
        if job_success_rate < 80:
            return BackupStatus.CRITICAL
        
        # Warning conditions
        if protected_percent < 95:
            return BackupStatus.WARNING
        if hours_since_backup is not None and hours_since_backup > 24:
            return BackupStatus.WARNING
        if job_success_rate < 95:
            return BackupStatus.WARNING
        
        return BackupStatus.HEALTHY
    
    def _determine_rto_status(
        self,
        actual: Optional[int],
        target: int,
    ) -> BackupStatus:
        """Determine RTO status."""
        if actual is None:
            return BackupStatus.UNKNOWN
        if actual > target * 1.5:
            return BackupStatus.CRITICAL
        if actual > target:
            return BackupStatus.WARNING
        return BackupStatus.HEALTHY
    
    def _determine_rpo_status(
        self,
        actual: Optional[int],
        target: int,
    ) -> BackupStatus:
        """Determine RPO status."""
        if actual is None:
            return BackupStatus.UNKNOWN
        if actual > target * 2:
            return BackupStatus.CRITICAL
        if actual > target:
            return BackupStatus.WARNING
        return BackupStatus.HEALTHY
    
    def _estimate_rto(self, protected_items: list[dict]) -> int:
        """
        Estimate RTO based on protected items.
        
        In production, this would use:
        - Historical recovery test times
        - Backup sizes
        - Network throughput estimates
        """
        # Simple estimation: base time + time per item
        base_hours = 4
        per_item_hours = 0.5
        
        return int(base_hours + len(protected_items) * per_item_hours)
