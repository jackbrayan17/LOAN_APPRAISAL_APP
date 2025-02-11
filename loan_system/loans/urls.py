from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.home, name='home'),
    path('loan-form/<str:loan_type>/', views.loan_form, name='loan_form'),
]