from django.urls import path
from . import views

app_name = 'public'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('maps', views.MapsView.as_view(), name='maps'),
    path('my-india', views.MyIndiaView.as_view(), name='my_india'),
]
