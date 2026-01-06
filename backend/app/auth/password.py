from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerifyMismatchError

from app.utils.logger import get_logger

logger = get_logger(__name__)

# Argon2 hasher with secure defaults
_hasher = PasswordHasher(
    time_cost=3,        # Number of iterations
    memory_cost=65536,  # 64 MB memory usage
    parallelism=4,      # Number of parallel threads
    hash_len=32,        # Length of the hash
    salt_len=16         # Length of the random salt
)


def hash_password(password: str) -> str:
    """
    Hash a password using Argon2id.

    Args:
        password: The plaintext password to hash

    Returns:
        The hashed password string
    """
    return _hasher.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash.

    Args:
        plain_password: The plaintext password to verify
        hashed_password: The stored hash to verify against

    Returns:
        True if password matches, False otherwise
    """
    try:
        _hasher.verify(hashed_password, plain_password)
        return True
    except VerifyMismatchError:
        return False
    except InvalidHashError as e:
        logger.error(f"Invalid hash format: {e}")
        return False


def needs_rehash(hashed_password: str) -> bool:
    """
    Check if a password hash needs to be updated.

    This is useful when security parameters are increased.

    Args:
        hashed_password: The stored hash to check

    Returns:
        True if rehashing is recommended
    """
    return _hasher.check_needs_rehash(hashed_password)
