from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
import datetime


# Create your models here.
class Users(AbstractUser):
    """
       Here is a new default table for the user's registration for project.
           Here, we add new fields for the user registration.
       :param is_activated: bool. This is activation a new account after the \
           authentication. By link from the email of User, we make authentication.
       :param is_sent: bool. This is email's message, we sent to \
           the single user. His is the new user from the registration.
       :param username: str. Max length is 150 characters. This is unique\
           name of user
       :param first_name: str or None. Max length is 150 characters.
       :param last_name: str or None. Max length is 150 characters.
       :param last_login: str or None, format date-time.
       :param email: str. User email. Max length is 320 characters.
       :param is_staff: bool. Designates whether the user can log into \
           this admin site.
       :param is_active: bool. Designates whether this user should be treated \
           as active.
       :param is_superuser: bool. Designates that this user has \
           all permissions. He is the admin site and only one.
       :param  password: str. Max length of characters is 128 and min is 3.
       """

    password = models.CharField(_("password"), max_length=255)
    is_sent = models.BooleanField(
        default=False,
        verbose_name="Message was sent",
        help_text=_(
            "Part is registration of new user.It is message sending \
to user's email. User indicates his email at the registrations moment."
        ),
    )
    is_verified = models.BooleanField(_("is_verified"), default=False)
    verification_code = models.CharField(
        _("verification_code"), max_length=6, blank=True, null=True
    )
    balance = models.PositiveIntegerField(_("balance"), default=0)
    created_at = models.DateTimeField(
        _("created_at"),
        auto_now_add=True,
    )
    updated_at = models.DateTimeField(_("updated_at"), auto_now=True)

    def __str__(self):
        return "User: %s Regisrated was: %s" % (self.username, self.created_at)

    class Meta(AbstractUser.Meta):
        indexes = [models.Index(fields=["is_active"])]
