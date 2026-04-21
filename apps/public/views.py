from django.shortcuts import render
from django.views import View
from django.core.paginator import Paginator
from apps.pages.models import Page


def _published_pages(category=None):
    """Return published pages, optionally filtered by category."""
    qs = Page.objects.filter(status=Page.STATUS_PUBLISHED).select_related('editor')
    if category:
        qs = qs.filter(category=category)
    return qs.order_by('-published_at')


class HomeView(View):
    template_name = 'public/home.html'

    def get(self, request):
        all_pages = _published_pages()
        paginator = Paginator(all_pages, 9)
        page_number = request.GET.get('page', 1)
        page_obj = paginator.get_page(page_number)

        # Latest 3 per section for the section previews
        maps_pages = _published_pages(category=Page.CATEGORY_MAPS)[:3]
        my_india_pages = _published_pages(category=Page.CATEGORY_MY_INDIA)[:3]

        return render(request, self.template_name, {
            'page_obj': page_obj,
            'maps_pages': maps_pages,
            'my_india_pages': my_india_pages,
            'active_tab': 'home',
            'page_title': 'Maps of India — Explore India',
            'total_published': all_pages.count(),
        })


class MapsView(View):
    template_name = 'public/maps.html'

    def get(self, request):
        maps_pages = _published_pages(category=Page.CATEGORY_MAPS)
        paginator = Paginator(maps_pages, 9)
        page_number = request.GET.get('page', 1)
        page_obj = paginator.get_page(page_number)

        return render(request, self.template_name, {
            'page_obj': page_obj,
            'active_tab': 'maps',
            'page_title': 'Maps — Maps of India',
            'total': maps_pages.count(),
        })


class MyIndiaView(View):
    template_name = 'public/my_india.html'

    def get(self, request):
        my_india_pages = _published_pages(category=Page.CATEGORY_MY_INDIA)
        paginator = Paginator(my_india_pages, 9)
        page_number = request.GET.get('page', 1)
        page_obj = paginator.get_page(page_number)

        return render(request, self.template_name, {
            'page_obj': page_obj,
            'active_tab': 'my_india',
            'page_title': 'My India — Maps of India',
            'total': my_india_pages.count(),
        })
