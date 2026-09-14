import time
from threading import Thread
from ml.escalation_engine import calculate_escalation
from datetime import datetime
from zoneinfo import ZoneInfo
from sqlalchemy.exc import SQLAlchemyError

from app import app, db, EmergencyIncident, socketio, AuditLog

def ist_now():
    return datetime.now(
        ZoneInfo("Asia/Kolkata")
    ).replace(tzinfo=None)


def escalation_monitor():
    print("🚨 SafeShield Background Escalation Monitor Started")

    while True:

        try:

            with app.app_context():

                incidents = EmergencyIncident.query.filter(
                    EmergencyIncident.status.in_([
                        "ACTIVE",
                        "ACKNOWLEDGED",
                        "RESPONDING"
                    ])
                ).all()

                updated_incidents = []

                for incident in incidents:

                    try:

                        escalation = calculate_escalation(
                            incident.priority,
                            incident.status,
                            incident.created_at
                        )

                        old_level = incident.escalation_level
                        old_status = incident.escalation_status

                        new_level = escalation["level"]
                        new_status = escalation["status"]

                        if (
                            old_level != new_level
                            or old_status != new_status
                        ):

                            incident.escalation_level = new_level
                            incident.escalation_status = new_status
                            incident.escalation_reason = escalation["reason"]

                            if (
                                new_status == "ESCALATED"
                                and incident.escalated_at is None
                            ):
                                incident.escalated_at = ist_now()

                            audit = AuditLog(
                                actor_id=None,
                                actor_role="SYSTEM",
                                action="INCIDENT_ESCALATION_UPDATED",
                                incident_id=incident.id,
                                description=(
                                    f"System escalation changed from "
                                    f"Level {old_level}/{old_status} "
                                    f"to Level {new_level}/{new_status}. "
                                    f"Reason: {escalation['reason']}"
                                )
                            )

                            db.session.add(audit)

                            updated_incidents.append(incident)

                    except Exception as e:

                        print(
                            f"⚠️ Incident #{incident.id} "
                            f"processing error: {e}"
                        )

                        db.session.rollback()

                if updated_incidents:

                    try:

                        db.session.commit()

                        print(
                            f"✅ Saved "
                            f"{len(updated_incidents)} "
                            f"escalation update(s)."
                        )

                    except SQLAlchemyError as e:

                        db.session.rollback()

                        print(
                            "❌ Escalation database commit error:",
                            e
                        )

                        updated_incidents = []

                for incident in updated_incidents:

                    try:

                        socketio.emit(
                            "incident_escalated",
                            {
                                "id": incident.id,
                                "priority": incident.priority,
                                "status": incident.status,
                                "escalation_level": incident.escalation_level,
                                "escalation_status": incident.escalation_status,
                                "escalation_reason": incident.escalation_reason,
                                "latitude": incident.latitude,
                                "longitude": incident.longitude,
                                "created_at": incident.created_at.strftime(
                                    "%Y-%m-%d %H:%M:%S"
                                )
                            },
                            room="authority"
                        )

                        print(
                            f"🚨 Incident #{incident.id} "
                            f"escalation updated → "
                            f"Level {incident.escalation_level}"
                        )

                    except Exception as e:

                        print(
                            f"⚠️ Socket.IO error "
                            f"for incident #{incident.id}: {e}"
                        )

        except SQLAlchemyError as e:

            db.session.rollback()

            print(
                "❌ Escalation monitor database error:",
                e
            )

        except Exception as e:

            db.session.rollback()

            print(
                "❌ Escalation monitor unexpected error:",
                e
            )

        time.sleep(30)
def start_monitor():

    monitor_thread = Thread(
        target=escalation_monitor,
        daemon=True,
        name="SafeShield-Escalation-Monitor"
    )

    monitor_thread.start()


if __name__ == "__main__":

    start_monitor()

    while True:
        time.sleep(60)