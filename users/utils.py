from string import ascii_uppercase, digits
from random import choices
from .models import InviteCode

def generate_invite_code():
    """
    Generates a random 6-character invite code consisting of uppercase letters and digits.
    """
    return ''.join(choices(ascii_uppercase + digits, k=6))


def generate_unique_invite_code():
    """
    Generates a unique 6-character invite code that does not exist in the database.

    The function attempts to generate a unique code up to 10 times. If all attempts fail,
    it raises an exception.
    """
    invite_code = generate_invite_code()
    for i in range(10):
        if not InviteCode.objects.filter(invite_code=invite_code).exists():
            return invite_code
    else:
        raise Exception("Could not generate a unique invite code")
