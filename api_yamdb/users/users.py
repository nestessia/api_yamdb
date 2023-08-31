from django.contrib.auth.models import AbstractUser
from django.db import models


USER = 'user'
ADMIN = 'admin'
MODERATOR = 'moderator'

ROLE_CHOICES = [
    (USER, USER),
    (ADMIN, ADMIN),
    (MODERATOR, MODERATOR),
]


class User(AbstractUser):
    bio = models.CharField(max_length=150, blank=True)
    role = models.CharField(max_length=150,
                            blank=True,
                            choices=ROLE_CHOICES,
                            default=USER,)
    email = models.EmailField(max_length=254, unique=True)
    first_name = models.CharField(max_length=150,
                                  blank=True)
    last_name = models.CharField(max_length=150,
                                 blank=True)
    confirmation_code = models.CharField(
        'Код подтверждения',
        max_length=100,
        null=True
    )

    @property
    def is_user(self):
        return self.role == USER

    @property
    def is_admin(self):
        return self.role == ADMIN

    @property
    def is_moderator(self):
        return self.role == MODERATOR

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "пользователи"
        ordering = ("id",)
