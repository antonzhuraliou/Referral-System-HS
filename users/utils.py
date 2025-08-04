from string import ascii_uppercase, digits
from random import choices
from .models import InviteCode
from random import randint
from django.core.cache import cache
import logging
from rest_framework.response import Response
from rest_framework import status


logger = logging.getLogger(__name__)

OTP_TIMEOUT = 120

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


def create_phone_key(request):
    phone = request.data.get('phone')
    return phone


def set_code_redis(request):

    key = create_phone_key(request)

    code = f'{randint(1000, 9999)}'
    cache.set(key, code, timeout=OTP_TIMEOUT)

    logger.info(f"Verification code {code} sent to {key}")

    return Response(status=status.HTTP_201_CREATED)


def check_rate_limit(key):
    if cache.get(key):
        return Response(
                {'error': 'Please wait before requesting another code.'},
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )


