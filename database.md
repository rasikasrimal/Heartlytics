# Database Schema

This document lists the tables in the application's database and includes `DESC` commands to inspect each table. Key columns are annotated to highlight primary keys (PK) and foreign keys (FK) linking related tables.

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

## patient

```sql
DESC patient;
```

| Column | Type | Key | References |
| --- | --- | --- | --- |
| id | INTEGER | PK | - |
| entered_by_user_id | INTEGER | FK | user.id |
| patient_data | JSON |  |  |
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
| patient_name | VARCHAR(120) |  |  |
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
| role | VARCHAR(20) |  |  |
| status | VARCHAR(20) |  |  |
| requested_role | VARCHAR(20) |  |  |
| created_at | DATETIME |  |  |
| updated_at | DATETIME |  |  |
| last_login | DATETIME |  |  |
| avatar | VARCHAR(255) |  |  |

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
