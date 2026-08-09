from uuid import uuid4

from app.core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)


def test_password_hash_roundtrip() -> None:
    hashed = hash_password("agenda123")
    assert hashed != "agenda123"
    assert verify_password("agenda123", hashed)
    assert not verify_password("errada", hashed)


def test_jwt_roundtrip() -> None:
    user_id = uuid4()
    token = create_access_token(user_id, extra={"email": "veronica@escritorio.com"})
    payload = decode_access_token(token)
    assert payload["sub"] == str(user_id)
    assert payload["email"] == "veronica@escritorio.com"
