from django.urls import path
from . import views

app_name = 'pages'

urlpatterns = [
    path('create/', views.PageCreateView.as_view(), name='create'),
    path('<int:pk>/edit/', views.PageEditView.as_view(), name='edit'),
    path('<int:pk>/detail/', views.PageDetailView.as_view(), name='detail'),
    path('<int:pk>/delete/', views.PageDeleteView.as_view(), name='delete'),
    path('<int:pk>/preview/', views.PagePreviewView.as_view(), name='preview'),
    path('<int:pk>/publish/', views.PagePublishView.as_view(), name='publish'),
    path('<int:pk>/unpublish/', views.PageUnpublishView.as_view(), name='unpublish'),
]
