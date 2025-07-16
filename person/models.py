from django.db import models
from django.contrib.auth.models import AbstractUser
import datetime
# Create your models here.
class Users(AbstractUser):
    is_verified = models.BooleanField(default=False)
    verification_code = models.CharField(max_length=6, blank=True, null=True)
    balance = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True, )
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "User: %s Regisrated was: %s" %  (self.username, self.created_at)

    class Meta(AbstractUser.Meta):
        indexes = [models.Index(fields=["is_active"])]
