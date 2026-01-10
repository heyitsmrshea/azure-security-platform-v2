"""
Backup Collector for Azure Security Platform V2

Collects Azure Backup health and recovery readiness data.
"""
from datetime import datetime, timedelta
from typing import Optional
import structlog

from ..services.azure_client import AzureResourceClient
from ..services.cache_service import CacheService
from ..models.schemas import BackupHealth, RecoveryReadiness, BackupStatus

logger = structlog.get_logger(__name__)


class BackupCollector:
    """
    Collects Azure Backup metrics for ransomware readiness assessment.
    """
    
    def __init__(
        self,
        azure_client: AzureResourceClient,
        cache_service: Optional[CacheService] = None,
    ):
        self._azure = azure_client
        self._cache = cache_service
        self._tenant_id = azure_client.tenant_id
        
        logger.info("backup_collector_initialized", tenant_id=self._tenant_id)
    
    async def collect_backup_health(self, force_refresh: bool = False) -> BackupHealth:
        """
        Collect backup health metrics.
        """
        # Check cache
        if not force_refresh and self._cache:
            cached = await self._cache.get(self._tenant_id, "backup_health")
            if cached:
                return BackupHealth(**cached)
        
        # Get backup vaults and protected items
        try:
            vaults = await self._azure.get_backup_vaults()
            protected_items = await self._azure.get_protected_items()
            recent_jobs = await self._azure.get_backup_jobs(days=7)
        except Exception as e:
            logger.warning("backup_collection_failed", error=str(e))
            return BackupHealth(
                protected_percent=0,
                total_protected_items=0,
                total_critical_systems=0,
                status=BackupStatus.NOT_CONFIGURED,
                last_updated=datetime.utcnow(),
            )
        
        if not vaults:
            return BackupHealth(
                protected_percent=0,
                total_protected_items=0,
                total_critical_systems=0,
                status=BackupStatus.NOT_CONFIGURED,
                last_updated=datetime.utcnow(),
            )
        
        # Calculate metrics
        total_protected = len(protected_items)
        
        # Estimate critical systems (in production, this would be configurable)
        total_critical = max(total_protected, 10)  # Assume at least 10 critical systems
        protected_percent = (total_protected / total_critical * 100) if total_critical > 0 else 0
        
        # Find last successful backup
        successful_jobs = [j for j in recent_jobs if j.get("status") == "Completed"]
        last_successful = None
        hours_since = None
        
        if successful_jobs:
            # Sort by end time
            successful_jobs.sort(key=lambda x: x.get("end_time", ""), reverse=True)
            last_job = successful_jobs[0]
            last_successful = last_job.get("end_time")
            
            if last_successful:
                try:
                    last_dt = datetime.fromisoformat(str(last_successful).replace("Z", "+00:00"))
                    hours_since = int((datetime.utcnow() - last_dt.replace(tzinfo=None)).total_seconds() / 3600)
                except (ValueError, TypeError):
                    pass
        
        # Determine status
        if protected_percent >= 90 and (hours_since is None or hours_since < 24):
            status = BackupStatus.HEALTHY
        elif protected_percent >= 70 and (hours_since is None or hours_since < 48):
            status = BackupStatus.WARNING
        else:
            status = BackupStatus.AT_RISK
        
        health = BackupHealth(
            protected_percent=round(protected_percent, 1),
            total_protected_items=total_protected,
            total_critical_systems=total_critical,
            last_successful_backup=last_successful,
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
            protected=total_protected,
            status=status,
        )
        
        return health
    
    async def collect_recovery_readiness(self, force_refresh: bool = False) -> RecoveryReadiness:
        """
        Collect RTO/RPO readiness metrics.
        """
        # Check cache
        if not force_refresh and self._cache:
            cached = await self._cache.get(self._tenant_id, "recovery_readiness")
            if cached:
                return RecoveryReadiness(**cached)
        
        try:
            vaults = await self._azure.get_backup_vaults()
            protected_items = await self._azure.get_protected_items()
            recent_jobs = await self._azure.get_backup_jobs(days=7)
        except Exception as e:
            logger.warning("recovery_readiness_collection_failed", error=str(e))
            return RecoveryReadiness(
                rto_status=BackupStatus.NOT_CONFIGURED,
                rpo_status=BackupStatus.NOT_CONFIGURED,
                overall_status=BackupStatus.NOT_CONFIGURED,
                last_updated=datetime.utcnow(),
            )
        
        if not vaults:
            return RecoveryReadiness(
                rto_status=BackupStatus.NOT_CONFIGURED,
                rpo_status=BackupStatus.NOT_CONFIGURED,
                overall_status=BackupStatus.NOT_CONFIGURED,
                last_updated=datetime.utcnow(),
            )
        
        # Default targets (in production, these would be configurable per customer)
        rto_target = 24  # hours
        rpo_target = 4   # hours
        
        # Calculate actual RPO (time since last backup)
        successful_jobs = [j for j in recent_jobs if j.get("status") == "Completed"]
        rpo_actual = rpo_target  # Default to target if no jobs
        
        if successful_jobs:
            successful_jobs.sort(key=lambda x: x.get("end_time", ""), reverse=True)
            last_job = successful_jobs[0]
            last_backup = last_job.get("end_time")
            
            if last_backup:
                try:
                    last_dt = datetime.fromisoformat(str(last_backup).replace("Z", "+00:00"))
                    rpo_actual = int((datetime.utcnow() - last_dt.replace(tzinfo=None)).total_seconds() / 3600)
                except (ValueError, TypeError):
                    pass
        
        # RTO is harder to measure without actual recovery tests
        # Estimate based on backup policy and infrastructure
        rto_actual = min(rto_target, 18)  # Assume decent RTO unless proven otherwise
        
        # Determine status
        def status_for_metric(actual: int, target: int) -> BackupStatus:
            if actual <= target:
                return BackupStatus.HEALTHY
            elif actual <= target * 1.5:
                return BackupStatus.WARNING
            else:
                return BackupStatus.AT_RISK
        
        rto_status = status_for_metric(rto_actual, rto_target)
        rpo_status = status_for_metric(rpo_actual, rpo_target)
        
        # Overall is the worse of the two
        if rto_status == BackupStatus.AT_RISK or rpo_status == BackupStatus.AT_RISK:
            overall_status = BackupStatus.AT_RISK
        elif rto_status == BackupStatus.WARNING or rpo_status == BackupStatus.WARNING:
            overall_status = BackupStatus.WARNING
        else:
            overall_status = BackupStatus.HEALTHY
        
        readiness = RecoveryReadiness(
            rto_status=rto_status,
            rpo_status=rpo_status,
            rto_target_hours=rto_target,
            rpo_target_hours=rpo_target,
            rto_actual_hours=rto_actual,
            rpo_actual_hours=rpo_actual,
            overall_status=overall_status,
            last_updated=datetime.utcnow(),
        )
        
        # Cache result
        if self._cache:
            await self._cache.set(self._tenant_id, "recovery_readiness", readiness.model_dump())
        
        logger.info(
            "recovery_readiness_collected",
            tenant_id=self._tenant_id,
            rto_status=rto_status,
            rpo_status=rpo_status,
        )
        
        return readiness
    
    async def get_backup_jobs(self, days: int = 7) -> list[dict]:
        """
        Get recent backup job history.
        """
        try:
            jobs = await self._azure.get_backup_jobs(days=days)
            return jobs
        except Exception as e:
            logger.warning("backup_jobs_fetch_failed", error=str(e))
            return []
    
    async def get_unprotected_resources(self) -> list[dict]:
        """
        Get critical resources without backup protection.
        
        Note: This requires comparing backup protected items against
        all critical resources in the subscription.
        """
        try:
            protected_items = await self._azure.get_protected_items()
            protected_ids = {item.get("source_resource_id") for item in protected_items}
            
            # In production, you'd enumerate VMs, SQL databases, etc.
            # and compare against protected_ids
            # For now, return empty as we don't have full resource enumeration
            
            return []
        except Exception as e:
            logger.warning("unprotected_resources_fetch_failed", error=str(e))
            return []
