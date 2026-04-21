import os
from django.conf import settings


def regenerate():
    """
    Fetch all published pages and write sitemap/sitemap.xml.
    Called after every publish, unpublish, or delete of a published page.
    """
    # Import here to avoid circular imports
    from apps.pages.models import Page

    pages = Page.objects.filter(status=Page.STATUS_PUBLISHED).order_by('-updated_at')

    url_entries = []
    for page in pages:
        loc = f'{settings.SITE_DOMAIN}/published_pages/{page.slug}.html'
        lastmod = page.updated_at.strftime('%Y-%m-%d')
        url_entries.append(
            f'  <url>\n'
            f'    <loc>{loc}</loc>\n'
            f'    <lastmod>{lastmod}</lastmod>\n'
            f'    <changefreq>weekly</changefreq>\n'
            f'    <priority>0.8</priority>\n'
            f'  </url>'
        )

    xml_content = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + '\n'.join(url_entries)
        + '\n</urlset>\n'
    )

    sitemap_dir = settings.SITEMAP_DIR
    sitemap_dir.mkdir(parents=True, exist_ok=True)

    tmp_path = sitemap_dir / 'sitemap.xml.tmp'
    final_path = sitemap_dir / 'sitemap.xml'

    tmp_path.write_text(xml_content, encoding='utf-8')
    os.replace(tmp_path, final_path)  # atomic swap

    return final_path
