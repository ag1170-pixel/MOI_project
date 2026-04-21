from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from .models import Page


class EditorRequiredMixin(LoginRequiredMixin):
    """Allows Admin and Editor roles (not Viewer).
    Permission is checked BEFORE the view runs.
    """
    login_url = '/login/'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not request.user.is_editor_user():
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


class AdminRequiredMixin(LoginRequiredMixin):
    """Allows Admin role only."""
    login_url = '/login/'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not request.user.is_admin_user():
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


class AdminOrOwnerMixin(LoginRequiredMixin):
    """Admin can act on any page; Editor can only act on their own pages.
    Viewers are denied. Permission is checked BEFORE the view runs.
    """
    login_url = '/login/'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not request.user.is_editor_user():
            raise PermissionDenied
        if not request.user.is_admin_user():
            page = get_object_or_404(Page, pk=kwargs.get('pk'))
            if page.editor != request.user:
                raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)
