from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
import datetime
# Create your models here.
class Users(AbstractUser):
    password = models.CharField(_("password"), max_length=255)
    is_verified = models.BooleanField(_("is_verified"), default=False)
    verification_code = models.CharField(_("verification_code"), max_length=6, blank=True, null=True)
    balance = models.PositiveIntegerField(_("balance"), default=0)
    created_at = models.DateTimeField(_("created_at"), auto_now_add=True, )
    updated_at = models.DateTimeField(_("updated_at"), auto_now=True)

    def __str__(self):
        return "User: %s Regisrated was: %s" %  (self.username, self.created_at)

    class Meta(AbstractUser.Meta):
        indexes = [models.Index(fields=["is_active"])]
