"""
Azure Resource Manager Client for Azure Security Platform V2

Handles Azure Backup and Recovery Services APIs.
"""
from datetime import datetime, timedelta
from typing import Optional
import structlog

from azure.identity import ClientSecretCredential
from azure.mgmt.recoveryservices import RecoveryServicesClient
from azure.mgmt.recoveryservicesbackup import RecoveryServicesBackupClient
from azure.mgmt.recoveryservicesbackup.models import (
    JobQueryObject,
    BackupManagementType,
)

logger = structlog.get_logger(__name__)


class AzureClient:
    """
    Azure Resource Manager client for backup and recovery data.
    
    Handles:
    - Recovery Services Vaults
    - Backup Jobs
    - Protected Items
    - Backup Policies
    """
    
    def __init__(
        self,
        tenant_id: str,
        client_id: str,
        client_secret: str,
        subscription_id: str,
    ):
        """
        Initialize Azure RM client with service principal credentials.
        
        Args:
            tenant_id: Azure AD tenant ID
            client_id: App registration client ID
            client_secret: App registration client secret
            subscription_id: Azure subscription ID
        """
        self.tenant_id = tenant_id
        self.subscription_id = subscription_id
        
        # Create credential
        self._credential = ClientSecretCredential(
            tenant_id=tenant_id,
            client_id=client_id,
            client_secret=client_secret,
        )
        
        # Create Recovery Services clients
        self._rs_client = RecoveryServicesClient(
            credential=self._credential,
            subscription_id=subscription_id,
        )
        
        self._backup_client = RecoveryServicesBackupClient(
            credential=self._credential,
            subscription_id=subscription_id,
        )
        
        logger.info("azure_client_initialized", tenant_id=tenant_id, subscription_id=subscription_id)
    
    # ========================================================================
    # Recovery Services Vaults
    # ========================================================================
    
    async def get_recovery_vaults(self) -> list[dict]:
        """
        Get all Recovery Services vaults in the subscription.
        """
        try:
            vaults = []
            for vault in self._rs_client.vaults.list_by_subscription_id():
                vaults.append({
                    "id": vault.id,
                    "name": vault.name,
                    "location": vault.location,
                    "resource_group": self._extract_resource_group(vault.id),
                    "type": vault.type,
                    "sku": vault.sku.name if vault.sku else None,
                    "provisioning_state": vault.properties.provisioning_state if vault.properties else None,
                })
            
            logger.info("recovery_vaults_fetched", count=len(vaults))
            return vaults
        except Exception as e:
            logger.error("recovery_vaults_error", error=str(e))
            raise
    
    def _extract_resource_group(self, resource_id: str) -> str:
        """Extract resource group name from resource ID."""
        parts = resource_id.split("/")
        try:
            rg_index = parts.index("resourceGroups") + 1
            return parts[rg_index]
        except (ValueError, IndexError):
            return ""
    
    # ========================================================================
    # Backup Jobs
    # ========================================================================
    
    async def get_backup_jobs(
        self,
        vault_name: str,
        resource_group: str,
        days: int = 7,
    ) -> list[dict]:
        """
        Get backup jobs for a specific vault.
        
        Args:
            vault_name: Name of the Recovery Services vault
            resource_group: Resource group containing the vault
            days: Number of days to look back for jobs
        """
        try:
            start_time = datetime.utcnow() - timedelta(days=days)
            
            filter_query = JobQueryObject(
                start_time=start_time.isoformat() + "Z",
            )
            
            jobs = []
            for job in self._backup_client.backup_jobs.list(
                vault_name=vault_name,
                resource_group_name=resource_group,
            ):
                jobs.append({
                    "id": job.id,
                    "name": job.name,
                    "vault_name": vault_name,
                    "status": job.properties.status if job.properties else "Unknown",
                    "operation": job.properties.operation if job.properties else None,
                    "start_time": job.properties.start_time if job.properties else None,
                    "end_time": job.properties.end_time if job.properties else None,
                    "duration_seconds": self._calculate_duration(job.properties) if job.properties else None,
                    "entity_friendly_name": job.properties.entity_friendly_name if job.properties else None,
                    "backup_management_type": str(job.properties.backup_management_type) if job.properties and job.properties.backup_management_type else None,
                    "error_details": self._extract_error_details(job.properties) if job.properties else None,
                })
            
            logger.info("backup_jobs_fetched", vault=vault_name, count=len(jobs))
            return jobs
        except Exception as e:
            logger.error("backup_jobs_error", vault=vault_name, error=str(e))
            raise
    
    def _calculate_duration(self, properties) -> Optional[int]:
        """Calculate job duration in seconds."""
        if not properties or not properties.start_time:
            return None
        end_time = properties.end_time or datetime.utcnow()
        if isinstance(properties.start_time, str):
            return None  # Can't calculate without proper datetime
        return int((end_time - properties.start_time).total_seconds())
    
    def _extract_error_details(self, properties) -> Optional[str]:
        """Extract error details from job properties."""
        if not properties or not hasattr(properties, 'error_details'):
            return None
        if not properties.error_details:
            return None
        return properties.error_details.message if hasattr(properties.error_details, 'message') else str(properties.error_details)
    
    # ========================================================================
    # Protected Items
    # ========================================================================
    
    async def get_protected_items(
        self,
        vault_name: str,
        resource_group: str,
    ) -> list[dict]:
        """
        Get all backup protected items in a vault.
        
        Args:
            vault_name: Name of the Recovery Services vault
            resource_group: Resource group containing the vault
        """
        try:
            items = []
            for item in self._backup_client.backup_protected_items.list(
                vault_name=vault_name,
                resource_group_name=resource_group,
            ):
                props = item.properties if item.properties else None
                items.append({
                    "id": item.id,
                    "name": item.name,
                    "vault_name": vault_name,
                    "friendly_name": props.friendly_name if props else None,
                    "protection_status": props.protection_status if props else None,
                    "protection_state": str(props.protection_state) if props and props.protection_state else None,
                    "health_status": str(props.health_status) if props and hasattr(props, 'health_status') else None,
                    "last_backup_status": props.last_backup_status if props and hasattr(props, 'last_backup_status') else None,
                    "last_backup_time": props.last_backup_time if props and hasattr(props, 'last_backup_time') else None,
                    "policy_id": props.policy_id if props and hasattr(props, 'policy_id') else None,
                    "source_resource_id": props.source_resource_id if props and hasattr(props, 'source_resource_id') else None,
                    "workload_type": str(props.workload_type) if props and hasattr(props, 'workload_type') else None,
                })
            
            logger.info("protected_items_fetched", vault=vault_name, count=len(items))
            return items
        except Exception as e:
            logger.error("protected_items_error", vault=vault_name, error=str(e))
            raise
    
    # ========================================================================
    # Aggregate Methods
    # ========================================================================
    
    async def get_all_backup_data(self) -> dict:
        """
        Get all backup-related data across all vaults.
        
        Returns comprehensive backup health information.
        """
        vaults = await self.get_recovery_vaults()
        
        all_jobs = []
        all_protected_items = []
        
        for vault in vaults:
            vault_name = vault["name"]
            resource_group = vault["resource_group"]
            
            try:
                jobs = await self.get_backup_jobs(vault_name, resource_group)
                all_jobs.extend(jobs)
            except Exception as e:
                logger.warning("vault_jobs_error", vault=vault_name, error=str(e))
            
            try:
                items = await self.get_protected_items(vault_name, resource_group)
                all_protected_items.extend(items)
            except Exception as e:
                logger.warning("vault_items_error", vault=vault_name, error=str(e))
        
        return {
            "vaults": vaults,
            "jobs": all_jobs,
            "protected_items": all_protected_items,
            "summary": self._calculate_backup_summary(all_jobs, all_protected_items),
        }
    
    def _calculate_backup_summary(
        self,
        jobs: list[dict],
        protected_items: list[dict],
    ) -> dict:
        """
        Calculate backup health summary.
        """
        total_items = len(protected_items)
        
        # Find most recent successful backup
        successful_jobs = [
            j for j in jobs 
            if j.get("status") in ["Completed", "CompletedWithWarnings"]
            and j.get("operation") == "Backup"
        ]
        
        last_successful = None
        if successful_jobs:
            sorted_jobs = sorted(
                successful_jobs,
                key=lambda x: x.get("end_time") or x.get("start_time") or datetime.min,
                reverse=True,
            )
            if sorted_jobs:
                last_successful = sorted_jobs[0].get("end_time") or sorted_jobs[0].get("start_time")
        
        # Calculate job success rate
        recent_jobs = [j for j in jobs if j.get("operation") == "Backup"]
        successful_count = len([j for j in recent_jobs if j.get("status") in ["Completed", "CompletedWithWarnings"]])
        failed_count = len([j for j in recent_jobs if j.get("status") in ["Failed"]])
        
        # Calculate hours since last backup
        hours_since_backup = None
        if last_successful:
            if isinstance(last_successful, datetime):
                hours_since_backup = int((datetime.utcnow() - last_successful).total_seconds() / 3600)
        
        return {
            "total_protected_items": total_items,
            "total_vaults": len(set(j.get("vault_name") for j in jobs)),
            "recent_jobs_count": len(recent_jobs),
            "successful_jobs_count": successful_count,
            "failed_jobs_count": failed_count,
            "job_success_rate": (successful_count / len(recent_jobs) * 100) if recent_jobs else 0,
            "last_successful_backup": last_successful,
            "hours_since_backup": hours_since_backup,
        }
