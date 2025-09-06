# Security and Encryption

This document summarizes the security controls implemented in the HeartLytics web application and provides best-practice guidance for handling user data.

## Authentication
- Session-based authentication powered by **Flask-Login**.
- Login attempts are rate limited to five per 15 minutes to mitigate brute-force attacks.
- Sessions are marked as permanent and respect server-side timeouts.

## Authorization
- Role-based access control with roles such as **User**, **Doctor**, **Admin**, and **SuperAdmin**.
- Route-level restrictions ensure users only access permitted views.

## Password Storage
- Passwords are hashed using Werkzeug's `generate_password_hash` (PBKDF2 + SHA256).
- `check_password_hash` is used for verification without exposing plaintext passwords.

## CSRF Protection
- Forms and API routes include CSRF tokens verified on every non-GET request.
- Tokens are stored in the session and compared against form fields or headers.

## Security Headers
- Responses include headers like `X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`, and `Permissions-Policy` to reduce attack surface.

## Encryption
- HTTPS/TLS should be enforced in production to encrypt data in transit.
- Sensitive configuration such as `SECRET_KEY` and database credentials are loaded from environment variables.
- Database files and backups should reside on encrypted storage.

## Data Protection & Compliance
- Collect only necessary personal data and retain it for the minimum time required.
- Follow **OWASP Top 10** guidelines for web application security.
- For deployments targeting EU residents, ensure compliance with **GDPR** regarding consent, data subject rights, and breach notification.

## Best Practices
- Use parameterized queries and ORM safeguards to prevent SQL injection.
- Keep dependencies updated and apply security patches promptly.
- Review access logs and audit trails for suspicious activity.
- Regularly back up data and test recovery procedures.

