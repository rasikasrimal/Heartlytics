# Test Cases

| Test Case ID | Test Case Description | Module | Priority | Test Type | Status |
| --- | --- | --- | --- | --- | --- |
| TC-001 | Successful login redirects user to dashboard. | Authentication & Roles | 🔴 High | 🧪 Functional | ⏳ Not Run |
| TC-002 | Rate limiting blocks more than five invalid logins in 15 min. | Authentication & Roles | 🔴 High | 🔒 Security | ⏳ Not Run |
| TC-003 | Doctor/Admin signup remains pending until approved. | Authentication & Roles | 🟡 Medium | 🧪 Functional | ⏳ Not Run |
| TC-004 | Regular user cannot access `/superadmin`. | Authentication & Roles | 🔴 High | 🔒 Security | ⏳ Not Run |
| TC-005 | Logout endpoint terminates session. | Authentication & Roles | 🟡 Medium | 🧪 Functional | ⏳ Not Run |
| TC-006 | Unauthenticated user is redirected to login when accessing dashboard. | Authentication & Roles | 🔴 High | 🔒 Security | ⏳ Not Run |
| TC-007 | Submitting valid data returns prediction label, probability, risk band, and confidence. | Prediction | 🔴 High | 🧪 Functional | ⏳ Not Run |
| TC-008 | Invalid values in prediction form show validation errors. | Prediction | 🟡 Medium | 🧪 Functional | ⏳ Not Run |
| TC-009 | Prediction result can be downloaded as PDF report. | Prediction | 🟡 Medium | 🧪 Functional | ⏳ Not Run |
| TC-010 | CSV upload cleans data and shows progress. | Batch Upload & EDA | 🔴 High | 🧪 Functional | ⏳ Not Run |
| TC-011 | EDA highlights outliers using multiple algorithms. | Batch Upload & EDA | 🟡 Medium | 🧪 Functional | ⏳ Not Run |
| TC-012 | Dashboard export creates PDF with KPIs and charts. | Batch Upload & EDA | 🟡 Medium | 🧪 Functional | ⏳ Not Run |
| TC-013 | Doctor dashboard lists only doctor’s own patients. | Doctor Dashboard | 🔴 High | 🧪 Functional | ⏳ Not Run |
| TC-014 | SuperAdmin approves a pending user. | SuperAdmin Management | 🔴 High | 🧪 Functional | ⏳ Not Run |
| TC-015 | SuperAdmin changes user role or status with audit log. | SuperAdmin Management | 🟡 Medium | 🧪 Functional | ⏳ Not Run |
| TC-016 | SuperAdmin resets a user password. | SuperAdmin Management | 🔴 High | 🔒 Security | ⏳ Not Run |
| TC-017 | Audit log displays administrative actions. | SuperAdmin Management | 🟡 Medium | 🧪 Functional | ⏳ Not Run |
| TC-018 | User updates profile information and avatar. | User Settings | 🟡 Medium | 🧪 Functional | ⏳ Not Run |
| TC-019 | User changes password successfully. | User Settings | 🔴 High | 🔒 Security | ⏳ Not Run |
| TC-020 | Activity log shows recent user actions. | User Settings | 🟢 Low | 🧪 Functional | ⏳ Not Run |
| TC-021 | Simulation shows risk curves for varying variables. | Simulations | 🟢 Low | 🧪 Functional | ⏳ Not Run |
| TC-022 | Research paper renders with sections and figures. | Research Paper Viewer | 🟢 Low | 🧪 Functional | ⏳ Not Run |
| TC-023 | Submitting POST without CSRF token is rejected. | Security | 🔴 High | 🔒 Security | ⏳ Not Run |
| TC-024 | Session times out after inactivity. | Security | 🔴 High | 🔒 Security | ⏳ Not Run |

