from django.urls import path
from . import views
urlpatterns = [
    path("top-purchaser/", views.top_purchaser, name="dashboard.top_purchaser"),
]