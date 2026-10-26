"""
Unit tests for 🔒 PII encryption helper (DPDP Act 2023 compliance).
"""

from app.security import encrypt_text, decrypt_text, EncryptedString


def test_encryption_roundtrip_ascii():
    """Verify standard ASCII string round-trip."""
    plain = "Ramesh Patil"
    cipher = encrypt_text(plain)
    assert cipher is not None
    assert cipher != plain
    decrypted = decrypt_text(cipher)
    assert decrypted == plain


def test_encryption_roundtrip_marathi():
    """Verify vernacular Marathi Unicode strings encrypt and decrypt losslessly."""
    plain = "सुनीता कांबळे"
    cipher = encrypt_text(plain)
    assert cipher is not None
    assert cipher != plain
    decrypted = decrypt_text(cipher)
    assert decrypted == plain


def test_encryption_roundtrip_phone_and_income():
    """Verify numerical and formatted identity attributes."""
    phone = "+919876543210"
    income = "180000.00"

    cipher_phone = encrypt_text(phone)
    cipher_income = encrypt_text(income)

    assert decrypt_text(cipher_phone) == phone
    assert decrypt_text(cipher_income) == income


def test_encryption_none_handling():
    """Verify None input returns None."""
    assert encrypt_text(None) is None
    assert decrypt_text(None) is None


def test_type_decorator():
    """Verify EncryptedString TypeDecorator hooks."""
    decorator = EncryptedString()
    raw = "Kavita Shinde"
    processed = decorator.process_bind_param(raw, None)
    assert processed is not None
    assert processed != raw
    retrieved = decorator.process_result_value(processed, None)
    assert retrieved == raw
