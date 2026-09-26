import secrets

def generate_verification_otp() -> str:
    """
    Generates a secure 4-digit numerical OTP.
    """
    return f"{secrets.randbelow(9000) + 1000}"