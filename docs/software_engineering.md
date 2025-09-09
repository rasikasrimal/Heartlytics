# Software Engineering Methodology and Architecture

This document summarizes the engineering practices and design choices behind **Heartlytics**.

## Methodology
- **Iterative development** with Git version control and code reviews to maintain quality.
- **Testing** through pytest suites covering authentication, predictions, and security-critical flows.
- **Documentation** in Markdown files to capture design decisions and operating procedures.
- **Security-first mindset**: features are built with encryption, CSRF protection, and MFA.

## Architecture
- **Flask Blueprints** segment functionality into domains like auth, doctor, user, and admin dashboards.
- **Service layer** in `services/` encapsulates business logic for authentication, data processing, PDF generation, and more, keeping routes slim.
- **Modular templates**: Jinja2 templates are organized by feature with reusable components under `templates/_components`.
- **Extensible design**: new blueprints or services can be added without impacting existing modules thanks to clear boundaries.

These approaches yield a maintainable, testable, and secure codebase suitable for ongoing enhancements.
