"""
Secure Score Collector for Azure Security Platform V2

Collects and processes Microsoft Secure Score data.
"""
from datetime import datetime, timedelta
from typing import Optional
import structlog

from ..services.graph_client import GraphClient
from ..services.cache_service import CacheService
from ..services.cosmos_service import CosmosService
from ..models.schemas import (
    SecurityScore,
    MetricTrend,
    TrendDirection,
)

logger = structlog.get_logger(__name__)


class SecureScoreCollector:
    """
    Collects Microsoft Secure Score data from Graph API.
    
    Features:
    - Fetches current secure score and control details
    - Calculates trend from historical data
    - Computes percentile/benchmark comparison
    - Caches results for performance
    """
    
    def __init__(
        self,
        graph_client: GraphClient,
        cache_service: Optional[CacheService] = None,
        cosmos_service: Optional[CosmosService] = None,
    ):
        """
        Initialize collector.
        
        Args:
            graph_client: Initialized Graph API client
            cache_service: Optional cache service for performance
            cosmos_service: Optional CosmosDB service for historical data
        """
        self._graph = graph_client
        self._cache = cache_service
        self._cosmos = cosmos_service
        self._tenant_id = graph_client.tenant_id
        
        logger.info("secure_score_collector_initialized", tenant_id=self._tenant_id)
    
    async def collect(self, force_refresh: bool = False) -> SecurityScore:
        """
        Collect current secure score.
        
        Args:
            force_refresh: Bypass cache and fetch fresh data
            
        Returns:
            SecurityScore model with current data
        """
        # Check cache first
        if not force_refresh and self._cache:
            cached = await self._cache.get(self._tenant_id, "secure_score")
            if cached:
                logger.debug("secure_score_cache_hit", tenant_id=self._tenant_id)
                return SecurityScore(**cached)
        
        # Fetch from Graph API
        logger.info("fetching_secure_score", tenant_id=self._tenant_id)
        raw_data = await self._graph.get_secure_score()
        
        # Calculate percentile (in production, this would compare to benchmark data)
        percentile = self._calculate_percentile(raw_data["current_score"])
        
        # Get trend from historical data
        trend = await self._calculate_trend()
        
        # Build response model
        score = SecurityScore(
            current_score=raw_data["current_score"],
            max_score=raw_data["max_score"],
            percentile=percentile,
            trend=trend,
            comparison_label=self._get_comparison_label(percentile),
            last_updated=datetime.utcnow(),
        )
        
        # Cache the result
        if self._cache:
            await self._cache.set(
                self._tenant_id,
                "secure_score",
                score.model_dump(),
            )
        
        # Save to CosmosDB for historical tracking
        if self._cosmos:
            await self._cosmos.save_security_score(
                self._tenant_id,
                {
                    "current_score": score.current_score,
                    "max_score": score.max_score,
                    "percentile": score.percentile,
                },
            )
        
        logger.info(
            "secure_score_collected",
            tenant_id=self._tenant_id,
            score=score.current_score,
            max_score=score.max_score,
        )
        
        return score
    
    async def get_control_scores(self) -> list[dict]:
        """
        Get detailed control scores.
        
        Returns list of individual control scores with recommendations.
        """
        raw_data = await self._graph.get_secure_score()
        return raw_data.get("control_scores", [])
    
    async def get_improvement_actions(self) -> list[dict]:
        """
        Get recommended improvement actions sorted by impact.
        
        Returns:
            List of actions with potential score improvement
        """
        controls = await self.get_control_scores()
        
        # Sort by potential improvement (max_score - current_score)
        actions = []
        for control in controls:
            potential = (control.get("max_score", 0) or 0) - (control.get("score", 0) or 0)
            if potential > 0:
                actions.append({
                    "name": control.get("name"),
                    "description": control.get("description"),
                    "current_score": control.get("score", 0),
                    "max_score": control.get("max_score", 0),
                    "potential_improvement": potential,
                })
        
        # Sort by potential improvement descending
        actions.sort(key=lambda x: x["potential_improvement"], reverse=True)
        
        return actions
    
    async def _calculate_trend(self) -> Optional[MetricTrend]:
        """
        Calculate score trend from historical data.
        """
        if not self._cosmos:
            return None
        
        try:
            history = await self._cosmos.get_security_score_history(
                self._tenant_id,
                days=7,
            )
            
            if len(history) < 2:
                return MetricTrend(
                    direction=TrendDirection.STABLE,
                    change_value=0,
                    period="7d",
                )
            
            # Compare current to 7 days ago
            current = history[0].get("current_score", 0)
            previous = history[-1].get("current_score", 0)
            
            change = current - previous
            change_percent = (change / previous * 100) if previous > 0 else 0
            
            if change > 0.5:
                direction = TrendDirection.UP
            elif change < -0.5:
                direction = TrendDirection.DOWN
            else:
                direction = TrendDirection.STABLE
            
            return MetricTrend(
                direction=direction,
                change_value=round(change, 1),
                change_percent=round(change_percent, 1),
                period="7d",
            )
            
        except Exception as e:
            logger.warning("trend_calculation_error", error=str(e))
            return None
    
    def _calculate_percentile(self, score: float) -> int:
        """
        Calculate percentile based on industry benchmarks.
        
        In production, this would use actual benchmark data.
        """
        # Rough percentile calculation based on typical score distribution
        # Average secure score is around 50-60
        if score >= 80:
            return 95
        elif score >= 70:
            return 75
        elif score >= 60:
            return 50
        elif score >= 50:
            return 35
        elif score >= 40:
            return 20
        else:
            return 10
    
    def _get_comparison_label(self, percentile: int) -> str:
        """
        Get human-readable comparison label.
        """
        if percentile >= 90:
            return "Top 10%"
        elif percentile >= 75:
            return "Top 25%"
        elif percentile >= 50:
            return "Top 50%"
        elif percentile >= 25:
            return "Bottom 50%"
        else:
            return "Bottom 25%"
