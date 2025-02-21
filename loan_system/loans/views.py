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

from django.shortcuts import render, get_object_or_404
from .models import LoanOfficer, Loan
from .forms import LoanForm
from datetime import timedelta
from django.utils.timezone import now
from django.shortcuts import render, get_object_or_404
from .models import Loan, LoanOfficer
from .forms import LoanForm

def loan_officer_dashboard(request, loan_type):
    credit_score = None  # Default value if the form is not submitted
    loan_officer = get_object_or_404(LoanOfficer, user=request.user)  # Get the Loan Officer for the logged-in user

    if request.method == 'POST':
        form = LoanForm(request.POST)
        
        if form.is_valid():
            cleaned_data = form.cleaned_data
            # Ensure all values are safely converted to integers (default to 0 if None)
            def safe_int(value):
                return int(value) if value is not None else 0
            
            # Assigning Scores to Each Section
            character_score = (
                (5 if cleaned_data.get('has_good_repayment_history') else 0) +
                (5 if cleaned_data.get('has_good_reputation') else 2 if cleaned_data.get('has_good_reputation') == 'average' else 0) +
                (5 if not cleaned_data.get('blacklisted') else 0) +
                (5 if cleaned_data.get('community_reputation') else 2 if cleaned_data.get('community_reputation') == 'average' else 0) +
                (2 if cleaned_data.get('community_leader') else 0) +
                (2 if cleaned_data.get('community_duration') == 'more_than_2' else 1) +
                (2 if cleaned_data.get('family_relationship') == 'good' else 1 if cleaned_data.get('family_relationship') == 'average' else 0.5) +
                (2 if cleaned_data.get('workplace_relationship') == 'good' else 1 if cleaned_data.get('workplace_relationship') == 'average' else 0.5) +
                (2 if cleaned_data.get('community_relationship') == 'good' else 1 if cleaned_data.get('community_relationship') == 'average' else 0.5)
            )

            capacity_to_repay_score = (
                (10 if cleaned_data.get('has_stable_job') else 0) +
                (10 if cleaned_data.get('stable_job_duration') == 'more_than_5' else 5) +
                (10 if cleaned_data.get('regular_income_frequency') == 'monthly' else 5 if cleaned_data.get('regular_income_frequency') == 'weekly' else 2) +
                (10 if not cleaned_data.get('has_other_loans') else 0)
            )

            capital_status_score = (
                (5 if cleaned_data.get('maintains_savings') else 0) +
                (5 if cleaned_data.get('has_sufficient_collateral') else 0)
            )

            collateral_score = (
                (5 if cleaned_data.get('spouse_approval') else 0)
            )

            credit_conditions_score = (
                (5 if cleaned_data.get('business_is_legal') else 0)
            )

            # Calculate Total Credit Score
            credit_score = (
                character_score +
                capacity_to_repay_score +
                capital_status_score +
                collateral_score +
                credit_conditions_score
            )

            # Assign Score Label
            if credit_score <= 70:
                score_label = "Disapproved, high probability of failure"
            elif 71 <= credit_score <= 80:
                score_label = "Approved but requires collateral, co-makers, savings, and close supervision"
            elif 81 <= credit_score <= 90:
                score_label = "Approved but needs collateral and close supervision"
            elif 91 <= credit_score <= 100:
                score_label = "Approved with or without collateral"
            else:
                score_label = "Unknown"
            
            # Save the Loan application with calculated credit score and score label
            loan = form.save(commit=False)
            loan.loan_type = loan_type  # Assign loan type
            loan.capacity_to_repay_score = capacity_to_repay_score
            loan.capital_status_score = capital_status_score
            loan.character_score = character_score
            loan.collateral_score = collateral_score
            loan.credit_conditions_score = credit_conditions_score
            loan.credit_score = credit_score  # Assign calculated score
            loan.score_label = score_label  # Assign score label
            loan.loan_officer = loan_officer  # Assign the authenticated loan officer
            
            loan.save()  # Save the loan to the database

            # Render the result with the calculated score
            return render(request, 'loan_form.html', {
                'form': form, 
                'credit_score': credit_score,
                'score_label': score_label, 
                'credit_conditions_score': credit_conditions_score,
                'collateral_score':collateral_score,
                'character_score':character_score,
                'capital_status_score':capital_status_score,
                'capacity_to_repay_score':capacity_to_repay_score,
            })

    else:
        form = LoanForm(initial={'loan_type': loan_type})  # Initialize form with loan type

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
        loan.approval_date = now().date()  # Set approval date

        # ✅ Correctly calculate estimated repayment date
        estimated_repayment_date = loan.approval_date + timedelta(days=loan.repayment_period * 30)
        actual_repayment_date = now().date()  # Current date
        if actual_repayment_date > estimated_repayment_date:
            loan.delay_days += (actual_repayment_date - estimated_repayment_date).days  # Add overdue days
        else:
            loan.delay_days = 0  # No delay

        loan.save()
        return redirect('branch_manager_dashboard')  # Redirect to dashboard after validation

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
