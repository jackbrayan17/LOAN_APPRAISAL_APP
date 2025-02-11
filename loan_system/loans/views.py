from django.shortcuts import render
from django.utils.translation import gettext_lazy as _

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

def loan_form(request, loan_type):
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

def dashboard(request):
    return render(request, 'dashboard.html')