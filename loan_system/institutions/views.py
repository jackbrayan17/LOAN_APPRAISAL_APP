from django.shortcuts import render
from django.contrib.auth.models import User
from loans.models import LoanOfficer
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.models import User
from django.shortcuts import render
from loans.models import LoanOfficer, BranchManager, Loan
from django.contrib.auth.models import User

from django.http import HttpResponse
import openpyxl
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from django.http import JsonResponse
from loans.models import Loan

def loan_details(request, loan_id):
    loan = Loan.objects.get(id=loan_id)
    data = {
        'account_number': loan.account_number,
        'account_name': loan.account_name,
        'saving_amount': loan.saving_amount,
        'loan_amount': loan.loan_amount,
        'loan_type': loan.loan_type,
        'status': loan.status,
        'credit_score': loan.credit_score,
        'approval_date': loan.approval_date,
        'delay_days': loan.delay_days,
        'loan_officer': loan.loan_officer.user.username
    }
    return JsonResponse(data)

def download_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="loans.pdf"'

    c = canvas.Canvas(response, pagesize=letter)
    c.drawString(100, 750, "Loans Report")

    # Add loan data to PDF
    loans = Loan.objects.all()
    y_position = 730
    for loan in loans:
        c.drawString(100, y_position, f"Account: {loan.account_number} | Name: {loan.account_name}")
        y_position -= 20

    c.showPage()
    c.save()
    return response

def download_excel(request):
    # Create Excel file
    wb = openpyxl.Workbook()
    sheet = wb.active
    sheet.title = "Loans"
    
    # Define headers
    headers = ["Account Number", "Account Name", "Saving Amount", "Loan Amount", "Loan Type", "Status", "Credit Score", "Approval Date", "Delay Days", "Loan Officer"]
    sheet.append(headers)

    # Add loan data to the sheet
    loans = Loan.objects.all()
    for loan in loans:
        row = [loan.account_number, loan.account_name, loan.saving_amount, loan.loan_amount, loan.loan_type, loan.status, loan.credit_score, loan.approval_date, loan.delay_days, loan.loan_officer.user.username]
        sheet.append(row)

    # Set response headers for file download
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="loans.xlsx"'
    wb.save(response)
    return response


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
