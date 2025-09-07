# Forgot Password / 2-Step Verification Flow

## 1. Overview
The forgot-password and verification flow allows users to reset credentials securely when access is lost. It delivers a time-bound one-time password (OTP) over email and requires a second factor (TOTP or backup codes) to mitigate account takeover.

### Functional Requirements
- Deliver OTP via email with configurable templates.
- OTP and verification TTL of 5 minutes; resend cooldown of 30 seconds.
- Enforce rate limits per user and IP; maximum 5 attempts per hour.
- Support email delivery and TOTP challenge when enabled.

### Non-Functional Requirements
- Security: hash+pepper OTP, constant-time comparison, HSTS, secure cookies.
- Privacy: PII minimisation, audit logs redacting secrets.
- Reliability: retryable email queue, transactional database updates.
- Accessibility: screen-reader labels, focus management on dialogs.

## 2. BPMN 2.0 Process

```mermaid
flowchart LR
  subgraph userLane [User]
    u_start((Start))
    u_request[Submit Email]
    u_receive[Enter OTP]
    u_end((Finish))
  end
  subgraph systemLane [System]
    check_user{Account Exists?}
    send_mail[[Send Email]]
    delivery_err{Delivery Error?}
    wait_code((Cooldown))
    verify_code{OTP Valid?}
    update_pwd[Update Credential]
    lock_account[Lockout]
  end

  u_start --> u_request -.-> check_user
  check_user -->|yes| send_mail
  check_user -->|no| u_end
  send_mail --> delivery_err
  delivery_err -->|yes| u_end
  delivery_err -->|no| wait_code
  wait_code --> u_receive -.-> verify_code
  verify_code -->|valid| update_pwd --> u_end
  verify_code -->|invalid| lock_account --> u_end
  wait_code -.->|timer| send_mail
```

The process begins when the user submits a reset request. The system verifies the account and invokes a call activity to send the email. A boundary error event handles delivery failures, short-circuiting to a user-facing error. Upon success, the user waits through a cooldown timer before receiving the OTP. Verification passes through an exclusive gateway that updates the credential or triggers a lockout. A compensation note indicates that a lockout is rolled back if later verification succeeds.

## 3. Data Flow Diagrams
### Level‑0 Context
```mermaid
flowchart LR
  actor((User))
  sys([Auth System])
  mail((Email Service))
  db[(UserDB<br/>PII)]
  store[(OTPStore<br/>Secrets)]

  actor -->|Reset Request / PII| sys
  sys -->|Lookup| db
  sys -->|Store OTP| store
  sys -->|Send OTP| mail
  mail -->|Email with OTP| actor

```
The context diagram shows the user interacting with the Auth System. Data stores are internal, while the Email Service is external and untrusted. PII and secrets never leave the system boundary except for the minimal OTP sent via email.

### Level‑1 Process
```mermaid
flowchart TB
  req[Request Reset]
  gen[Generate OTP]
  send[Send Email]
  verify[Verify OTP]
  cool[Enforce Cooldown]
  update[Update Credential]
  db1[(UserDB)]
  store1[(OTPStore)]
  mail1[(EmailSvc)]

  req --> gen --> store1
  gen --> cool
  cool --> send --> mail1
  send --> verify
  verify -->|valid| update --> db1
  verify -->|invalid| req
```
Level‑1 expands the system into discrete processes. Data flows are labelled, and trust boundaries exist around the Email Service. Cooldown enforcement happens before sending to avoid spamming.

### Level‑2 Internal Details
```mermaid


flowchart LR
  subgraph "OTP Generation"
    hashPepper["Hash + Pepper"]
    ttlCheck["TTL Check"]
    rateLimit["Rate-Limit user+IP"]
  end

  subgraph Verification
    audit["Audit Log"]
    compare["Constant-Time Compare"]
    lock[Lockout]
  end

  hashPepper --> ttlCheck --> rateLimit
  rateLimit --> audit
  compare -- match --> audit
  compare -- mismatch --> lock


```
Level‑2 details cryptographic handling, TTL enforcement, rate limiting, and audit logging. Each subprocess runs within the system's trust boundary; only audit logs are exported to immutable storage.

## 4. C4 Model (Architecture)
### C1 Context
```mermaid
flowchart LR
  user((User))
  auth[(Auth Service)]
  emailSvc((SMTP Provider))
  kms((KMS))
  user --> auth
  auth --> emailSvc
  auth --> kms
```
The context view positions the Auth Service between the user, the SMTP provider, and key management.

### C2 Container
```mermaid
flowchart LR
  web[Web App]
  worker[Worker/Queue]
  db[(Postgres DB)]
  cache[(Redis Cache)]
  smtp[(SMTP Relay)]
  kms2[(Key Management)]

  web --> db
  web --> cache
  web --> worker
  worker --> smtp
  worker --> kms2
  worker --> db
```
The container view shows the web application accepting requests, delegating email work to a background worker that interacts with SMTP and KMS, while using Postgres and Redis.

### C3 Component
```mermaid
flowchart LR
  authCtrl[Auth Controller]
  otpSvc[OTP Service]
  emailAdp[Email Adapter]
  rate[Rate Limiter]
  auditLog[Audit Logger]
  crypto[Crypto/Keyring]
  tpl[Template Engine]

  authCtrl --> otpSvc
  authCtrl --> rate
  authCtrl --> tpl
  otpSvc --> crypto
  otpSvc --> emailAdp
  emailAdp --> auditLog
  rate --> auditLog
```
Components show how the Auth Controller orchestrates services. The OTP Service relies on crypto and email adapters; rate limiting and auditing provide cross-cutting concerns.

## 5. Sequence Diagram (End-to-End)
```mermaid
sequenceDiagram
  participant U as User
  participant W as WebApp
  participant Q as Worker
  participant E as EmailSvc
  U->>W: Request reset
  W->>Q: Queue send
  Q->>E: SMTP send
  E-->>U: Email with OTP
  U->>W: Submit OTP
  W->>Q: Verify OTP
  Q-->>W: OK
  W-->>U: Success
  alt Code expired
    Q-->>W: Expired
    W-->>U: Error & Cooldown
    Note over W,U: Resend allowed after cooldown
  end
  Note over U,W: TTL=5m, Cooldown=30s
```

## 6. State Machine (OTP Lifecycle)
```mermaid
stateDiagram-v2
  [*] --> Created
  Created --> Sent
  Sent --> Verified: correct code
  Sent --> Expired: TTL elapsed
  Sent --> Locked: max attempts
  Locked --> Expired: cooldown elapse
```

## 7. Timing Diagram (Resend Cooldown)
```mermaid
timeline
  title Resend Window
  t0 : Code issued
  t0+30s : Earliest resend
  t0+300s : OTP expires
```

## 8. Threat Model (Security)
### STRIDE
| Threat | Vector | Mitigation |
| --- | --- | --- |
| Spoofing | forged emails | DKIM, SPF, 2FA |
| Tampering | OTP replay | hash+pepper, TLS |
| Repudiation | denial of request | immutable audit logs |
| Info Disclosure | brute-force OTP | rate limits, lockout |
| DoS | mass requests | IP+user throttling |
| EoP | code guessing | strong entropy, cooldown |

### Attack/Abuse Tree
```mermaid
mindmap
  root((Account Takeover))
    - Spoof Reset
      - Mitigation: DKIM
    - Brute-force OTP
      - Mitigation: Rate Limits
    - Session Hijack
      - Mitigation: Secure Cookies
```

## 9. Data & Schema
```mermaid

erDiagram
  USER ||--o{ OTP_CODE : has
  USER ||--o{ AUDIT_EVENT : generates
  USER ||--o{ EMAIL_QUEUE : requests

  OTP_CODE {
    string hashed_code PK
    uuid user_id FK
    datetime expires_at
  }

  AUDIT_EVENT {
    uuid id PK
    uuid user_id
    datetime created_at
  }

  EMAIL_QUEUE {
    uuid id PK
    uuid user_id
    datetime queued_at
  }

  %% Notes:
  %% - Add DB indexes in schema: OTP_CODE.expires_at, OTP_CODE.user_id, AUDIT_EVENT.user_id, EMAIL_QUEUE.user_id
  %% - Implement TTL/retention at the DB/job level for EMAIL_QUEUE. Not supported as an ER attribute flag.

```
Data retention: OTP codes auto-delete after TTL via scheduled job. Audit events retained 1 year. PII stored encrypted at rest and decrypted only in memory.

## 10. Observability & Metrics
- Audit events: reset_requested, otp_sent, otp_verified, otp_failed, account_locked.
- Metrics: send_success, send_latency, verify_success_rate, lockout_count.

## 11. Test Plan
- Unit: OTP generation/verification, TTL expiry, cooldown enforcement, lockout threshold.
- Integration: simulate email failures, rate-limit counters per IP, audit logging.
- UI: ensure "Resend Code" is disabled until countdown completes.

## 12. Appendix: Rendering Notes
GitHub Markdown lacks native BPMN support. The canonical BPMN diagram is provided as an embedded SVG (`assets/forget_password_bpmn.svg`) with a Mermaid flowchart fallback above for inline rendering.
