from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from institutions.views import institution_dashboard, deactivate_user
from loans.views import branch_manager_dashboard, loan_officer_dashboard
from loans.views import submit_suggestion, validate_loan, reject_loan,regulation_page, loan_details
from institutions.views import loan_details, download_excel, download_pdf
def redirect_to_login(request):
    # Redirect to the login page if not authenticated
    return redirect('account_login')  # Redirect to the allauth login page

def user_dashboard_redirect(request):
    # Redirect users to their respective dashboards based on their roles
    if request.user.is_authenticated:
        if request.user.is_loan_officer:
            return redirect('home')
        elif request.user.is_branch_manager:
            return redirect('branch_manager_dashboard')
        elif request.user.is_institution:
            return redirect('institution_dashboard')
        
        else:
            # Default redirect for non-specific users
            return redirect('home')  # A default dashboard view if needed
    else:
        return redirect('account_login')  # Redirect to login if not authenticated

urlpatterns = [
    path('', redirect_to_login),  # Redirect root URL to login page
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),  # Django Allauth authentication
    path('loans/', include('loans.urls')),
    path('theme/', include('theme.urls')),
    path('loan/<int:loan_id>/details/', loan_details, name='loan_details'),
    path('download/excel/<int:loan_id>/', download_excel, name='download_excel'),
    path('download/pdf/<int:loan_id>/', download_pdf, name='download_pdf'),
    path('regulations/', regulation_page, name='regulations'),
    # Institution-related URLs
    path('institution/dashboard/', institution_dashboard, name='institution_dashboard'),
    path('institution/deactivate/<int:user_id>/', deactivate_user, name='deactivate_user'),
    path('submit-suggestion/', submit_suggestion, name='submit_suggestion'),
    # Redirect to respective dashboards after login
    path('dashboard/', user_dashboard_redirect, name='user_dashboard_redirect'),
    path('branch-manager/dashboard/', branch_manager_dashboard, name='branch_manager_dashboard'),
    path('loan-officer/dashboard/', loan_officer_dashboard, name='loan_officer_dashboard'),
    path('loan/validate/<int:loan_id>/', validate_loan, name='validate_loan'),
    path('loan/reject/<int:loan_id>/', reject_loan, name='reject_loan'),
    path('loan/details/<int:loan_id>/', loan_details, name='loan_details'),
]
