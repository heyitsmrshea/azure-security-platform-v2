"""
Scheduler Service for Azure Security Platform V2

Handles scheduled data collection jobs using APScheduler.
"""
import asyncio
from datetime import datetime
from typing import Optional, Callable
import structlog

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.executors.asyncio import AsyncIOExecutor

logger = structlog.get_logger(__name__)


class SchedulerService:
    """
    Manages scheduled data collection jobs.
    
    Collection Frequencies (from requirements):
    - Secure Score: Every 4 hours
    - MFA Status: Every 4 hours
    - Risky Users: Every 1 hour
    - Security Alerts: Every 15 minutes
    - Conditional Access: Every 1 hour
    - PIM Assignments: Every 1 hour
    - Audit Logs: Every 30 minutes
    - Device Compliance: Every 4 hours
    - Guest Users: Daily
    - Backup Status: Every 4 hours
    """
    
    def __init__(self):
        jobstores = {
            'default': MemoryJobStore()
        }
        executors = {
            'default': AsyncIOExecutor()
        }
        job_defaults = {
            'coalesce': True,  # Combine missed jobs into one
            'max_instances': 1,  # Only one instance of each job
            'misfire_grace_time': 60 * 5,  # 5 minutes grace period
        }
        
        self._scheduler = AsyncIOScheduler(
            jobstores=jobstores,
            executors=executors,
            job_defaults=job_defaults,
        )
        
        self._jobs = {}
        logger.info("scheduler_service_initialized")
    
    def start(self):
        """Start the scheduler."""
        if not self._scheduler.running:
            self._scheduler.start()
            logger.info("scheduler_started")
    
    def shutdown(self, wait: bool = True):
        """Shutdown the scheduler."""
        if self._scheduler.running:
            self._scheduler.shutdown(wait=wait)
            logger.info("scheduler_shutdown")
    
    def add_job(
        self,
        job_id: str,
        func: Callable,
        trigger: str,
        **trigger_args,
    ) -> str:
        """
        Add a scheduled job.
        
        Args:
            job_id: Unique job identifier
            func: Async function to execute
            trigger: 'interval' or 'cron'
            **trigger_args: Arguments for the trigger
            
        Returns:
            Job ID
        """
        if trigger == 'interval':
            trigger_obj = IntervalTrigger(**trigger_args)
        elif trigger == 'cron':
            trigger_obj = CronTrigger(**trigger_args)
        else:
            raise ValueError(f"Unknown trigger type: {trigger}")
        
        job = self._scheduler.add_job(
            func,
            trigger_obj,
            id=job_id,
            replace_existing=True,
        )
        
        self._jobs[job_id] = job
        logger.info("job_added", job_id=job_id, trigger=trigger)
        
        return job_id
    
    def remove_job(self, job_id: str) -> bool:
        """Remove a scheduled job."""
        try:
            self._scheduler.remove_job(job_id)
            self._jobs.pop(job_id, None)
            logger.info("job_removed", job_id=job_id)
            return True
        except Exception as e:
            logger.warning("job_remove_failed", job_id=job_id, error=str(e))
            return False
    
    def pause_job(self, job_id: str) -> bool:
        """Pause a scheduled job."""
        try:
            self._scheduler.pause_job(job_id)
            logger.info("job_paused", job_id=job_id)
            return True
        except Exception as e:
            logger.warning("job_pause_failed", job_id=job_id, error=str(e))
            return False
    
    def resume_job(self, job_id: str) -> bool:
        """Resume a paused job."""
        try:
            self._scheduler.resume_job(job_id)
            logger.info("job_resumed", job_id=job_id)
            return True
        except Exception as e:
            logger.warning("job_resume_failed", job_id=job_id, error=str(e))
            return False
    
    def get_job_status(self, job_id: str) -> Optional[dict]:
        """Get status of a job."""
        job = self._scheduler.get_job(job_id)
        if not job:
            return None
        
        return {
            "id": job.id,
            "name": job.name,
            "next_run": job.next_run_time.isoformat() if job.next_run_time else None,
            "pending": job.pending,
        }
    
    def get_all_jobs(self) -> list[dict]:
        """Get status of all jobs."""
        jobs = []
        for job in self._scheduler.get_jobs():
            jobs.append({
                "id": job.id,
                "name": job.name,
                "next_run": job.next_run_time.isoformat() if job.next_run_time else None,
                "pending": job.pending,
            })
        return jobs


class DataCollectionScheduler:
    """
    Manages data collection schedules for all tenants.
    """
    
    def __init__(self, scheduler: SchedulerService):
        self._scheduler = scheduler
        self._tenant_collectors = {}
        
    def setup_tenant_collection(
        self,
        tenant_id: str,
        collectors: dict,
    ):
        """
        Set up data collection jobs for a tenant.
        
        Args:
            tenant_id: Tenant identifier
            collectors: Dict of collector name -> collector instance
        """
        jobs = []
        
        # Secure Score - every 4 hours
        if 'secure_score' in collectors:
            job_id = self._scheduler.add_job(
                f"{tenant_id}_secure_score",
                collectors['secure_score'].collect,
                'interval',
                hours=4,
            )
            jobs.append(job_id)
        
        # Identity (MFA, Risky Users) - hourly
        if 'identity' in collectors:
            # MFA - every 4 hours
            job_id = self._scheduler.add_job(
                f"{tenant_id}_mfa",
                collectors['identity'].collect_mfa_coverage,
                'interval',
                hours=4,
            )
            jobs.append(job_id)
            
            # Risky Users - every hour
            job_id = self._scheduler.add_job(
                f"{tenant_id}_risky_users",
                collectors['identity'].collect_risky_users,
                'interval',
                hours=1,
            )
            jobs.append(job_id)
            
            # Privileged Accounts - every hour
            job_id = self._scheduler.add_job(
                f"{tenant_id}_privileged",
                collectors['identity'].collect_privileged_accounts,
                'interval',
                hours=1,
            )
            jobs.append(job_id)
        
        # Threats (Alerts) - every 15 minutes
        if 'threats' in collectors:
            job_id = self._scheduler.add_job(
                f"{tenant_id}_alerts",
                collectors['threats'].collect_alert_summary,
                'interval',
                minutes=15,
            )
            jobs.append(job_id)
        
        # Devices - every 4 hours
        if 'devices' in collectors:
            job_id = self._scheduler.add_job(
                f"{tenant_id}_devices",
                collectors['devices'].collect_device_compliance,
                'interval',
                hours=4,
            )
            jobs.append(job_id)
        
        # Backup - every 4 hours
        if 'backup' in collectors:
            job_id = self._scheduler.add_job(
                f"{tenant_id}_backup",
                collectors['backup'].collect_backup_health,
                'interval',
                hours=4,
            )
            jobs.append(job_id)
            
            job_id = self._scheduler.add_job(
                f"{tenant_id}_recovery",
                collectors['backup'].collect_recovery_readiness,
                'interval',
                hours=4,
            )
            jobs.append(job_id)
        
        # Vendor Risk (Guests) - daily
        if 'vendor_risk' in collectors:
            job_id = self._scheduler.add_job(
                f"{tenant_id}_guests",
                collectors['vendor_risk'].get_guest_user_inventory,
                'cron',
                hour=2,  # 2 AM
            )
            jobs.append(job_id)
        
        # Accountability - every 4 hours
        if 'accountability' in collectors:
            job_id = self._scheduler.add_job(
                f"{tenant_id}_accountability",
                collectors['accountability'].collect_patch_sla_compliance,
                'interval',
                hours=4,
            )
            jobs.append(job_id)
        
        self._tenant_collectors[tenant_id] = jobs
        logger.info("tenant_collection_setup", tenant_id=tenant_id, job_count=len(jobs))
    
    def remove_tenant_collection(self, tenant_id: str):
        """Remove all collection jobs for a tenant."""
        jobs = self._tenant_collectors.pop(tenant_id, [])
        for job_id in jobs:
            self._scheduler.remove_job(job_id)
        logger.info("tenant_collection_removed", tenant_id=tenant_id, job_count=len(jobs))
    
    async def run_immediate_collection(self, tenant_id: str, collectors: dict):
        """
        Run immediate data collection for a tenant (on-demand sync).
        """
        logger.info("immediate_collection_started", tenant_id=tenant_id)
        
        tasks = []
        
        if 'secure_score' in collectors:
            tasks.append(collectors['secure_score'].collect(force_refresh=True))
        
        if 'identity' in collectors:
            tasks.append(collectors['identity'].collect_mfa_coverage(force_refresh=True))
            tasks.append(collectors['identity'].collect_risky_users(force_refresh=True))
            tasks.append(collectors['identity'].collect_privileged_accounts(force_refresh=True))
        
        if 'threats' in collectors:
            tasks.append(collectors['threats'].collect_alert_summary(force_refresh=True))
        
        if 'devices' in collectors:
            tasks.append(collectors['devices'].collect_device_compliance(force_refresh=True))
        
        if 'backup' in collectors:
            tasks.append(collectors['backup'].collect_backup_health(force_refresh=True))
            tasks.append(collectors['backup'].collect_recovery_readiness(force_refresh=True))
        
        # Run all collectors concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        success_count = sum(1 for r in results if not isinstance(r, Exception))
        error_count = sum(1 for r in results if isinstance(r, Exception))
        
        logger.info(
            "immediate_collection_completed",
            tenant_id=tenant_id,
            success=success_count,
            errors=error_count,
        )
        
        return {
            "tenant_id": tenant_id,
            "success_count": success_count,
            "error_count": error_count,
            "timestamp": datetime.utcnow().isoformat(),
        }


# Global scheduler instance
scheduler_service = SchedulerService()
data_collection_scheduler = DataCollectionScheduler(scheduler_service)
