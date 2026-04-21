from django import forms
from django.forms import inlineformset_factory
from django.utils.text import slugify
from .models import Page, RelatedLink


class PageForm(forms.ModelForm):
    class Meta:
        model = Page
        fields = [
            'title', 'slug', 'category', 'description', 'keywords',
            'og_title', 'og_description', 'og_image',
            'canonical_url',
            'body_content', 'featured_image',
            'schema_json',
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Page title',
                'id': 'id_title',
            }),
            'slug': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'url-slug (auto-generated)',
                'id': 'id_slug',
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Meta description (150-160 characters recommended)',
            }),
            'category': forms.Select(attrs={
                'class': 'form-select',
            }),
            'keywords': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'keyword1, keyword2, keyword3',
            }),
            'og_title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Open Graph title (leave blank to use page title)',
            }),
            'og_description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Open Graph description',
            }),
            'og_image': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
            }),
            'canonical_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://example.com/page (leave blank to auto-generate)',
            }),
            'featured_image': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
            }),
            'schema_json': forms.Textarea(attrs={
                'class': 'form-control font-monospace',
                'rows': 8,
                'placeholder': '{\n  "@context": "https://schema.org",\n  "@type": "Article",\n  "headline": "Your title"\n}',
                'spellcheck': 'false',
            }),
        }

    def clean_slug(self):
        slug = self.cleaned_data.get('slug', '').strip()
        if not slug:
            title = self.cleaned_data.get('title', '')
            slug = slugify(title)
        return slug


class RelatedLinkForm(forms.ModelForm):
    class Meta:
        model = RelatedLink
        fields = ['label', 'url', 'open_new_tab', 'order']
        widgets = {
            'label': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Link text'}),
            'url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://'}),
            'open_new_tab': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'order': forms.NumberInput(attrs={'class': 'form-control', 'style': 'width:80px'}),
        }


RelatedLinkFormSet = inlineformset_factory(
    Page,
    RelatedLink,
    form=RelatedLinkForm,
    fields=['label', 'url', 'open_new_tab', 'order'],
    extra=1,
    can_delete=True,
)
