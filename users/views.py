import logging
import re
from typing import Optional

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.template.response import TemplateResponse
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiResponse,
    extend_schema,
)
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from users.utils import check_rate_limit, create_phone_key, set_code_redis

from .serializers import (
    MyUserSerializer,
    SendCodeRequestSerializer,
    TokenResponseSerializer,
    UseInviteCodeRequestSerializer,
    VerifyCodeRequestSerializer,
)

logger = logging.getLogger(__name__)

User = get_user_model()

BELARUS_PHONE_REGEX = r'^\+375(25|29|33|44)\d{7}$'


class SendCodeView(APIView):
    """
    Send a 4-digit verification code to a Belarusian phone number.
    """

    @extend_schema(
        tags=["Auth"],
        responses={
            200: OpenApiResponse(
                response=None,
                description="Returns the HTML page for sending the code."
            ),
        },
    )
    def get(self, request):
        return TemplateResponse(request, 'send_code.html')

    @extend_schema(
        tags=["Auth"],
        request=SendCodeRequestSerializer,
        responses={
            200: OpenApiResponse(
                response=None, description="Code successfully sent."
            ),
            400: OpenApiResponse(
                response=None, description="Missing or invalid phone number."
            ),
            429: OpenApiResponse(
                response=None, description="Too many requests."
            ),
        },
        examples=[
            OpenApiExample(
                name="Send code request",
                value={"phone": "+375291234567"},
                request_only=True,
            )
        ],
    )
    def post(self, request) -> Response:
        phone: Optional[str] = request.data.get('phone')

        if not phone:
            return Response(
                {'error': 'Please provide your phone number.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not re.match(BELARUS_PHONE_REGEX, phone):
            return Response(
                {
                    'error': 'Only Belarusian phone numbers are allowed. Format: +375XXXXXXXXX'
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        key = f"{phone}"

        check_rate_limit(key)

        set_code_redis(request)

        return Response(
            {'message': 'Verification code has been sent successfully'},
            status=status.HTTP_200_OK,
        )


class VerifyCodeView(APIView):
    """
    Verify the 4-digit code and return JWT tokens.
    """

    @extend_schema(
        tags=["Auth"],
        request=VerifyCodeRequestSerializer,
        responses={
            200: TokenResponseSerializer,
            400: OpenApiResponse(
                response=None,
                description="Missing/invalid data or code expired.",
            ),
        },
        examples=[
            OpenApiExample(
                name="Verify code request",
                value={"phone": "+375291234567", "code": "1234"},
                request_only=True,
            ),
            OpenApiExample(
                name="Verify code response",
                value={"refresh": "xxx", "access": "yyy", "user_id": 1},
                response_only=True,
            ),
        ],
    )
    def post(self, request) -> Response:
        phone: Optional[str] = request.data.get('phone')
        code: Optional[str] = request.data.get('code')

        if not phone or not code:
            return Response(
                {
                    'error': 'Please provide your phone number and the verification code.'
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        key = f"{phone}"
        cached_code = cache.get(key)

        if cached_code is None:
            return Response(
                {
                    'error': 'The verification code has expired or was not requested.'
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if str(cached_code) != str(code):
            return Response(
                {'error': 'Incorrect code. Please try again.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        cache.delete(key)

        user = User.objects.filter(phone=phone).first()
        if not user:
            user = User.objects.create_user(phone=phone)

        refresh = RefreshToken.for_user(user)

        logger.info(
            f"User {user.id} authenticated successfully via phone {phone}"
        )

        return Response(
            {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user_id': user.id,
            },
            status=status.HTTP_200_OK,
        )


class ResendCodeView(APIView):
    """
    Resend a 4-digit verification code to a Belarusian phone number.
    """

    @extend_schema(
        tags=["Auth"],
        request=SendCodeRequestSerializer,
        responses={
            201: OpenApiResponse(
                response=None,
                description="Verification code resent successfully."
            ),
            429: OpenApiResponse(
                response=None,
                description="Too many requests."
            ),
        },
        examples=[
            OpenApiExample(
                name="Resend code request",
                value={"phone": "+375291234567"},
                request_only=True,
            )
        ],
    )
    def post(self, request):

        key = create_phone_key(request)

        error_response = check_rate_limit(key)

        if error_response:
            return error_response

        set_code_redis(request)

        return Response(status=status.HTTP_201_CREATED)


class GetProfileView(APIView):
    """
    Retrieve authenticated user's profile.
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["User"],
        responses={
            200: MyUserSerializer,
            401: OpenApiResponse(
                response=None,
                description="Authentication credentials were not provided or invalid."
            ),
        },
    )
    def get(self, request) -> Response:
        user = User.objects.get(id=request.user.id)
        serializer = MyUserSerializer(user)
        return Response(
            {'profile': serializer.data}, status=status.HTTP_200_OK
        )


class UseInviteView(APIView):
    """
    Apply another user's invite code. Can be done only once.
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["User"],
        request=UseInviteCodeRequestSerializer,
        responses={
            200: OpenApiResponse(
                response=None,
                description="Invite code successfully applied."
            ),
            400: OpenApiResponse(
                response=None,
                description="Invalid input or code already used."
            ),
            404: OpenApiResponse(
                response=None,
                description="Invite code not found."
            ),
            401: OpenApiResponse(
                response=None,
                description="Authentication credentials were not provided or invalid."
            ),
        },
        examples=[
            OpenApiExample(
                name="Apply invite code",
                value={"invite_code": "ABC123"},
                request_only=True,
            )
        ],
    )
    def post(self, request) -> Response:
        user = request.user
        invite_code: Optional[str] = request.data.get('invite_code')

        if not invite_code:
            return Response(
                {"error": "Please enter an invite code."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if user.invited_by is not None:
            return Response(
                {
                    "error": "You have already used an invite code. It can only be entered once."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user_invited_by = User.objects.get(
                own_invite_code__invite_code=invite_code
            )
        except User.DoesNotExist:
            return Response(
                {
                    "error": "Invite code not found. Please check the code and try again."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        if user.id == user_invited_by.id:
            return Response(
                {"error": "You cannot use your own invite code."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.invited_by = user_invited_by
        user.save()

        logger.info(
            f"User {user.id} used invite code from user {user_invited_by.id}"
        )

        return Response(
            {"message": "Invite code applied successfully. Welcome!"},
            status=status.HTTP_200_OK,
        )
