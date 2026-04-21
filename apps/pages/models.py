from django.db import models
from django.utils.text import slugify
from django.conf import settings
from django_ckeditor_5.fields import CKEditor5Field


class Page(models.Model):
    STATUS_DRAFT = 'draft'
    STATUS_PUBLISHED = 'published'
    STATUS_CHOICES = [
        (STATUS_DRAFT, 'Draft'),
        (STATUS_PUBLISHED, 'Published'),
    ]

    CATEGORY_GENERAL = 'general'
    CATEGORY_MAPS = 'maps'
    CATEGORY_MY_INDIA = 'my_india'
    CATEGORY_CHOICES = [
        (CATEGORY_GENERAL, 'General'),
        (CATEGORY_MAPS, 'Maps'),
        (CATEGORY_MY_INDIA, 'My India'),
    ]

    # Core fields
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, help_text='Meta description for SEO')
    keywords = models.CharField(max_length=500, blank=True, help_text='Comma-separated SEO keywords')
    slug = models.SlugField(max_length=255, unique=True, help_text='Unique URL path (auto-generated from title if left blank)')
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default=CATEGORY_GENERAL,
        help_text='Which section this page belongs to (used for nav tabs)',
    )

    # Open Graph
    og_title = models.CharField(max_length=255, blank=True, help_text='Leave blank to use page title')
    og_description = models.TextField(blank=True, help_text='Leave blank to use description')
    og_image = models.ImageField(upload_to='uploads/og_images/', blank=True, null=True)

    # Canonical
    canonical_url = models.URLField(blank=True, help_text='Leave blank to auto-generate from slug')

    # Content
    body_content = CKEditor5Field(blank=True, config_name='extends')
    featured_image = models.ImageField(upload_to='uploads/featured_images/', blank=True, null=True)

    # Structured data
    schema_json = models.TextField(blank=True, help_text='Paste raw JSON-LD structured data here')

    # Status
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_DRAFT)

    # Tracking
    editor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='pages_created',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-updated_at']
        verbose_name = 'Page'
        verbose_name_plural = 'Pages'

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_published_path(self):
        return settings.PUBLISHED_PAGES_DIR / f'{self.slug}.html'

    def is_published(self):
        return self.status == self.STATUS_PUBLISHED


class RelatedLink(models.Model):
    page = models.ForeignKey(Page, on_delete=models.CASCADE, related_name='related_links')
    label = models.CharField(max_length=255)
    url = models.URLField()
    open_new_tab = models.BooleanField(default=False)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f'{self.label} → {self.url}'
