def compute_priority(task) -> float:
    """
    Score = (urgency × 0.5) + (lives_at_risk × 0.3) + (time_sensitivity × 0.2)
    Returns 0.0–1.0
    """
    urgency_score        = task.urgency / 5.0
    lives_score          = min(task.lives_at_risk / 100, 1.0)
    time_score           = 1.0  # extend later: decay over time if unassigned

    return round(
        (urgency_score * 0.5) +
        (lives_score   * 0.3) +
        (time_score    * 0.2),
        3
    )
