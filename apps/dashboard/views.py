from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from apps.pages.models import Page


class DashboardView(LoginRequiredMixin, ListView):
    model = Page
    template_name = 'dashboard/index.html'
    context_object_name = 'pages'
    login_url = '/login/'
    paginate_by = 20

    def get_queryset(self):
        return Page.objects.select_related('editor').order_by('-updated_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        qs = Page.objects.all()
        context['total_count'] = qs.count()
        context['draft_count'] = qs.filter(status=Page.STATUS_DRAFT).count()
        context['published_count'] = qs.filter(status=Page.STATUS_PUBLISHED).count()
        return context
