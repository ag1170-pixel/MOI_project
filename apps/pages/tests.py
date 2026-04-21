from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from pathlib import Path
from django.conf import settings
import shutil

from .models import Page, RelatedLink

User = get_user_model()


class PageModelTest(TestCase):
    """Test Page model functionality and database operations."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            role='editor'
        )

    def test_page_creation(self):
        """Test that a page can be created and saved to database."""
        page = Page.objects.create(
            title='Test Page',
            slug='test-page',
            description='Test description',
            editor=self.user
        )
        self.assertEqual(page.title, 'Test Page')
        self.assertEqual(page.slug, 'test-page')
        self.assertEqual(page.status, Page.STATUS_DRAFT)
        self.assertIsNotNone(page.id)

    def test_slug_auto_generation(self):
        """Test that slug is auto-generated from title if not provided."""
        page = Page.objects.create(
            title='Auto Slug Test',
            editor=self.user
        )
        self.assertEqual(page.slug, 'auto-slug-test')

    def test_slug_uniqueness(self):
        """Test that slugs must be unique."""
        Page.objects.create(
            title='Test Page',
            slug='test-page',
            editor=self.user
        )
        with self.assertRaises(Exception):
            Page.objects.create(
                title='Another Page',
                slug='test-page',
                editor=self.user
            )

    def test_page_status_methods(self):
        """Test page status helper methods."""
        page = Page.objects.create(
            title='Status Test',
            slug='status-test',
            status=Page.STATUS_PUBLISHED,
            editor=self.user
        )
        self.assertTrue(page.is_published())

        page.status = Page.STATUS_DRAFT
        page.save()
        self.assertFalse(page.is_published())

    def test_related_links(self):
        """Test that related links can be added to a page."""
        page = Page.objects.create(
            title='Links Test',
            slug='links-test',
            editor=self.user
        )
        link = RelatedLink.objects.create(
            page=page,
            label='Test Link',
            url='https://example.com',
            order=1
        )
        self.assertEqual(page.related_links.count(), 1)
        self.assertEqual(link.label, 'Test Link')

    def test_published_path(self):
        """Test that get_published_path returns correct path."""
        page = Page.objects.create(
            title='Path Test',
            slug='path-test',
            editor=self.user
        )
        expected_path = settings.PUBLISHED_PAGES_DIR / 'path-test.html'
        self.assertEqual(page.get_published_path(), expected_path)


class PageViewTest(TestCase):
    """Test page views and URL routing."""

    def setUp(self):
        self.client = Client()
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='adminpass123',
            role='admin'
        )
        self.editor_user = User.objects.create_user(
            username='editor',
            email='editor@example.com',
            password='editorpass123',
            role='editor'
        )
        self.viewer_user = User.objects.create_user(
            username='viewer',
            email='viewer@example.com',
            password='viewerpass123',
            role='viewer'
        )
        self.page = Page.objects.create(
            title='Test Page',
            slug='test-page',
            editor=self.editor_user
        )

    def test_page_create_get_requires_login(self):
        """Test that page creation requires authentication."""
        response = self.client.get(reverse('pages:create'))
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_page_create_get_as_editor(self):
        """Test that editor can access page creation form."""
        self.client.login(username='editor', password='editorpass123')
        response = self.client.get(reverse('pages:create'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Create New Page')

    def test_page_create_post(self):
        """Test that a page can be created via POST."""
        self.client.login(username='editor', password='editorpass123')
        data = {
            'title': 'New Test Page',
            'slug': 'new-test-page',
            'description': 'Test description',
            'keywords': 'test, page',
            'body_content': '<p>Test content</p>',
            'related_links-TOTAL_FORMS': '0',
            'related_links-INITIAL_FORMS': '0',
            'related_links-MIN_NUM_FORMS': '0',
            'related_links-MAX_NUM_FORMS': '1000',
        }
        response = self.client.post(reverse('pages:create'), data)
        self.assertEqual(response.status_code, 302)  # Redirect after success
        self.assertTrue(Page.objects.filter(slug='new-test-page').exists())

    def test_page_edit_get(self):
        """Test that page edit form loads correctly."""
        self.client.login(username='editor', password='editorpass123')
        response = self.client.get(reverse('pages:edit', args=[self.page.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Page')

    def test_page_edit_post(self):
        """Test that a page can be updated via POST."""
        self.client.login(username='editor', password='editorpass123')
        data = {
            'title': 'Updated Title',
            'slug': 'test-page',
            'description': 'Updated description',
            'body_content': '<p>Updated content</p>',
            'related_links-TOTAL_FORMS': '0',
            'related_links-INITIAL_FORMS': '0',
            'related_links-MIN_NUM_FORMS': '0',
            'related_links-MAX_NUM_FORMS': '1000',
        }
        response = self.client.post(reverse('pages:edit', args=[self.page.pk]), data)
        self.assertEqual(response.status_code, 302)
        self.page.refresh_from_db()
        self.assertEqual(self.page.title, 'Updated Title')

    def test_page_delete_get(self):
        """Test that page delete confirmation page loads."""
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get(reverse('pages:delete', args=[self.page.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Page')

    def test_page_delete_post(self):
        """Test that a page can be deleted."""
        self.client.login(username='admin', password='adminpass123')
        response = self.client.post(reverse('pages:delete', args=[self.page.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Page.objects.filter(pk=self.page.pk).exists())

    def test_page_preview(self):
        """Test that page preview works."""
        self.client.login(username='editor', password='editorpass123')
        response = self.client.get(reverse('pages:preview', args=[self.page.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Page')

    def test_viewer_cannot_create_page(self):
        """Test that viewer role cannot create pages."""
        self.client.login(username='viewer', password='viewerpass123')
        response = self.client.get(reverse('pages:create'))
        self.assertEqual(response.status_code, 403)  # Forbidden

    def test_viewer_cannot_edit_page(self):
        """Test that viewer role cannot edit pages."""
        self.client.login(username='viewer', password='viewerpass123')
        response = self.client.get(reverse('pages:edit', args=[self.page.pk]))
        self.assertEqual(response.status_code, 403)  # Forbidden


class PagePublishTest(TestCase):
    """Test page publishing and static file generation."""

    def setUp(self):
        self.client = Client()
        self.editor_user = User.objects.create_user(
            username='editor',
            email='editor@example.com',
            password='editorpass123',
            role='editor'
        )
        self.page = Page.objects.create(
            title='Publish Test',
            slug='publish-test',
            body_content='<p>Test content</p>',
            editor=self.editor_user
        )
        # Ensure directories exist
        settings.PUBLISHED_PAGES_DIR.mkdir(parents=True, exist_ok=True)
        settings.SITEMAP_DIR.mkdir(parents=True, exist_ok=True)

    def tearDown(self):
        # Clean up generated files
        if settings.PUBLISHED_PAGES_DIR.exists():
            shutil.rmtree(settings.PUBLISHED_PAGES_DIR, ignore_errors=True)
        if settings.SITEMAP_DIR.exists():
            shutil.rmtree(settings.SITEMAP_DIR, ignore_errors=True)

    def test_page_publish_creates_static_file(self):
        """Test that publishing a page creates a static HTML file."""
        self.client.login(username='editor', password='editorpass123')
        response = self.client.post(reverse('pages:publish', args=[self.page.pk]))
        self.assertEqual(response.status_code, 302)

        static_file = settings.PUBLISHED_PAGES_DIR / 'publish-test.html'
        self.assertTrue(static_file.exists())

        self.page.refresh_from_db()
        self.assertEqual(self.page.status, Page.STATUS_PUBLISHED)
        self.assertIsNotNone(self.page.published_at)

    def test_page_unpublish_removes_static_file(self):
        """Test that unpublishing removes the static file."""
        # First publish
        self.client.login(username='editor', password='editorpass123')
        self.client.post(reverse('pages:publish', args=[self.page.pk]))

        # Then unpublish
        response = self.client.post(reverse('pages:unpublish', args=[self.page.pk]))
        self.assertEqual(response.status_code, 302)

        static_file = settings.PUBLISHED_PAGES_DIR / 'publish-test.html'
        self.assertFalse(static_file.exists())

        self.page.refresh_from_db()
        self.assertEqual(self.page.status, Page.STATUS_DRAFT)
        self.assertIsNone(self.page.published_at)

    def test_sitemap_generation(self):
        """Test that sitemap is generated after publishing."""
        self.client.login(username='editor', password='editorpass123')
        self.client.post(reverse('pages:publish', args=[self.page.pk]))

        sitemap_file = settings.SITEMAP_DIR / 'sitemap.xml'
        self.assertTrue(sitemap_file.exists())

        content = sitemap_file.read_text(encoding='utf-8')
        self.assertIn('publish-test.html', content)
        self.assertIn('<?xml version="1.0"', content)


class URLRoutingTest(TestCase):
    """Test URL routing configuration."""

    def test_page_create_url(self):
        """Test that page create URL resolves correctly."""
        url = reverse('pages:create')
        self.assertEqual(url, '/pages/create/')

    def test_page_edit_url(self):
        """Test that page edit URL resolves correctly."""
        url = reverse('pages:edit', args=[1])
        self.assertEqual(url, '/pages/1/edit/')

    def test_page_detail_url(self):
        """Test that page detail URL resolves correctly."""
        url = reverse('pages:detail', args=[1])
        self.assertEqual(url, '/pages/1/detail/')

    def test_page_delete_url(self):
        """Test that page delete URL resolves correctly."""
        url = reverse('pages:delete', args=[1])
        self.assertEqual(url, '/pages/1/delete/')

    def test_page_preview_url(self):
        """Test that page preview URL resolves correctly."""
        url = reverse('pages:preview', args=[1])
        self.assertEqual(url, '/pages/1/preview/')

    def test_page_publish_url(self):
        """Test that page publish URL resolves correctly."""
        url = reverse('pages:publish', args=[1])
        self.assertEqual(url, '/pages/1/publish/')

    def test_page_unpublish_url(self):
        """Test that page unpublish URL resolves correctly."""
        url = reverse('pages:unpublish', args=[1])
        self.assertEqual(url, '/pages/1/unpublish/')


class DatabaseFlowTest(TestCase):
    """Test complete database flow for page lifecycle."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            role='editor'
        )

    def test_complete_page_lifecycle(self):
        """Test complete page lifecycle: create -> edit -> publish -> unpublish -> delete."""
        # 1. Create page
        page = Page.objects.create(
            title='Lifecycle Test',
            slug='lifecycle-test',
            editor=self.user
        )
        self.assertEqual(page.status, Page.STATUS_DRAFT)
        self.assertIsNotNone(page.id)

        # 2. Edit page
        page.title = 'Updated Lifecycle Test'
        page.body_content = '<p>New content</p>'
        page.save()
        page.refresh_from_db()
        self.assertEqual(page.title, 'Updated Lifecycle Test')

        # 3. Publish page
        page.status = Page.STATUS_PUBLISHED
        page.published_at = timezone.now()
        page.save()
        page.refresh_from_db()
        self.assertTrue(page.is_published())
        self.assertIsNotNone(page.published_at)

        # 4. Unpublish page
        page.status = Page.STATUS_DRAFT
        page.published_at = None
        page.save()
        page.refresh_from_db()
        self.assertFalse(page.is_published())
        self.assertIsNone(page.published_at)

        # 5. Delete page
        page_id = page.id
        page.delete()
        self.assertFalse(Page.objects.filter(id=page_id).exists())

    def test_related_links_flow(self):
        """Test that related links are properly associated with pages."""
        page = Page.objects.create(
            title='Links Flow Test',
            slug='links-flow-test',
            editor=self.user
        )

        # Add links
        link1 = RelatedLink.objects.create(
            page=page,
            label='Link 1',
            url='https://example.com/1',
            order=1
        )
        link2 = RelatedLink.objects.create(
            page=page,
            label='Link 2',
            url='https://example.com/2',
            order=2
        )

        self.assertEqual(page.related_links.count(), 2)

        # Delete page - links should be cascade deleted
        page.delete()
        self.assertEqual(RelatedLink.objects.count(), 0)

    def test_editor_association(self):
        """Test that pages are correctly associated with editors."""
        page = Page.objects.create(
            title='Editor Test',
            slug='editor-test',
            editor=self.user
        )

        self.assertEqual(page.editor, self.user)
        self.assertEqual(self.user.pages_created.count(), 1)

        # Change editor
        new_user = User.objects.create_user(
            username='newuser',
            email='new@example.com',
            password='newpass123',
            role='editor'
        )
        page.editor = new_user
        page.save()

        self.assertEqual(page.editor, new_user)
        self.assertEqual(self.user.pages_created.count(), 0)
        self.assertEqual(new_user.pages_created.count(), 1)


class IntegrationTest(TestCase):
    """Integration tests for the complete page workflow."""

    def setUp(self):
        self.client = Client()
        self.editor = User.objects.create_user(
            username='editor',
            email='editor@example.com',
            password='editorpass123',
            role='editor'
        )
        settings.PUBLISHED_PAGES_DIR.mkdir(parents=True, exist_ok=True)
        settings.SITEMAP_DIR.mkdir(parents=True, exist_ok=True)

    def tearDown(self):
        if settings.PUBLISHED_PAGES_DIR.exists():
            shutil.rmtree(settings.PUBLISHED_PAGES_DIR, ignore_errors=True)
        if settings.SITEMAP_DIR.exists():
            shutil.rmtree(settings.SITEMAP_DIR, ignore_errors=True)

    def test_full_workflow_via_http(self):
        """Test complete workflow via HTTP requests."""
        # Login
        self.client.login(username='editor', password='editorpass123')

        # Create page
        create_data = {
            'title': 'Integration Test Page',
            'slug': 'integration-test',
            'description': 'Integration test description',
            'body_content': '<p>Integration test content</p>',
            'related_links-TOTAL_FORMS': '0',
            'related_links-INITIAL_FORMS': '0',
            'related_links-MIN_NUM_FORMS': '0',
            'related_links-MAX_NUM_FORMS': '1000',
        }
        response = self.client.post(reverse('pages:create'), create_data)
        self.assertEqual(response.status_code, 302)

        # Get the created page
        page = Page.objects.get(slug='integration-test')
        self.assertIsNotNone(page)

        # Edit page
        edit_data = {
            'title': 'Updated Integration Test',
            'slug': 'integration-test',
            'description': 'Updated description',
            'body_content': '<p>Updated content</p>',
            'related_links-TOTAL_FORMS': '0',
            'related_links-INITIAL_FORMS': '0',
            'related_links-MIN_NUM_FORMS': '0',
            'related_links-MAX_NUM_FORMS': '1000',
        }
        response = self.client.post(reverse('pages:edit', args=[page.pk]), edit_data)
        self.assertEqual(response.status_code, 302)
        page.refresh_from_db()
        self.assertEqual(page.title, 'Updated Integration Test')

        # Publish page
        response = self.client.post(reverse('pages:publish', args=[page.pk]))
        self.assertEqual(response.status_code, 302)
        page.refresh_from_db()
        self.assertTrue(page.is_published())

        # Check static file exists
        static_file = settings.PUBLISHED_PAGES_DIR / 'integration-test.html'
        self.assertTrue(static_file.exists())

        # Unpublish page
        response = self.client.post(reverse('pages:unpublish', args=[page.pk]))
        self.assertEqual(response.status_code, 302)
        page.refresh_from_db()
        self.assertFalse(page.is_published())

        # Delete page
        response = self.client.post(reverse('pages:delete', args=[page.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Page.objects.filter(slug='integration-test').exists())
