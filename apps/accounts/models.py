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

    def save(self, *args, **kwargs):
        # Django superusers must have at least the admin role in our panel.
        # This prevents a superuser from accidentally locking themselves out,
        # and ensures role is always the single source of truth for RBAC.
        if self.is_superuser and self.role != self.ROLE_ADMIN:
            self.role = self.ROLE_ADMIN
        super().save(*args, **kwargs)

    def is_admin_user(self):
        """Returns True only when the user's role is 'admin'.
        is_superuser is intentionally NOT checked here — role is the
        single source of truth so that changing a role to 'viewer' is
        immediately respected everywhere."""
        return self.role == self.ROLE_ADMIN

    def is_editor_user(self):
        """Returns True for admin and editor roles (not viewer)."""
        return self.role in (self.ROLE_ADMIN, self.ROLE_EDITOR)

    def get_role_badge_color(self):
        colors = {
            self.ROLE_ADMIN: 'danger',
            self.ROLE_EDITOR: 'primary',
            self.ROLE_VIEWER: 'secondary',
        }
        return colors.get(self.role, 'secondary')
