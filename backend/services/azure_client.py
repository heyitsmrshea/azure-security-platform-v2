"""
Azure Resource Manager Client for Azure Security Platform V2

Handles Azure ARM API interactions for backup and infrastructure data.
"""
from datetime import datetime, timedelta
from typing import Optional
import structlog

from azure.identity import ClientSecretCredential
from azure.mgmt.recoveryservices import RecoveryServicesClient
from azure.mgmt.recoveryservicesbackup import RecoveryServicesBackupClient
from azure.mgmt.resource import SubscriptionClient

logger = structlog.get_logger(__name__)


class AzureResourceClient:
    """
    Azure Resource Manager client for infrastructure data collection.
    
    Handles:
    - Recovery Services (Backup) vaults
    - Backup jobs and protected items
    - Subscription enumeration
    """
    
    def __init__(
        self,
        tenant_id: str,
        client_id: str,
        client_secret: str,
    ):
        """
        Initialize Azure RM client.
        
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
        
        # Will be populated with subscription IDs
        self._subscriptions: list[str] = []
        
        logger.info("azure_client_initialized", tenant_id=tenant_id)
    
    async def _get_subscriptions(self) -> list[str]:
        """Get all accessible subscription IDs."""
        if self._subscriptions:
            return self._subscriptions
        
        try:
            sub_client = SubscriptionClient(self._credential)
            self._subscriptions = [sub.subscription_id for sub in sub_client.subscriptions.list()]
            logger.info("subscriptions_enumerated", count=len(self._subscriptions))
            return self._subscriptions
        except Exception as e:
            logger.error("subscription_enumeration_failed", error=str(e))
            return []
    
    async def get_backup_vaults(self) -> list[dict]:
        """
        Get all Recovery Services vaults across subscriptions.
        """
        vaults = []
        subscriptions = await self._get_subscriptions()
        
        for sub_id in subscriptions:
            try:
                rs_client = RecoveryServicesClient(self._credential, sub_id)
                
                for vault in rs_client.vaults.list_by_subscription_id():
                    vaults.append({
                        "id": vault.id,
                        "name": vault.name,
                        "location": vault.location,
                        "subscription_id": sub_id,
                        "resource_group": vault.id.split("/")[4] if vault.id else None,
                        "type": vault.type,
                    })
            except Exception as e:
                logger.warning(
                    "vault_enumeration_failed",
                    subscription_id=sub_id,
                    error=str(e),
                )
        
        logger.info("backup_vaults_collected", count=len(vaults))
        return vaults
    
    async def get_protected_items(self) -> list[dict]:
        """
        Get all backup protected items across vaults.
        """
        items = []
        vaults = await self.get_backup_vaults()
        
        for vault in vaults:
            try:
                sub_id = vault.get("subscription_id")
                rg = vault.get("resource_group")
                vault_name = vault.get("name")
                
                if not all([sub_id, rg, vault_name]):
                    continue
                
                backup_client = RecoveryServicesBackupClient(self._credential, sub_id)
                
                # List protected items in vault
                for item in backup_client.backup_protected_items.list(vault_name, rg):
                    items.append({
                        "id": item.id,
                        "name": item.name,
                        "vault_name": vault_name,
                        "source_resource_id": getattr(item.properties, "source_resource_id", None) if item.properties else None,
                        "protection_status": getattr(item.properties, "protection_status", None) if item.properties else None,
                        "last_backup_time": getattr(item.properties, "last_backup_time", None) if item.properties else None,
                        "policy_id": getattr(item.properties, "policy_id", None) if item.properties else None,
                    })
            except Exception as e:
                logger.warning(
                    "protected_items_fetch_failed",
                    vault=vault.get("name"),
                    error=str(e),
                )
        
        logger.info("protected_items_collected", count=len(items))
        return items
    
    async def get_backup_jobs(self, days: int = 7) -> list[dict]:
        """
        Get backup jobs from the last N days.
        
        Args:
            days: Number of days to look back
        """
        jobs = []
        vaults = await self.get_backup_vaults()
        
        filter_start = datetime.utcnow() - timedelta(days=days)
        
        for vault in vaults:
            try:
                sub_id = vault.get("subscription_id")
                rg = vault.get("resource_group")
                vault_name = vault.get("name")
                
                if not all([sub_id, rg, vault_name]):
                    continue
                
                backup_client = RecoveryServicesBackupClient(self._credential, sub_id)
                
                # List backup jobs
                for job in backup_client.backup_jobs.list(vault_name, rg):
                    job_props = job.properties
                    if not job_props:
                        continue
                    
                    # Filter by date
                    start_time = getattr(job_props, "start_time", None)
                    if start_time and start_time < filter_start:
                        continue
                    
                    jobs.append({
                        "id": job.id,
                        "name": job.name,
                        "vault_name": vault_name,
                        "operation": getattr(job_props, "operation", None),
                        "status": getattr(job_props, "status", None),
                        "start_time": start_time,
                        "end_time": getattr(job_props, "end_time", None),
                        "duration": getattr(job_props, "duration", None),
                        "entity_friendly_name": getattr(job_props, "entity_friendly_name", None),
                    })
            except Exception as e:
                logger.warning(
                    "backup_jobs_fetch_failed",
                    vault=vault.get("name"),
                    error=str(e),
                )
        
        # Sort by start time (newest first)
        jobs.sort(key=lambda x: x.get("start_time") or "", reverse=True)
        
        logger.info("backup_jobs_collected", count=len(jobs), days=days)
        return jobs
    
    async def get_backup_policies(self) -> list[dict]:
        """
        Get backup policies across vaults.
        """
        policies = []
        vaults = await self.get_backup_vaults()
        
        for vault in vaults:
            try:
                sub_id = vault.get("subscription_id")
                rg = vault.get("resource_group")
                vault_name = vault.get("name")
                
                if not all([sub_id, rg, vault_name]):
                    continue
                
                backup_client = RecoveryServicesBackupClient(self._credential, sub_id)
                
                for policy in backup_client.backup_policies.list(vault_name, rg):
                    policy_props = policy.properties
                    policies.append({
                        "id": policy.id,
                        "name": policy.name,
                        "vault_name": vault_name,
                        "backup_management_type": getattr(policy_props, "backup_management_type", None) if policy_props else None,
                    })
            except Exception as e:
                logger.warning(
                    "backup_policies_fetch_failed",
                    vault=vault.get("name"),
                    error=str(e),
                )
        
        logger.info("backup_policies_collected", count=len(policies))
        return policies

# Singleton instance
_azure_client_instance: Optional[AzureResourceClient] = None

def get_azure_client() -> Optional[AzureResourceClient]:
    """Get singleton instance of AzureResourceClient."""
    global _azure_client_instance
    
    if _azure_client_instance is None:
        import os
        tenant_id = os.getenv("AZURE_TENANT_ID")
        client_id = os.getenv("AZURE_CLIENT_ID")
        client_secret = os.getenv("AZURE_CLIENT_SECRET")
        
        if tenant_id and client_id and client_secret:
            try:
                _azure_client_instance = AzureResourceClient(
                    tenant_id=tenant_id,
                    client_id=client_id,
                    client_secret=client_secret
                )
            except Exception as e:
                logger.error("azure_client_init_failed", error=str(e))
        else:
            logger.warning("missing_azure_credentials_for_client")
            
    return _azure_client_instance
