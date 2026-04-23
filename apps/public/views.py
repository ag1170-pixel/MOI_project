from django.shortcuts import render
from django.views import View
from django.core.paginator import Paginator
from apps.pages.models import Page, SiteSettings


def _published(category=None):
    qs = Page.objects.filter(status=Page.STATUS_PUBLISHED).select_related('editor')
    if category:
        qs = qs.filter(category=category)
    return qs.order_by('-published_at')


class HomeView(View):
    template_name = 'public/home.html'

    def get(self, request):
        settings = SiteSettings.get_settings()
        n = settings.pages_per_section

        all_pages = _published()
        paginator = Paginator(all_pages, 9)
        page_obj = paginator.get_page(request.GET.get('page', 1))

        # Split hero_title_line2 into 3 parts for coloured words
        words = settings.hero_title_line2.split()
        hero_word1 = words[0] if len(words) > 0 else 'Like'
        hero_word2 = ' '.join(words[1:-1]) if len(words) > 2 else 'Never'
        hero_word3 = words[-1] if len(words) > 1 else 'Before'

        return render(request, self.template_name, {
            'page_obj':       page_obj,
            'maps_pages':     _published(category=Page.CATEGORY_MAPS)[:n],
            'my_india_pages': _published(category=Page.CATEGORY_MY_INDIA)[:n],
            'total_published': all_pages.count(),
            'page_title':     'My India — Discover India Like Never Before',
            'site':           settings,
            'hero_word1':     hero_word1,
            'hero_word2':     hero_word2,
            'hero_word3':     hero_word3,
        })


class MapsView(View):
    template_name = 'public/maps.html'

    def get(self, request):
        maps_qs = _published(category=Page.CATEGORY_MAPS)
        page_obj = Paginator(maps_qs, 9).get_page(request.GET.get('page', 1))

        return render(request, self.template_name, {
            'page_obj':   page_obj,
            'total':      maps_qs.count(),
            'page_title': 'Maps of India — Explore Every Corner',
            'site':       SiteSettings.get_settings(),
        })


class MyIndiaView(View):
    template_name = 'public/my_india.html'

    def get(self, request):
        qs = _published(category=Page.CATEGORY_MY_INDIA)
        page_obj = Paginator(qs, 9).get_page(request.GET.get('page', 1))

        return render(request, self.template_name, {
            'page_obj':   page_obj,
            'total':      qs.count(),
            'page_title': 'My India — Stories, Culture & Heritage',
            'site':       SiteSettings.get_settings(),
        })
