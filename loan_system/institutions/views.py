from django.shortcuts import render
from django.contrib.auth.models import User
from loans.models import LoanOfficer
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.models import User
from django.shortcuts import render
from loans.models import LoanOfficer, BranchManager, Loan
from django.contrib.auth.models import User

def deactivate_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.is_active = False
    user.save()
    return redirect('institution_dashboard')
def institution_dashboard(request):
    if request.user.is_authenticated and request.user.is_institution:
        # Fetch the institution related to the logged-in user
        institution = request.user.institution
        
        # Fetch loan officers related to this institution
        loan_officers = LoanOfficer.objects.filter(institution=institution)
        branch_manager = BranchManager.objects.filter(institution=institution)
        
        # Fetch loans related to the loan officers of this institution
        loans = Loan.objects.filter(loan_officer__institution=institution)
        
        return render(request, 'institutions/dashboard.html', {
            'branch_manager': branch_manager,
            'loan_officers': loan_officers,
            'loans': loans,
        })
    else:
        return redirect('account_login')  # Or another appropriate redirect
