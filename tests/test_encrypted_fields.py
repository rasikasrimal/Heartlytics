from app import db, Patient, User


def test_patient_encryption_round_trip(app):
    app.config["ENCRYPTION_ENABLED"] = True
    with app.app_context():
        user = User(username="u1", email="u1@example.com", role="Doctor", status="approved")
        db.session.add(user)
        db.session.commit()
        p = Patient(entered_by_user_id=user.id)
        p.patient_data = {"foo": "bar"}
        db.session.add(p)
        db.session.commit()
        assert p.patient_data_ct is not None
        assert p.patient_data == {"foo": "bar"}
        # legacy fallback
        app.config["ENCRYPTION_ENABLED"] = False
        app.config["READ_LEGACY_PLAINTEXT"] = True
        assert p.patient_data == {"foo": "bar"}
