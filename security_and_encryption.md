# Security and Encryption

This document summarizes the security controls implemented in the HeartLytics web application and provides best-practice guidance for handling user data.

## Authentication
- Session-based authentication powered by **Flask-Login**.
- Login attempts are rate limited to five per 15 minutes to mitigate brute-force attacks.
- Sessions are marked as permanent and respect server-side timeouts.

## Authorization
- Strict role-based access control with roles **User**, **Doctor**, **Admin**, and **SuperAdmin**.
- Policy matrix:
  - **SuperAdmin** – full access
  - **Admin** – no access to Predict, Batch, Dashboard, Research modules
  - **Doctor** – access to all modules
  - **User** – Predict only
- Server-side decorators enforce checks before any sensitive processing.
- `RBAC_STRICT` environment flag (default `1`) ensures checks are always active.
- Top navigation reads the policy to hide unauthorized links before a request is made.

## Password Storage
- Passwords are hashed using `argon2-cffi` with the Argon2id algorithm.
- Legacy PBKDF2 hashes are accepted and upgraded to Argon2id on successful login.
- Password reset codes are 6-digit OTPs hashed with SHA-256 and expire after 10 minutes.

## CSRF Protection
- Forms and API routes include CSRF tokens verified on every non-GET request.
- Tokens are stored in the session and compared against form fields or headers.

## Security Headers
- Responses include headers like `X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`, and `Permissions-Policy` to reduce attack surface.

## Cookies
- A `theme` preference cookie is stored for UI purposes only. It contains no
  sensitive data and is sent with every request so the server can render the
  correct color scheme.

## Encryption
- HTTPS/TLS should be enforced in production to encrypt data in transit.
- Sensitive configuration such as `SECRET_KEY` and database credentials are loaded from environment variables.
- Database files and backups should reside on encrypted storage.
- Selected fields (patient data and patient names) are encrypted at the application layer
  using AES-256-GCM with per-record data keys wrapped by a keyring.

## Data Protection & Compliance
- Collect only necessary personal data and retain it for the minimum time required.
- Follow **OWASP Top 10** guidelines for web application security.
- For deployments targeting EU residents, ensure compliance with **GDPR** regarding consent, data subject rights, and breach notification.

## Best Practices
- Use parameterized queries and ORM safeguards to prevent SQL injection.
- Keep dependencies updated and apply security patches promptly.
- Review access logs and audit trails for suspicious activity.
- Regularly back up data and test recovery procedures.

