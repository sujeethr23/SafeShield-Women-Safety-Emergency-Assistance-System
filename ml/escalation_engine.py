from datetime import datetime


def calculate_escalation(priority, status, created_at):
    """
    Priority-aware escalation engine.

    This is a deterministic safety policy layer.
    The ML model provides the priority; this engine
    determines the recommended escalation level.
    """

    priority = str(priority or "MEDIUM").upper()
    status = str(status or "ACTIVE").upper()

    # Resolved incidents do not require escalation.
    if status == "RESOLVED":
        return {
            "level": 0,
            "status": "NORMAL",
            "reason": "Incident resolved.",
        }

    # Calculate how long the incident has remained open.
    elapsed_minutes = 0

    if created_at:
        try:
            elapsed_seconds = (
                datetime.now() - created_at
            ).total_seconds()

            elapsed_minutes = max(
                0,
                int(elapsed_seconds / 60)
            )
        except Exception:
            elapsed_minutes = 0

    # -------------------------------------------------
    # CRITICAL
    # -------------------------------------------------

    if priority == "CRITICAL":

        return {
            "level": 3,
            "status": "ESCALATED",
            "reason": "Critical priority incident requires immediate attention.",
        }

    # -------------------------------------------------
    # HIGH
    # -------------------------------------------------

    if priority == "HIGH":

        if elapsed_minutes >= 5:
            return {
                "level": 3,
                "status": "ESCALATED",
                "reason": "High priority incident has remained open for 5 minutes or more.",
            }

        return {
            "level": 2,
            "status": "ESCALATED",
            "reason": "High priority incident requires urgent attention.",
        }

    # -------------------------------------------------
    # MEDIUM
    # -------------------------------------------------

    if priority == "MEDIUM":

        if elapsed_minutes >= 10:
            return {
                "level": 2,
                "status": "ESCALATED",
                "reason": "Medium priority incident has remained open for 10 minutes or more.",
            }

        return {
            "level": 1,
            "status": "ESCALATED",
            "reason": "Medium priority incident requires priority attention.",
        }

    # -------------------------------------------------
    # LOW
    # -------------------------------------------------

    if priority == "LOW":

        if elapsed_minutes >= 20:
            return {
                "level": 1,
                "status": "ESCALATED",
                "reason": "Low priority incident has remained open for 20 minutes or more.",
            }

        return {
            "level": 0,
            "status": "NORMAL",
            "reason": "Low priority incident.",
        }

    # -------------------------------------------------
    # FALLBACK
    # -------------------------------------------------

    return {
        "level": 1,
        "status": "ESCALATED",
        "reason": "Unknown priority; manual authority review recommended.",
    }