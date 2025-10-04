# Contributing to Heartlytics

Thank you for taking the time to improve the Heart Disease Risk Prediction web application! These guidelines outline the
expectations for contributors and the workflow we follow to keep the project healthy.

## 🧭 Ways to Contribute
- Fix bugs or implement new features in Flask blueprints, services, or templates.
- Improve the machine learning helpers, batch analysis utilities, or simulations.
- Enhance automated tests under `tests/` or add fixtures.
- Expand documentation in `docs/` or update this file when the workflow changes.

If you are unsure whether an idea fits the project, open a GitHub issue first so we can discuss it.

## 🛠 Development Environment
1. Fork the repository and clone your fork.
2. Create a virtual environment and activate it:
   ```bash
   python -m venv .venv
   source .venv/bin/activate   # Linux / macOS
   .venv\Scripts\activate      # Windows
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Copy `.env.example` to `.env` and adjust values for your environment. At a minimum set secrets, email credentials, and any
   encryption keys you require for local testing.
5. Run the development server with `flask run` and visit http://127.0.0.1:5000.

## ✅ Pull Request Checklist
Before submitting a PR, please ensure:
- [ ] Code is formatted according to PEP 8. We recommend using `black` or your editor's auto-formatting.
- [ ] Unit tests pass locally with `pytest`.
- [ ] Relevant templates render in both light and dark mode without breaking layout.
- [ ] Any new configuration values are documented in `README.md` (environment variables table) and have sensible defaults.
- [ ] User-facing changes include screenshots or GIFs in the PR description when possible.
- [ ] Documentation or inline comments are updated alongside code changes.

## 🧪 Testing
We rely on the `pytest` suite in the `tests/` directory. Please add or update tests that cover new functionality or bug fixes.
Run them locally before pushing changes:
```bash
pytest
```
If you add new CLI commands, services, or template logic, include tests or fixtures demonstrating expected behavior.

## 🔐 Security & Privacy Notes
- Never commit real secrets, private keys, or production datasets. Use `.env` or example values instead.
- Respect the encryption helpers in `services/security.py` and `helpers.py`; do not bypass them when touching encrypted
  models or database fields.
- Validate and sanitize all new user inputs. Follow existing patterns for CSRF protection and Flask form validation.

## 🗂 Branching & Commit Messages
- Create feature branches from `main` with a descriptive name (e.g., `feature/improve-batch-eda`).
- Write concise commit messages (present tense) that explain the change, e.g., `Add PDF export button to doctor dashboard`.
- Squash or rebase your branch to keep history clean before opening the PR.

## 💬 Communication
- Use draft pull requests for work-in-progress to gather early feedback.
- Reference related issues with `Fixes #123` or `Closes #123` in the PR description when applicable.
- Be respectful and collaborative. Follow the [GitHub Community Guidelines](https://docs.github.com/en/site-policy/github-terms/github-community-guidelines) in discussions and reviews.

We appreciate your help in making Heartlytics a reliable tool for understanding heart disease risk. Happy coding!
