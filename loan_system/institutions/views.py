from django.shortcuts import render
from django.contrib.auth.models import User
from loans.models import LoanOfficer
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.models import User
from django.shortcuts import render
from loans.models import LoanOfficer, BranchManager, Loan
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from io import BytesIO
import xlsxwriter
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
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
        'account_number': loan.member_account_number,
        'account_name': loan.member_full_name,
        'saving_amount': loan.member_saving_account,
        'loan_amount': loan.loan_amount,
        'loan_type': loan.loan_type,
        'status': loan.status,
        'credit_score': loan.credit_score,
        'approval_date': loan.approval_date,
        'delay_days': loan.delay_days,
        'loan_officer': loan.loan_officer.user.username
    }
    return JsonResponse(data)


# PDF Download View
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO

def download_pdf(request, loan_id):
    loan = get_object_or_404(Loan, id=loan_id)
    
    # Generate PDF in memory
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    
    # Title
    p.setFont("Helvetica-Bold", 16)
    p.drawString(100, 750, f"Loan Information Report for {loan.member_full_name} by {loan.loan_officer}")
    
    # Loan Details
    p.setFont("Helvetica", 12)
    p.drawString(100, 720, f"Account Number: {loan.member_account_number}")
    p.drawString(100, 700, f"Loan Amount: {loan.loan_amount} CFA")
    p.drawString(100, 680, f"Loan Type: {loan.get_loan_type_display()}")
    p.drawString(100, 660, f"Status: {loan.status}")
    p.drawString(100, 640, f"Approval Date: {loan.approval_date or 'Not Approved'}")
    p.drawString(100, 620, f"Delay Days: {loan.delay_days}")

    # Appraisal Elements
    p.drawString(100, 580, "Appraisal Elements Score:")
    p.drawString(120, 560, f"Character Score: {loan.character_score}/30")
    p.drawString(120, 540, f"Capacity to Repay Score: {loan.capacity_to_repay_score}/40")
    p.drawString(120, 520, f"Capital Status Score: {loan.capital_status_score}/10")
    p.drawString(120, 500, f"Collateral Score: {loan.collateral_score}/5")
    p.drawString(120, 480, f"Credit Conditions Score: {loan.credit_conditions_score}/5")

    
    # Credit Score
    p.drawString(100, 420, f"Credit Score: {loan.credit_score}")
    p.drawString(100, 400, f"Score Label: {loan.score_label}")

    # Additional Information
    p.drawString(100, 360, "Additional Appraisal Information:")
    p.drawString(120, 340, f"Has Good Repayment History: {'Yes' if loan.has_good_repayment_history else 'No'}")
    p.drawString(120, 320, f"Has Good Reputation: {'Yes' if loan.has_good_reputation else 'No'}")
    p.drawString(120, 300, f"Has Stable Job: {'Yes' if loan.has_stable_job else 'No'}")
    p.drawString(120, 280, f"Regular Income Frequency: {loan.get_regular_income_frequency_display()}")
    p.drawString(120, 260, f"Has Other Loans: {'Yes' if loan.has_other_loans else 'No'}")
    p.drawString(120, 240, f"Maintains Savings: {'Yes' if loan.maintains_savings else 'No'}")
    p.drawString(120, 220, f"Has Sufficient Collateral: {'Yes' if loan.has_sufficient_collateral else 'No'}")
    p.drawString(120, 200, f"Spouse Approval: {'Yes' if loan.spouse_approval else 'No'}")
    p.drawString(120, 180, f"Business is Legal: {'Yes' if loan.business_is_legal else 'No'}")

    # Closing statement
    p.setFont("Helvetica-Bold", 14)
    p.drawString(100, 140, "This report is generated for financial analysis purposes.")
    p.drawString(100, 120, f"For any inquiries, please contact your loan officer.")

    p.showPage()
    p.save()
    
    buffer.seek(0)
    
    # Return PDF as response
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="loan_{loan.id}.pdf"'
    return response
# Excel Download View
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from openpyxl import Workbook

def download_excel(request, loan_id):
    loan = get_object_or_404(Loan, id=loan_id)
    
    # Create an Excel workbook and sheet
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = f"Loan Report for {loan.member_full_name}"
    
    # Set column titles
    columns = [
        "Field", "Value"
    ]
    sheet.append(columns)

    # Loan Details
    sheet.append(["Account Number", loan.member_account_number])
    sheet.append(["Loan Amount", f"{loan.loan_amount} CFA"])
    sheet.append(["Loan Type", loan.get_loan_type_display()])
    sheet.append(["Status", loan.status])
    sheet.append(["Approval Date", loan.approval_date or 'Not Approved'])
    sheet.append(["Delay Days", loan.delay_days])

    # Appraisal Elements
    sheet.append(["", ""])  # Empty row for spacing
    sheet.append(["Appraisal Elements", ""])
    sheet.append(["Character Score", loan.character_score])
    sheet.append(["Capacity to Repay Score", loan.capacity_to_repay_score])
    sheet.append(["Capital Status Score", loan.capital_status_score])
    sheet.append(["Collateral Score", loan.collateral_score])
    sheet.append(["Credit Conditions Score", loan.credit_conditions_score])
    sheet.append(["Total Appraisal Score", loan.total_appraisal_score])

    # Credit Score
    sheet.append(["Credit Score", loan.credit_score])
    sheet.append(["Score Label", loan.score_label])

    # Additional Information
    sheet.append(["", ""])  # Empty row for spacing
    sheet.append(["Additional Appraisal Information", ""])
    sheet.append(["Has Good Repayment History", "Yes" if loan.has_good_repayment_history else "No"])
    sheet.append(["Has Good Reputation", "Yes" if loan.has_good_reputation else "No"])
    sheet.append(["Has Stable Job", "Yes" if loan.has_stable_job else "No"])
    sheet.append(["Regular Income Frequency", loan.get_regular_income_frequency_display()])
    sheet.append(["Has Other Loans", "Yes" if loan.has_other_loans else "No"])
    sheet.append(["Maintains Savings", "Yes" if loan.maintains_savings else "No"])
    sheet.append(["Has Sufficient Collateral", "Yes" if loan.has_sufficient_collateral else "No"])
    sheet.append(["Spouse Approval", "Yes" if loan.spouse_approval else "No"])
    sheet.append(["Business is Legal", "Yes" if loan.business_is_legal else "No"])

    # Save the workbook to a BytesIO stream
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="loan_{loan.id}.xlsx"'
    
    # Write the workbook to the response
    workbook.save(response)
    
    return response

def deactivate_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.is_active = False
    user.save()
    return redirect('institution_dashboard')
from django.shortcuts import render, redirect
from django.utils.dateparse import parse_date

def institution_dashboard(request):
    if request.user.is_authenticated and request.user.is_institution:
        # Fetch the institution related to the logged-in user
        institution = request.user.institution

        # Fetch loan officers and branch managers related to this institution
        loan_officers = LoanOfficer.objects.filter(institution=institution)
        branch_manager = BranchManager.objects.filter(institution=institution)

        # Fetch all loans related to this institution
        loans = Loan.objects.filter(loan_officer__institution=institution)

        # Get filter parameters from request
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        loan_type = request.GET.get('loan_type')
        loan_officer = request.GET.get('loan_officer')
        status = request.GET.get('status')

        # Apply filters
        if start_date:
            loans = loans.filter(approval_date__gte=parse_date(start_date))
        if end_date:
            loans = loans.filter(approval_date__lte=parse_date(end_date))
        if loan_type:
            loans = loans.filter(loan_type=loan_type)
        if loan_officer:
            loans = loans.filter(loan_officer__user__id=loan_officer)
        if status:
            loans = loans.filter(status=status)

        # Get distinct values for dropdown filters
        loan_types = Loan.objects.filter(loan_officer__institution=institution).values_list('loan_type', flat=True).distinct()
        statuses = Loan.objects.filter(loan_officer__institution=institution).values_list('status', flat=True).distinct()

        return render(request, 'institutions/dashboard.html', {
            'branch_manager': branch_manager,
            'loan_officers': loan_officers,
            'loans': loans,
            'loan_types': loan_types,
            'statuses': statuses,  # Pass statuses for filtering
        })
    
    return redirect('account_login')  # Redirect if not authenticated or not an institution user
