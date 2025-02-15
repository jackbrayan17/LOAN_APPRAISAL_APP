from django import forms
from .models import Loan


class LoginForm(forms.Form):
    username = forms.CharField(max_length=100)
    password = forms.CharField(widget=forms.PasswordInput)
    
class LoanForm(forms.ModelForm):
    class Meta:
        model = Loan
        fields = [
            'loan_type', 'member_account_number', 'member_full_name', 'member_share',
            'member_saving_account', 'loan_amount', 'loan_purpose', 'repayment_period',
            'collateral_details', 'credit_score',
        ]
        widgets = {
            'loan_type': forms.Select(attrs={'class': 'form-control'}),
            'member_account_number': forms.TextInput(attrs={'class': 'form-control'}),
            'member_full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'member_share': forms.NumberInput(attrs={'class': 'form-control'}),
            'member_saving_account': forms.NumberInput(attrs={'class': 'form-control'}),
            'loan_amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'loan_purpose': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'repayment_period': forms.NumberInput(attrs={'class': 'form-control'}),
            'collateral_details': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            # 'credit_score': forms.NumberInput(attrs={'class': 'form-control'}),
        }