"""Minimal Jinja templates used during tests.

These templates replace the legacy Bootstrap-based frontend so the Flask
application can continue to render essential flows while the modern Next.js
frontend lives in the `frontend/` workspace.  Only the markup required by the
backend logic and tests is included here.  Pages share a compact base layout
that exposes navigation links, theme data, and flash messages to keep behaviour
compatible with the original application.
"""
from __future__ import annotations

from typing import Dict

TEMPLATES: Dict[str, str] = {
    "base.html": """
    <!doctype html>
    <html lang=\"en\" data-bs-theme=\"{{ theme|default('light') }}\">
    <head>
      <meta charset=\"utf-8\">
      <title>{% block title %}Heartlytics{% endblock %}</title>
    </head>
    <body>
      <header>
        {% if current_user.is_authenticated %}
        <nav aria-label=\"primary\">
          <ul>
          {% for item in nav_items %}
            <li><a href=\"{{ url_for(item.endpoint) }}\">{{ item.label }}</a></li>
          {% endfor %}
          </ul>
        </nav>
        {% endif %}
      </header>
      <main class=\"{% block main_classes %}{% endblock %}\">
        {% with messages = get_flashed_messages(with_categories=true) %}
          {% if messages %}
            <ul class=\"flash-messages\">
            {% for category, message in messages %}
              <li data-category=\"{{ category }}\">{{ message }}</li>
            {% endfor %}
            </ul>
          {% endif %}
        {% endwith %}
        {% block content %}{% endblock %}
      </main>
    </body>
    </html>
    """,
    "error.html": """
    {% extends 'base.html' %}
    {% block title %}Error{% endblock %}
    {% block content %}
    <section>
      <h1>{{ title or 'Error' }}</h1>
      <p>{{ message or 'Something went wrong.' }}</p>
      {% if messages %}
        <ul>{% for msg in messages %}<li>{{ msg }}</li>{% endfor %}</ul>
      {% endif %}
    </section>
    {% endblock %}
    """,
    "errors/403.html": """
    {% extends 'base.html' %}
    {% block title %}Forbidden{% endblock %}
    {% block content %}<p>Access forbidden.</p>{% endblock %}
    """,
    "predict/form.html": """
    {% extends 'base.html' %}
    {% block title %}Assessment{% endblock %}
    {% block content %}
    <h1>Risk Assessment</h1>
    <form method=\"post\">
      {% for key, value in defaults.items() %}
        <label for=\"field-{{ key }}\">{{ key }}</label>
        <input id=\"field-{{ key }}\" name=\"{{ key }}\" value=\"{{ value }}\" />
      {% endfor %}
      <button type=\"submit\">Submit</button>
    </form>
    {% if quick_actions %}
      <section aria-label=\"Assistant actions\">
        <ul>{% for action in quick_actions %}<li>{{ action.label }}</li>{% endfor %}</ul>
      </section>
    {% endif %}
    {% endblock %}
    """,
    "predict/result.html": """
    {% extends 'base.html' %}
    {% block title %}Result{% endblock %}
    {% block content %}
    <h1>Risk Result</h1>
    <p>{{ prediction_label }}</p>
    <p>Probability: {{ probability }}</p>
    {% endblock %}
    """,
    "dashboard/index.html": """
    {% extends 'base.html' %}
    {% block title %}Dashboard{% endblock %}
    {% block content %}
    <h1>Dashboard</h1>
    <section id=\"summary\">
      <p>Total records: {{ data|length }}</p>
    </section>
    <section id=\"records\">
      <table>
        <thead>
          <tr><th>Patient</th><th>Risk</th></tr>
        </thead>
        <tbody>
          {% for row in data %}
          <tr><td>{{ row.patient_name }}</td><td>{{ row.prediction }}</td></tr>
          {% endfor %}
        </tbody>
      </table>
    </section>
    {% endblock %}
    """,
    "dashboard/outliers.html": """
    {% extends 'base.html' %}
    {% block title %}Outliers{% endblock %}
    {% block content %}
    <h1>Outlier Analysis</h1>
    <form method=\"post\">
      {% for key, label in methods.items() %}
        <label><input type=\"checkbox\" name=\"methods\" value=\"{{ key }}\" {% if key in selected %}checked{% endif %}/> {{ label }}</label>
      {% endfor %}
      <button type=\"submit\">Run</button>
    </form>
    <section>
      <p>Total outliers: {{ total_outliers }}</p>
      {% for name, result in results.items() %}
        <article>
          <h2>{{ name }}</h2>
          <p>{{ result.summary }}</p>
        </article>
      {% endfor %}
    </section>
    {% endblock %}
    """,
    "dashboard/pdf.html": """
    {% extends 'base.html' %}
    {% block title %}Dashboard PDF{% endblock %}
    {% block content %}
    <h1>PDF Export</h1>
    <p>Preview {{ records|length }} records</p>
    {% endblock %}
    """,
    "auth/login.html": """
    {% extends 'base.html' %}
    {% block title %}Login{% endblock %}
    {% block main_classes %}auth-page{% endblock %}
    {% block content %}
    <h1>Sign in</h1>
    <form method=\"post\" autocomplete=\"off\">
      {{ form.hidden_tag() if form else '' }}
      {% set identifier = form.identifier.data if form and form.identifier.data else None %}
      <label>Email or Username</label>
      <input type=\"text\" name=\"identifier\" {% if identifier %}value=\"{{ identifier }}\"{% endif %} autocomplete=\"off\" required />
      <label>Password</label>
      <input type=\"password\" name=\"password\" autocomplete=\"off\" required />
      <button type=\"submit\">Login</button>
      <div class=\"links\">
        <a href=\"{{ url_for('auth.forgot') }}\">Forgot password?</a>
        <a href=\"{{ url_for('auth.signup') }}\">Create new account</a>
      </div>
    </form>
    {% endblock %}
    """,
    "auth/signup.html": """
    {% extends 'base.html' %}
    {% block title %}Sign up{% endblock %}
    {% block content %}
    <h1>Create account</h1>
    <form method=\"post\">
      {{ form.hidden_tag() if form else '' }}
      <label>Username<input name=\"username\" value=\"{{ form.username.data if form else '' }}\" /></label>
      <label>Email<input name=\"email\" value=\"{{ form.email.data if form else '' }}\" /></label>
      <label>Password<input type=\"password\" name=\"password\" /></label>
      <label>Confirm<input type=\"password\" name=\"confirm\" /></label>
      <button type=\"submit\">Submit</button>
    </form>
    {% endblock %}
    """,
    "auth/forgot.html": """
    {% extends 'base.html' %}
    {% block title %}Forgot password{% endblock %}
    {% block content %}
    <h1>Reset your password</h1>
    <form method=\"post\">
      {{ form.hidden_tag() if form else '' }}
      <label>Email or Username<input type=\"text\" name=\"identifier\" autocomplete=\"off\" /></label>
      <button type=\"submit\">Send code</button>
    </form>
    {% endblock %}
    """,
    "auth/verify.html": """
    {% extends 'base.html' %}
    {% block title %}Verify code{% endblock %}
    {% block content %}
    <h1>Enter verification code</h1>
    <form method=\"post\">
      {{ form.hidden_tag() if form else '' }}
      <label>Code<input name=\"code\" autocomplete=\"off\" /></label>
      <button type=\"submit\">Verify</button>
    </form>
    <p>Resend available in {{ cooldown }} seconds</p>
    {% endblock %}
    """,
    "auth/reset.html": """
    {% extends 'base.html' %}
    {% block title %}Reset password{% endblock %}
    {% block content %}
    <h1>Choose a new password</h1>
    <form method=\"post\">
      {{ form.hidden_tag() if form else '' }}
      <label>New password<input type=\"password\" name=\"password\" /></label>
      <label>Confirm<input type=\"password\" name=\"confirm\" /></label>
      <button type=\"submit\">Reset</button>
    </form>
    {% endblock %}
    """,
    "auth/mfa_setup.html": """
    {% extends 'base.html' %}
    {% block title %}Two-step verification{% endblock %}
    {% block content %}
    <h1>Two-Step Verification</h1>
    <p>Scan the QR code or use the secret key below.</p>
    <pre>{{ secret }}</pre>
    <form method=\"post\">
      {{ form.hidden_tag() if form else '' }}
      <label>Code<input name=\"code\" autocomplete=\"off\" /></label>
      <button type=\"submit\">Enable</button>
    </form>
    {% endblock %}
    """,
    "auth/mfa_verify.html": """
    {% extends 'base.html' %}
    {% block title %}Verify MFA{% endblock %}
    {% block content %}
    <h1>Enter authentication code</h1>
    <p>We've sent a code to {{ masked_email }}</p>
    <form method=\"post\">
      {{ form.hidden_tag() if form else '' }}
      <label>Code<input name=\"code\" autocomplete=\"off\" /></label>
      <button type=\"submit\">Verify</button>
    </form>
    <a href=\"{{ url_for('auth.mfa_email') }}\">Use email instead</a>
    {% endblock %}
    """,
    "auth/mfa_email.html": """
    {% extends 'base.html' %}
    {% block title %}Email code{% endblock %}
    {% block content %}
    <h1>Email Verification</h1>
    <form method=\"post\">
      {{ form.hidden_tag() if form else '' }}
      <label>Code<input name=\"code\" autocomplete=\"off\" /></label>
      <button type=\"submit\">Submit</button>
    </form>
    {% endblock %}
    """,
    "auth/mfa_recovery.html": """
    {% extends 'base.html' %}
    {% block title %}Recovery codes{% endblock %}
    {% block content %}
    <h1>Recovery Codes</h1>
    <ul>{% for code in codes %}<li>{{ code }}</li>{% endfor %}</ul>
    {% endblock %}
    """,
    "auth/mfa_disable.html": """
    {% extends 'base.html' %}
    {% block title %}Disable MFA{% endblock %}
    {% block content %}
    <h1>Disable two-step verification</h1>
    <form method=\"post\">
      {{ form.hidden_tag() if form else '' }}
      <label>Password<input type=\"password\" name=\"password\" /></label>
      <label>Code<input name=\"code\" autocomplete=\"off\" /></label>
      <button type=\"submit\">Disable</button>
    </form>
    {% endblock %}
    """,
    "debug/theme.html": """
    {% extends 'base.html' %}
    {% block title %}Theme Debug{% endblock %}
    {% block content %}
    <h1>Theme Debug</h1>
    <p id=\"theme-value\">data-bs-theme: {{ theme }}</p>
    {% endblock %}
    """,
    "debug/mail.html": """
    {% extends 'base.html' %}
    {% block title %}Mail Debug{% endblock %}
    {% block content %}
    <h1>Mail Debug</h1>
    <form method=\"post\">
      <label>Email<input type=\"email\" name=\"address\" /></label>
      <button type=\"submit\">Send</button>
    </form>
    {% if events %}
      <ul>{% for evt in events %}<li>{{ evt.message }}</li>{% endfor %}</ul>
    {% endif %}
    {% endblock %}
    """,
    "doctor/dashboard.html": """
    {% extends 'base.html' %}
    {% block title %}Doctor Dashboard{% endblock %}
    {% block content %}
    <h1>Doctor Dashboard</h1>
    <p>Total patients: {{ patients|length }}</p>
    {% endblock %}
    """,
    "user/dashboard.html": """
    {% extends 'base.html' %}
    {% block title %}User Dashboard{% endblock %}
    {% block content %}
    <h1>User Dashboard</h1>
    <p>Welcome {{ current_user.username }}</p>
    {% endblock %}
    """,
    "simulations/index.html": """
    {% extends 'base.html' %}
    {% block title %}Simulations{% endblock %}
    {% block content %}
    <h1>Simulation Playground</h1>
    <form method=\"post\" action=\"{{ url_for('simulations.run') }}\">
      <label>Variable<select name=\"variable\">
        <option value=\"age\">Age</option>
        <option value=\"exercise_angina\">Exercise Angina</option>
      </select></label>
      <button type=\"submit\">Run</button>
    </form>
    {% endblock %}
    """,
    "uploads/form.html": """
    {% extends 'base.html' %}
    {% block title %}Bulk Upload{% endblock %}
    {% block content %}
    <h1>Upload CSV</h1>
    <form method=\"post\" enctype=\"multipart/form-data\">
      <input type=\"file\" name=\"file\" />
      <button type=\"submit\">Upload</button>
    </form>
    {% endblock %}
    """,
    "uploads/columns_map.html": """
    {% extends 'base.html' %}
    {% block title %}Map Columns{% endblock %}
    {% block content %}
    <h1>Map Columns</h1>
    <form method=\"post\">
      {% for field, column in mapping.items() %}
        <label>{{ field }}<input name=\"{{ field }}\" value=\"{{ column }}\" /></label>
      {% endfor %}
      <button type=\"submit\">Continue</button>
    </form>
    {% endblock %}
    """,
    "uploads/preprocess.html": """
    {% extends 'base.html' %}
    {% block title %}Preprocess{% endblock %}
    {% block content %}
    <h1>Preprocess</h1>
    <p>Cleaning steps</p>
    {% if steps %}
      <ul>{% for step in steps %}<li>{{ step }}</li>{% endfor %}</ul>
    {% endif %}
    {% endblock %}
    """,
    "uploads/eda.html": """
    {% extends 'base.html' %}
    {% block title %}EDA{% endblock %}
    {% block content %}
    <h1>Exploratory Data Analysis</h1>
    <section id=\"summary\">
      <p>Total rows: {{ summary.total_rows if summary is defined and summary is not none else 0 }}</p>
    </section>
    {% endblock %}
    """,
    "settings/index.html": """
    {% extends 'base.html' %}
    {% block title %}Settings{% endblock %}
    {% block content %}
    <h1>Account Settings</h1>
    <section>
      <h2>Two-Step Verification</h2>
      <a href=\"{{ url_for('auth.mfa_setup') }}\">Set up MFA</a>
    </section>
    {% endblock %}
    """,
    "research/plain.html": """
    {% extends 'base.html' %}
    {% block title %}Research{% endblock %}
    {% block content %}
    {% set doc = paper if paper is defined and paper is not none else {'title': 'Research Library', 'sections': []} %}
    <article>
      <h1>{{ doc.title }}</h1>
      <section>
        {% for section in doc.sections %}
          <h2>{{ section.heading }}</h2>
          <p>{{ section.body }}</p>
        {% endfor %}
      </section>
    </article>
    {% endblock %}
    """,
    "superadmin/dashboard.html": """
    {% extends 'base.html' %}
    {% block title %}SuperAdmin{% endblock %}
    {% block content %}
    <h1>SuperAdmin Dashboard</h1>
    <table>
      <thead><tr><th>Username</th><th>Status</th></tr></thead>
      <tbody>
        {% for u in users %}
          <tr><td>{{ u.username }}</td><td>{{ u.status }}</td></tr>
        {% endfor %}
      </tbody>
    </table>
    {% endblock %}
    """,
    "superadmin/encryption.html": """
    {% extends 'base.html' %}
    {% block title %}Encryption Keys{% endblock %}
    {% block content %}
    <h1>Encryption</h1>
    <pre>{{ key_info }}</pre>
    {% endblock %}
    """,
    "superadmin/audit.html": """
    {% extends 'base.html' %}
    {% block title %}Audit Log{% endblock %}
    {% block content %}
    <h1>Audit Log</h1>
    <ul>{% for entry in records %}<li>{{ entry.action }}</li>{% endfor %}</ul>
    {% endblock %}
    """,
}
