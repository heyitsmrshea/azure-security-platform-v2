"""
Storage Service for Azure Security Platform V2

Provides an abstract storage interface with implementations for:
- CosmosDB (production)
- Local JSON files (development fallback)

This enables historical trending without requiring CosmosDB in dev environments.
"""
import json
import os
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List
import structlog

logger = structlog.get_logger(__name__)


class StorageService(ABC):
    """
    Abstract storage service for dashboard snapshots and historical data.
    """
    
    @abstractmethod
    async def save_dashboard_snapshot(
        self,
        tenant_id: str,
        dashboard_type: str,
        data: dict,
    ) -> None:
        """Save a dashboard snapshot for historical trending."""
        pass
    
    @abstractmethod
    async def get_dashboard_history(
        self,
        tenant_id: str,
        dashboard_type: str,
        days: int = 180,
    ) -> List[dict]:
        """Get historical dashboard snapshots for trend analysis."""
        pass
    
    @abstractmethod
    async def save_security_score(
        self,
        tenant_id: str,
        score_data: dict,
    ) -> None:
        """Save a security score snapshot."""
        pass
    
    @abstractmethod
    async def get_security_score_history(
        self,
        tenant_id: str,
        days: int = 180,
    ) -> List[dict]:
        """Get security score history for trend charts."""
        pass
    
    @abstractmethod
    async def save_finding(
        self,
        tenant_id: str,
        finding: dict,
    ) -> None:
        """Save a security finding."""
        pass
    
    @abstractmethod
    async def get_open_findings(
        self,
        tenant_id: str,
        severity: Optional[str] = None,
    ) -> List[dict]:
        """Get open findings for a tenant."""
        pass


class LocalStorageService(StorageService):
    """
    JSON file-based storage for development without CosmosDB.
    
    Stores data in:
    - data/snapshots/{tenant_id}/dashboard_{type}_{date}.json
    - data/snapshots/{tenant_id}/scores_{date}.json
    - data/snapshots/{tenant_id}/findings.json
    """
    
    def __init__(self, data_dir: Optional[Path] = None):
        if data_dir is None:
            # Default to project root data/snapshots
            self.data_dir = Path(__file__).parent.parent.parent / "data" / "snapshots"
        else:
            self.data_dir = Path(data_dir)
        
        self.data_dir.mkdir(parents=True, exist_ok=True)
        logger.info("local_storage_initialized", data_dir=str(self.data_dir))
    
    def _get_tenant_dir(self, tenant_id: str) -> Path:
        """Get or create tenant-specific directory."""
        tenant_dir = self.data_dir / tenant_id
        tenant_dir.mkdir(parents=True, exist_ok=True)
        return tenant_dir
    
    def _get_date_str(self, dt: Optional[datetime] = None) -> str:
        """Get date string for file naming."""
        if dt is None:
            dt = datetime.utcnow()
        return dt.strftime("%Y%m%d")
    
    async def save_dashboard_snapshot(
        self,
        tenant_id: str,
        dashboard_type: str,
        data: dict,
    ) -> None:
        """Save dashboard snapshot to JSON file."""
        tenant_dir = self._get_tenant_dir(tenant_id)
        date_str = self._get_date_str()
        
        # One file per day per dashboard type
        filename = f"dashboard_{dashboard_type}_{date_str}.json"
        filepath = tenant_dir / filename
        
        snapshot = {
            "tenant_id": tenant_id,
            "dashboard_type": dashboard_type,
            "timestamp": datetime.utcnow().isoformat(),
            "date": date_str,
            "data": data,
        }
        
        with open(filepath, "w") as f:
            json.dump(snapshot, f, indent=2, default=str)
        
        logger.debug("dashboard_snapshot_saved", 
                    tenant_id=tenant_id, 
                    dashboard_type=dashboard_type,
                    filepath=str(filepath))
    
    async def get_dashboard_history(
        self,
        tenant_id: str,
        dashboard_type: str,
        days: int = 180,
    ) -> List[dict]:
        """Load historical dashboard snapshots from JSON files."""
        tenant_dir = self._get_tenant_dir(tenant_id)
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        cutoff_str = self._get_date_str(cutoff_date)
        
        snapshots = []
        pattern = f"dashboard_{dashboard_type}_*.json"
        
        for filepath in sorted(tenant_dir.glob(pattern), reverse=True):
            try:
                # Extract date from filename
                date_part = filepath.stem.split("_")[-1]
                if date_part < cutoff_str:
                    continue
                
                with open(filepath, "r") as f:
                    snapshot = json.load(f)
                    snapshots.append(snapshot)
            except (json.JSONDecodeError, IOError) as e:
                logger.warning("snapshot_read_error", filepath=str(filepath), error=str(e))
                continue
        
        logger.debug("dashboard_history_loaded", 
                    tenant_id=tenant_id,
                    dashboard_type=dashboard_type,
                    count=len(snapshots))
        
        return snapshots
    
    async def save_security_score(
        self,
        tenant_id: str,
        score_data: dict,
    ) -> None:
        """Save security score snapshot."""
        tenant_dir = self._get_tenant_dir(tenant_id)
        date_str = self._get_date_str()
        
        filename = f"scores_{date_str}.json"
        filepath = tenant_dir / filename
        
        snapshot = {
            "tenant_id": tenant_id,
            "timestamp": datetime.utcnow().isoformat(),
            "date": date_str,
            **score_data,
        }
        
        with open(filepath, "w") as f:
            json.dump(snapshot, f, indent=2, default=str)
        
        logger.debug("security_score_saved", tenant_id=tenant_id, filepath=str(filepath))
    
    async def get_security_score_history(
        self,
        tenant_id: str,
        days: int = 180,
    ) -> List[dict]:
        """Load security score history from JSON files."""
        tenant_dir = self._get_tenant_dir(tenant_id)
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        cutoff_str = self._get_date_str(cutoff_date)
        
        scores = []
        pattern = "scores_*.json"
        
        for filepath in sorted(tenant_dir.glob(pattern), reverse=True):
            try:
                date_part = filepath.stem.split("_")[-1]
                if date_part < cutoff_str:
                    continue
                
                with open(filepath, "r") as f:
                    score = json.load(f)
                    scores.append(score)
            except (json.JSONDecodeError, IOError) as e:
                logger.warning("score_read_error", filepath=str(filepath), error=str(e))
                continue
        
        return scores
    
    async def save_finding(
        self,
        tenant_id: str,
        finding: dict,
    ) -> None:
        """Save or update a finding in the findings file."""
        tenant_dir = self._get_tenant_dir(tenant_id)
        filepath = tenant_dir / "findings.json"
        
        # Load existing findings
        findings = []
        if filepath.exists():
            try:
                with open(filepath, "r") as f:
                    findings = json.load(f)
            except (json.JSONDecodeError, IOError):
                findings = []
        
        # Add or update finding
        finding_id = finding.get("id")
        if finding_id:
            # Update existing
            updated = False
            for i, f in enumerate(findings):
                if f.get("id") == finding_id:
                    findings[i] = {**f, **finding, "_updated": datetime.utcnow().isoformat()}
                    updated = True
                    break
            if not updated:
                finding["_created"] = datetime.utcnow().isoformat()
                findings.append(finding)
        else:
            # New finding
            finding["id"] = f"finding_{tenant_id}_{datetime.utcnow().timestamp()}"
            finding["_created"] = datetime.utcnow().isoformat()
            findings.append(finding)
        
        with open(filepath, "w") as f:
            json.dump(findings, f, indent=2, default=str)
        
        logger.debug("finding_saved", tenant_id=tenant_id, finding_id=finding.get("id"))
    
    async def get_open_findings(
        self,
        tenant_id: str,
        severity: Optional[str] = None,
    ) -> List[dict]:
        """Get open findings from JSON file."""
        tenant_dir = self._get_tenant_dir(tenant_id)
        filepath = tenant_dir / "findings.json"
        
        if not filepath.exists():
            return []
        
        try:
            with open(filepath, "r") as f:
                findings = json.load(f)
        except (json.JSONDecodeError, IOError):
            return []
        
        # Filter for open findings
        open_findings = [
            f for f in findings 
            if f.get("status", "open") == "open"
        ]
        
        # Filter by severity if specified
        if severity:
            open_findings = [
                f for f in open_findings 
                if f.get("severity") == severity
            ]
        
        return open_findings


class CosmosStorageService(StorageService):
    """
    CosmosDB-backed storage service for production.
    
    Wraps the existing CosmosService with the StorageService interface.
    """
    
    def __init__(self, cosmos_service):
        """
        Initialize with an existing CosmosService instance.
        
        Args:
            cosmos_service: Initialized CosmosService from cosmos_service.py
        """
        self._cosmos = cosmos_service
        logger.info("cosmos_storage_initialized")
    
    async def save_dashboard_snapshot(
        self,
        tenant_id: str,
        dashboard_type: str,
        data: dict,
    ) -> None:
        """Save dashboard snapshot to CosmosDB."""
        await self._cosmos.save_dashboard_snapshot(tenant_id, dashboard_type, data)
    
    async def get_dashboard_history(
        self,
        tenant_id: str,
        dashboard_type: str,
        days: int = 180,
    ) -> List[dict]:
        """Get dashboard history from CosmosDB."""
        return await self._cosmos.get_dashboard_history(tenant_id, dashboard_type, days)
    
    async def save_security_score(
        self,
        tenant_id: str,
        score_data: dict,
    ) -> None:
        """Save security score to CosmosDB."""
        await self._cosmos.save_security_score(tenant_id, score_data)
    
    async def get_security_score_history(
        self,
        tenant_id: str,
        days: int = 180,
    ) -> List[dict]:
        """Get security score history from CosmosDB."""
        return await self._cosmos.get_security_score_history(tenant_id, days)
    
    async def save_finding(
        self,
        tenant_id: str,
        finding: dict,
    ) -> None:
        """Save finding to CosmosDB."""
        await self._cosmos.save_finding(tenant_id, finding)
    
    async def get_open_findings(
        self,
        tenant_id: str,
        severity: Optional[str] = None,
    ) -> List[dict]:
        """Get open findings from CosmosDB."""
        return await self._cosmos.get_open_findings(tenant_id, severity)


# Singleton storage service instance
_storage_service: Optional[StorageService] = None


def get_storage_service() -> StorageService:
    """
    Get the storage service instance.
    
    Uses CosmosDB if COSMOS_ENDPOINT and COSMOS_KEY are set,
    otherwise falls back to local JSON storage.
    """
    global _storage_service
    
    if _storage_service is None:
        cosmos_endpoint = os.getenv("COSMOS_ENDPOINT")
        cosmos_key = os.getenv("COSMOS_KEY")
        
        if cosmos_endpoint and cosmos_key:
            try:
                from .cosmos_service import CosmosService
                cosmos = CosmosService(
                    endpoint=cosmos_endpoint,
                    key=cosmos_key,
                )
                _storage_service = CosmosStorageService(cosmos)
                logger.info("using_cosmos_storage")
            except Exception as e:
                logger.error("cosmos_init_failed", error=str(e))
                _storage_service = LocalStorageService()
                logger.info("falling_back_to_local_storage")
        else:
            _storage_service = LocalStorageService()
            logger.info("using_local_storage", 
                       reason="COSMOS_ENDPOINT or COSMOS_KEY not set")
    
    return _storage_service


def reset_storage_service():
    """Reset the storage service singleton (useful for testing)."""
    global _storage_service
    _storage_service = None
