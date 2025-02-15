from django.shortcuts import render
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect
from .forms import LoginForm

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
from .forms import LoanForm

def loan_officer_dashboard(request, loan_type):
    credit_score = None
    if request.method == 'POST':
        form = LoanForm(request.POST)
        if form.is_valid():
            # Extract form data
            loan_amount = form.cleaned_data['loan_amount']
            repayment_period = form.cleaned_data['repayment_period']
            member_share = form.cleaned_data['member_share']
            member_saving_account = form.cleaned_data['member_saving_account']
            collateral_details = form.cleaned_data['collateral_details']

            # Calculate credit score (example logic)
            credit_score = min(100, int(
                (loan_amount / 1000) +  # Higher loan amount reduces score
                (repayment_period * 2) +  # Longer repayment period increases score
                (member_share / 100) +  # Higher member share increases score
                (member_saving_account / 1000)  # Higher savings increase score
            ))

            # Save the loan application
            loan = form.save(commit=False)
            loan.loan_type = loan_type
            loan.credit_score = credit_score
            loan.save()

            # Render the form with the credit score
            return render(request, 'loan_form.html', {'form': form, 'credit_score': credit_score})
    else:
        form = LoanForm(initial={'loan_type': loan_type})

    return render(request, 'loan_form.html', {'form': form, 'credit_score': credit_score})

from .models import Loan
def branch_manager_dashboard(request):
    loans = Loan.objects.filter(status='SUBMITTED')
    return render(request, 'branch_manager_dashboard.html', {'loans': loans})