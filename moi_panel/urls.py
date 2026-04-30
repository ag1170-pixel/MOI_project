from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse, HttpResponsePermanentRedirect
from django.shortcuts import render

# Custom error handlers
def handler403(request, exception=None):
    return render(request, '403.html', status=403)

def handler404(request, exception=None):
    return render(request, '404.html', status=404)


def sitemap_view(request):
    """Serve sitemap.xml — create an empty one if it doesn't exist yet."""
    sitemap_path = settings.SITEMAP_DIR / 'sitemap.xml'
    if not sitemap_path.exists():
        from apps.pages.utils import sitemap_generator
        sitemap_generator.regenerate()
    content = sitemap_path.read_text(encoding='utf-8')
    return HttpResponse(content, content_type='application/xml')


def article_view(request, slug):
    """
    Serve a published article at the clean URL /articles/<slug>.

    Priority:
    1. Serve the cached static HTML file if it exists (fast path).
    2. If the file is missing (e.g. published via Django admin), generate it
       on-the-fly from the DB and cache it for next time.
    3. If generation fails for any reason, render dynamically without caching.
    """
    page_path = settings.PUBLISHED_PAGES_DIR / f'{slug}.html'

    # Fast path — static file already exists
    if page_path.exists():
        return HttpResponse(page_path.read_text(encoding='utf-8'), content_type='text/html')

    # DB fallback
    from apps.pages.models import Page
    from django.http import Http404
    from django.template.loader import render_to_string
    from apps.pages.utils.static_generator import _get_absolute_media_url, generate

    try:
        page = Page.objects.get(slug=slug, status=Page.STATUS_PUBLISHED)
    except Page.DoesNotExist:
        raise Http404('Article not found')

    # Try to generate and cache the static file
    try:
        generate(page)
        if page_path.exists():
            return HttpResponse(page_path.read_text(encoding='utf-8'), content_type='text/html')
    except Exception:
        pass  # fall through to dynamic render

    # Pure dynamic render (no caching)
    canonical = page.canonical_url or f'{settings.SITE_DOMAIN}/articles/{slug}'
    context = {
        'page': page,
        'related_links': page.related_links.all(),
        'canonical_url': canonical,
        'og_image_url': _get_absolute_media_url(page.og_image),
        'featured_image_url': _get_absolute_media_url(page.featured_image),
        'site_domain': settings.SITE_DOMAIN,
    }
    html = render_to_string('base_layout.html', context)
    return HttpResponse(html, content_type='text/html')


def legacy_article_redirect(request, slug):
    """301-redirect old /published_pages/<slug>.html → /articles/<slug>."""
    return HttpResponsePermanentRedirect(f'/articles/{slug}')


urlpatterns = [
    path('admin/', admin.site.urls),
    path('ckeditor5/', include('django_ckeditor_5.urls')),

    # App URL includes
    path('', include('apps.public.urls')),
    path('', include('apps.accounts.urls')),
    path('dashboard/', include('apps.dashboard.urls')),
    path('pages/', include('apps.pages.urls')),

    # Clean article URLs  (e.g. /articles/vaishali-district-map)
    path('articles/<slug:slug>', article_view, name='article'),

    # Legacy redirect — keeps old bookmarks/links working
    path('published_pages/<slug:slug>.html', legacy_article_redirect, name='published_page'),

    # Sitemap
    path('sitemap.xml', sitemap_view, name='sitemap'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Wire up custom error pages (Django looks for these names at the module level)
# handler403 and handler404 are already defined as functions above
