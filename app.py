import os
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO, join_room, leave_room
from flask_wtf.csrf import CSRFProtect
from sqlalchemy.exc import SQLAlchemyError
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from ml.priority_predictor import predict_priority
from ml.escalation_engine import calculate_escalation
from datetime import datetime
from zoneinfo import ZoneInfo
def ist_now():
    return datetime.now(
        ZoneInfo("Asia/Kolkata")
    ).replace(tzinfo=None)
app = Flask(__name__)

# =========================================================
# ENVIRONMENT
# =========================================================

APP_ENV = os.environ.get(
    "SAFE_SHIELD_ENV",
    "development"
).lower()

IS_PRODUCTION = APP_ENV == "production"

# =========================================================
# SECRET KEY
# =========================================================

SECRET_KEY = os.environ.get("SAFE_SHIELD_SECRET_KEY")

if IS_PRODUCTION and not SECRET_KEY:
    raise RuntimeError(
        "SAFE_SHIELD_SECRET_KEY must be set in production."
    )

if not SECRET_KEY:
    SECRET_KEY = "safeshield-development-secret-key"

app.config["SECRET_KEY"] = SECRET_KEY

# =========================================================
# SESSION SECURITY
# =========================================================

app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

# Local development uses HTTP.
# Production should use HTTPS.
app.config["SESSION_COOKIE_SECURE"] = IS_PRODUCTION

app.config["PERMANENT_SESSION_LIFETIME"] = 3600
app.config["SESSION_REFRESH_EACH_REQUEST"] = True

# =========================================================
# CSRF PROTECTION
# =========================================================

csrf = CSRFProtect(app)

# =========================================================
# DATABASE
# =========================================================

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# =========================================================
# SOCKET.IO
# =========================================================

socketio = SocketIO(
    app,
    cors_allowed_origins=[
        "http://127.0.0.1:5000",
        "http://localhost:5000"
    ],
    async_mode="threading"
)
# =========================================================
# SOCKET.IO AUTHORITY + USER ACCESS CONTROL
# =========================================================

@socketio.on("connect")
def handle_socket_connect(auth=None):

    # -----------------------------------------------------
    # AUTHORITY SOCKET CONNECTION
    # -----------------------------------------------------

    authority_id = session.get("authority_id")

    if authority_id:

        authority = db.session.get(
            User,
            authority_id
        )

        if authority and authority.role == "AUTHORITY":

            join_room("authority")

            print(
                f"🔐 Authority Socket.IO connection established "
                f"for authority #{authority.id}"
            )

            return True

    # -----------------------------------------------------
    # USER SOCKET CONNECTION
    # -----------------------------------------------------

    user_id = session.get("user_id")

    if user_id:

        user = db.session.get(
            User,
            user_id
        )

        if user and user.role == "USER":

            user_room = f"user_{user.id}"

            join_room(user_room)

            print(
                f"👤 User Socket.IO connection established "
                f"for user #{user.id}"
            )

            return True

    # -----------------------------------------------------
    # NON-AUTHENTICATED CONNECTION
    # -----------------------------------------------------

    print(
        "ℹ️ Non-authenticated Socket.IO connection established."
    )

    return True


@socketio.on("disconnect")
def handle_socket_disconnect():

    print(
        "ℹ️ Socket.IO client disconnected."
    )


# =========================================================
# USER AUTHENTICATION DECORATOR
# =========================================================

def user_required(f):

    @wraps(f)
    def decorated_function(*args, **kwargs):

        user_id = session.get("user_id")

        if not user_id:

            return jsonify({
                "success": False,
                "message": "User login required."
            }), 401

        user = db.session.get(
            User,
            user_id
        )

        if not user or user.role != "USER":

            session.pop(
                "user_id",
                None
            )

            session.pop(
                "user_name",
                None
            )

            return jsonify({
                "success": False,
                "message": "Valid user authentication required."
            }), 401

        return f(
            *args,
            **kwargs
        )

    return decorated_function


# =========================================================
# AUTHORITY AUTHENTICATION DECORATOR
# =========================================================

def authority_required(f):

    @wraps(f)
    def decorated_function(*args, **kwargs):

        authority_id = session.get("authority_id")

        if not authority_id:

            return jsonify({
                "success": False,
                "message": "Authority login required."
            }), 401

        authority = db.session.get(
            User,
            authority_id
        )

        if not authority or authority.role != "AUTHORITY":

            session.pop(
                "authority_id",
                None
            )

            session.pop(
                "authority_name",
                None
            )

            return jsonify({
                "success": False,
                "message": "Valid authority authentication required."
            }), 401

        return f(
            *args,
            **kwargs
        )

    return decorated_function

# =========================================================
# USER
# =========================================================

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100), nullable=False)

    email = db.Column(db.String(120), unique=True, nullable=False)

    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default="USER")


    created_at = db.Column(
        db.DateTime,
        default=ist_now
    )
# =========================================================
# EMERGENCY INCIDENT
# =========================================================

class EmergencyIncident(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    latitude = db.Column(db.Float, nullable=False)

    longitude = db.Column(db.Float, nullable=False)

    status = db.Column(
        db.String(50),
        default="ACTIVE"
    )

    priority = db.Column(
        db.String(20),
        default="MEDIUM"
    )
    # User-submitted emergency details
    category = db.Column(
        db.String(100),
        nullable=True
    )

    location_description = db.Column(
        db.String(255),
        nullable=True
    )

    severity = db.Column(
        db.Integer,
        nullable=True
    )

    urgency = db.Column(
        db.Integer,
        nullable=True
    )

    user_message = db.Column(
        db.Text,
        nullable=True
    )
    escalation_level = db.Column(
    	db.Integer,
    	default=0
    )

    escalation_status = db.Column(
    	db.String(20),
    	default="NORMAL"
    )

    escalation_reason = db.Column(
    	db.String(255),
    	nullable=True
    )

    escalated_at = db.Column(
    	db.DateTime,
    	nullable=True
    )
    response_notes = db.Column(db.Text, nullable=True
    )
    resolution_summary = db.Column(db.Text, nullable=True
    )

    created_at = db.Column(
        db.DateTime,
        default=ist_now
    )

    # New user connection
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=True
    )

    contact_id = db.Column(
        db.Integer,
        db.ForeignKey("emergency_contact.id"),
        nullable=True
    )

    user = db.relationship(
        "User",
        backref="incidents"
    )

    contact = db.relationship(
        "EmergencyContact",
        foreign_keys=[contact_id]
    )
# Create tables
# =========================================================
# EMERGENCY NOTIFICATION LOG
# =========================================================

class EmergencyNotification(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    incident_id = db.Column(
        db.Integer,
        db.ForeignKey("emergency_incident.id"),
        nullable=False
    )

    recipient_name = db.Column(
        db.String(100),
        nullable=True
    )

    recipient_phone = db.Column(
        db.String(20),
        nullable=True
    )

    notification_type = db.Column(
        db.String(50),
        nullable=False,
        default="EMERGENCY_CONTACT"
    )

    message = db.Column(
        db.Text,
        nullable=False
    )

    status = db.Column(
        db.String(30),
        nullable=False,
        default="SIMULATED"
    )

    created_at = db.Column(
        db.DateTime,
        default=ist_now
    )

    incident = db.relationship(
        "EmergencyIncident",
        backref=db.backref(
            "notifications",
            lazy=True
        )
    )
@socketio.on("connect")
def handle_socket_connect(auth=None):

    authority_id = session.get("authority_id")

    if authority_id:
        authority = db.session.get(User, authority_id)

        if authority and authority.role == "AUTHORITY":
            join_room("authority")

            print(
                f"🔐 Authority Socket.IO connection established "
                f"for authority #{authority.id}"
            )

            return True

    print("ℹ️ Non-authority Socket.IO connection established.")

    return True


@socketio.on("disconnect")
def handle_socket_disconnect():

    print("ℹ️ Socket.IO client disconnected.")
# =========================================================
# HOME
# =========================================================

@app.route("/")
def home():

    return render_template("home.html")
# =========================================================
# REGISTER
# =========================================================

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")

        if not name or not email or not password:

            return render_template(
                "register.html",
                error="All fields are required."
            )

        existing_user = User.query.filter_by(
            email=email
        ).first()

        if existing_user:

            return render_template(
                "register.html",
                error="An account with this email already exists."
            )

        hashed_password = generate_password_hash(
            password
        )

        user = User(
            name=name,
            email=email,
            password=hashed_password
        )

        db.session.add(user)

        try:

            db.session.commit()
        except SQLAlchemyError as e:

    	    db.session.rollback()

    	    print("❌ Registration database error:", e)

        return render_template(
            "register.html",
            error="Unable to create the account. Please try again."
    	)

        return redirect(url_for("login"))

    return render_template("register.html")
# =========================================================
# LOGIN
# =========================================================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(
            email=email
        ).first()

        if user and check_password_hash(user.password, password):
            # Keep any existing authority session intact so both
            # authenticated areas can coexist in separate tabs during
            # local testing.
            session.permanent = True
            session["user_id"] = user.id
            session["user_name"] = user.name

            return redirect(url_for("user_dashboard"))

        return render_template(
            "login.html",
            error="Invalid email or password."
        )

    return render_template("login.html")
@app.route("/authority-login", methods=["GET", "POST"])
def authority_login():

    if request.method == "POST":

        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(
            email=email
        ).first()

        if user and user.role == "AUTHORITY" and check_password_hash(
            user.password,
            password
        ):

            # Keep any existing user session intact so both
            # authenticated areas can coexist in separate tabs during
            # local testing.
            session.permanent = True
            session["authority_id"] = user.id
            session["authority_name"] = user.name

            return redirect(url_for("admin_dashboard"))

        return render_template(
            "authority_login.html",
            error="Invalid authority credentials."
        )

    return render_template("authority_login.html")
# =========================================================
# LOGOUT
# =========================================================

@app.route("/logout")
def logout():
    # User logout only removes the user-side session keys.
    # Any authority session remains available in another tab.
    session.pop("user_id", None)
    session.pop("user_name", None)

    return redirect(url_for("login"))


@app.route("/authority-logout")
def authority_logout():
    # Authority logout only removes the authority-side session keys.
    # Any user session remains available in another tab.
    session.pop("authority_id", None)
    session.pop("authority_name", None)

    return redirect(url_for("authority_login"))

# =========================================================
# USER DASHBOARD
# =========================================================

@app.route("/dashboard")
@user_required
def user_dashboard():

    unread_notifications = UserNotification.query.filter_by(
        user_id=session["user_id"],
        is_read=False
    ).count()

    return render_template(
        "dashboard.html",
        user_name=session["user_name"],
        unread_notifications=unread_notifications
    )
# =========================================================
# EMERGENCY CONTACTS
# =========================================================

@app.route(
    "/emergency-contacts",
    methods=["GET", "POST"]
)
def emergency_contacts():

    if "user_id" not in session:
        return redirect(url_for("login"))
    if request.method == "POST":

        name = request.form.get("name")
        phone = request.form.get("phone")
        relationship = request.form.get("relationship")

        if not name or not phone or not relationship:

            return render_template(
                "emergency_contacts.html",
                error="All fields are required.",
                contacts=[]
            )

        contact = EmergencyContact(
            user_id=session["user_id"],
            name=name,
            phone=phone,
            relationship=relationship
        )

        db.session.add(contact)
        db.session.commit()

    contacts = EmergencyContact.query.filter_by(
        user_id=session["user_id"]
    ).all()

    return render_template(
        "emergency_contacts.html",
        contacts=contacts
    )
def get_user_contact(contact_id):
    return EmergencyContact.query.filter_by(
        id=contact_id,
        user_id=session["user_id"]
    ).first()
# =========================================================
# CREATE SOS
# =========================================================

@app.route("/api/sos", methods=["POST"])
@user_required
def create_sos():

    if "user_id" not in session:
        return jsonify({
            "success": False,
            "message": "Please login before using SOS."
        }), 401

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "success": False,
            "message": "Invalid request data."
        }), 400

    # -----------------------------------------------------
    # LOCATION VALIDATION
    # -----------------------------------------------------

    latitude = data.get("latitude")
    longitude = data.get("longitude")

    if latitude is None or longitude is None:
        return jsonify({
            "success": False,
            "message": "Location not received."
        }), 400

    try:
        latitude = float(latitude)
        longitude = float(longitude)

    except (TypeError, ValueError):
        return jsonify({
            "success": False,
            "message": "Invalid location coordinates."
        }), 400

    if not (-90 <= latitude <= 90):
        return jsonify({
            "success": False,
            "message": "Invalid latitude."
        }), 400

    if not (-180 <= longitude <= 180):
        return jsonify({
            "success": False,
            "message": "Invalid longitude."
        }), 400

    # -----------------------------------------------------
    # INPUT VALIDATION
    # -----------------------------------------------------

    category = str(data.get("category", "Other")).strip()
    location = str(data.get("location", "Road")).strip()
    message = str(data.get("message", "")).strip()

    try:
        severity = int(data.get("severity", 3))
        urgency = int(data.get("urgency", 3))

    except (TypeError, ValueError):
        return jsonify({
            "success": False,
            "message": "Invalid severity or urgency."
        }), 400

    if not (1 <= severity <= 5):
        return jsonify({
            "success": False,
            "message": "Severity must be between 1 and 5."
        }), 400

    if not (1 <= urgency <= 5):
        return jsonify({
            "success": False,
            "message": "Urgency must be between 1 and 5."
        }), 400

    if len(message) > 500:
        return jsonify({
            "success": False,
            "message": "Emergency message is too long."
        }), 400

    # -----------------------------------------------------
    # DUPLICATE SOS PROTECTION
    # -----------------------------------------------------

    from datetime import timedelta

    recent_incident = EmergencyIncident.query.filter(
        EmergencyIncident.user_id == session["user_id"]
    ).order_by(
        EmergencyIncident.created_at.desc()
    ).first()

    if recent_incident:

        elapsed = ist_now() - recent_incident.created_at

        if elapsed < timedelta(seconds=60):

            return jsonify({
                "success": True,
                "duplicate": True,
                "incident_id": recent_incident.id,
                "message": "A recent SOS was already submitted. Please wait before submitting another."
            })

    # -----------------------------------------------------
    # AI PRIORITY
    # -----------------------------------------------------

    priority = predict_priority(
        category,
        location,
        severity,
        urgency
    )

    # -----------------------------------------------------
    # GET EMERGENCY CONTACT
    # -----------------------------------------------------

    contact = EmergencyContact.query.filter_by(
        user_id=session["user_id"]
    ).first()

    # -----------------------------------------------------
    # DATABASE TRANSACTION
    # -----------------------------------------------------

    try:

        # Create incident
        incident = EmergencyIncident(
            latitude=latitude,
            longitude=longitude,
            status="ACTIVE",
            priority=priority,
            category=category,
            location_description=location,
            severity=severity,
            urgency=urgency,
            user_message=message,
            user_id=session["user_id"],
            contact_id=contact.id if contact else None
        )

        db.session.add(incident)

        # Get generated incident ID
        db.session.flush()

        # -------------------------------------------------
        # AUDIT: INCIDENT CREATED
        # -------------------------------------------------

        audit_created = AuditLog(
            actor_id=session["user_id"],
            actor_role="USER",
            action="INCIDENT_CREATED",
            incident_id=incident.id,
            description="User created a new emergency incident."
        )

        db.session.add(audit_created)

        # -------------------------------------------------
        # EMERGENCY CONTACT NOTIFICATION
        # -------------------------------------------------

        notification_message = f"""
🚨 SAFESHIELD EMERGENCY

Incident ID: #{incident.id}
Category: {category}
Location Type: {location}
Severity: {severity}/5
Urgency: {urgency}/5
AI Priority: {priority}

Emergency Details:
{message or "No additional details provided."}

Status: ACTIVE

This is a SafeShield development notification.
"""

        notification = EmergencyNotification(
            incident_id=incident.id,
            recipient_name=contact.name if contact else "Emergency Contact",
            recipient_phone=contact.phone if contact else None,
            notification_type="EMERGENCY_CONTACT",
            message=notification_message,
            status="SIMULATED"
        )

        db.session.add(notification)

        # -------------------------------------------------
        # AUDIT: NOTIFICATION CREATED
        # -------------------------------------------------

        audit_notification = AuditLog(
            actor_id=session["user_id"],
            actor_role="USER",
            action="EMERGENCY_NOTIFICATION_CREATED",
            incident_id=incident.id,
            description="Emergency contact notification was created for the incident."
        )

        db.session.add(audit_notification)

        # -------------------------------------------------
        # INITIAL STATUS HISTORY
        # -------------------------------------------------

        history = IncidentStatusHistory(
            incident_id=incident.id,
            old_status=None,
            new_status="ACTIVE",
            changed_by=None
        )

        db.session.add(history)

        # -------------------------------------------------
        # ESCALATION CALCULATION
        # -------------------------------------------------

        escalation = calculate_escalation(
            incident.priority,
            incident.status,
            incident.created_at
        )

        incident.escalation_level = escalation["level"]
        incident.escalation_status = escalation["status"]
        incident.escalation_reason = escalation["reason"]

        if escalation["status"] == "ESCALATED":
            incident.escalated_at = ist_now()

        # -------------------------------------------------
        # ONE FINAL COMMIT
        # -------------------------------------------------

        db.session.commit()

    except SQLAlchemyError as e:

        # Cancel the entire transaction
        db.session.rollback()

        print("❌ SOS database error:", e)

        return jsonify({
            "success": False,
            "message": "Unable to create the emergency incident. Please try again."
        }), 500

    except Exception as e:

        # Safety rollback for unexpected errors
        db.session.rollback()

        print("❌ SOS unexpected error:", e)

        return jsonify({
            "success": False,
            "message": "An unexpected error occurred while creating the emergency incident."
        }), 500

    # -----------------------------------------------------
    # REAL-TIME AUTHORITY NOTIFICATION
    # -----------------------------------------------------
    # Emit ONLY AFTER successful database commit.
    # Do not expose private emergency-contact information.

    try:

        socketio.emit(
            "new_emergency",
            {
                "id": incident.id,
                "latitude": incident.latitude,
                "longitude": incident.longitude,
                "status": incident.status,
                "priority": incident.priority,
                "escalation_level": incident.escalation_level,
                "escalation_status": incident.escalation_status,
                "escalation_reason": incident.escalation_reason,
                "created_at": incident.created_at.strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
            },
	    room="authority"
        )

    except Exception as e:

        # The incident is already safely stored.
        # Socket failure must NOT make SOS creation fail.

        print("⚠️ Socket.IO notification error:", e)

    # -----------------------------------------------------
    # SUCCESS RESPONSE
    # -----------------------------------------------------

    return jsonify({
        "success": True,
        "incident_id": incident.id,
        "status": incident.status,
        "priority": incident.priority,
        "contact_name": contact.name if contact else None,
        "contact_phone": contact.phone if contact else None,
        "message": "Emergency incident created successfully."
    })
# =========================================================
# USER EMERGENCY TRACKING
# =========================================================
@app.route("/my-emergency")
@user_required
def my_emergency():

    user_id = session["user_id"]

    # First show the user's currently active emergency
    incident = EmergencyIncident.query.filter(
        EmergencyIncident.user_id == user_id,
        EmergencyIncident.status.in_([
            "ACTIVE",
            "ACKNOWLEDGED",
            "RESPONDING"
        ])
    ).order_by(
        EmergencyIncident.created_at.desc()
    ).first()

    # If there is no active emergency, show the most recently resolved one
    if incident is None:

        incident = EmergencyIncident.query.filter(
            EmergencyIncident.user_id == user_id,
            EmergencyIncident.status == "RESOLVED"
        ).order_by(
            EmergencyIncident.created_at.desc()
        ).first()

    if incident is None:

        return render_template(
            "my_emergency.html",
            incident=None,
            status_history=[]
        )

    status_history = IncidentStatusHistory.query.filter_by(
        incident_id=incident.id
    ).order_by(
        IncidentStatusHistory.changed_at.asc()
    ).all()

    return render_template(
        "my_emergency.html",
        incident=incident,
        status_history=status_history
    )
@app.route("/notifications")
@user_required
def notifications():

    user_notifications = UserNotification.query.filter_by(
        user_id=session["user_id"]
    ).order_by(
        UserNotification.created_at.desc()
    ).all()

    for notification in user_notifications:
        notification.is_read = True

    db.session.commit()

    return render_template(
        "notifications.html",
        notifications=user_notifications
    )
# =========================================================
# ADMIN DASHBOARD
# =========================================================
@app.route("/admin")
def admin_dashboard():

    if "authority_id" not in session:
        return redirect(url_for("authority_login"))

    # Get search and filter values
    search = request.args.get("search", "").strip()
    status = request.args.get("status", "").strip().upper()

    # Current page
    page = request.args.get("page", 1, type=int)

    # Start query
    query = EmergencyIncident.query

    # Search across all incidents
    if search:

        search_pattern = f"%{search}%"

        query = query.outerjoin(User).outerjoin(
            EmergencyContact,
            EmergencyIncident.contact_id == EmergencyContact.id
        ).filter(
            db.or_(
                db.cast(EmergencyIncident.id, db.String).like(search_pattern),
                User.name.ilike(search_pattern),
                EmergencyContact.name.ilike(search_pattern),
                EmergencyContact.phone.ilike(search_pattern)
            )
        )

    # Status filter
    if status in [
    	"ACTIVE",
    	"ACKNOWLEDGED",
    	"RESPONDING",
    	"RESOLVED"
    ]:
    	query = query.filter(
       	    EmergencyIncident.status == status
        )

    elif status == "ESCALATED":
        query = query.filter(
            EmergencyIncident.escalation_status == "ESCALATED"
        )

    # Pagination
    incidents_pagination = query.order_by(
        EmergencyIncident.created_at.desc()
    ).paginate(
        page=page,
        per_page=10,
        error_out=False
    )

    incidents = incidents_pagination.items

    # Dashboard statistics
    users_count = User.query.count()

    total_incidents = EmergencyIncident.query.count()

    active_count = EmergencyIncident.query.filter(
        EmergencyIncident.status.in_([
            "ACTIVE",
            "ACKNOWLEDGED",
            "RESPONDING"
        ])
    ).count()

    acknowledged_count = EmergencyIncident.query.filter_by(
        status="ACKNOWLEDGED"
    ).count()

    responding_count = EmergencyIncident.query.filter_by(
        status="RESPONDING"
    ).count()

    resolved_count = EmergencyIncident.query.filter_by(
        status="RESOLVED"
    ).count()
    status_distribution = {
        "ACTIVE": active_count,
        "ACKNOWLEDGED": acknowledged_count,
        "RESPONDING": responding_count,
        "RESOLVED": resolved_count
    }
    # Escalated incidents
    escalated_count = EmergencyIncident.query.filter_by(
        escalation_status="ESCALATED"
    ).count()
    level1_count = EmergencyIncident.query.filter_by(
        escalation_level=1
    ).count()

    level2_count = EmergencyIncident.query.filter_by(
        escalation_level=2
    ).count()

    level3_count = EmergencyIncident.query.filter_by(
        escalation_level=3
    ).count()
    critical_count = EmergencyIncident.query.filter_by(
        priority="CRITICAL"
    ).count()

    high_count = EmergencyIncident.query.filter_by(
        priority="HIGH"
    ).count()

    medium_count = EmergencyIncident.query.filter_by(
        priority="MEDIUM"
    ).count()

    low_count = EmergencyIncident.query.filter_by(
        priority="LOW"
    ).count()
    priority_escalation = {
        "CRITICAL": {
            "total": critical_count,
            "escalated": EmergencyIncident.query.filter_by(
                priority="CRITICAL",
                escalation_status="ESCALATED"
            ).count()
        },

        "HIGH": {
            "total": high_count,
            "escalated": EmergencyIncident.query.filter_by(
                priority="HIGH",
                escalation_status="ESCALATED"
            ).count()
        },

        "MEDIUM": {
            "total": medium_count,
            "escalated": EmergencyIncident.query.filter_by(
                priority="MEDIUM",
                escalation_status="ESCALATED"
            ).count()
        },

        "LOW": {
            "total": low_count,
            "escalated": EmergencyIncident.query.filter_by(
                priority="LOW",
                escalation_status="ESCALATED"
            ).count()
        }
    }
    escalation_changed = False

    escalation_changed = False
    # =====================================================
    # UPDATE ESCALATION STATUS
    # =====================================================

    escalation_changed = False

    for incident in incidents:

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
            or incident.escalation_reason != escalation["reason"]
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

            escalation_changed = True

    if escalation_changed:

        try:

            db.session.commit()

        except SQLAlchemyError as e:

            db.session.rollback()

            print(
                "❌ Admin escalation update error:",
                e
            )
    return render_template(
    	"admin.html",
    	incidents=incidents,
    	users_count=users_count,
    	total_incidents=total_incidents,
    	active_count=active_count,
    	acknowledged_count=acknowledged_count,
    	responding_count=responding_count,
    	resolved_count=resolved_count,
    	escalated_count=escalated_count,
    	level1_count=level1_count,
    	level2_count=level2_count,
    	level3_count=level3_count,
    	critical_count=critical_count,
    	high_count=high_count,
    	medium_count=medium_count,
    	low_count=low_count,
    	priority_escalation=priority_escalation,
    	status_distribution=status_distribution,
    	pagination=incidents_pagination,
    	search=search,
    	status=status
    )
#=========================================================
# UPDATE STATUS
# =========================================================
@app.route(
    "/api/incident/<int:incident_id>/status",
    methods=["POST"]
)
@authority_required
def update_status(incident_id):

    incident = EmergencyIncident.query.get_or_404(incident_id)

    data = request.get_json() or {}
    new_status = data.get("status")

    valid_statuses = [
        "ACTIVE",
        "ACKNOWLEDGED",
        "RESPONDING",
        "RESOLVED"
    ]

    if new_status not in valid_statuses:
        return jsonify({
            "success": False,
            "message": "Invalid incident status."
        }), 400

    if incident.status == new_status:
        return jsonify({
            "success": False,
            "message": "Incident is already in this status."
        }), 400

    allowed_transitions = {
        "ACTIVE": "ACKNOWLEDGED",
        "ACKNOWLEDGED": "RESPONDING",
        "RESPONDING": "RESOLVED"
    }

    if allowed_transitions.get(incident.status) != new_status:
        return jsonify({
            "success": False,
            "message": "Invalid status transition."
        }), 400

    old_status = incident.status
    
    incident.status = new_status
    # Create persistent notification for the incident owner
    notification_messages = {
        "ACKNOWLEDGED": (
            "Emergency acknowledged",
            "Your emergency has been acknowledged by the authority."
        ),
        "RESPONDING": (
            "Response being coordinated",
            "Response is being coordinated for your emergency."
        ),
        "RESOLVED": (
    	    "Emergency resolved",
    	    f"Your SafeShield incident #{incident.id} has been marked as resolved."
	)
    }

    title, message = notification_messages[new_status]

    user_notification = UserNotification(
    	user_id=incident.user_id,
    	incident_id=incident.id,
    	notification_type="INCIDENT_STATUS",
    	title=title,
    	message=message
    )

    db.session.add(user_notification)
    history=IncidentStatusHistory(
        incident_id=incident.id,
        old_status=old_status,
        new_status=new_status,
        changed_by=session["authority_id"]
    )

    db.session.add(history)

    # =====================================================
    # SECURITY AUDIT LOG
    # =====================================================

    audit = AuditLog(
        actor_id=session["authority_id"],
        actor_role="AUTHORITY",
        action="INCIDENT_STATUS_UPDATED",
        incident_id=incident.id,
        description=(
            f"Incident status changed from "
            f"{old_status} to {new_status}."
        )
    )

    db.session.add(audit)

    # =====================================================
    # DATABASE COMMIT
    # =====================================================

    try:

        db.session.commit()

    except SQLAlchemyError as e:

        db.session.rollback()

        print(
            "❌ Status update database error:",
            e
        )

        return jsonify({
            "success": False,
            "message": "Unable to update incident status."
        }), 500

    # =====================================================
    # REAL-TIME AUTHORITY + USER NOTIFICATION
    # =====================================================

    try:

        # Send update to authority dashboard
        socketio.emit(
            "incident_status_updated",
            {
                "id": incident.id,
                "old_status": old_status,
                "new_status": new_status
            },
            room="authority"
        )

        # Send private update to the incident owner
        socketio.emit(
            "my_incident_status_updated",
            {
                "id": incident.id,
                "old_status": old_status,
                "new_status": new_status
            },
            room=f"user_{incident.user_id}"
        )

    except Exception as e:

        print(
            "⚠️ Socket.IO status notification error:",
            e
        )

    return jsonify({
        "success": True,
        "message": "Incident status updated successfully.",
        "status": incident.status
    })
# =========================================================
# SAVE RESPONSE NOTES
# =========================================================

@app.route(
    "/api/incident/<int:incident_id>/response-notes",
    methods=["POST"]
)
@authority_required
def save_response_notes(incident_id):

    incident = EmergencyIncident.query.get_or_404(incident_id)

    data = request.get_json() or {}

    response_notes = data.get(
        "response_notes",
        ""
    ).strip()

    incident.response_notes = response_notes

    # =====================================================
    # SECURITY AUDIT LOG
    # =====================================================

    audit = AuditLog(
        actor_id=session["authority_id"],
        actor_role="AUTHORITY",
        action="RESPONSE_NOTES_UPDATED",
        incident_id=incident.id,
        description="Authority updated the incident response notes."
    )

    db.session.add(audit)

    try:

        db.session.commit()

    except SQLAlchemyError as e:

        db.session.rollback()

        print(
            f"❌ Response notes database error for incident #{incident.id}:",
            e
        )

        return jsonify({
            "success": False,
            "message": "Unable to save response notes. Please try again."
        }), 500

    return jsonify({
        "success": True,
        "message": "Response notes saved successfully."
    })

# =========================================================
# SAVE RESOLUTION SUMMARY
# =========================================================

@app.route(
    "/api/incident/<int:incident_id>/resolution-summary",
    methods=["POST"]
)
@authority_required
def save_resolution_summary(incident_id):

    incident = EmergencyIncident.query.get_or_404(incident_id)

    if incident.status != "RESPONDING":
        return jsonify({
            "success": False,
            "message": "Only incidents in RESPONDING status can be resolved."
        }), 400

    data = request.get_json() or {}

    resolution_summary = data.get(
        "resolution_summary",
        ""
    ).strip()

    if not resolution_summary:
        return jsonify({
            "success": False,
            "message": "Resolution summary is required."
        }), 400

    incident.resolution_summary = resolution_summary

    # =====================================================
    # SECURITY AUDIT LOG
    # =====================================================

    audit = AuditLog(
        actor_id=session["authority_id"],
        actor_role="AUTHORITY",
        action="RESOLUTION_SUMMARY_UPDATED",
        incident_id=incident.id,
        description="Authority added or updated the incident resolution summary."
    )

    db.session.add(audit)

    try:

        db.session.commit()

    except SQLAlchemyError as e:

        db.session.rollback()

        print(
            f"❌ Resolution summary database error for incident #{incident.id}:",
            e
        )

        return jsonify({
            "success": False,
            "message": "Unable to save resolution summary. Please try again."
        }), 500

    return jsonify({
        "success": True,
        "message": "Resolution summary saved successfully."
    })
# =========================================================
# EMERGENCY CONTACT
# =========================================================

class EmergencyContact(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )

    name = db.Column(
        db.String(100),
        nullable=False
    )

    phone = db.Column(
        db.String(20),
        nullable=False
    )

    relationship = db.Column(
        db.String(50),
        nullable=False
    )

    user = db.relationship(
        "User",
        backref="emergency_contacts"
    )
class IncidentStatusHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    incident_id = db.Column(
        db.Integer,
        db.ForeignKey("emergency_incident.id"),
        nullable=False
    )

    old_status = db.Column(
        db.String(50),
        nullable=True
    )

    new_status = db.Column(
        db.String(50),
        nullable=False
    )

    changed_by = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=True
    )

    changed_at = db.Column(
        db.DateTime,
        default=ist_now
    )

    incident = db.relationship(
        "EmergencyIncident",
        backref="status_history"
    )

    authority = db.relationship(
        "User",
        foreign_keys=[changed_by]
    )
class UserNotification(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )

    incident_id = db.Column(
        db.Integer,
        db.ForeignKey("emergency_incident.id"),
        nullable=True
    )

    notification_type = db.Column(
        db.String(50),
        nullable=False
    )

    title = db.Column(
        db.String(150),
        nullable=False
    )

    message = db.Column(
        db.String(500),
        nullable=False
    )

    is_read = db.Column(
        db.Boolean,
        default=False
    )

    created_at = db.Column(
        db.DateTime,
        default=ist_now
    )

    user = db.relationship(
        "User",
        backref="user_notifications"
    )

    incident = db.relationship(
        "EmergencyIncident"
    )
# =========================================================
# SECURITY AUDIT LOG
# =========================================================

class AuditLog(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    actor_id = db.Column(
        db.Integer,
        nullable=True
    )

    actor_role = db.Column(
        db.String(30),
        nullable=True
    )

    action = db.Column(
        db.String(100),
        nullable=False
    )

    incident_id = db.Column(
        db.Integer,
        nullable=True
    )

    description = db.Column(
        db.Text,
        nullable=True
    )

    created_at = db.Column(
        db.DateTime,
        default=ist_now
    )
# =========================================================
# DATABASE INITIALIZATION
# =========================================================

with app.app_context():
    db.create_all()
# =========================================================
# RUN
# =========================================================
# =========================================================
# INCIDENT DETAILS
# =========================================================

@app.route("/admin/incident/<int:incident_id>")
def incident_details(incident_id):

    # -----------------------------------------------------
    # 1. Authority authentication
    # -----------------------------------------------------

    if "authority_id" not in session:
        return redirect(url_for("authority_login"))
    # -----------------------------------------------------
    # 2. Find incident
    # -----------------------------------------------------

    incident = EmergencyIncident.query.get_or_404(
        incident_id
    )

    # -----------------------------------------------------
    # 3. Calculate current escalation
    # -----------------------------------------------------

    escalation = calculate_escalation(
        incident.priority,
        incident.status,
        incident.created_at
    )

    # -----------------------------------------------------
    # 4. Save escalation information
    # -----------------------------------------------------

    incident.escalation_level = escalation["level"]

    incident.escalation_status = escalation["status"]

    incident.escalation_reason = escalation["reason"]

    if escalation["status"] == "ESCALATED":

        if incident.escalated_at is None:
            incident.escalated_at = ist_now()

    else:

        incident.escalated_at = None

    # -----------------------------------------------------
    # 5. Save changes
    # -----------------------------------------------------

    try:

        db.session.commit()

    except SQLAlchemyError as e:

        db.session.rollback()

        print(
            f"❌ Incident details escalation update error for #{incident.id}:",
            e
        )

        return (
            "Unable to load incident details.",
            500
        )
    # -----------------------------------------------------
    # 6. Display incident details
    # -----------------------------------------------------

    return render_template(
        "incident_details.html",
        incident=incident
    )
if __name__ == "__main__":

    from background_monitor import start_monitor

    start_monitor()

    socketio.run(
        app,
        debug=not IS_PRODUCTION,
        use_reloader=False
    )