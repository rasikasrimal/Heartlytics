# Database Schema

This document lists the tables in the application's database and includes `DESC` commands to inspect each table. Key columns are annotated to highlight primary keys (PK) and foreign keys (FK) linking related tables.

User interface theme preferences are stored in client-side cookies and
`localStorage`; no database tables persist this information.

Recent theming updates (transparent charts and table header styling) do
not introduce any new columns.
Cleaning-log normalization and the auth-page theme toggle are handled
in application logic and likewise require no schema changes.
The new simulations auto-update loader and timestamped status also run
entirely on the client and do not impact the database schema.

The password reset feature introduces a `password_reset_request` table storing short-lived verification codes.
Email-based MFA uses an `mfa_email_challenge` table recording hashed codes, attempts, and resend timestamps.
The redesigned forgot-password interface and segmented OTP inputs are client-side only and do not alter the database schema.
Similarly, the signup flow's email verification card is purely UI and introduces no new tables.
The `user` table enforces uniqueness on both `username` and `email` fields, while `nickname` remains non-unique.

## audit_log

```sql
DESC audit_log;
```

| Column | Type | Key | References |
| --- | --- | --- | --- |
| id | INTEGER | PK | - |
| timestamp | DATETIME |  |  |
| acting_user_id | INTEGER | FK | user.id |
| target_user_id | INTEGER | FK | user.id |
| action | VARCHAR(50) |  |  |
| old_value | VARCHAR(120) |  |  |
| new_value | VARCHAR(120) |  |  |

## cluster_summary

```sql
DESC cluster_summary;
```

| Column | Type | Key | References |
| --- | --- | --- | --- |
| cluster_id | INTEGER | PK | - |
| count | INTEGER |  |  |
| avg_age | FLOAT |  |  |
| avg_cholesterol | FLOAT |  |  |
| avg_resting_blood_pressure | FLOAT |  |  |
| avg_st_depression | FLOAT |  |  |
| avg_risk_pct | FLOAT |  |  |
| pct_male | FLOAT |  |  |
| pct_female | FLOAT |  |  |
| common_chest_pain_type | VARCHAR(50) |  |  |
| common_thalassemia_type | VARCHAR(50) |  |  |

## password_reset_request

```sql
DESC password_reset_request;
```

| Column | Type | Key | References |
| --- | --- | --- | --- |
| id | INTEGER | PK | - |
| request_id | VARCHAR(36) | UNIQUE | - |
| user_id | INTEGER | FK | user.id |
| hashed_code | VARCHAR(64) |  |  |
| expires_at | DATETIME |  |  |
| attempts | INTEGER |  |  |
| resend_count | INTEGER |  |  |
| last_sent_at | DATETIME |  |  |
| status | VARCHAR(20) |  |  |
| requester_ip | VARCHAR(45) |  |  |
| user_agent | VARCHAR(200) |  |  |

Requests expire after 10 minutes and are stored as SHA-256 hashes with a server-side pepper. Submitted codes are verified using constant-time comparisons to prevent timing attacks.

## patient

```sql
DESC patient;
```

| Column | Type | Key | References |
| --- | --- | --- | --- |
| id | INTEGER | PK | - |
| entered_by_user_id | INTEGER | FK | user.id |
| patient_data | JSON (legacy) |  |  |
| patient_data_ct | BLOB |  |  |
| patient_data_nonce | BLOB |  |  |
| patient_data_tag | BLOB |  |  |
| patient_data_wrapped_dk | BLOB |  |  |
| patient_data_kid | VARCHAR(64) |  |  |
| patient_data_kver | INTEGER |  |  |
| prediction_result | VARCHAR(50) |  |  |
| created_at | DATETIME |  |  |

## prediction

```sql
DESC prediction;
```

| Column | Type | Key | References |
| --- | --- | --- | --- |
| id | INTEGER | PK | - |
| created_at | DATETIME |  |  |
| patient_name | VARCHAR(120) (legacy) |  |  |
| patient_name_ct | BLOB |  |  |
| patient_name_nonce | BLOB |  |  |
| patient_name_tag | BLOB |  |  |
| patient_name_wrapped_dk | BLOB |  |  |
| patient_name_kid | VARCHAR(64) |  |  |
| patient_name_kver | INTEGER |  |  |
| age | INTEGER |  |  |
| sex | INTEGER |  |  |
| chest_pain_type | VARCHAR(50) |  |  |
| resting_bp | FLOAT |  |  |
| cholesterol | FLOAT |  |  |
| fasting_blood_sugar | INTEGER |  |  |
| resting_ecg | VARCHAR(50) |  |  |
| max_heart_rate | FLOAT |  |  |
| exercise_angina | INTEGER |  |  |
| oldpeak | FLOAT |  |  |
| st_slope | VARCHAR(50) |  |  |
| num_major_vessels | INTEGER |  |  |
| thalassemia_type | VARCHAR(50) |  |  |
| prediction | INTEGER |  |  |
| confidence | FLOAT |  |  |
| model_version | VARCHAR(120) |  |  |
| cluster_id | INTEGER | FK | cluster_summary.cluster_id |

Note: `num_major_vessels` accepts `NULL` when missing in uploaded data.

## role

```sql
DESC role;
```

| Column | Type | Key | References |
| --- | --- | --- | --- |
| id | INTEGER | PK | - |
| role_name | VARCHAR(50) |  |  |
| permissions | JSON |  |  |

## user

```sql
DESC user;
```

| Column | Type | Key | References |
| --- | --- | --- | --- |
| id | INTEGER | PK | - |
| uid | VARCHAR(36) |  |  |
| username | VARCHAR(80) |  |  |
| nickname | VARCHAR(80) |  |  |
| email | VARCHAR(120) |  |  |
| password_hash | VARCHAR(128) |  |  |
| role | VARCHAR(20) |  | SuperAdmin/Admin/Doctor/User |
| status | VARCHAR(20) |  |  |
| requested_role | VARCHAR(20) |  |  |
| created_at | DATETIME |  |  |
| updated_at | DATETIME |  |  |
| last_login | DATETIME |  |  |
| avatar | VARCHAR(255) |  |  |
| mfa_enabled | BOOLEAN |  |  |
| mfa_email_enabled | BOOLEAN |  |  |
| mfa_email_verified_at | DATETIME |  |  |
| mfa_secret_ct | BLOB |  |  |
| mfa_secret_nonce | BLOB |  |  |
| mfa_secret_tag | BLOB |  |  |
| mfa_secret_wrapped_dk | BLOB |  |  |
| mfa_secret_kid | VARCHAR(64) |  |  |
| mfa_secret_kver | INTEGER |  |  |
| mfa_recovery_hashes | JSON |  |  |
| mfa_last_enforced_at | DATETIME |  |  |

Note: Users can log in using either the `username` or `email` field. The `last_login` column stores the timestamp of the most recent successful login. Login credentials are never persisted; the form clears identifier and password fields after each request.
The `role` column drives RBAC enforcement with allowed values `SuperAdmin`, `Admin`, `Doctor`, and `User`.
TOTP multi-factor authentication uses the `mfa_*` columns to hold an encrypted secret, recovery code hashes, and enforcement timestamps. Email MFA stores its enablement and verification time in `mfa_email_*` fields.

## mfa_email_challenge

| Column | Type | Notes |
| --- | --- | --- |
| id | INTEGER | Primary key |
| user_id | INTEGER | FK to user.id |
| code_hash | VARCHAR(64) | Hashed one-time code |
| expires_at | DATETIME | Expiration time |
| attempts | INTEGER | Attempt counter |
| resend_count | INTEGER | Number of sends |
| last_sent_at | DATETIME | Last send timestamp |
| status | VARCHAR(20) | pending/verified/expired |
| requester_ip | VARCHAR(45) |  |
| user_agent | VARCHAR(200) |  |

## user_roles

```sql
DESC user_roles;
```

| Column | Type | Key | References |
| --- | --- | --- | --- |
| user_id | INTEGER | PK, FK | user.id |
| role_id | INTEGER | PK, FK | role.id |

## Relationships

- `audit_log.acting_user_id` → `user.id`
- `audit_log.target_user_id` → `user.id`
- `patient.entered_by_user_id` → `user.id`
- `prediction.cluster_id` → `cluster_summary.cluster_id`
- `user_roles.user_id` → `user.id`
- `user_roles.role_id` → `role.id`

### Notes
- UI navigation and motion system refinements do not require schema changes.
