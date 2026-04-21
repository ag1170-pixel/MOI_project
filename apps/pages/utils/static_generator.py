import os
from django.template.loader import render_to_string
from django.conf import settings


def _get_absolute_media_url(file_field):
    """Return absolute URL for a media file field, or empty string."""
    if file_field and file_field.name:
        return f'{settings.SITE_DOMAIN}{settings.MEDIA_URL}{file_field.name}'
    return ''


def generate(page):
    """
    Render the page using base_layout.html and write a static .html file
    to published_pages/{slug}.html. Returns the output Path.
    """
    canonical = page.canonical_url or f'{settings.SITE_DOMAIN}/published_pages/{page.slug}.html'

    context = {
        'page': page,
        'related_links': page.related_links.all(),
        'canonical_url': canonical,
        'og_image_url': _get_absolute_media_url(page.og_image),
        'featured_image_url': _get_absolute_media_url(page.featured_image),
        'site_domain': settings.SITE_DOMAIN,
    }

    html = render_to_string('base_layout.html', context)

    out_dir = settings.PUBLISHED_PAGES_DIR
    out_dir.mkdir(parents=True, exist_ok=True)

    tmp_path = out_dir / f'{page.slug}.html.tmp'
    final_path = out_dir / f'{page.slug}.html'

    tmp_path.write_text(html, encoding='utf-8')
    os.replace(tmp_path, final_path)  # atomic swap

    return final_path


def delete_static_file(slug):
    """Delete the static .html file for the given slug if it exists."""
    path = settings.PUBLISHED_PAGES_DIR / f'{slug}.html'
    if path.exists():
        path.unlink()
