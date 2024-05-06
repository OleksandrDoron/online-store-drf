from django.contrib.auth.models import AbstractUser
from django.db import models
from rest_framework.exceptions import ValidationError


class User(AbstractUser):
    balance = models.DecimalField(
        default=0.00,
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Balance",
    )
    groups = models.ManyToManyField("Group", related_name="user_groups")

    class Meta:
        swappable = "AUTH_USER_MODEL"

    def save(self, *args, **kwargs):
        if self.balance < 0:
            raise ValidationError("The balance cannot be negative.")
        super().save(*args, **kwargs)


class Group(models.Model):
    name = models.CharField(max_length=50, unique=True)
