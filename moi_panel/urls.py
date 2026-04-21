from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse


def sitemap_view(request):
    """Serve sitemap.xml — create an empty one if it doesn't exist yet."""
    sitemap_path = settings.SITEMAP_DIR / 'sitemap.xml'
    if not sitemap_path.exists():
        # Auto-generate (empty or with existing published pages)
        from apps.pages.utils import sitemap_generator
        sitemap_generator.regenerate()
    content = sitemap_path.read_text(encoding='utf-8')
    return HttpResponse(content, content_type='application/xml')


def published_page_view(request, slug):
    """Serve published static HTML files."""
    page_path = settings.PUBLISHED_PAGES_DIR / f'{slug}.html'
    if not page_path.exists():
        from django.http import Http404
        raise Http404("Published page not found")
    content = page_path.read_text(encoding='utf-8')
    return HttpResponse(content, content_type='text/html')


urlpatterns = [
    path('admin/', admin.site.urls),
    path('ckeditor5/', include('django_ckeditor_5.urls')),

    # App URL includes
    path('', include('apps.public.urls')),
    path('', include('apps.accounts.urls')),
    path('dashboard/', include('apps.dashboard.urls')),
    path('pages/', include('apps.pages.urls')),

    # Published pages — serve static HTML files
    path('published_pages/<slug:slug>.html', published_page_view, name='published_page'),

    # Sitemap — served dynamically, creates empty one if missing
    path('sitemap.xml', sitemap_view, name='sitemap'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
