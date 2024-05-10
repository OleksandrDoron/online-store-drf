from django.contrib.auth.models import AbstractUser
from django.db import models
from rest_framework.exceptions import ValidationError


class User(AbstractUser):
    ADMIN = 1
    CLIENT = 2
    ROLE_CHOICES = (
        (ADMIN, "Administrator"),
        (CLIENT, "Client"),
    )
    balance = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=0,
    )
    role = models.PositiveIntegerField(
        choices=ROLE_CHOICES, blank=True, null=True, default=CLIENT
    )

    @property
    def is_admin(self):
        return self.role == self.ADMIN

    @property
    def is_client(self):
        return self.role == self.CLIENT

    def save(self, *args, **kwargs):
        if self.balance < 0:
            raise ValidationError("Баланс не может быть отрицательным")
        super().save(*args, **kwargs)
