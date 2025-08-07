from rest_framework import serializers

from .models import InviteCode, MyUser


class SendCodeRequestSerializer(serializers.Serializer):
    phone = serializers.CharField(
        max_length=13,
    )


class VerifyCodeRequestSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=13)
    code = serializers.CharField(max_length=4)


class TokenResponseSerializer(serializers.Serializer):
    refresh = serializers.CharField(read_only=True)
    access = serializers.CharField(read_only=True)
    user_id = serializers.IntegerField(read_only=True)


class UseInviteCodeRequestSerializer(serializers.Serializer):
    invite_code = serializers.CharField(max_length=20)


class InviteCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = InviteCode
        fields = ['invite_code']


class UserShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = MyUser
        fields = ['id', 'phone']


class UserInviteCodeSerializer(serializers.ModelSerializer):
    invite_code = serializers.CharField(source='own_invite_code.invite_code')

    class Meta:
        model = MyUser
        fields = ['invite_code']


class MyUserSerializer(serializers.ModelSerializer):
    referrals = UserShortSerializer(many=True)
    invited_by = UserInviteCodeSerializer()
    own_invite_code = serializers.CharField(
        source='own_invite_code.invite_code'
    )

    class Meta:
        model = MyUser
        fields = ['id', 'phone', 'own_invite_code', 'invited_by', 'referrals']
