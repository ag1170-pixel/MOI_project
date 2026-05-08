from django.urls import path
from . import views

app_name = 'public'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('maps/', views.MapsView.as_view(), name='maps'),
    path('maps', views.MapsView.as_view()),          # no-slash alias
    path('my-india/', views.MyIndiaView.as_view(), name='my_india'),
    path('my-india', views.MyIndiaView.as_view()),   # no-slash alias
    path('search/', views.SearchView.as_view(), name='search'),
]
