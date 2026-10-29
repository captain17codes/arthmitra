"""Self-service sign-up (OTP + PIN), per-person data isolation and account erasure."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import select, update

from models.auth_otp import OtpCode
from models.case import Case
from models.organization import User

from .test_core_api import api_client  # noqa: F401  (fixture)


async def _age_otps(factory) -> None:
    """Pretend earlier OTPs were sent a while ago (bypass the 30 s resend gap)."""
    async with factory() as s:
        await s.execute(update(OtpCode).values(created_at=datetime.now(UTC) - timedelta(minutes=1)))
        await s.commit()


async def _sign_up(client, phone: str, name: str, pin: str = "4321") -> str:
    r = await client.post("/auth/otp/request", json={"phone": phone})
    assert r.status_code == 200, r.text
    otp = r.json()["dev_otp"]
    r = await client.post("/auth/otp/verify", json={"phone": phone, "otp": otp})
    assert r.status_code == 200, r.text
    assert r.json()["is_new_user"] is True
    r = await client.post("/auth/pin", json={"setup_token": r.json()["setup_token"], "pin": pin, "name": name})
    assert r.status_code == 200, r.text
    assert r.json()["user"]["role"] == "citizen"
    return r.json()["access_token"]


async def _new_plan(client, token: str) -> int:
    h = {"Authorization": f"Bearer {token}"}
    b = await client.post("/beneficiaries", headers=h, json={
        "first_name": "Asha", "gender": "female", "age": 30, "category": "SC",
        "annual_family_income": 90000, "consent": {"method": "tap", "language": "mr"},
    })
    assert b.status_code == 201, b.text
    c = await client.post("/cases", headers=h, json={
        "beneficiary_id": b.json()["id"], "village_lgd": 555001, "business_code": "kirana",
        "margin_available": 10000, "language": "mr",
    })
    assert c.status_code == 201, c.text
    return c.json()["id"]


@pytest.mark.asyncio
async def test_sign_up_login_and_wrong_otp(api_client):  # noqa: F811
    client, _ = api_client
    r = await client.post("/auth/otp/request", json={"phone": "12345"})
    assert r.status_code == 422

    r = await client.post("/auth/otp/request", json={"phone": "+91 98220 11111"})
    otp = r.json()["dev_otp"]
    assert len(otp) == 6
    wrong = "000000" if otp != "000000" else "111111"
    assert (await client.post("/auth/otp/verify", json={"phone": "9822011111", "otp": wrong})).status_code == 400
    v = await client.post("/auth/otp/verify", json={"phone": "9822011111", "otp": otp})
    assert v.status_code == 200
    # name is required for a new account
    r = await client.post("/auth/pin", json={"setup_token": v.json()["setup_token"], "pin": "4321"})
    assert r.status_code == 422
    r = await client.post("/auth/pin", json={"setup_token": v.json()["setup_token"], "pin": "4321", "name": "Asha"})
    assert r.status_code == 200
    # OTP cannot be reused
    assert (await client.post("/auth/otp/verify", json={"phone": "9822011111", "otp": otp})).status_code == 400

    r = await client.post("/auth/login", json={"phone": "9822011111", "pin": "4321"})
    assert r.status_code == 200
    me = await client.get("/auth/me", headers={"Authorization": f"Bearer {r.json()['access_token']}"})
    assert me.json()["name"] == "Asha" and me.json()["role"] == "citizen"


@pytest.mark.asyncio
async def test_setup_token_is_not_an_access_token(api_client):  # noqa: F811
    client, _ = api_client
    r = await client.post("/auth/otp/request", json={"phone": "9822022222"})
    v = await client.post("/auth/otp/verify", json={"phone": "9822022222", "otp": r.json()["dev_otp"]})
    st = v.json()["setup_token"]
    assert (await client.get("/auth/me", headers={"Authorization": f"Bearer {st}"})).status_code == 401
    token = await _sign_up_from_setup(client, st)
    assert (await client.post("/auth/pin", json={"setup_token": token, "pin": "1111"})).status_code == 401


async def _sign_up_from_setup(client, st: str) -> str:
    r = await client.post("/auth/pin", json={"setup_token": st, "pin": "4321", "name": "Ravi"})
    return r.json()["access_token"]


@pytest.mark.asyncio
async def test_otp_rate_limits_and_attempts(api_client):  # noqa: F811
    client, factory = api_client
    assert (await client.post("/auth/otp/request", json={"phone": "9822033333"})).status_code == 200
    assert (await client.post("/auth/otp/request", json={"phone": "9822033333"})).status_code == 429  # 30 s gap
    await _age_otps(factory)
    r = await client.post("/auth/otp/request", json={"phone": "9822033333"})
    otp = r.json()["dev_otp"]
    wrong = "000000" if otp != "000000" else "111111"
    for _ in range(5):
        await client.post("/auth/otp/verify", json={"phone": "9822033333", "otp": wrong})
    # after 5 wrong tries even the right code is refused
    assert (await client.post("/auth/otp/verify", json={"phone": "9822033333", "otp": otp})).status_code == 400
    await _age_otps(factory)
    assert (await client.post("/auth/otp/request", json={"phone": "9822033333"})).status_code == 200
    await _age_otps(factory)
    assert (await client.post("/auth/otp/request", json={"phone": "9822033333"})).status_code == 429  # 3 per 15 min


@pytest.mark.asyncio
async def test_pin_lockout_and_reset_with_otp(api_client):  # noqa: F811
    client, factory = api_client
    await _sign_up(client, "9822044444", "Meena", pin="2580")
    for _ in range(5):
        assert (await client.post("/auth/login", json={"phone": "9822044444", "pin": "0000"})).status_code == 401
    assert (await client.post("/auth/login", json={"phone": "9822044444", "pin": "2580"})).status_code == 429

    await _age_otps(factory)
    r = await client.post("/auth/otp/request", json={"phone": "9822044444"})
    v = await client.post("/auth/otp/verify", json={"phone": "9822044444", "otp": r.json()["dev_otp"]})
    assert v.json()["is_new_user"] is False and v.json()["name"] == "Meena"
    r = await client.post("/auth/pin", json={"setup_token": v.json()["setup_token"], "pin": "1470"})
    assert r.status_code == 200
    assert (await client.post("/auth/login", json={"phone": "9822044444", "pin": "1470"})).status_code == 200
    assert (await client.post("/auth/login", json={"phone": "9822044444", "pin": "2580"})).status_code == 401
    async with factory() as s:
        n = len((await s.execute(select(User).where(User.name == "Meena"))).scalars().all())
    assert n == 1  # reset did not create a second account


@pytest.mark.asyncio
async def test_each_person_sees_only_their_own_plans(api_client):  # noqa: F811
    client, _ = api_client
    t_a = await _sign_up(client, "9822055555", "A")
    t_b = await _sign_up(client, "9822066666", "B")
    case_a = await _new_plan(client, t_a)
    ha, hb = {"Authorization": f"Bearer {t_a}"}, {"Authorization": f"Bearer {t_b}"}
    assert [c["id"] for c in (await client.get("/cases", headers=ha)).json()] == [case_a]
    assert (await client.get("/cases", headers=hb)).json() == []
    assert (await client.get(f"/cases/{case_a}", headers=hb)).status_code == 404
    assert (await client.get("/beneficiaries", headers=hb)).json() == []


@pytest.mark.asyncio
async def test_profile_update_and_account_erasure(api_client):  # noqa: F811
    client, factory = api_client
    token = await _sign_up(client, "9822077777", "Kavita")
    h = {"Authorization": f"Bearer {token}"}
    case_id = await _new_plan(client, token)
    ben_id = (await client.get("/beneficiaries", headers=h)).json()[0]["id"]
    r = await client.patch(f"/beneficiaries/{ben_id}", headers=h, json={"annual_family_income": 120000, "age": 31})
    assert r.status_code == 200 and r.json()["annual_family_income"] == 120000 and r.json()["age"] == 31

    assert (await client.delete("/auth/me", headers=h)).status_code == 200
    assert (await client.post("/auth/login", json={"phone": "9822077777", "pin": "4321"})).status_code == 401
    async with factory() as s:
        assert (await s.execute(select(Case).where(Case.id == case_id))).scalar_one_or_none() is None
    # the number can sign up again afresh
    await _sign_up(client, "9822077777", "Kavita")


@pytest.mark.asyncio
async def test_non_personal_accounts_cannot_self_erase(api_client):  # noqa: F811
    client, _ = api_client
    r = await client.post("/auth/login", json={"phone": "9876543210", "pin": "1234"})
    h = {"Authorization": f"Bearer {r.json()['access_token']}"}
    assert (await client.delete("/auth/me", headers=h)).status_code == 403


def _fake_firebase(monkeypatch):
    """Sign tokens with our own key and serve its cert as if it were Google's."""
    import datetime as dt

    from cryptography import x509
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import rsa
    from cryptography.x509.oid import NameOID

    from app import firebase_auth
    from app.config import settings

    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "test")])
    now = dt.datetime.now(dt.UTC)
    cert = (
        x509.CertificateBuilder().subject_name(name).issuer_name(name).public_key(key.public_key())
        .serial_number(1).not_valid_before(now - dt.timedelta(days=1)).not_valid_after(now + dt.timedelta(days=1))
        .sign(key, hashes.SHA256())
    )
    pem = cert.public_bytes(serialization.Encoding.PEM).decode()
    monkeypatch.setattr(settings, "firebase_project_id", "arthmitra-test")
    monkeypatch.setattr(settings, "otp_provider", "firebase")
    firebase_auth._cache.update(certs={"k1": pem}, exp=1e12)

    def make(phone="+919822088888", provider="phone", aud="arthmitra-test", kid="k1"):
        import time

        import jwt as pyjwt

        t = int(time.time())
        claims = {"iss": f"https://securetoken.google.com/{aud}", "aud": aud, "sub": "u1", "iat": t, "exp": t + 3600,
                  "auth_time": t, "phone_number": phone, "firebase": {"sign_in_provider": provider}}
        return pyjwt.encode(claims, key, algorithm="RS256", headers={"kid": kid})

    return make


@pytest.mark.asyncio
async def test_firebase_phone_login(api_client, monkeypatch):  # noqa: F811
    client, _ = api_client
    make = _fake_firebase(monkeypatch)
    # Built-in OTP is switched off when Firebase sends the SMS
    assert (await client.post("/auth/otp/request", json={"phone": "9822088888"})).status_code == 400
    assert (await client.get("/auth/config")).json() == {"otp_provider": "firebase"}

    r = await client.post("/auth/firebase", json={"id_token": make()})
    assert r.status_code == 200 and r.json()["is_new_user"] is True
    r = await client.post("/auth/pin", json={"setup_token": r.json()["setup_token"], "pin": "3690", "name": "Lata"})
    assert r.status_code == 200
    assert (await client.post("/auth/login", json={"phone": "9822088888", "pin": "3690"})).status_code == 200

    for bad in (make(aud="other-project"), make(provider="password"), make(kid="nope"), "garbage"):
        assert (await client.post("/auth/firebase", json={"id_token": bad})).status_code == 401
