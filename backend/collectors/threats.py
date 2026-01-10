"""
Threat Collector for Azure Security Platform V2

Collects security alerts and threat information from Microsoft Defender.
"""
from datetime import datetime
from typing import Optional
import structlog

from ..services.graph_client import GraphClient
from ..services.cache_service import CacheService
from ..models.schemas import AlertSummary, BlockedThreats

logger = structlog.get_logger(__name__)


class ThreatCollector:
    """
    Collects security alerts and threat data.
    """
    
    def __init__(
        self,
        graph_client: GraphClient,
        cache_service: Optional[CacheService] = None,
    ):
        self._graph = graph_client
        self._cache = cache_service
        self._tenant_id = graph_client.tenant_id
        
        logger.info("threat_collector_initialized", tenant_id=self._tenant_id)
    
    async def collect_alert_summary(self, force_refresh: bool = False) -> AlertSummary:
        """
        Collect security alert summary by severity.
        """
        # Check cache
        if not force_refresh and self._cache:
            cached = await self._cache.get(self._tenant_id, "alert_summary")
            if cached:
                return AlertSummary(**cached)
        
        # Fetch alerts
        alerts = await self._graph.get_security_alerts()
        
        # Filter to active alerts only
        active = [a for a in alerts if a.get("status") not in ["resolved", "dismissed"]]
        
        # Count by severity
        critical = len([a for a in active if a.get("severity") == "high" and "critical" in a.get("title", "").lower()])
        high = len([a for a in active if a.get("severity") == "high"]) - critical
        medium = len([a for a in active if a.get("severity") == "medium"])
        low = len([a for a in active if a.get("severity") in ["low", "informational"]])
        
        summary = AlertSummary(
            critical_count=critical,
            high_count=high,
            medium_count=medium,
            low_count=low,
            total_active=len(active),
            last_updated=datetime.utcnow(),
        )
        
        # Cache result
        if self._cache:
            await self._cache.set(self._tenant_id, "alert_summary", summary.model_dump())
        
        logger.info(
            "alert_summary_collected",
            tenant_id=self._tenant_id,
            total=len(active),
            critical=critical,
            high=high,
        )
        
        return summary
    
    async def get_active_alerts(self) -> list[dict]:
        """
        Get list of active security alerts with details.
        """
        alerts = await self._graph.get_security_alerts()
        
        active = []
        for alert in alerts:
            if alert.get("status") not in ["resolved", "dismissed"]:
                active.append({
                    "id": alert.get("id"),
                    "title": alert.get("title"),
                    "description": alert.get("description"),
                    "severity": alert.get("severity"),
                    "status": alert.get("status"),
                    "category": alert.get("category"),
                    "source": alert.get("service_source"),
                    "created_at": alert.get("created_at"),
                    "last_updated": alert.get("last_updated"),
                })
        
        # Sort by severity (critical first)
        severity_order = {"high": 0, "medium": 1, "low": 2, "informational": 3}
        active.sort(key=lambda x: severity_order.get(x.get("severity", "informational"), 4))
        
        return active
    
    async def collect_blocked_threats(self, force_refresh: bool = False) -> BlockedThreats:
        """
        Collect blocked threat statistics.
        
        Note: Full implementation requires Microsoft 365 Defender ATP access.
        This is a simplified version using available Graph API data.
        """
        # Check cache
        if not force_refresh and self._cache:
            cached = await self._cache.get(self._tenant_id, "blocked_threats")
            if cached:
                return BlockedThreats(**cached)
        
        # Get alerts to estimate blocked threats
        alerts = await self._graph.get_security_alerts()
        
        # Count by category (estimates)
        phishing = len([a for a in alerts if "phish" in (a.get("title", "") + a.get("category", "")).lower()])
        malware = len([a for a in alerts if "malware" in (a.get("title", "") + a.get("category", "")).lower()])
        
        # Note: In production, you'd query Microsoft Defender for actual blocked counts
        threats = BlockedThreats(
            phishing_blocked=phishing * 10,  # Estimate multiplier
            malware_blocked=malware * 5,
            spam_blocked=0,  # Requires Exchange Online Protection data
            total_blocked=(phishing * 10) + (malware * 5),
            period="30d",
            last_updated=datetime.utcnow(),
        )
        
        # Cache result
        if self._cache:
            await self._cache.set(self._tenant_id, "blocked_threats", threats.model_dump())
        
        return threats
    
    async def get_alerts_by_category(self) -> dict:
        """
        Get alert counts grouped by category.
        """
        alerts = await self._graph.get_security_alerts()
        
        categories = {}
        for alert in alerts:
            category = alert.get("category", "Other")
            categories[category] = categories.get(category, 0) + 1
        
        return categories
    
    async def get_recent_incidents(self, days: int = 7) -> list[dict]:
        """
        Get recent security incidents.
        """
        from datetime import timedelta
        cutoff = datetime.utcnow() - timedelta(days=days)
        
        alerts = await self._graph.get_security_alerts()
        
        recent = []
        for alert in alerts:
            created = alert.get("created_at")
            if created:
                try:
                    created_dt = datetime.fromisoformat(str(created).replace("Z", "+00:00"))
                    if created_dt.replace(tzinfo=None) >= cutoff:
                        recent.append(alert)
                except (ValueError, TypeError):
                    pass
        
        return recent
