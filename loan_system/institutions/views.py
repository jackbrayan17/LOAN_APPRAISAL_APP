from django.shortcuts import render
from django.contrib.auth.models import User
from loans.models import LoanOfficer
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.models import User

def deactivate_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.is_active = False
    user.save()
    return redirect('institution_dashboard')

def institution_dashboard(request):
    loan_officers = LoanOfficer.objects.filter(institution=request.user.institution)
    return render(request, 'institutions/dashboard.html', {'loan_officers': loan_officers})