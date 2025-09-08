# Security and Encryption

This canonical document consolidates all security guidance for HeartLytics. It
merges the previous `encryption.md` and `security_and_encryption.md` files and
links to the dedicated [Forgot Password / 2‑Step Verification flow](forget_password.md).

> **Assurance notes:** All sensitive operations are logged, protected by rate
> limits, and validated using constant‑time comparisons. Application data is
> encrypted with AEAD and keys are rotated on a regular schedule.

## Authentication

- Session-based authentication with **Flask‑Login**.
- Email and TOTP factors provide optional multi-factor authentication.
- Verification emails display masked addresses and respect resend cooldowns enforced on the server.
- Password resets force a fresh login and send a notification email.
- Login, OTP request, and verification endpoints enforce per‑IP and per‑ID
  limits to deter brute force attempts.
- Redesigned forgot-password page uses segmented OTP inputs and a visible countdown badge without exposing full email addresses.
- Sign-up form features a client-side password strength meter and requires email verification using the same OTP component.
- Email verification codes are stored hashed with expirations in the `email_verification` table; migration backfills `email_verified_at` for existing users and SuperAdmin-created accounts are stamped verified immediately.

## Authorization

Role-based access control (RBAC) restricts modules to specific roles: User,
Doctor, Admin and SuperAdmin. Server-side decorators check roles before any
action is executed, and the top navigation hides links the user cannot access.

```mermaid
flowchart TB
  subgraph Roles
    U(User)
    D(Doctor)
    A(Admin)
    S(SuperAdmin)
  end
  subgraph Modules
    Predict
    Dashboard
    AdminPanel(Admin)
  end
  U --> Predict
  D --> Predict & Dashboard
  A --> AdminPanel
  S --> Predict & Dashboard & AdminPanel
```

## Password Storage

- Passwords use Argon2id via `argon2-cffi`.
- Legacy PBKDF2 hashes are upgraded on successful login.
- OTPs are six digits, hashed with a server-side pepper and compared in
  constant time.

## Envelope Encryption

HeartLytics employs application-layer envelope encryption for patient data and
MFA secrets.

```mermaid
flowchart LR
  user([User]) -->|submit data| api[[Web/API]]
  api -->|request data key| kms[KMS]
  kms -->|data key| api
  api --> crypto((Crypto Service))
  crypto -->|AES-GCM| db[(Database)]
  db --> api --> user
```

- A random 256‑bit data-encryption key (DEK) is generated per operation.
- Data is encrypted with AES‑256‑GCM; nonces are 12 random bytes.
- The DEK is wrapped by the configured keyring and stored alongside the
  ciphertext, nonce, tag, key id (`kid`) and version (`kver`).
- Associated data binds table and column: `table:column|kid|kver`.
- TOTP secrets use the same envelope structure and never appear in plaintext.

### Key rotation & erasure

1. Provision a new master key and update `KMS_KEY_ID`.
2. Rewrap existing DEKs with the new key, incrementing `kver`.
3. Disabling or deleting the master key renders stored ciphertext
   undecryptable, providing cryptographic erasure.

## Data Flow Diagram

```mermaid
flowchart LR
  %% Trust boundaries
  subgraph Client_Boundary[Trust Boundary: Client]
    user([User/Doctor])
  end

  subgraph App_Boundary[Trust Boundary: App Backend]
    auth((Auth/OTP Service))
    crypto((Crypto Service))
    api[[Web/API]]
  end

  subgraph Infra_Boundary[Trust Boundary: Infra/3rd Party]
    kms[[KMS]]
    smtp[[Email Service]]
    db[(Encrypted Patient Store)]
    audit[(Audit Log)]
    cache[(Cache/RateLimit)]
  end

  %% Flows
  user -- "username/email (PII)" --> api
  api --> auth
  auth -- "issue OTP (hashed+pepper, TTL)" --> cache
  auth -- "send OTP request" --> smtp
  user -- "submit code" --> api --> auth
  auth -- "verify (constant-time compare)" --> cache
  api -- "result + session" --> user

  api --> crypto
  crypto -- "DEK gen + AES-GCM encrypt" --> db
  crypto -- "wrap DEK with KMS (KID)" --> kms
  api --> audit

  %% Styling
  classDef sens fill:#ffe9e6,stroke:#cc3333,stroke-width:1px;
  class audit sens;

```

The DFD highlights trust boundaries and data classifications. Only ciphertext
and wrapped keys leave the application trust zone; KMS and SMTP reside in a
separate infrastructure boundary. Failure to unwrap a key or authenticate data
results in a logged error and safe abort.

## C4 Model

### C4‑1 Context

```mermaid
flowchart TB
  user[(User)]
  subgraph HeartLytics
    api[[Web App]]
  end
  kms[[KMS]]
  smtp[[SMTP]]
  user --> api
  api --> kms
  api --> smtp
```

Users interact with the web app, which in turn communicates with external KMS
and email services.

### C4‑2 Containers

```mermaid
flowchart TB
  user[(User)]

  subgraph WebApp[Web App]
    api[[Flask API]]
    worker[[Worker/Queue]]
    crypto[[Crypto Service]]
    auth[[Auth/OTP Module]]
  end

  db[(PostgreSQL: Encrypted Data)]
  cache[(Redis: OTP/Cooldowns)]
  kms[[KMS]]
  smtp[[Email/SMS Provider]]

  user --> api
  api --> auth --> cache
  api --> worker --> smtp
  api --> crypto --> kms
  api --> db
```

### C4‑3 Components

```mermaid
flowchart LR
  authCtrl[Auth Controller] --> otpSvc[OTP Service]
  authCtrl --> rate[Rate Limiter]
  authCtrl --> tpl[Templating]
  otpSvc --> cryptoSvc[Crypto Service]
  otpSvc --> emailAdp[Email Adapter]
  emailAdp --> auditLog[Audit Logger]
  rate --> auditLog
```

## Sequence: Envelope Encryption

```mermaid
sequenceDiagram
  participant A as API
  participant C as Crypto
  participant K as KMS
  participant D as DB

  A->>C: request encrypt(table:column)
  C->>C: generate 256-bit DEK
  C->>C: AES-GCM encrypt
  C->>K: wrap DEK
  K-->>C: wrapped key + kid
  C->>D: store ct, nonce, tag, wrapped key, kid, kver
  D-->>A: ok
```

If wrapping fails or KMS is unavailable, the operation aborts and the request
is logged.

## Deployment

```mermaid
flowchart TB
  subgraph VPC
    lb[ALB]
    subgraph Private
      app[Flask App]
      worker[Worker]
      db[(PostgreSQL)]
      cache[(Redis)]
    end
  end
  kms[[KMS]]
  smtp[[SMTP]]
  user((User))

  user -->|TLS| lb --> app
  app --> worker
  app --> db
  app --> cache
  app -->|wrap/unwrap| kms
  worker --> smtp
```

TLS terminates at the load balancer. Security groups restrict inbound traffic to
HTTPS and database ports. Secrets and configuration are injected via environment
variables.

## ERD

```mermaid
erDiagram
  USERS ||--o{ RESET_TOKEN : has
  USERS ||--o{ AUDIT_LOG   : records

  USERS {
    UUID id PK
    STRING email
    STRING password_hash
  }
  RESET_TOKEN {
    UUID id PK
    UUID user_id FK
    STRING code_hash
    DATETIME expires_at
    INT attempts
  }
  AUDIT_LOG {
    UUID id PK
    UUID acting_user_id
    UUID target_user_id
    STRING action
    DATETIME timestamp
  }
  KEY_VERSION {
    STRING kid PK
    INT kver
  }

```

## Threat Model Quickview

| Threat | Vector | Mitigation |
| --- | --- | --- |
| Spoofing | forged reset emails | DKIM, SPF, MFA |
| Tampering | ciphertext or key wrapping | AEAD, key integrity checks |
| Repudiation | denial of action | immutable audit logs |
| Information Disclosure | stolen DB | envelope encryption, KMS |
| Denial of Service | mass OTP requests | per‑IP/per‑ID rate limits |
| Elevation of Privilege | role abuse | strict RBAC |

```mermaid
mindmap
  root((Compromise))
    BruteForce
      Lockout
    Phishing
      MFA
    KeyTheft
      KMS
```

---

For password reset specifics see [Forgot Password / 2‑Step Verification](forget_password.md).

