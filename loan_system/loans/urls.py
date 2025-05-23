from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    # path('dashboard/', views.dashboard, name='home'),
    path('regulations/', views.regulation_page, name='regulations'),
    path('loan-form/<str:loan_type>/', views.loan_officer_dashboard, name='loan_form'),
]