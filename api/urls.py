from django.urls import path

from . import views

urlpatterns = [
    path('campaign/create', views.create_campaign),
    path('campaign/<int:campaign_id>', views.get_campaign)
]
