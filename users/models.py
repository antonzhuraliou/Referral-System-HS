from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from django.db import transaction


class MyUserManager(BaseUserManager):
    def create_user(self, phone, **extra_fields):
        """
        Creates and saves a User with the given phone and create a InviteCode instance with
        a unique invite code.
        """

        if not phone:
            raise ValueError("Users must have a phone number")

        with transaction.atomic():
            from users.utils import generate_unique_invite_code
            invite_code = generate_unique_invite_code()

            user = self.model(phone=phone, **extra_fields)
            user.set_unusable_password()
            user.save()

            InviteCode.objects.create(invite_code=invite_code, owner=user)

            return user


    def create_superuser(self, phone, **extra_fields):
        """
        Creates and saves a superuser with the given phone.
        """

        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(phone, **extra_fields)



class MyUser(AbstractBaseUser, PermissionsMixin):
    """
    Custom user model that uses phone number as the unique identifier.
    Each user has a unique invite code and may be invited by another user.
    """

    phone = models.CharField(max_length=15,unique=True,db_index=True)
    invited_by = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='referrals')

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = MyUserManager()

    USERNAME_FIELD = "phone"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.phone


class InviteCode(models.Model):
    """
    Model representing a unique invite code used to invite new users.
    """

    invite_code = models.CharField(max_length=6, unique=True)
    owner = models.OneToOneField('MyUser', on_delete=models.CASCADE, related_name='own_invite_code', null=True)

    def __str__(self):
        return self.invite_code
