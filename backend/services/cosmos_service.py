"""
CosmosDB Service for Azure Security Platform V2

Handles data persistence with tenant isolation.
"""
from datetime import datetime
from typing import Any, Optional
import structlog

from azure.cosmos.aio import CosmosClient
from azure.cosmos import PartitionKey

logger = structlog.get_logger(__name__)


class CosmosService:
    """
    CosmosDB service for persistent storage.
    
    Features:
    - Tenant-isolated data storage (partitioned by tenantId)
    - Historical data for trend analysis
    - Findings and remediation tracking
    """
    
    # Container configurations
    CONTAINERS = {
        "tenants": {
            "partition_key": "/id",
            "ttl": None,  # No expiration for tenant configs
        },
        "security_scores": {
            "partition_key": "/tenantId",
            "ttl": 7776000,  # 90 days
        },
        "findings": {
            "partition_key": "/tenantId",
            "ttl": 31536000,  # 1 year
        },
        "alerts": {
            "partition_key": "/tenantId",
            "ttl": 7776000,  # 90 days
        },
        "backup_status": {
            "partition_key": "/tenantId",
            "ttl": 7776000,  # 90 days
        },
        "audit_logs": {
            "partition_key": "/tenantId",
            "ttl": 7776000,  # 90 days
        },
        "dashboard_snapshots": {
            "partition_key": "/tenantId",
            "ttl": 31536000,  # 1 year - for historical trends
        },
    }
    
    def __init__(
        self,
        endpoint: str,
        key: str,
        database_name: str = "security_platform",
    ):
        """
        Initialize CosmosDB service.
        
        Args:
            endpoint: CosmosDB account endpoint
            key: CosmosDB account key
            database_name: Database name
        """
        self._endpoint = endpoint
        self._database_name = database_name
        self._client = CosmosClient(endpoint, credential=key)
        self._database = None
        self._containers: dict = {}
        
        logger.info("cosmos_service_initialized", endpoint=endpoint, database=database_name)
    
    async def initialize(self) -> None:
        """
        Initialize database and containers.
        Creates them if they don't exist.
        """
        # Get or create database
        self._database = await self._client.create_database_if_not_exists(
            id=self._database_name,
        )
        logger.info("database_initialized", database=self._database_name)
        
        # Get or create containers
        for container_name, config in self.CONTAINERS.items():
            container = await self._database.create_container_if_not_exists(
                id=container_name,
                partition_key=PartitionKey(path=config["partition_key"]),
                default_ttl=config["ttl"],
            )
            self._containers[container_name] = container
            logger.info("container_initialized", container=container_name)
    
    async def close(self) -> None:
        """Close CosmosDB connection."""
        await self._client.close()
        logger.info("cosmos_connection_closed")
    
    def _get_container(self, name: str):
        """Get a container client."""
        if name not in self._containers:
            raise ValueError(f"Unknown container: {name}")
        return self._containers[name]
    
    # ========================================================================
    # Generic CRUD Operations
    # ========================================================================
    
    async def upsert_item(
        self,
        container_name: str,
        item: dict,
    ) -> dict:
        """
        Insert or update an item.
        """
        container = self._get_container(container_name)
        
        # Ensure required fields
        if "id" not in item:
            raise ValueError("Item must have 'id' field")
        
        item["_updated"] = datetime.utcnow().isoformat()
        
        result = await container.upsert_item(item)
        logger.debug("item_upserted", container=container_name, id=item["id"])
        return result
    
    async def get_item(
        self,
        container_name: str,
        item_id: str,
        partition_key: str,
    ) -> Optional[dict]:
        """
        Get an item by ID.
        """
        container = self._get_container(container_name)
        
        try:
            item = await container.read_item(
                item=item_id,
                partition_key=partition_key,
            )
            return item
        except Exception:
            return None
    
    async def query_items(
        self,
        container_name: str,
        query: str,
        parameters: Optional[list] = None,
        partition_key: Optional[str] = None,
    ) -> list[dict]:
        """
        Query items with SQL.
        """
        container = self._get_container(container_name)
        
        items = []
        async for item in container.query_items(
            query=query,
            parameters=parameters or [],
            partition_key=partition_key,
        ):
            items.append(item)
        
        return items
    
    async def delete_item(
        self,
        container_name: str,
        item_id: str,
        partition_key: str,
    ) -> bool:
        """
        Delete an item.
        """
        container = self._get_container(container_name)
        
        try:
            await container.delete_item(
                item=item_id,
                partition_key=partition_key,
            )
            logger.debug("item_deleted", container=container_name, id=item_id)
            return True
        except Exception as e:
            logger.warning("delete_failed", container=container_name, id=item_id, error=str(e))
            return False
    
    # ========================================================================
    # Security Score Operations
    # ========================================================================
    
    async def save_security_score(
        self,
        tenant_id: str,
        score_data: dict,
    ) -> dict:
        """
        Save a security score snapshot for trend tracking.
        """
        item = {
            "id": f"{tenant_id}_{datetime.utcnow().strftime('%Y%m%d%H%M')}",
            "tenantId": tenant_id,
            "timestamp": datetime.utcnow().isoformat(),
            **score_data,
        }
        
        return await self.upsert_item("security_scores", item)
    
    async def get_security_score_history(
        self,
        tenant_id: str,
        days: int = 180,
    ) -> list[dict]:
        """
        Get security score history for trend analysis.
        """
        query = """
        SELECT c.timestamp, c.current_score, c.max_score
        FROM c
        WHERE c.tenantId = @tenantId
        ORDER BY c.timestamp DESC
        """
        
        return await self.query_items(
            "security_scores",
            query,
            [{"name": "@tenantId", "value": tenant_id}],
            partition_key=tenant_id,
        )
    
    # ========================================================================
    # Findings Operations
    # ========================================================================
    
    async def save_finding(
        self,
        tenant_id: str,
        finding: dict,
    ) -> dict:
        """
        Save a security finding.
        """
        item = {
            "tenantId": tenant_id,
            "created_at": datetime.utcnow().isoformat(),
            **finding,
        }
        
        if "id" not in item:
            item["id"] = f"{tenant_id}_{finding.get('type', 'finding')}_{datetime.utcnow().timestamp()}"
        
        return await self.upsert_item("findings", item)
    
    async def get_open_findings(
        self,
        tenant_id: str,
        severity: Optional[str] = None,
    ) -> list[dict]:
        """
        Get open findings for a tenant.
        """
        query = """
        SELECT *
        FROM c
        WHERE c.tenantId = @tenantId
        AND (c.status = 'open' OR NOT IS_DEFINED(c.status))
        """
        
        params = [{"name": "@tenantId", "value": tenant_id}]
        
        if severity:
            query += " AND c.severity = @severity"
            params.append({"name": "@severity", "value": severity})
        
        query += " ORDER BY c.created_at DESC"
        
        return await self.query_items(
            "findings",
            query,
            params,
            partition_key=tenant_id,
        )
    
    async def get_finding_age_distribution(
        self,
        tenant_id: str,
    ) -> dict:
        """
        Get distribution of finding ages for accountability metrics.
        """
        findings = await self.get_open_findings(tenant_id)
        
        now = datetime.utcnow()
        distribution = {
            "age_0_7": 0,
            "age_7_30": 0,
            "age_30_90": 0,
            "age_90_plus": 0,
        }
        
        for finding in findings:
            created = datetime.fromisoformat(finding.get("created_at", now.isoformat()).replace("Z", ""))
            age_days = (now - created).days
            
            if age_days <= 7:
                distribution["age_0_7"] += 1
            elif age_days <= 30:
                distribution["age_7_30"] += 1
            elif age_days <= 90:
                distribution["age_30_90"] += 1
            else:
                distribution["age_90_plus"] += 1
        
        distribution["total_open"] = len(findings)
        return distribution
    
    # ========================================================================
    # Dashboard Snapshot Operations
    # ========================================================================
    
    async def save_dashboard_snapshot(
        self,
        tenant_id: str,
        dashboard_type: str,  # "executive" or "it"
        snapshot: dict,
    ) -> dict:
        """
        Save a dashboard snapshot for historical tracking.
        """
        item = {
            "id": f"{tenant_id}_{dashboard_type}_{datetime.utcnow().strftime('%Y%m%d')}",
            "tenantId": tenant_id,
            "dashboard_type": dashboard_type,
            "timestamp": datetime.utcnow().isoformat(),
            "data": snapshot,
        }
        
        return await self.upsert_item("dashboard_snapshots", item)
    
    async def get_dashboard_history(
        self,
        tenant_id: str,
        dashboard_type: str,
        days: int = 180,
    ) -> list[dict]:
        """
        Get historical dashboard snapshots for trend charts.
        """
        query = """
        SELECT c.timestamp, c.data
        FROM c
        WHERE c.tenantId = @tenantId
        AND c.dashboard_type = @dashboardType
        ORDER BY c.timestamp DESC
        """
        
        return await self.query_items(
            "dashboard_snapshots",
            query,
            [
                {"name": "@tenantId", "value": tenant_id},
                {"name": "@dashboardType", "value": dashboard_type},
            ],
            partition_key=tenant_id,
        )
    
    # ========================================================================
    # MTTR Calculation
    # ========================================================================
    
    async def calculate_mttr(
        self,
        tenant_id: str,
        days: int = 30,
    ) -> dict:
        """
        Calculate Mean Time to Remediate for resolved findings.
        """
        query = """
        SELECT c.severity, c.created_at, c.resolved_at
        FROM c
        WHERE c.tenantId = @tenantId
        AND c.status = 'resolved'
        AND c.resolved_at != null
        """
        
        findings = await self.query_items(
            "findings",
            query,
            [{"name": "@tenantId", "value": tenant_id}],
            partition_key=tenant_id,
        )
        
        total_days = 0
        critical_days = 0
        high_days = 0
        critical_count = 0
        high_count = 0
        
        for finding in findings:
            created = datetime.fromisoformat(finding.get("created_at", "").replace("Z", ""))
            resolved = datetime.fromisoformat(finding.get("resolved_at", "").replace("Z", ""))
            resolution_days = (resolved - created).days
            
            total_days += resolution_days
            
            if finding.get("severity") == "critical":
                critical_days += resolution_days
                critical_count += 1
            elif finding.get("severity") == "high":
                high_days += resolution_days
                high_count += 1
        
        return {
            "mttr_days": total_days / len(findings) if findings else 0,
            "critical_mttr_days": critical_days / critical_count if critical_count else 0,
            "high_mttr_days": high_days / high_count if high_count else 0,
            "findings_resolved_count": len(findings),
        }
