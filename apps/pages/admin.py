from django.contrib import admin
from .models import Page, RelatedLink, SiteSettings


class RelatedLinkInline(admin.TabularInline):
    model = RelatedLink
    extra = 1
    fields = ['label', 'url', 'open_new_tab', 'order']


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display  = ['title', 'slug', 'category', 'status', 'editor', 'published_at', 'updated_at']
    list_filter   = ['status', 'category', 'created_at']
    search_fields = ['title', 'slug', 'description', 'keywords']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['created_at', 'updated_at', 'published_at']
    inlines = [RelatedLinkInline]
    fieldsets = (
        ('Basic Info', {
            'fields': ('title', 'slug', 'category', 'description', 'keywords', 'status', 'editor')
        }),
        ('Open Graph', {
            'fields': ('og_title', 'og_description', 'og_image'),
            'classes': ('collapse',),
        }),
        ('Content', {
            'fields': ('body_content', 'featured_image', 'canonical_url'),
        }),
        ('Schema', {
            'fields': ('schema_json',),
            'classes': ('collapse',),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'published_at'),
            'classes': ('collapse',),
        }),
    )


@admin.register(RelatedLink)
class RelatedLinkAdmin(admin.ModelAdmin):
    list_display  = ['label', 'url', 'page', 'open_new_tab', 'order']
    list_filter   = ['open_new_tab']
    search_fields = ['label', 'url']


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Hero Section', {
            'fields': (
                'hero_image',
                'hero_title_line1', 'hero_title_line2',
                'hero_subtitle',
                'hero_cta_text', 'hero_cta_url',
            ),
            'description': 'Controls the home page hero banner.',
        }),
        ('Site Identity', {
            'fields': ('site_name', 'tagline', 'pages_per_section'),
        }),
    )

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False
