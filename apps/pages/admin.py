from django.contrib import admin
from .models import Page, RelatedLink


class RelatedLinkInline(admin.TabularInline):
    model = RelatedLink
    extra = 1
    fields = ['label', 'url', 'open_new_tab', 'order']


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug', 'category', 'status', 'editor', 'created_at', 'updated_at', 'published_at']
    list_filter = ['status', 'category', 'created_at']
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
    list_display = ['label', 'url', 'page', 'open_new_tab', 'order']
    list_filter = ['open_new_tab']
    search_fields = ['label', 'url']
