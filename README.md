

🛡️ SafeShield — Women Safety \& Emergency Assistance System

SafeShield is a software-based emergency assistance and incident-management platform designed to help users report safety incidents and allow an authorized response team to monitor, prioritize, track, and close those incidents through a structured workflow.



The project focuses on the complete emergency lifecycle:



SOS Report → Priority Prediction → Authority Monitoring → Escalation → Response Tracking → Resolution → User Notification



Important: This is a local/development prototype. It does not directly dispatch police, emergency services, or other real-world responders. Real emergency-service integration would require verified APIs, institutional authorization, privacy controls, and deployment-specific security measures.



✨ Key Highlights

🚨 One-tap SOS incident reporting



📍 Latitude/longitude capture for incident location



🤖 AI-based emergency priority prediction



⚠️ Automatic escalation based on incident priority and response state



👮 Secure authority login and role-based access



📊 Authority monitoring dashboard



🔎 Incident search and status filtering



📄 Server-side pagination



🔄 Real-time status updates using Socket.IO



🧾 Incident status history and audit trail



📝 Authority response notes



✅ Resolution summary and incident closure workflow



📢 User emergency tracking page



🔔 Persistent user notifications



🔢 Unread notification count



👥 Emergency contact support



🛡️ Session, CSRF, validation, privacy, and error-handling measures



🕒 Background escalation monitoring



🎯 Problem Statement

During a safety emergency, simply collecting an SOS message is not enough.



A useful emergency-management system should also be able to:



Receive and securely store the emergency report.



Record the incident location and relevant information.



Help prioritize incidents.



Escalate high-priority incidents.



Give authorized responders a clear monitoring interface.



Track response progress.



Keep an auditable history of status changes.



Inform the user about the progress of her incident.



Close the incident with a clear resolution record.



SafeShield was developed around this complete workflow.



💡 Solution Overview

SafeShield connects the user-facing emergency experience with an authority-facing incident-management dashboard.



User flow

User Login

&#x20;   ↓

SOS Emergency Report

&#x20;   ↓

Location + Emergency Details

&#x20;   ↓

AI Priority Prediction

&#x20;   ↓

Incident Created

&#x20;   ↓

User Can Track Emergency

&#x20;   ↓

Live Status Notifications

&#x20;   ↓

Resolution

&#x20;   ↓

Closure + Notification

Authority flow

Authority Login

&#x20;   ↓

Monitoring Dashboard

&#x20;   ↓

View Active Incidents

&#x20;   ↓

Review Priority / Escalation

&#x20;   ↓

Acknowledge

&#x20;   ↓

Responding

&#x20;   ↓

Add Response Notes

&#x20;   ↓

Resolve

&#x20;   ↓

Add Resolution Summary

🧩 Main Modules

1\. User Authentication

Users can create accounts and securely log in.



The application separates normal users from authorized authority users through role-based access control.



User role

Register



Login



View dashboard



Report emergency



Manage emergency contacts



Track current emergency



View notifications



Authority role

Secure authority login



Monitor emergency incidents



Search/filter incidents



Review priority and escalation



Update incident status



Add response notes



Resolve incidents



View audit information



🚨 2. SOS Emergency Reporting

A logged-in user can submit an emergency report containing information such as:



Latitude



Longitude



Incident category



Location description/type



Severity



Urgency



Emergency message



The application validates the submitted values before processing the incident.



SafeShield also includes protection against repeated SOS submissions within a short period to reduce accidental duplicate incidents.



📍 3. Emergency Location

Each incident can store geographic coordinates.



The authority can review the reported coordinates, while the user can view her reported location through a map link.



Example:



Latitude: 12.xxxxx

Longitude: 76.xxxxx

The prototype stores and displays the location supplied by the client. Production deployment should use additional location-security controls, consent, retention policies, and access monitoring.



🤖 4. AI Priority Prediction

SafeShield uses a machine-learning priority predictor to classify an incident based on emergency information.



The priority levels used in the system are:



CRITICAL

HIGH

MEDIUM

LOW

Priority information is displayed to authorized authorities and is used by the escalation engine.



The AI component is intended as a decision-support mechanism, not as a replacement for human judgment.



⚠️ 5. Automatic Escalation

SafeShield includes an escalation engine that evaluates factors such as:



Incident priority



Current incident status



Time since the incident was created



The system assigns an escalation level and status when escalation conditions are reached.



Example lifecycle:



Level 1 → Normal monitoring

Level 2 → Higher attention

Level 3 → Escalated / immediate attention

The application also contains a background escalation monitor that checks incidents periodically.



👮 6. Authority Monitoring Dashboard

Authorized authorities can monitor emergency incidents from a dedicated dashboard.



The dashboard provides information such as:



Active emergency count



Total incidents



Incident status



Priority



Escalation status



Location



Incident details



Response progress



The interface is intended to provide a centralized view of ongoing incidents.



🔎 7. Search, Filtering \& Pagination

The authority dashboard supports search across stored incidents, status filtering for ACTIVE, ACKNOWLEDGED, RESPONDING, and RESOLVED, and server-side pagination for larger incident lists.



🔄 8. Emergency Status Workflow

Every incident follows a controlled workflow:



ACTIVE

&#x20;  ↓

ACKNOWLEDGED

&#x20;  ↓

RESPONDING

&#x20;  ↓

RESOLVED

Invalid status transitions are rejected by the server.



This provides a predictable incident lifecycle and helps maintain reliable audit records.



📝 9. Response Notes \& Resolution Summary

Authorities can record operational information through response notes during an active response and a resolution summary when closing the incident.



This gives the final incident record a clear history instead of simply changing the status to RESOLVED.



📋 10. Incident Timeline \& Audit Trail

SafeShield records incident status changes in a dedicated status-history table.



Example:



🔴 SOS Received

&#x20;       ↓

🟡 Authority Acknowledged

&#x20;       ↓

🚑 Response Being Coordinated

&#x20;       ↓

✅ Incident Resolved

The system also maintains audit information for important operations.



This helps with accountability, debugging, incident review, and system traceability.



📢 11. User Emergency Tracking

Users can open:



/my-emergency

to view their current emergency.



The page can show:



Incident ID



Current status



Live monitoring state



Incident timeline



Emergency location



Map link



Resolution summary after closure



When an incident is resolved, the user sees a final closure state such as:



✅ Emergency Closed

🔔 12. Real-Time User Notifications

SafeShield uses Flask-SocketIO for real-time updates.



User-specific Socket.IO rooms are used so that a status update is sent only to the appropriate logged-in user.



The affected user can receive live updates when the incident moves through:



ACKNOWLEDGED

RESPONDING

RESOLVED

🔔 13. Persistent Notification System

SafeShield stores user notifications in a dedicated notification table.



Each notification can contain:



User ID



Incident ID



Notification type



Title



Message



Read/unread state



Creation time



The user can open:



/notifications

to review notification history.



The dashboard can display an unread count:



🔔 Notifications (2)

Opening the notifications page marks displayed notifications as read.



👥 14. Emergency Contacts

Users can maintain emergency contact information.



The system can associate an emergency contact with an incident and record a simulated/local notification for development purposes.



The current prototype should not be represented as sending real SMS, WhatsApp, or emergency-service alerts unless an actual verified integration is implemented.



🛡️ 15. Security \& Privacy

SafeShield includes application-level security measures such as password hashing, session-based authentication, role separation, HTTP-only cookies, SameSite protection, production secure-cookie configuration, CSRF protection, input validation, controlled status transitions, and server-side Socket.IO room assignment.



Private information is intentionally excluded from live event payloads when it is not needed.



Production deployment should additionally implement HTTPS, strong production secrets, database access controls, encryption at rest where appropriate, secure logging, data retention policies, consent/privacy notices, rate limiting, monitoring, and an operational security process.



🧯 16. Error Handling \& Reliability

SafeShield uses database rollback handling for database failures, validates requests before processing, prevents invalid state transitions, and runs the escalation monitor independently of the browser interface.



🏗️ Technology Stack

Technology	Purpose

Python	Core application logic

Flask	Web application framework

Flask-SQLAlchemy	Database ORM

SQLite	Development database

Flask-SocketIO	Real-time communication

Flask-WTF CSRF	CSRF protection

SQLAlchemy	Database interaction

HTML5	Frontend structure

CSS3	Frontend styling

JavaScript	Frontend interaction

Scikit-learn	Machine-learning components

Pandas	ML/data processing

Google Maps link	Reported-location visualization

📂 Project Structure

SafeShield/

│

├── app.py

├── background\_monitor.py

├── requirements.txt

├── README.md

│

├── ml/

│   ├── priority\_predictor.py

│   └── escalation\_engine.py

│

├── templates/

│   ├── login.html

│   ├── register.html

│   ├── dashboard.html

│   ├── my\_emergency.html

│   ├── notifications.html

│   └── ...

│

├── static/

│   ├── css/

│   ├── js/

│   └── shield.png

│

└── instance/

&#x20;   └── database.db

The exact template list may change as the project evolves.



⚙️ Local Installation

1\. Clone the repository

git clone <YOUR\_GITHUB\_REPOSITORY\_URL>

cd SafeShield

2\. Create a virtual environment

Windows:



python -m venv venv

3\. Activate the virtual environment

venv\\Scripts ctivate

4\. Install dependencies

pip install -r requirements.txt

5\. Run the application

python app.py

The development server should start at:



http://127.0.0.1:5000

🔐 Development Credentials

For local testing, the project may contain development/test accounts.



Test User

Email: test@safeshield.local

Password: Test@12345

Role: USER

Development Authority

Email: authority@safeshield.local

Password: Authority@12345

Role: AUTHORITY

Do not use these credentials in production. Replace all development credentials and secrets before deployment.



🧪 Recommended Demo Flow

Use only safe local test data during demonstrations.



Step 1 — User login

Open:



/login

Step 2 — Report emergency

Create a test SOS with sample information.



Step 3 — Authority monitoring

Open the authority dashboard and show the new incident.



Step 4 — Show AI priority

Demonstrate the predicted priority and escalation information.



Step 5 — Update response state

Move the incident through:



ACTIVE

→ ACKNOWLEDGED

→ RESPONDING

→ RESOLVED

Step 6 — User tracking

Keep the user emergency page open and demonstrate the live status update.



Step 7 — Notifications

Show the notification arriving and then open:



/notifications

Step 8 — Closure

Show:



Resolved state



Resolution summary



Final timeline



Emergency Closed message



🖼️ Suggested Screenshots for GitHub

For a professional repository, include screenshots such as:



SafeShield login page



User dashboard



SOS/emergency reporting page



Authority monitoring dashboard



Incident details page



AI priority and escalation section



User emergency tracking page



Live notification



Notifications page



Resolved incident with resolution summary



A suitable repository folder is:



docs/screenshots/

📊 System Architecture

&#x20;                ┌───────────────────────┐

&#x20;                │       USER            │

&#x20;                │ Login / SOS / Track   │

&#x20;                └───────────┬───────────┘

&#x20;                            │

&#x20;                            ▼

&#x20;                ┌───────────────────────┐

&#x20;                │      FLASK APP        │

&#x20;                │ Authentication        │

&#x20;                │ Validation            │

&#x20;                │ Incident Management   │

&#x20;                └───────────┬───────────┘

&#x20;                            │

&#x20;         ┌──────────────────┼──────────────────┐

&#x20;         ▼                  ▼                  ▼

┌─────────────────┐ ┌─────────────────┐ ┌──────────────────┐

│ ML Priority     │ │ Escalation      │ │ SQLite Database  │

│ Prediction      │ │ Engine          │ │ \& Audit Records  │

└─────────────────┘ └─────────────────┘ └──────────────────┘

&#x20;                            │

&#x20;                            ▼

&#x20;                ┌───────────────────────┐

&#x20;                │ AUTHORITY DASHBOARD   │

&#x20;                │ Monitor / Respond     │

&#x20;                │ Track / Resolve      │

&#x20;                └──────────┬────────────┘

&#x20;                           │

&#x20;                           ▼

&#x20;                ┌───────────────────────┐

&#x20;                │ Flask-SocketIO        │

&#x20;                │ Real-Time Updates     │

&#x20;                └──────────┬────────────┘

&#x20;                           │

&#x20;                           ▼

&#x20;                ┌───────────────────────┐

&#x20;                │ USER NOTIFICATIONS    │

&#x20;                │ Status / Closure      │

&#x20;                └───────────────────────┘

🎓 Project Objectives

The project was developed to demonstrate practical skills in:



Web application development



Backend API development



Database design



Authentication and authorization



Machine learning integration



Real-time communication



Incident workflow design



Security and privacy



Audit logging



Error handling



User experience design



🚀 Future Scope

Potential future improvements include:



Integration with authorized emergency-response systems



Verified SMS/voice notification services



Push notifications



Mobile application



Secure cloud deployment



Multi-agency authority management



Geofencing



Real-time responder location sharing where legally and technically appropriate



Stronger ML models trained on validated operational data



Advanced analytics and reporting



Multi-language support



Offline emergency capture



Security monitoring and operational observability



Any real deployment would require appropriate legal, organizational, privacy, security, and emergency-service approvals.



⚠️ Limitations

SafeShield is currently a software prototype for development, demonstration, and educational purposes.



It does not currently guarantee:



Real-world emergency response



Police dispatch



Ambulance dispatch



Verified responder availability



Guaranteed delivery of external SMS/email/voice messages



Accurate responder physical location



Production-grade emergency-service availability



The authority dashboard in the prototype represents an application-level response center.



🧠 Design Philosophy

SafeShield is intentionally designed around the idea that an emergency application should not stop at:



"User pressed SOS"

Instead, it models the complete workflow:



Report

&#x20; ↓

Prioritize

&#x20; ↓

Monitor

&#x20; ↓

Escalate

&#x20; ↓

Respond

&#x20; ↓

Notify

&#x20; ↓

Resolve

&#x20; ↓

Audit

This makes the project a demonstration of incident-management architecture, not just a button-based safety demo.



👨‍💻 Author

Sujeeth R



Engineering Student — Electronics and Communication Engineering



Project: SafeShield — Women Safety \& Emergency Assistance System



📜 License

Choose a license appropriate for your repository before publishing.



For example, a project may use the MIT License if its author chooses to release the code under those terms.



Do not claim an open-source license unless the repository actually includes that license.



⭐ SafeShield

Report. Prioritize. Respond. Resolve

