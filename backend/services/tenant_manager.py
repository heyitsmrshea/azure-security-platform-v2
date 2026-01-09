"""
Multi-Tenant Manager for Azure Security Platform V2

Handles tenant registration, credential management, and data isolation.
"""
from datetime import datetime
from typing import Optional
import structlog

from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

from ..models.schemas import Tenant, TenantCreate

logger = structlog.get_logger(__name__)


class TenantManager:
    """
    Manages multi-tenant operations with secure credential storage.
    
    Features:
    - Tenant registration and configuration
    - Secure credential storage in Azure Key Vault
    - Tenant data isolation (CosmosDB partitioning)
    - Tenant-specific client instantiation
    """
    
    def __init__(
        self,
        key_vault_url: str,
        cosmos_client=None,
        database_name: str = "security_platform",
    ):
        """
        Initialize tenant manager.
        
        Args:
            key_vault_url: URL of Azure Key Vault for credential storage
            cosmos_client: CosmosDB client instance
            database_name: Name of the CosmosDB database
        """
        self.key_vault_url = key_vault_url
        self._cosmos_client = cosmos_client
        self._database_name = database_name
        
        # Initialize Key Vault client
        credential = DefaultAzureCredential()
        self._secret_client = SecretClient(
            vault_url=key_vault_url,
            credential=credential,
        )
        
        # Cache for tenant configurations
        self._tenant_cache: dict[str, dict] = {}
        
        logger.info("tenant_manager_initialized", key_vault=key_vault_url)
    
    # ========================================================================
    # Tenant Management
    # ========================================================================
    
    async def register_tenant(self, tenant: TenantCreate) -> Tenant:
        """
        Register a new tenant.
        
        Args:
            tenant: Tenant creation data including credentials
            
        Returns:
            Created tenant (without sensitive data)
        """
        # Store credentials securely in Key Vault
        secret_name = f"tenant-{tenant.id}-credentials"
        secret_value = f"{tenant.client_id}:{tenant.client_secret}"
        
        try:
            self._secret_client.set_secret(secret_name, secret_value)
            logger.info("tenant_credentials_stored", tenant_id=tenant.id)
        except Exception as e:
            logger.error("credential_storage_error", tenant_id=tenant.id, error=str(e))
            raise
        
        # Create tenant record in CosmosDB
        tenant_data = {
            "id": tenant.id,
            "name": tenant.name,
            "azure_tenant_id": tenant.azure_tenant_id,
            "is_active": tenant.is_active,
            "created_at": datetime.utcnow().isoformat(),
            "last_sync": None,
            "partition_key": tenant.id,  # For CosmosDB partitioning
        }
        
        if self._cosmos_client:
            container = self._get_tenants_container()
            await container.upsert_item(tenant_data)
        
        # Update cache
        self._tenant_cache[tenant.id] = tenant_data
        
        return Tenant(
            id=tenant.id,
            name=tenant.name,
            azure_tenant_id=tenant.azure_tenant_id,
            is_active=tenant.is_active,
            created_at=datetime.utcnow(),
        )
    
    async def get_tenant(self, tenant_id: str) -> Optional[Tenant]:
        """
        Get tenant by ID.
        """
        # Check cache first
        if tenant_id in self._tenant_cache:
            data = self._tenant_cache[tenant_id]
            return self._dict_to_tenant(data)
        
        # Fetch from CosmosDB
        if self._cosmos_client:
            container = self._get_tenants_container()
            try:
                item = await container.read_item(
                    item=tenant_id,
                    partition_key=tenant_id,
                )
                self._tenant_cache[tenant_id] = item
                return self._dict_to_tenant(item)
            except Exception:
                return None
        
        return None
    
    async def list_tenants(self, active_only: bool = True) -> list[Tenant]:
        """
        List all tenants.
        """
        if not self._cosmos_client:
            return [self._dict_to_tenant(t) for t in self._tenant_cache.values()]
        
        container = self._get_tenants_container()
        
        query = "SELECT * FROM c"
        if active_only:
            query += " WHERE c.is_active = true"
        
        tenants = []
        async for item in container.query_items(query=query):
            tenants.append(self._dict_to_tenant(item))
            self._tenant_cache[item["id"]] = item
        
        return tenants
    
    async def update_tenant(self, tenant_id: str, updates: dict) -> Optional[Tenant]:
        """
        Update tenant configuration.
        """
        tenant_data = self._tenant_cache.get(tenant_id)
        
        if not tenant_data and self._cosmos_client:
            container = self._get_tenants_container()
            try:
                tenant_data = await container.read_item(
                    item=tenant_id,
                    partition_key=tenant_id,
                )
            except Exception:
                return None
        
        if not tenant_data:
            return None
        
        # Update fields
        for key, value in updates.items():
            if key not in ["id", "created_at", "partition_key"]:
                tenant_data[key] = value
        
        # Save to CosmosDB
        if self._cosmos_client:
            container = self._get_tenants_container()
            await container.upsert_item(tenant_data)
        
        # Update cache
        self._tenant_cache[tenant_id] = tenant_data
        
        return self._dict_to_tenant(tenant_data)
    
    async def deactivate_tenant(self, tenant_id: str) -> bool:
        """
        Deactivate a tenant (soft delete).
        """
        result = await self.update_tenant(tenant_id, {"is_active": False})
        return result is not None
    
    # ========================================================================
    # Credential Management
    # ========================================================================
    
    def get_tenant_credentials(self, tenant_id: str) -> tuple[str, str]:
        """
        Retrieve tenant credentials from Key Vault.
        
        Returns:
            Tuple of (client_id, client_secret)
        """
        secret_name = f"tenant-{tenant_id}-credentials"
        
        try:
            secret = self._secret_client.get_secret(secret_name)
            client_id, client_secret = secret.value.split(":", 1)
            return client_id, client_secret
        except Exception as e:
            logger.error("credential_retrieval_error", tenant_id=tenant_id, error=str(e))
            raise
    
    async def rotate_credentials(
        self,
        tenant_id: str,
        new_client_id: str,
        new_client_secret: str,
    ) -> bool:
        """
        Rotate tenant credentials.
        """
        secret_name = f"tenant-{tenant_id}-credentials"
        secret_value = f"{new_client_id}:{new_client_secret}"
        
        try:
            self._secret_client.set_secret(secret_name, secret_value)
            logger.info("credentials_rotated", tenant_id=tenant_id)
            return True
        except Exception as e:
            logger.error("credential_rotation_error", tenant_id=tenant_id, error=str(e))
            return False
    
    # ========================================================================
    # Sync Management
    # ========================================================================
    
    async def update_last_sync(self, tenant_id: str) -> None:
        """
        Update the last sync timestamp for a tenant.
        """
        await self.update_tenant(tenant_id, {
            "last_sync": datetime.utcnow().isoformat(),
        })
    
    async def get_tenants_needing_sync(self, max_age_minutes: int = 240) -> list[Tenant]:
        """
        Get tenants that need data sync (haven't been synced recently).
        
        Args:
            max_age_minutes: Maximum age of last sync before re-sync needed
        """
        all_tenants = await self.list_tenants(active_only=True)
        
        cutoff = datetime.utcnow().timestamp() - (max_age_minutes * 60)
        
        tenants_needing_sync = []
        for tenant in all_tenants:
            if tenant.last_sync is None:
                tenants_needing_sync.append(tenant)
            elif tenant.last_sync.timestamp() < cutoff:
                tenants_needing_sync.append(tenant)
        
        return tenants_needing_sync
    
    # ========================================================================
    # Helper Methods
    # ========================================================================
    
    def _get_tenants_container(self):
        """Get the tenants CosmosDB container."""
        if not self._cosmos_client:
            raise RuntimeError("CosmosDB client not initialized")
        
        database = self._cosmos_client.get_database_client(self._database_name)
        return database.get_container_client("tenants")
    
    def _dict_to_tenant(self, data: dict) -> Tenant:
        """Convert dict to Tenant model."""
        return Tenant(
            id=data["id"],
            name=data["name"],
            azure_tenant_id=data["azure_tenant_id"],
            is_active=data.get("is_active", True),
            created_at=datetime.fromisoformat(data["created_at"]) if isinstance(data.get("created_at"), str) else data.get("created_at", datetime.utcnow()),
            last_sync=datetime.fromisoformat(data["last_sync"]) if data.get("last_sync") and isinstance(data["last_sync"], str) else data.get("last_sync"),
        )
