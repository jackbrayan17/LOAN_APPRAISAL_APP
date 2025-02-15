from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.utils.translation import gettext_lazy as _

# Custom User Model
class User(AbstractUser):
    is_admin = models.BooleanField(default=False)
    is_institution = models.BooleanField(default=False)
    is_branch_manager = models.BooleanField(default=False)
    is_loan_officer = models.BooleanField(default=False)
    groups = models.ManyToManyField(Group, related_name="loans_user_set", blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name="loans_user_permissions_set", blank=True)

    def __str__(self):
        return self.username

# Institution Model
class Institution(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField()
    contact = models.CharField(max_length=15)
    user = models.OneToOneField('loans.User', on_delete=models.CASCADE, related_name='institution')

    def __str__(self):
        return self.name

# Branch Manager Model
class BranchManager(models.Model):
    user = models.OneToOneField('loans.User', on_delete=models.CASCADE, related_name='branch_manager')
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username

# Loan Officer Model
class LoanOfficer(models.Model):
    user = models.OneToOneField('loans.User', on_delete=models.CASCADE, related_name='loan_officer')
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username

# Customer Model
class Customer(models.Model):
    name = models.CharField(max_length=255)
    contact = models.CharField(max_length=15)
    loan_officer = models.ForeignKey(LoanOfficer, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

# Loan Model
class Loan(models.Model):
    LOAN_TYPES = [
        ('WITHIN_SAVINGS', _('Loans within Savings')),
        ('ABOVE_SAVINGS', _('Loans Above Savings')),
        ('COVERED_BY_SALARY', _('Loans Covered by Salary')),
        ('COVERED_BY_STANDING_ORDER', _('Loans Covered by Standing Order')),
        ('MORTGAGE', _('Mortgage Loans')),
    ]
    loan_type = models.CharField(max_length=50, choices=LOAN_TYPES)
    member_account_number = models.CharField(max_length=20, verbose_name=_('Member Account Number'))
    member_full_name = models.CharField(max_length=100, verbose_name=_('Member Full Name'))
    member_share = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("Member's Share"))
    member_saving_account = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("Member's Saving Account"))
    loan_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('Loan Amount'))
    loan_purpose = models.TextField(verbose_name=_('Loan Purpose'))
    repayment_period = models.IntegerField(verbose_name=_('Repayment Period (Months)'))
    collateral_details = models.TextField(blank=True, null=True, verbose_name=_('Collateral Details'))
    credit_score = models.IntegerField(verbose_name=_('Credit Score'))
    status = models.CharField(max_length=20, default='SUBMITTED')
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    loan_officer = models.ForeignKey(LoanOfficer, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.member_full_name} - {self.loan_type}"
