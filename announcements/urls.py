from django.urls import path
from . import views

urlpatterns = [
    path('api/announcements/', views.announcement_list, name='announcement-list'),
    path('api/announcements/create/', views.announcement_create, name='announcement-create'),
    path('api/announcements/<int:pk>/', views.announcement_detail, name='announcement-detail'),
    path('api/announcements/<int:pk>/update/', views.announcement_update, name='announcement-update'),
    path('api/announcements/<int:pk>/delete/', views.announcement_delete, name='announcement-delete'),
]
