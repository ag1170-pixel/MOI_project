from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.utils import timezone
from django.views import View

from .models import Page
from .forms import PageForm, RelatedLinkFormSet
from .mixins import EditorRequiredMixin, AdminOrOwnerMixin
from .utils import static_generator, sitemap_generator


class PageCreateView(EditorRequiredMixin, View):
    template_name = 'pages/page_form.html'

    def get(self, request):
        form = PageForm()
        formset = RelatedLinkFormSet()
        return render(request, self.template_name, {
            'form': form,
            'formset': formset,
            'page_title': 'Create New Page',
            'is_create': True,
        })

    def post(self, request):
        form = PageForm(request.POST, request.FILES)
        formset = RelatedLinkFormSet(request.POST, request.FILES)

        if form.is_valid() and formset.is_valid():
            page = form.save(commit=False)
            page.editor = request.user
            page.save()
            formset.instance = page
            formset.save()
            messages.success(request, f'Page "{page.title}" saved as draft.')
            return redirect('dashboard:index')

        return render(request, self.template_name, {
            'form': form,
            'formset': formset,
            'page_title': 'Create New Page',
            'is_create': True,
        })


class PageEditView(EditorRequiredMixin, View):
    template_name = 'pages/page_form.html'

    def get_page(self, request, pk):
        page = get_object_or_404(Page, pk=pk)
        if not request.user.is_admin_user() and page.editor != request.user:
            raise PermissionDenied
        return page

    def get(self, request, pk):
        page = self.get_page(request, pk)
        form = PageForm(instance=page)
        formset = RelatedLinkFormSet(instance=page)
        return render(request, self.template_name, {
            'form': form,
            'formset': formset,
            'page': page,
            'page_title': f'Edit: {page.title}',
            'is_create': False,
        })

    def post(self, request, pk):
        page = self.get_page(request, pk)
        original_slug = page.slug
        was_published = page.is_published()

        form = PageForm(request.POST, request.FILES, instance=page)
        formset = RelatedLinkFormSet(request.POST, request.FILES, instance=page)

        if form.is_valid() and formset.is_valid():
            page = form.save(commit=False)
            if not page.editor:
                page.editor = request.user
            page.save()
            formset.save()

            # Handle slug rename for published pages
            if was_published and page.slug != original_slug:
                static_generator.delete_static_file(original_slug)
                static_generator.generate(page)
                sitemap_generator.regenerate()

            messages.success(request, f'Page "{page.title}" updated successfully.')
            return redirect('dashboard:index')

        return render(request, self.template_name, {
            'form': form,
            'formset': formset,
            'page': page,
            'page_title': f'Edit: {page.title}',
            'is_create': False,
        })


class PageDetailView(LoginRequiredMixin, View):
    login_url = '/login/'
    template_name = 'pages/page_detail.html'

    def get(self, request, pk):
        page = get_object_or_404(Page, pk=pk)
        return render(request, self.template_name, {'page': page})


class PageDeleteView(AdminOrOwnerMixin, View):
    template_name = 'pages/page_confirm_delete.html'

    def get(self, request, pk):
        page = get_object_or_404(Page, pk=pk)
        return render(request, self.template_name, {'page': page})

    def post(self, request, pk):
        page = get_object_or_404(Page, pk=pk)
        title = page.title
        was_published = page.is_published()
        slug = page.slug

        if was_published:
            static_generator.delete_static_file(slug)

        page.delete()

        if was_published:
            sitemap_generator.regenerate()

        messages.success(request, f'Page "{title}" has been deleted.')
        return redirect('dashboard:index')


class PagePreviewView(LoginRequiredMixin, View):
    login_url = '/login/'

    def get(self, request, pk):
        page = get_object_or_404(Page, pk=pk)
        from django.conf import settings

        canonical = page.canonical_url or f'{settings.SITE_DOMAIN}/published_pages/{page.slug}.html'

        context = {
            'page': page,
            'related_links': page.related_links.all(),
            'canonical_url': canonical,
            'og_image_url': _get_media_url(page.og_image),
            'featured_image_url': _get_media_url(page.featured_image),
            'site_domain': settings.SITE_DOMAIN,
            'is_preview': True,
        }
        html = render_to_string('base_layout.html', context, request=request)
        return HttpResponse(html)


class PagePublishView(EditorRequiredMixin, View):
    def post(self, request, pk):
        page = get_object_or_404(Page, pk=pk)

        if not request.user.is_admin_user() and page.editor != request.user:
            raise PermissionDenied

        if not page.title or not page.slug:
            messages.error(request, 'Page must have a title and slug before publishing.')
            return redirect('pages:edit', pk=pk)

        try:
            static_generator.generate(page)
            page.status = Page.STATUS_PUBLISHED
            page.published_at = timezone.now()
            page.save(update_fields=['status', 'published_at'])
            sitemap_generator.regenerate()
            messages.success(request, f'Page "{page.title}" is now live! Static file generated.')
        except Exception as e:
            messages.error(request, f'Publish failed: {e}')

        return redirect('dashboard:index')


class PageUnpublishView(EditorRequiredMixin, View):
    def post(self, request, pk):
        page = get_object_or_404(Page, pk=pk)

        if not request.user.is_admin_user() and page.editor != request.user:
            raise PermissionDenied

        static_generator.delete_static_file(page.slug)
        page.status = Page.STATUS_DRAFT
        page.published_at = None
        page.save(update_fields=['status', 'published_at'])
        sitemap_generator.regenerate()
        messages.info(request, f'Page "{page.title}" has been unpublished.')
        return redirect('dashboard:index')


def _get_media_url(file_field):
    from django.conf import settings
    if file_field and file_field.name:
        return f'{settings.SITE_DOMAIN}{settings.MEDIA_URL}{file_field.name}'
    return ''
