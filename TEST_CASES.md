# Test Cases

## Authentication & Roles
- **Login succeeds**
  1. Navigate to `/auth/login`.
  2. Enter valid credentials and submit.
  - Expected: user is redirected to their dashboard.
- **Login rate limit**
  1. Attempt to log in with invalid credentials five times.
  - Expected: further attempts show "Too many login attempts".
- **Signup requires approval for Doctors/Admins**
  1. Submit the signup form selecting the Doctor role.
  - Expected: account status is `pending` and cannot log in until approved.
- **Role restriction**
  1. Log in as a regular user.
  2. Navigate to `/superadmin`.
  - Expected: `403 Forbidden`.

## Prediction
- **Single prediction**
  1. Open the home page and submit the prediction form with valid data.
  - Expected: prediction label, probability, risk band, and confidence are displayed.
- **Validation errors**
  1. Submit the prediction form with invalid values (e.g., text in numeric field).
  - Expected: form redisplays with error messages.
- **Patient PDF report**
  1. After a prediction, click the PDF download link.
  - Expected: PDF containing patient details and model outputs is downloaded.

## Batch Upload & EDA
- **CSV upload**
  1. Navigate to the upload page and drop a CSV file.
  2. Map columns and start the batch process.
  - Expected: cleaned data preview and progress feedback.
- **Outlier detection**
  1. Run EDA after upload.
  - Expected: tables highlighting IQR, Isolation Forest, Z‑Score, LOF, and DBSCAN outliers.
- **Dashboard export**
  1. From the dashboard, export the PDF report.
  - Expected: PDF with KPIs, charts, and table of contents.

## Doctor Dashboard
- **Doctor sees own patients**
  1. Log in as a doctor who has submitted predictions.
  - Expected: dashboard lists only patients entered by that doctor.

## SuperAdmin Management
- **Approve user**
  1. Log in as SuperAdmin and open the dashboard.
  2. Approve a pending user.
  - Expected: user status changes to `approved`.
- **Change role or status**
  1. From the dashboard, update a user's role or suspend them.
  - Expected: change is persisted and recorded in audit logs.
- **Reset password**
  1. Trigger a password reset for a user.
  - Expected: temporary password is displayed.
- **View audit log**
  1. Open `/superadmin/audit`.
  - Expected: paginated list of administrative actions.

## User Settings
- **Update profile and avatar**
  1. Navigate to `/settings` and change profile fields and upload an avatar.
  - Expected: new information and image are saved.
- **Change password**
  1. Provide current and new passwords on the settings page.
  - Expected: password updated confirmation.
- **Activity log**
  1. Visit `/settings`.
  - Expected: recent actions appear in the activity table.

## Simulations
- **Exercise‑induced angina sensitivity**
  1. Open `/simulations` and run the simulation for different variables.
  - Expected: curves display risk changes and highlight the current baseline.

## Research Paper Viewer
- **Paper renders**
  1. Navigate to `/research` (or corresponding route).
  - Expected: LaTeX manuscript rendered with sections, figures, and references.

## Security
- **CSRF protection**
  1. Submit a POST request without the CSRF token.
  - Expected: request is rejected.
- **Session timeout**
  1. Log in and remain idle beyond the configured timeout.
  - Expected: user is logged out on next request.

