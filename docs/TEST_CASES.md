# Test Cases

## Authentication & Roles
| Test Case ID | Test Case Description | Module | Priority | Test Type | Status |
| --- | --- | --- | --- | --- | --- |
| TC-001 | Successful login redirects user to dashboard. | Authentication & Roles | 🔴 High | 🧪 Functional | ⏳ Not Run |
| TC-002 | Rate limiting blocks more than five invalid logins in 15 min. | Authentication & Roles | 🔴 High | 🔒 Security | ⏳ Not Run |
| TC-003 | Doctor/Admin signup remains pending until approved. | Authentication & Roles | 🟡 Medium | 🧪 Functional | ⏳ Not Run |
| TC-004 | Pending doctor cannot log in before approval. | Authentication & Roles | 🔴 High | 🔒 Security | ⏳ Not Run |
| TC-005 | Regular user cannot access `/superadmin`. | Authentication & Roles | 🔴 High | 🔒 Security | ⏳ Not Run |
| TC-006 | Logout endpoint terminates session. | Authentication & Roles | 🟡 Medium | 🧪 Functional | ⏳ Not Run |
| TC-007 | Unauthenticated user is redirected to login when accessing dashboard. | Authentication & Roles | 🔴 High | 🔒 Security | ⏳ Not Run |
| TC-008 | Signup rejects duplicate email addresses. | Authentication & Roles | 🟡 Medium | 🧪 Functional | ⏳ Not Run |
| TC-009 | Password must include upper, lower, number and special character. | Authentication & Roles | 🟡 Medium | 🧪 Functional | ⏳ Not Run |
| TC-040 | Legacy password hashes upgrade to Argon2id on login. | Authentication & Roles | 🔴 High | 🔒 Security | ⏳ Not Run |
| TC-070 | Forgot password flow resets account password via emailed code. | Authentication & Roles | 🔴 High | 🧪 Functional | ⏳ Not Run |
| TC-071 | Resend is blocked during 30s cooldown. | Authentication & Roles | 🟡 Medium | 🔒 Security | ⏳ Not Run |
| TC-072 | Verification code expires after 10 minutes. | Authentication & Roles | 🟡 Medium | 🔒 Security | ⏳ Not Run |
| TC-081 | Resend button disabled during 60s countdown. | Authentication & Roles | 🟡 Medium | 🧪 Functional | ⏳ Not Run |
| TC-082 | Invalid verification codes decrement remaining attempts. | Authentication & Roles | 🟡 Medium | 🔒 Security | ⏳ Not Run |
| TC-083 | MFA verify page masks email address. | Authentication & Roles | 🟡 Medium | 🧪 Functional | ⏳ Not Run |
| TC-084 | Segmented OTP inputs auto-advance and support paste. | Authentication & Roles | 🟢 Low | 🧪 Functional | ⏳ Not Run |
| TC-085 | Countdown badge shows mm:ss while resend is disabled. | Authentication & Roles | 🟢 Low | 🧪 Functional | ⏳ Not Run |
| TC-086 | Signup button stays disabled until form fields are valid. | Authentication & Roles | 🟢 Low | 🧪 Functional | ⏳ Not Run |
| TC-087 | Password strength meter reflects complexity rules. | Authentication & Roles | 🟢 Low | 🧪 Functional | ⏳ Not Run |
| TC-088 | Signup requires email verification before login. | Authentication & Roles | 🔴 High | 🔒 Security | ⏳ Not Run |
| TC-073 | `/debug/mail` sends test email and lists recent events. | Authentication & Roles | 🟢 Low | 🧪 Functional | ⏳ Not Run |
| TC-074 | Password reset requires re-login; no automatic session. | Authentication & Roles | 🔴 High | 🔒 Security | ⏳ Not Run |
| TC-075 | User with TOTP enabled must enter valid code after password. | Authentication & Roles | 🔴 High | 🔒 Security | ⏳ Not Run |
| TC-076 | Recovery codes allow login without authenticator app. | Authentication & Roles | 🟡 Medium | 🔒 Security | ⏳ Not Run |
| TC-077 | User can enable email MFA after TOTP challenge. | Authentication & Roles | 🟡 Medium | 🧪 Functional | ⏳ Not Run |
| TC-078 | Login fallback via email code succeeds. | Authentication & Roles | 🔴 High | 🔒 Security | ⏳ Not Run |
| TC-079 | Email code resend blocked during 30s cooldown. | Authentication & Roles | 🟡 Medium | 🔒 Security | ⏳ Not Run |
| TC-080 | Disabling email codes requires password and TOTP. | Authentication & Roles | 🔴 High | 🔒 Security | ⏳ Not Run |

## Prediction
| Test Case ID | Test Case Description | Module | Priority | Test Type | Status |
| --- | --- | --- | --- | --- | --- |
| TC-010 | Submitting valid data returns prediction label, probability, risk band, and confidence. | Prediction | 🔴 High | 🧪 Functional | ⏳ Not Run |
| TC-011 | Invalid numeric or categorical values show validation errors. | Prediction | 🟡 Medium | 🧪 Functional | ⏳ Not Run |
| TC-012 | Patient name exceeding 120 characters is rejected. | Prediction | 🟡 Medium | 🧪 Functional | ⏳ Not Run |
| TC-013 | Prediction result can be downloaded as PDF report. | Prediction | 🟡 Medium | 🧪 Functional | ⏳ Not Run |
| TC-014 | Submitting when model is missing shows an informative error. | Prediction | 🔴 High | 🧪 Functional | ⏳ Not Run |
| TC-015 | Model exception returns friendly error message without crashing. | Prediction | 🟡 Medium | 🧪 Functional | ⏳ Not Run |

## Batch Upload & EDA
| Test Case ID | Test Case Description | Module | Priority | Test Type | Status |
| --- | --- | --- | --- | --- | --- |
| TC-016 | CSV upload cleans data and shows progress. | Batch Upload & EDA | 🔴 High | 🧪 Functional | ⏳ Not Run |
| TC-017 | Upload with invalid structure is rejected with error message. | Batch Upload & EDA | 🔴 High | 🧪 Functional | ⏳ Not Run |
| TC-018 | EDA highlights outliers using multiple algorithms. | Batch Upload & EDA | 🟡 Medium | 🧪 Functional | ⏳ Not Run |
| TC-019 | EDA payload separates traces for prediction labels. | Batch Upload & EDA | 🟡 Medium | 🧪 Functional | ⏳ Not Run |
| TC-020 | EDA payload groups by string target values. | Batch Upload & EDA | 🟡 Medium | 🧪 Functional | ⏳ Not Run |
| TC-021 | EDA payload handles dataset without target column. | Batch Upload & EDA | 🟢 Low | 🧪 Functional | ⏳ Not Run |
| TC-022 | Dashboard export creates PDF with KPIs and charts. | Batch Upload & EDA | 🟡 Medium | 🧪 Functional | ⏳ Not Run |

## Encryption
| Test Case ID | Test Case Description | Module | Priority | Test Type | Status |
| --- | --- | --- | --- | --- | --- |
| TC-041 | Patient data encrypted with envelope scheme when enabled. | Encryption | 🔴 High | 🔒 Security | ⏳ Not Run |

## RBAC
| Test Case ID | Test Case Description | Module | Priority | Test Type | Status |
| --- | --- | --- | --- | --- | --- |
| TC-050 | Admin role is forbidden from Predict, Batch, Dashboard, Research modules. | RBAC | 🔴 High | 🔒 Security | ⏳ Not Run |
| TC-051 | SuperAdmin bypasses all module restrictions. | RBAC | 🔴 High | 🔒 Security | ⏳ Not Run |

## Navigation & Motion
| Test Case ID | Test Case Description | Module | Priority | Test Type | Status |
| --- | --- | --- | --- | --- | --- |
| TC-060 | Nav shows only permitted items for each role. | Navigation | 🔴 High | 🧪 Functional | ⏳ Not Run |
| TC-061 | Theme toggle and user menu remain keyboard accessible after redesign. | Navigation | 🟡 Medium | 🧪 Accessibility | ⏳ Not Run |
| TC-062 | Animations disable when `prefers-reduced-motion` is set. | Motion | 🟡 Medium | 🧪 Accessibility | ⏳ Not Run |

## Doctor Dashboard
| Test Case ID | Test Case Description | Module | Priority | Test Type | Status |
| --- | --- | --- | --- | --- | --- |
| TC-023 | Doctor dashboard lists only doctor’s own patients. | Doctor Dashboard | 🔴 High | 🧪 Functional | ⏳ Not Run |
| TC-024 | Doctor cannot view other doctors’ patient records. | Doctor Dashboard | 🔴 High | 🔒 Security | ⏳ Not Run |
| TC-025 | Patient list is ordered with newest entries first. | Doctor Dashboard | 🟡 Medium | 🧪 Functional | ⏳ Not Run |

## SuperAdmin Management
| Test Case ID | Test Case Description | Module | Priority | Test Type | Status |
| --- | --- | --- | --- | --- | --- |
| TC-026 | SuperAdmin approves a pending user. | SuperAdmin Management | 🔴 High | 🧪 Functional | ⏳ Not Run |
| TC-027 | SuperAdmin changes user role or status with audit log. | SuperAdmin Management | 🟡 Medium | 🧪 Functional | ⏳ Not Run |
| TC-028 | SuperAdmin resets a user password. | SuperAdmin Management | 🔴 High | 🔒 Security | ⏳ Not Run |
| TC-029 | Audit log displays administrative actions. | SuperAdmin Management | 🟡 Medium | 🧪 Functional | ⏳ Not Run |
| TC-030 | Admin cannot approve non-doctor accounts. | SuperAdmin Management | 🟡 Medium | 🔒 Security | ⏳ Not Run |
| TC-031 | Admin cannot suspend or modify SuperAdmin status. | SuperAdmin Management | 🔴 High | 🔒 Security | ⏳ Not Run |
| TC-032 | Dashboard search filters users by username or email. | SuperAdmin Management | 🟡 Medium | 🧪 Functional | ⏳ Not Run |
| TC-033 | Dashboard supports sorting users by role, status, or creation date. | SuperAdmin Management | 🟢 Low | 🧪 Functional | ⏳ Not Run |
| TC-034 | SuperAdmin account is hidden from user list. | SuperAdmin Management | 🔴 High | 🔒 Security | ⏳ Not Run |

## User Settings
| Test Case ID | Test Case Description | Module | Priority | Test Type | Status |
| --- | --- | --- | --- | --- | --- |
| TC-035 | User updates profile information and avatar. | User Settings | 🟡 Medium | 🧪 Functional | ⏳ Not Run |
| TC-036 | User changes password successfully. | User Settings | 🔴 High | 🔒 Security | ⏳ Not Run |
| TC-037 | Activity log shows recent user actions. | User Settings | 🟢 Low | 🧪 Functional | ⏳ Not Run |
| TC-038 | Avatar upload rejects non-image files. | User Settings | 🟡 Medium | 🔒 Security | ⏳ Not Run |
| TC-039 | Password change with incorrect current password is rejected. | User Settings | 🟡 Medium | 🔒 Security | ⏳ Not Run |
| TC-040 | Profile update with invalid email format is rejected. | User Settings | 🟢 Low | 🧪 Functional | ⏳ Not Run |

## Simulations
| Test Case ID | Test Case Description | Module | Priority | Test Type | Status |
| --- | --- | --- | --- | --- | --- |
| TC-041 | Simulations page loads without chart until variable selected. | Simulations | 🟢 Low | 🧪 Functional | ⏳ Not Run |
| TC-042 | Simulation shows risk curve after selecting a variable. | Simulations | 🟢 Low | 🧪 Functional | ⏳ Not Run |
| TC-043 | Selecting unsupported variable returns warning message. | Simulations | 🟡 Medium | 🧪 Functional | ⏳ Not Run |
| TC-056 | Changing input triggers inline loader and update acknowledgment. | Simulations | 🟡 Medium | 🧪 Functional | ⏳ Not Run |
| TC-057 | Rapid changes cancel previous simulation requests. | Simulations | 🟡 Medium | 🧪 Functional | ⏳ Not Run |
| TC-058 | Failed simulation shows toast and keeps last result. | Simulations | 🟢 Low | 🧪 Functional | ⏳ Not Run |

## Research Paper Viewer
| Test Case ID | Test Case Description | Module | Priority | Test Type | Status |
| --- | --- | --- | --- | --- | --- |
| TC-044 | Research paper renders with sections and figures. | Research Paper Viewer | 🟢 Low | 🧪 Functional | ⏳ Not Run |
| TC-045 | Navigating to non-existent paper returns 404. | Research Paper Viewer | 🟢 Low | 🧪 Functional | ⏳ Not Run |

## Security
| Test Case ID | Test Case Description | Module | Priority | Test Type | Status |
| --- | --- | --- | --- | --- | --- |
| TC-046 | Submitting POST without CSRF token is rejected. | Security | 🔴 High | 🔒 Security | ⏳ Not Run |
| TC-047 | Session times out after inactivity. | Security | 🔴 High | 🔒 Security | ⏳ Not Run |
| TC-048 | Multiple failed logins trigger temporary account lock. | Security | 🔴 High | 🔒 Security | ⏳ Not Run |
| TC-049 | User-supplied data is HTML-escaped to prevent XSS. | Security | 🟡 Medium | 🔒 Security | ⏳ Not Run |
| TC-050 | Safe GET and HEAD requests bypass CSRF validation. | Security | 🟢 Low | 🧪 Functional | ⏳ Not Run |

## Regression
| Test Case ID | Test Case Description | Module | Priority | Test Type | Status |
| --- | --- | --- | --- | --- | --- |
| TC-051 | Batch prediction handles missing `num_major_vessels` values without error. | Batch Upload & EDA | 🟡 Medium | 🧪 Functional | ⏳ Not Run |

## UI & Layout
| Test Case ID | Test Case Description | Module | Priority | Test Type | Status |
| --- | --- | --- | --- | --- | --- |
| TC-052 | Login page shows branding, helpful links, and responsive design. | Authentication & Roles | 🟢 Low | 🧪 Functional | ⏳ Not Run |
| TC-053 | Password field eye icon toggles visibility on login page. | Authentication & Roles | 🟢 Low | 🧪 Functional | ⏳ Not Run |
| TC-054 | Identifier field on login page starts empty without displaying "None". | Authentication & Roles | 🟢 Low | 🧪 Functional | ⏳ Not Run |
| TC-055 | Login form disables autofill so fields remain blank. | Authentication & Roles | 🟢 Low | 🧪 Functional | ⏳ Not Run |

## UI Theming
| Test Case ID | Test Case Description | Module | Priority | Test Type | Status |
| --- | --- | --- | --- | --- | --- |
| TC-060 | Theme toggle updates `data-bs-theme`, cookie, and `localStorage` consistently. | UI Theming | 🟡 Medium | 🧪 Functional | ⏳ Not Run |
| TC-061 | Server-side rendering respects `theme` cookie to avoid flash of incorrect theme. | UI Theming | 🟡 Medium | 🧪 Functional | ⏳ Not Run |
| TC-062 | Charts and table headers render without white backgrounds in dark mode. | UI Theming | 🟡 Medium | 🧪 Functional | ⏳ Not Run |
| TC-063 | Cleaning log output removes blank or whitespace-only lines for compact display. | UI Theming | 🟢 Low | 🧪 Functional | ⏳ Not Run |
| TC-064 | Login and signup pages expose a persistent theme toggle with no flash on first paint. | UI Theming | 🟡 Medium | 🧪 Functional | ⏳ Not Run |
