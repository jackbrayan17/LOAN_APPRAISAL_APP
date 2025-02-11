from django.urls import path
from . import views  # Ensure this import is correct

urlpatterns = [
    path('theme-test/', views.theme_test, name='theme_test'),
]