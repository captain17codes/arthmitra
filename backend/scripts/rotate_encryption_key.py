"""
Encryption Key Rotation Script (TECH_SPEC §11).
Re-encrypts all database encrypted columns with a new Fernet key.
Usage:
  python scripts/rotate_encryption_key.py --old-key <OLD> --new-key <NEW>
"""

from __future__ import annotations

import argparse
import logging

from cryptography.fernet import Fernet
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.config import settings
from models.beneficiary import Beneficiary, Consent
from models.organization import User

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("key-rotation")


def rotate_keys(old_key: str, new_key: str, database_url: str) -> None:
    old_cipher = Fernet(old_key.encode("utf-8"))
    new_cipher = Fernet(new_key.encode("utf-8"))

    engine = create_engine(database_url)
    with Session(engine) as session:
        # 1. Users phone
        users = session.execute(select(User)).scalars().all()
        user_count = 0
        for u in users:
            if u.phone:
                try:
                    decrypted = old_cipher.decrypt(u.phone.encode("utf-8")).decode("utf-8")
                    u.phone = new_cipher.encrypt(decrypted.encode("utf-8")).decode("utf-8")
                    user_count += 1
                except Exception as e:
                    logger.warning(f"Skipping user {u.id}: {e}")

        # 2. Beneficiaries first_name
        bens = session.execute(select(Beneficiary)).scalars().all()
        ben_count = 0
        for b in bens:
            if b.first_name and b.first_name != "REDACTED":
                try:
                    decrypted = old_cipher.decrypt(b.first_name.encode("utf-8")).decode("utf-8")
                    b.first_name = new_cipher.encrypt(decrypted.encode("utf-8")).decode("utf-8")
                    ben_count += 1
                except Exception as e:
                    logger.warning(f"Skipping beneficiary {b.id}: {e}")

        # 3. Consents audio_object_key
        consents = session.execute(select(Consent)).scalars().all()
        consent_count = 0
        for c in consents:
            if c.audio_object_key:
                try:
                    decrypted = old_cipher.decrypt(c.audio_object_key.encode("utf-8")).decode("utf-8")
                    c.audio_object_key = new_cipher.encrypt(decrypted.encode("utf-8")).decode("utf-8")
                    consent_count += 1
                except Exception as e:
                    logger.warning(f"Skipping consent {c.id}: {e}")

        session.commit()
        logger.info(
            f"Successfully rotated encryption keys: {user_count} users, "
            f"{ben_count} beneficiaries, {consent_count} consents."
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Rotate database encryption keys")
    parser.add_argument("--old-key", required=True, help="Current 32-byte Fernet key")
    parser.add_argument("--new-key", required=True, help="New 32-byte Fernet key")
    args = parser.parse_args()

    rotate_keys(args.old_key, args.new_key, settings.database_url_sync)
