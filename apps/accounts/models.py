from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    ROLE_ADMIN = 'admin'
    ROLE_EDITOR = 'editor'
    ROLE_VIEWER = 'viewer'

    ROLE_CHOICES = [
        (ROLE_ADMIN, 'Admin'),
        (ROLE_EDITOR, 'Editor'),
        (ROLE_VIEWER, 'Viewer'),
    ]

    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default=ROLE_VIEWER,
    )

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def is_admin_user(self):
        return self.role == self.ROLE_ADMIN or self.is_superuser

    def is_editor_user(self):
        return self.role in (self.ROLE_ADMIN, self.ROLE_EDITOR) or self.is_superuser

    def get_role_badge_color(self):
        colors = {
            self.ROLE_ADMIN: 'danger',
            self.ROLE_EDITOR: 'primary',
            self.ROLE_VIEWER: 'secondary',
        }
        return colors.get(self.role, 'secondary')
