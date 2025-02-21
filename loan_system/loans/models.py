from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.utils.translation import gettext_lazy as _
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.timezone import now
from datetime import timedelta
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
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.user.username

# Loan Officer Model
class LoanOfficer(models.Model):
    user = models.OneToOneField('loans.User', on_delete=models.CASCADE, related_name='loan_officer')
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, null=True, blank=True)

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


from django.db import models
from django.utils.translation import gettext_lazy as _
from datetime import timedelta
from django.utils.timezone import now

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
    member_share = models.IntegerField(verbose_name=_("Member's Share"))
    member_saving_account = models.IntegerField(verbose_name=_("Member's Saving Account"))
    loan_amount = models.IntegerField(verbose_name=_('Loan Amount'))
    loan_purpose = models.TextField(verbose_name=_('Loan Purpose'))
    repayment_period = models.IntegerField(verbose_name=_('Repayment Period (Months)'))
    collateral_details = models.TextField(blank=True, null=True, verbose_name=_('Collateral Details'))
    credit_score = models.IntegerField(default=0, verbose_name=_('Credit Score'))
    score_label = models.CharField(max_length=100, blank=True, verbose_name=_('Score Label'))
    status = models.CharField(max_length=20, default='SUBMITTED')
    loan_officer = models.ForeignKey(LoanOfficer, on_delete=models.CASCADE)
    approval_date = models.DateField(blank=True, null=True, verbose_name=_('Approval Date'))
    delay_days = models.IntegerField(default=0, verbose_name=_('Estimated Delay Days'))

    # Appraisal Elements
    character_score = models.IntegerField(default=0, verbose_name=_('Character Score (30 Points)'))
    capacity_to_repay_score = models.IntegerField(default=0, verbose_name=_('Capacity to Repay Score (50 Points)'))
    capital_status_score = models.IntegerField(default=0, verbose_name=_('Capital Status Score (5 Points)'))
    collateral_score = models.IntegerField(default=0, verbose_name=_('Collateral/Co-Makers Score (10 Points)'))
    credit_conditions_score = models.IntegerField(default=0, verbose_name=_('Credit Conditions Score (5 Points)'))
    total_appraisal_score = models.IntegerField(default=0, verbose_name=_('Total Appraisal Score (100 Points)'))

    # New fields from appraisal elements
    has_good_repayment_history = models.BooleanField(default=False, verbose_name="Has a good repayment history")
    has_good_reputation = models.BooleanField(default=False, verbose_name="Has a good reputation in the community")
    has_stable_job = models.BooleanField(default=False, verbose_name="Has a stable job")
    regular_income_frequency = models.CharField(
        max_length=10,
        choices=[('monthly', 'Monthly'), ('weekly', 'Weekly'), ('daily', 'Daily')],
        verbose_name="Regular Income Frequency"
    )
    has_other_loans = models.BooleanField(default=False, verbose_name="Has other active loans")
    maintains_savings = models.BooleanField(default=False, verbose_name="Maintains regular savings")
    has_sufficient_collateral = models.BooleanField(default=False, verbose_name="Has sufficient collateral")
    spouse_approval = models.BooleanField(default=False, verbose_name="Spouse has approved the loan")
    business_is_legal = models.BooleanField(default=False, verbose_name="Business is legal and safe")

    # Additional appraisal elements
    proven_record_mfi = models.BooleanField(default=False, verbose_name="Proven record of repayment to MFI")
    proven_record_other_institutions = models.BooleanField(default=False, verbose_name="Proven record of repayment to other institutions")
    blacklisted = models.BooleanField(default=False, verbose_name="Has been blacklisted")
    community_reputation = models.BooleanField(default=False, verbose_name="Good reputation in the community")
    community_leader = models.BooleanField(default=False, verbose_name="Community leader or commands respect")
    community_duration = models.CharField(
        max_length=20,
        choices=[('less_than_2', 'Less than 2 years'), ('more_than_2', 'More than 2 years')],
        verbose_name="Duration in the community"
    )
    family_relationship = models.CharField(
        max_length=10,
        choices=[('good', 'Good'), ('average', 'Average'), ('poor', 'Poor')],
        verbose_name="Relationship with family"
    )
    workplace_relationship = models.CharField(
        max_length=10,
        choices=[('good', 'Good'), ('average', 'Average'), ('poor', 'Poor')],
        verbose_name="Relationship with colleagues"
    )
    community_relationship = models.CharField(
        max_length=10,
        choices=[('good', 'Good'), ('average', 'Average'), ('poor', 'Poor')],
        verbose_name="Relationship with community"
    )
    stable_job_duration = models.CharField(
        max_length=20,
        choices=[('less_than_5', 'Less than 5 years'), ('more_than_5', 'More than 5 years')],
        verbose_name="Stable job duration"
    )
    income_matches_amortization = models.BooleanField(default=False, verbose_name="Regular income matches loan amortization schedule")
    loan_duration_matches_job = models.BooleanField(default=False, verbose_name="Loan duration matches job/business")
    collateral_convertible = models.BooleanField(default=False, verbose_name="Collateral can easily be converted to cash")
    collateral_value_exceeds_loan = models.BooleanField(default=False, verbose_name="Collateral value exceeds loan amount")
    collateral_free_from_lien = models.BooleanField(default=False, verbose_name="Collateral free from encumbrances/lien")
    co_maker_pledge = models.BooleanField(default=False, verbose_name="Co-maker willing to pledge savings/shares")
    spouse_consent = models.BooleanField(default=False, verbose_name="Spouse has given consent for the loan")
    job_health_hazards = models.BooleanField(default=False, verbose_name="Job poses no health hazards")
    # def calculate_scores(self):
    #     """Calculate and update scores before saving."""
    #     self.character_score = (
    #         (5 if self.has_good_repayment_history else 0) +
    #         (5 if self.has_good_reputation == 'good' else 2 if self.has_good_reputation == 'average' else 0) +
    #         (5 if not self.blacklisted else 0) +
    #         (5 if self.community_reputation == 'good' else 2 if self.community_reputation == 'average' else 0) +
    #         (2 if self.community_leader else 0) +
    #         (2 if self.community_duration == 'more_than_2' else 1) +
    #         (1 if self.family_relationship == 'good' else 0.5 if self.family_relationship == 'average' else 0) +
    #         (1 if self.workplace_relationship == 'good' else 0.5 if self.workplace_relationship == 'average' else 0) +
    #         (1 if self.community_relationship == 'good' else 0.5 if self.community_relationship == 'average' else 0)
    #     )

    #     self.capacity_to_repay_score = (
    #         (10 if self.has_stable_job else 0) +
    #         (10 if self.stable_job_duration == 'more_than_5' else 5) +
    #         (10 if self.regular_income_frequency == 'monthly' else 5 if self.regular_income_frequency == 'weekly' else 2) +
    #         (10 if not self.has_other_loans else 0)
    #     )

    #     self.capital_status_score = (
    #         (5 if self.maintains_savings else 0) +
    #         (5 if self.has_sufficient_collateral else 0)
    #     )

    #     self.collateral_score = (
    #         (5 if self.spouse_approval else 0)
    #     )

    #     self.credit_conditions_score = (
    #         (5 if self.business_is_legal else 0)
    #     )
    #     self.total_appraisal_score = (
    #         self.character_score +
    #         self.capacity_to_repay_score +
    #         self.capital_status_score +
    #         self.collateral_score +
    #         self.credit_conditions_score
    #     )
    #     self.credit_score = min(self.total_appraisal_score, 100)  # Cap the credit score at 100
    #     self.score_label = self.get_score_label()  # Update score label
    #     self.save()

    # def save(self, *args, **kwargs):
    #     self.calculate_scores()  # Ensure scores are updated before saving
    #     super().save(*args, **kwargs)

    # def calculate_delay_days(self):
    #     """Calculates the number of delay days based on microfinance logic."""
    #     if self.approval_date:
    #         estimated_repayment_date = self.approval_date + timedelta(days=self.repayment_period * 30)
    #         actual_repayment_date = now().date()
            
    #         if actual_repayment_date > estimated_repayment_date:
    #             self.delay_days = (actual_repayment_date - estimated_repayment_date).days
    #         else:
    #             self.delay_days = 0
            
    #         self.save()

    # def get_score_label(self):
    #     """Returns the score label based on the credit score."""
    #     if self.credit_score <= 70:
    #         return "Disapproved, high probability of failure"
    #     elif 71 <= self.credit_score <= 80:
    #         return "Approved but requires collateral, co-makers, savings, and close supervision"
    #     elif 81 <= self.credit_score <= 90:
    #         return "Approved but needs collateral and close supervision"
    #     elif 91 <= self.credit_score <= 100:
    #         return "Approved with or without collateral"
    #     return "Unknown"

    def __str__(self):
        return f"{self.member_full_name} - {self.loan_type} (Score: {self.credit_score}, Label: {self.score_label})"
    
    