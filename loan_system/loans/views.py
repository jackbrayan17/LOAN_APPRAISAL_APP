from django.shortcuts import render
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect
from .forms import LoginForm
from django.shortcuts import render, redirect, get_object_or_404
from .models import Loan, LoanOfficer
from django.contrib.auth.decorators import login_required

def custom_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                if user.is_loan_officer:
                    return redirect('loan_officer_dashboard', loan_type='WITHIN_SAVINGS')  # Redirect to loan officer dashboard
                elif user.is_branch_manager:
                    return redirect('branch_manager_dashboard')  # Redirect to branch manager dashboard
                else:
                    return redirect('dashboard')  # Redirect to default dashboard for other users
            else:
                # Handle invalid login
                return redirect('login')
    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form})

from django.shortcuts import render, redirect
from .forms import LoanForm
from .models import Loan

def dashboard(request):
    if request.user.is_authenticated:
        if request.user.is_loan_officer:
            return redirect('loan_officer_dashboard', loan_type='WITHIN_SAVINGS')
        elif request.user.is_branch_manager:
            return redirect('branch_manager_dashboard')
        elif request.user.is_institution:
            return redirect('institution_dashboard')
        
        else:
            return render(request, 'dashboard.html')
    else:
        return redirect('login')  # Redirect to login if the user is not logged in


def home(request):
    loan_types = [
        ('WITHIN_SAVINGS', _('Loans within Savings')),
        ('ABOVE_SAVINGS', _('Loans Above Savings')),
        ('COVERED_BY_SALARY', _('Loans Covered by Salary')),
        ('COVERED_BY_STANDING_ORDER', _('Loans Covered by Standing Order')),
        ('MORTGAGE', _('Mortgage Loans')),
    ]
    return render(request, 'home.html', {'loan_types': loan_types})

from django.shortcuts import render, redirect
from .forms import LoanForm
from django.shortcuts import render, redirect
from .models import LoanOfficer, Loan
from .forms import LoanForm

from django.shortcuts import render
from .models import LoanOfficer, Loan
from .forms import LoanForm

def loan_officer_dashboard(request, loan_type):
    credit_score = None
    loan_officer = LoanOfficer.objects.get(user=request.user)  # Get the Loan Officer object for the logged-in user

    if request.method == 'POST':
        form = LoanForm(request.POST)
        if form.is_valid():
            # Extract form data from the submitted form
            loan_amount = form.cleaned_data['loan_amount']
            repayment_period = form.cleaned_data['repayment_period']
            member_share = form.cleaned_data['member_share']
            member_saving_account = form.cleaned_data['member_saving_account']
            collateral_details = form.cleaned_data['collateral_details']
            
            # Calculate the credit score based on the loan details (custom logic can be adjusted)
            credit_score = min(100, int(
                (loan_amount / 1000) +  # Higher loan amount reduces score
                (repayment_period * 2) +  # Longer repayment period increases score
                (member_share / 100) +  # Higher member share increases score
                (member_saving_account / 1000)  # Higher savings increase score
            ))

            # Save the loan application, but don’t commit yet
            loan = form.save(commit=False)
            loan.loan_type = loan_type  # Set the loan type
            loan.credit_score = credit_score  # Assign the calculated credit score
            loan.loan_officer = loan_officer  # Directly assign the authenticated loan officer
            loan.save()  # Save the loan to the database

            # After saving, render the form with the updated information
            return render(request, 'loan_form.html', {'form': form, 'credit_score': credit_score})

    else:
        form = LoanForm(initial={'loan_type': loan_type})  # Initialize the form with the loan type

    return render(request, 'loan_form.html', {'form': form, 'credit_score': credit_score})


from .models import Loan
@login_required
def branch_manager_dashboard(request):
    if request.user.is_authenticated and request.user.is_branch_manager:
        # Fetch loan officers related to this branch manager's institution
        institution = request.user.branch_manager.institution
        loan_officers = LoanOfficer.objects.filter(institution=institution)
        
        # Fetch loans related to the institution's loan officers
        loans = Loan.objects.filter(loan_officer__institution=institution)
        
        return render(request, 'branch_manager_dashboard.html', {
            'loan_officers': loan_officers,
            'loans': loans,
        })
    else:
        return redirect('account_login')

# Validate Loan
@login_required
def validate_loan(request, loan_id):
    loan = get_object_or_404(Loan, id=loan_id)
    if request.user.is_branch_manager and loan.status == 'SUBMITTED':
        loan.status = 'VALIDATED'
        loan.save()
        return redirect('branch_manager_dashboard')  # Redirect to dashboard after validating
    return redirect('account_login')

# Reject Loan
@login_required
def reject_loan(request, loan_id):
    loan = get_object_or_404(Loan, id=loan_id)
    if request.user.is_branch_manager and loan.status == 'SUBMITTED':
        loan.status = 'REJECTED'
        loan.save()
        return redirect('branch_manager_dashboard')  # Redirect to dashboard after rejecting
    return redirect('account_login')

# View Loan Details (Optional: Add a detailed view of the loan)
@login_required
def loan_details(request, loan_id):
    loan = get_object_or_404(Loan, id=loan_id)
    return render(request, 'loan_details.html', {'loan': loan})
