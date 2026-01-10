"""
Grading System for Security Assessments

Provides consistent scoring and grading across all assessments.
"""
from typing import Optional


def calculate_grade(score: float) -> str:
    """
    Calculate letter grade from numeric score.
    
    Grading Scale:
        A: 90-100 - Excellent, industry leading
        B: 75-89  - Good, above average
        C: 60-74  - Fair, meets minimum standards
        D: 40-59  - Poor, significant gaps
        F: 0-39   - Critical, immediate action required
    
    Args:
        score: Numeric score (0-100)
        
    Returns:
        Letter grade (A, B, C, D, or F)
    """
    if score >= 90:
        return "A"
    elif score >= 75:
        return "B"
    elif score >= 60:
        return "C"
    elif score >= 40:
        return "D"
    else:
        return "F"


def get_grade_description(grade: str) -> str:
    """Get description for a letter grade."""
    descriptions = {
        "A": "Excellent - Industry leading security posture",
        "B": "Good - Above average with minor improvements needed",
        "C": "Fair - Meets minimum standards but has gaps",
        "D": "Poor - Significant security gaps requiring attention",
        "F": "Critical - Immediate action required to address vulnerabilities",
    }
    return descriptions.get(grade, "Unknown")


def calculate_overall_score(
    secure_score: float,
    category_scores: dict[str, float],
) -> float:
    """
    Calculate overall security score.
    
    Weighted calculation:
        - Microsoft Secure Score: 30%
        - Identity: 25%
        - Data Protection: 15%
        - Backup/Recovery: 15%
        - Devices: 10%
        - Network: 5%
    
    Args:
        secure_score: Microsoft Secure Score (0-100)
        category_scores: Dictionary of category scores
        
    Returns:
        Overall score (0-100)
    """
    weights = {
        "identity": 0.25,
        "data_protection": 0.15,
        "backup": 0.15,
        "devices": 0.10,
        "network": 0.05,
    }
    
    # Secure score contributes 30%
    weighted_score = secure_score * 0.30
    
    # Add category scores
    for category, weight in weights.items():
        score = category_scores.get(category, 50)  # Default to 50 if missing
        weighted_score += score * weight
    
    return min(100, max(0, weighted_score))


def calculate_category_scores(raw_data: dict) -> dict[str, float]:
    """
    Calculate scores for each security category.
    
    Args:
        raw_data: Collected assessment data
        
    Returns:
        Dictionary of category scores
    """
    scores = {}
    
    # Identity score
    scores["identity"] = _calculate_identity_score(raw_data.get("identity", {}))
    
    # Data protection score (from secure score controls)
    scores["data_protection"] = _calculate_data_protection_score(raw_data.get("secure_score", {}))
    
    # Backup score
    scores["backup"] = _calculate_backup_score(raw_data.get("backup", {}))
    
    # Device score
    scores["devices"] = _calculate_device_score(raw_data.get("devices", {}))
    
    # Network score (from secure score controls)
    scores["network"] = _calculate_network_score(raw_data.get("secure_score", {}))
    
    return scores


def _calculate_identity_score(identity_data: dict) -> float:
    """
    Calculate identity security score.
    
    Factors:
        - MFA coverage (40%)
        - Privileged account management (30%)
        - Risk detection response (20%)
        - Conditional Access (10%)
    """
    score = 0
    
    # MFA coverage - 40 points
    mfa = identity_data.get("mfa_coverage", {})
    admin_mfa = mfa.get("admin_coverage_percent", 0)
    user_mfa = mfa.get("user_coverage_percent", 0)
    # Admins weighted more heavily
    mfa_score = (admin_mfa * 0.6 + user_mfa * 0.4) * 0.40
    score += mfa_score
    
    # Privileged accounts - 30 points
    priv = identity_data.get("privileged_accounts", {})
    global_admins = priv.get("global_admin_count", 0)
    # Ideal is 2-4 global admins
    if global_admins <= 4:
        priv_score = 30
    elif global_admins <= 6:
        priv_score = 20
    elif global_admins <= 10:
        priv_score = 10
    else:
        priv_score = 0
    score += priv_score
    
    # Risk detection - 20 points
    risky = identity_data.get("risky_users", {})
    high_risk = risky.get("high_risk_count", 0)
    if high_risk == 0:
        risk_score = 20
    elif high_risk <= 2:
        risk_score = 10
    else:
        risk_score = 0
    score += risk_score
    
    # Conditional Access - 10 points
    ca_policies = identity_data.get("conditional_access_policies", [])
    enabled_policies = len([p for p in ca_policies if p.get("state") == "enabled"])
    if enabled_policies >= 5:
        ca_score = 10
    elif enabled_policies >= 3:
        ca_score = 7
    elif enabled_policies >= 1:
        ca_score = 4
    else:
        ca_score = 0
    score += ca_score
    
    return min(100, max(0, score))


def _calculate_data_protection_score(secure_score_data: dict) -> float:
    """
    Calculate data protection score from secure score controls.
    
    Looks at data-related controls in Microsoft Secure Score.
    """
    controls = secure_score_data.get("controls", [])
    
    # Data protection related control categories
    data_controls = [
        c for c in controls
        if any(keyword in (c.get("name", "") or "").lower() 
               for keyword in ["encrypt", "dlp", "data", "information", "classification"])
    ]
    
    if not data_controls:
        return 60  # Default if no controls found
    
    # Calculate based on control scores
    total_score = 0
    total_max = 0
    for control in data_controls:
        total_score += control.get("score", 0) or 0
        total_max += control.get("max_score", 0) or 0
    
    if total_max == 0:
        return 60
    
    return (total_score / total_max) * 100


def _calculate_backup_score(backup_data: dict) -> float:
    """
    Calculate backup/recovery readiness score.
    
    Factors:
        - Backup coverage (50%)
        - RTO compliance (25%)
        - RPO compliance (25%)
    """
    health = backup_data.get("health", {})
    recovery = backup_data.get("recovery_readiness", {})
    
    # Not configured = 0
    if health.get("status") == "not_configured":
        return 0
    
    score = 0
    
    # Backup coverage - 50 points
    coverage = health.get("protected_percent", 0)
    score += coverage * 0.50
    
    # RTO compliance - 25 points
    rto_status = recovery.get("rto_status", "unknown")
    if rto_status == "healthy":
        score += 25
    elif rto_status == "warning":
        score += 15
    elif rto_status == "at_risk":
        score += 5
    
    # RPO compliance - 25 points
    rpo_status = recovery.get("rpo_status", "unknown")
    if rpo_status == "healthy":
        score += 25
    elif rpo_status == "warning":
        score += 15
    elif rpo_status == "at_risk":
        score += 5
    
    return min(100, max(0, score))


def _calculate_device_score(device_data: dict) -> float:
    """
    Calculate device compliance score.
    """
    compliance = device_data.get("compliance", {})
    
    # Direct compliance percentage
    return compliance.get("compliance_percent", 50)


def _calculate_network_score(secure_score_data: dict) -> float:
    """
    Calculate network security score from secure score controls.
    """
    controls = secure_score_data.get("controls", [])
    
    # Network-related control categories
    network_controls = [
        c for c in controls
        if any(keyword in (c.get("name", "") or "").lower() 
               for keyword in ["network", "firewall", "nsg", "vpn", "gateway"])
    ]
    
    if not network_controls:
        return 70  # Default if no controls found
    
    total_score = 0
    total_max = 0
    for control in network_controls:
        total_score += control.get("score", 0) or 0
        total_max += control.get("max_score", 0) or 0
    
    if total_max == 0:
        return 70
    
    return (total_score / total_max) * 100


def calculate_compliance_score(
    controls_passed: int,
    controls_total: int,
    critical_failures: int = 0,
) -> float:
    """
    Calculate compliance framework score.
    
    Base score is percentage of controls passed, with penalty for critical failures.
    
    Args:
        controls_passed: Number of controls passed
        controls_total: Total controls assessed
        critical_failures: Number of critical control failures
        
    Returns:
        Compliance score (0-100)
    """
    if controls_total == 0:
        return 0
    
    base_score = (controls_passed / controls_total) * 100
    
    # Penalty for critical failures (5 points each, max 25 point penalty)
    penalty = min(25, critical_failures * 5)
    
    return max(0, base_score - penalty)
