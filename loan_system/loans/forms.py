from django import forms
from .models import Loan
from .models import Suggestion

class SuggestionForm(forms.ModelForm):
    class Meta:
        model = Suggestion
        fields = ['suggestion_text']

class LoginForm(forms.Form):
    username = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))


class LoanForm(forms.ModelForm):
    # Additional fields for credit scoring
    has_good_repayment_history = forms.BooleanField(required=False, label="Has a good repayment history")
    has_good_reputation = forms.BooleanField(required=False, label="Has a good reputation in the community")
    has_stable_job = forms.BooleanField(required=False, label="Has a stable job")
    regular_income_frequency = forms.ChoiceField(
        choices=[('monthly', 'Monthly'), ('weekly', 'Weekly'), ('daily', 'Daily')],
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Regular Income Frequency"
    )
    has_other_loans = forms.BooleanField(required=False, label="Has other active loans")
    maintains_savings = forms.BooleanField(required=False, label="Maintains regular savings")
    has_sufficient_collateral = forms.BooleanField(required=False, label="Has sufficient collateral")
    spouse_approval = forms.BooleanField(required=False, label="Spouse has approved the loan")
    business_is_legal = forms.BooleanField(required=False, label="Business is legal and safe")
    
    # New fields from appraisal elements
    proven_record_mfi = forms.BooleanField(required=False, label="Proven record of repayment to MFI")
    proven_record_other_institutions = forms.BooleanField(required=False, label="Proven record of repayment to other institutions")
    blacklisted = forms.BooleanField(required=False, label="Has been blacklisted")
    community_reputation = forms.BooleanField(required=False, label="Good reputation in the community")
    community_leader = forms.BooleanField(required=False, label="Community leader or commands respect")
    community_duration = forms.ChoiceField(
        choices=[('less_than_2', 'Less than 2 years'), ('more_than_2', 'More than 2 years')],
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Duration in the community"
    )
    family_relationship = forms.ChoiceField(
        choices=[('good', 'Good'), ('average', 'Average'), ('poor', 'Poor')],
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Relationship with family"
    )
    workplace_relationship = forms.ChoiceField(
        choices=[('good', 'Good'), ('average', 'Average'), ('poor', 'Poor')],
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Relationship with colleagues"
    )
    community_relationship = forms.ChoiceField(
        choices=[('good', 'Good'), ('average', 'Average'), ('poor', 'Poor')],
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Relationship with community"
    )
    stable_job_duration = forms.ChoiceField(
        choices=[('less_than_5', 'Less than 5 years'), ('more_than_5', 'More than 5 years')],
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Stable job duration"
    )
    income_matches_amortization = forms.BooleanField(required=False, label="Regular income matches loan amortization schedule")
    loan_duration_matches_job = forms.BooleanField(required=False, label="Loan duration matches job/business")
    collateral_convertible = forms.BooleanField(required=False, label="Collateral can easily be converted to cash")
    collateral_value_exceeds_loan = forms.BooleanField(required=False, label="Collateral value exceeds loan amount")
    collateral_free_from_lien = forms.BooleanField(required=False, label="Collateral free from encumbrances/lien")
    co_maker_pledge = forms.BooleanField(required=False, label="Co-maker willing to pledge savings/shares")
    spouse_consent = forms.BooleanField(required=False, label="Spouse has given consent for the loan")
    job_health_hazards = forms.BooleanField(required=False, label="Job poses no health hazards")

    class Meta:
        model = Loan
        fields = [
            'loan_type', 'member_account_number', 'member_full_name', 'member_share',
            'member_saving_account', 'loan_amount', 'loan_purpose', 'repayment_period',
            'collateral_details',
        ]
        widgets = {
            'loan_type': forms.Select(attrs={'class': 'form-control'}),
            'member_account_number': forms.TextInput(attrs={'class': 'form-control'}),
            'member_full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'member_share': forms.NumberInput(attrs={'class': 'form-control'}),
            'member_saving_account': forms.TextInput(attrs={'class': 'form-control'}),
            'loan_amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'loan_purpose': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'repayment_period': forms.NumberInput(attrs={'class': 'form-control'}),
            'collateral_details': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def calculate_credit_score(self):
        score = 0
        
        # Character (30 points)
        if self.cleaned_data.get('proven_record_mfi'):
            score += 5
        if self.cleaned_data.get('proven_record_other_institutions'):
            score += 5
        if not self.cleaned_data.get('blacklisted'):
            score += 5
        if self.cleaned_data.get('community_reputation'):
            score += 5
        if self.cleaned_data.get('community_leader'):
            score += 5
        if self.cleaned_data.get('community_duration') == 'more_than_2':
            score += 5
        
        # Capacity to Repay (50 points)
        if self.cleaned_data.get('stable_job_duration') == 'more_than_5':
            score += 10
        if self.cleaned_data.get('regular_income_frequency') == 'monthly':
            score += 10
        if self.cleaned_data.get('income_matches_amortization'):
            score += 10
        if self.cleaned_data.get('loan_duration_matches_job'):
            score += 10
        if not self.cleaned_data.get('has_other_loans'):
            score += 10
        
        # Capital Status (5 points)
        if self.cleaned_data.get('maintains_savings'):
            score += 5
        
        # Collateral (10 points)
        if self.cleaned_data.get('collateral_convertible'):
            score += 2
        if self.cleaned_data.get('collateral_value_exceeds_loan'):
            score += 2
        if self.cleaned_data.get('collateral_free_from_lien'):
            score += 2
        if self.cleaned_data.get('co_maker_pledge'):
            score += 2
        if self.cleaned_data.get('spouse_consent'):
            score += 2
        
        # Credit Conditions (5 points)
        if not self.cleaned_data.get('business_is_legal'):
            score += 2
        if not self.cleaned_data.get('job_health_hazards'):
            score += 3
        
        return score
