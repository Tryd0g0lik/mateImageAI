from django.contrib.auth.hashers import (
    mask_hash,
    make_password,
    check_password,
    PBKDF2PasswordHasher,
)

from project.settings import SECRET_KEY


class Hasher(PBKDF2PasswordHasher):
    """
    <algorithm>$<iterations>$<salt>$<hash>
    https://docs.djangoproject.com/en/5.2/topics/auth/passwords/
    """

    def hashing(selfself, password: str, salt_:str, iterations=None):
        hasher_password = make_password(password, salt=salt_)
        return hasher_password
