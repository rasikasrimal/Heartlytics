import pytest
from services.crypto import envelope


def test_encrypt_round_trip(app):
    blob = envelope.encrypt_field(b"secret", "t:c|kid|1")
    assert envelope.decrypt_field(blob, "t:c|kid|1") == b"secret"


def test_tamper_detection(app):
    blob = envelope.encrypt_field(b"secret", "t:c|kid|1")
    blob["ciphertext"] = blob["ciphertext"][:-1] + b"x"
    with pytest.raises(Exception):
        envelope.decrypt_field(blob, "t:c|kid|1")


def test_nonce_uniqueness(app):
    nonces = set()
    for _ in range(50):
        blob = envelope.encrypt_field(b"data", "t:c|kid|1")
        assert blob["nonce"] not in nonces
        nonces.add(blob["nonce"])
