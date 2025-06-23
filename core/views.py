from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponse
from django.template.loader import render_to_string, get_template
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count
from datetime import date, timedelta, datetime
import json
from io import BytesIO
from xhtml2pdf import pisa
from django.views.generic import CreateView, UpdateView, ListView, DetailView, DeleteView
from .forms import ProjectForm
from django.urls import reverse_lazy
from .models import Customer, Quote, Project, QuoteItem, Invoice, InvoiceItem, Department, Employee, Attendance, Payroll
from .forms import (CustomerForm, QuoteForm, QuoteItemForm,ProjectForm, InvoiceForm, InvoiceItemFormSet,DepartmentForm, EmployeeForm, AttendanceForm, PayrollForm)
import logging
from django.forms import inlineformset_factory
from django.urls import reverse_lazy
from django.db.models import Q
from django.utils import timezone

# Dashboard View
def dashboard(request):
    # Calculate stats
    total_customers = Customer.objects.count()
    total_quotes = Quote.objects.count()
    total_projects = Project.objects.count()
    
    # Monthly target calculation
    current_month = datetime.now().month
    projects = Project.objects.filter(start_date__month=current_month)
    
    monthly_target = projects.aggregate(total=Sum('target_amount'))['total'] or 0
    monthly_achieved = projects.aggregate(total=Sum('achieved_amount'))['total'] or 0
    
    # Calculate progress percentage safely
    monthly_progress = 0
    if monthly_target > 0:
        monthly_progress = (monthly_achieved / monthly_target) * 100
    
    # Project status counts
    project_status = Project.objects.values('status').annotate(count=Count('id'))
    status_labels = {
        'planning': 'Planning',
        'in_progress': 'In Progress',
        'completed': 'Completed',
        'delayed': 'Delayed'
    }
    
    # Recent projects with progress calculation
    recent_projects = Project.objects.order_by('-start_date')[:5]
    for project in recent_projects:
        project.progress_percentage = 0
        if project.target_amount > 0:
            project.progress_percentage = (project.achieved_amount / project.target_amount) * 100
    
    # Prepare chart data
    chart_data = {
        'labels': [status_labels.get(p['status'], p['status']) for p in project_status],
        'data': [p['count'] for p in project_status],
        'colors': ['#3498db', '#2ecc71', '#f39c12', '#e74c3c']
    }
    
    context = {
        'total_customers': total_customers,
        'total_quotes': total_quotes,
        'total_projects': total_projects,
        'monthly_target': monthly_target,
        'monthly_achieved': monthly_achieved,
        'monthly_progress': round(monthly_progress, 2),
        'recent_projects': recent_projects,
        'chart_data_json': json.dumps(chart_data),
    }
    return render(request, 'core/dashboard.html', context)

# Customer Views
def customer_create(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            customer = form.save()
            messages.success(request, f'Customer "{customer.display_name}" created successfully!')
            return redirect('customer_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CustomerForm()
    return render(request, 'core/customer_form.html', {'form': form})


def customer_list(request):
    customers = Customer.objects.all()
    return render(request, 'core/customer_list.html', {'customers': customers})

def customer_edit(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            messages.success(request, 'Customer updated successfully!')
            return redirect('customer_list')
    else:
        form = CustomerForm(instance=customer)
    return render(request, 'core/customer_form.html', {'form': form})

def customer_delete(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    customer.delete()
    messages.success(request, 'Customer deleted successfully!')
    return redirect('customer_list')

# Quote Views
def quote_list(request):
    status = request.GET.get('status', 'all')
    if status == 'draft':
        quotes = Quote.objects.filter(status='draft')
    elif status == 'completed':
        quotes = Quote.objects.filter(status='completed')
    elif status == 'printed':
        quotes = Quote.objects.filter(status='printed')
    else:
        quotes = Quote.objects.all()
    
    return render(request, 'core/quote_list.html', {
        'quotes': quotes,
        'current_status': status
    })

def quote_create(request):
    QuoteItemFormSet = inlineformset_factory(
        Quote, 
        QuoteItem, 
        form=QuoteItemForm, 
        extra=1,
        can_delete=True
    )
    
    if request.method == 'POST':
        form = QuoteForm(request.POST)
        formset = QuoteItemFormSet(request.POST)
        
        if form.is_valid() and formset.is_valid():
            # Create quote instance but don't save yet
            quote = form.save(commit=False)
            # Set status to "sent" as requested
            quote.status = 'sent'
            quote.created_by = request.user
            quote.save()
            
            # Save formset with the quote instance
            instances = formset.save(commit=False)
            for instance in instances:
                instance.quote = quote
                instance.save()
            
            # Delete any marked for deletion
            for instance in formset.deleted_objects:
                instance.delete()
            
            # Check if we need to print
            if request.POST.get('print') == '1':
                # Update status to printed for print view
                quote.status = 'printed'
                quote.save()
                messages.success(request, 'Quote created and sent successfully! Redirecting to print...')
                return redirect('quote_print', pk=quote.pk)
            
            messages.success(request, 'Quote created and sent successfully!')
            return redirect('quote_list')
    else:
        form = QuoteForm()
        formset = QuoteItemFormSet()
    
    return render(request, 'core/quote_form.html', {
        'form': form,
        'formset': formset
    })

def quote_edit(request, pk):
    QuoteItemFormSet = inlineformset_factory(
        Quote, 
        QuoteItem, 
        form=QuoteItemForm, 
        extra=1,
        can_delete=True
    )
    
    quote = get_object_or_404(Quote, pk=pk)
    
    if request.method == 'POST':
        form = QuoteForm(request.POST, instance=quote)
        formset = QuoteItemFormSet(request.POST, instance=quote)
        
        if form.is_valid() and formset.is_valid():
            # Update quote instance but don't save yet
            quote = form.save(commit=False)
            # Set status to "sent" as requested
            quote.status = 'sent'
            quote.save()
            
            # Save formset
            instances = formset.save(commit=False)
            for instance in instances:
                instance.quote = quote
                instance.save()
            
            # Delete any marked for deletion
            for instance in formset.deleted_objects:
                instance.delete()
            
            # Check if we need to print
            if request.POST.get('print') == '1':
                # Update status to printed for print view
                quote.status = 'printed'
                quote.save()
                messages.success(request, 'Quote updated and sent successfully! Redirecting to print...')
                return redirect('quote_print', pk=quote.pk)
            
            messages.success(request, 'Quote updated and sent successfully!')
            return redirect('quote_list')
    else:
        form = QuoteForm(instance=quote)
        formset = QuoteItemFormSet(instance=quote)
    
    return render(request, 'core/quote_form.html', {
        'form': form,
        'formset': formset,
        'quote': quote
    })

def quote_print(request, pk):
    quote = get_object_or_404(Quote, pk=pk)
    # Status is already set to 'printed' in create/edit view
    return render(request, 'core/quote_print.html', {'quote': quote})

@require_POST
def quote_delete(request, pk):
    quote = get_object_or_404(Quote, pk=pk)
    quote_number = quote.quote_number
    quote.delete()
    messages.success(request, f'Quote "{quote_number}" has been deleted successfully!')
    return redirect('quote_list')

# Project Views
def project_list(request):
    projects = Project.objects.all()
    return render(request, 'core/project_list.html', {'projects': projects})

def project_create(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Project created successfully!')
            return redirect('project_list')
    else:
        form = ProjectForm()
    return render(request, 'core/project_form.html', {'form': form})

def project_edit(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            messages.success(request, 'Project updated successfully!')
            return redirect('project_list')
    else:
        form = ProjectForm(instance=project)
    return render(request, 'core/project_form.html', {'form': form})

def project_delete(request, pk):
    project = get_object_or_404(Project, pk=pk)
    project.delete()
    messages.success(request, 'Project deleted successfully!')
    return redirect('project_list')

# Invoice Views
# @login_required
def invoice_list(request):
    status = request.GET.get('status', 'all')
    
    if status == 'draft':
        invoices = Invoice.objects.filter(status='draft')
    elif status == 'sent':
        invoices = Invoice.objects.filter(status='sent')
    elif status == 'paid':
        invoices = Invoice.objects.filter(status='paid')
    elif status == 'overdue':
        invoices = Invoice.objects.filter(status='overdue')
    else:
        invoices = Invoice.objects.all()
    
    return render(request, 'core/invoice_list.html', {
        'invoices': invoices,
        'current_status': status
    })

# @login_required
def invoice_create(request):
    if request.method == 'POST':
        form = InvoiceForm(request.POST)
        formset = InvoiceItemFormSet(request.POST)
        
        if form.is_valid() and formset.is_valid():
            invoice = form.save(commit=False)
            invoice.save()
            
            formset.instance = invoice
            formset.save()
            
            # Update total amount
            invoice.update_total()
            
            messages.success(request, 'Invoice created successfully!')
            return redirect('invoice_list')
    else:
        # Generate next invoice number
        last_invoice = Invoice.objects.order_by('-id').first()
        next_number = f"INV-{datetime.now().year}-{last_invoice.id + 1}" if last_invoice else f"INV-{datetime.now().year}-1"
        
        form = InvoiceForm(initial={'invoice_number': next_number})
        formset = InvoiceItemFormSet()
    
    return render(request, 'core/invoice_form.html', {
        'form': form,
        'formset': formset,
        'title': 'Create Invoice'
    })

# @login_required
def invoice_detail(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    return render(request, 'core/invoice_detail.html', {'invoice': invoice})

# @login_required
def invoice_edit(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    
    if request.method == 'POST':
        form = InvoiceForm(request.POST, instance=invoice)
        formset = InvoiceItemFormSet(request.POST, instance=invoice)
        
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            
            # Update total amount
            invoice.update_total()
            
            messages.success(request, 'Invoice updated successfully!')
            return redirect('invoice_list')
    else:
        form = InvoiceForm(instance=invoice)
        formset = InvoiceItemFormSet(instance=invoice)
    
    return render(request, 'core/invoice_form.html', {
        'form': form,
        'formset': formset,
        'title': 'Edit Invoice'
    })

# @login_required
def invoice_delete(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    invoice.delete()
    messages.success(request, 'Invoice deleted successfully!')
    return redirect('invoice_list')

@require_POST
# @login_required
def mark_invoice_paid(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    
    if invoice.status != 'paid':
        invoice.status = 'paid'
        invoice.save()
        messages.success(request, f"Invoice #{invoice.invoice_number} marked as paid!")
    
    return redirect('invoice_detail', pk=pk)

def generate_pdf(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    items = invoice.items.all()
    
    template_path = 'core/invoice_pdf.html'
    context = {'invoice': invoice, 'items': items}
    
    # Render template
    template = get_template(template_path)
    html = template.render(context)
    
    # Create PDF
    result = BytesIO()
    
    try:
        pdf = pisa.pisaDocument(
            BytesIO(html.encode("UTF-8")),
            result,
            encoding='UTF-8'
        )
        
        if not pdf.err:
            response = HttpResponse(
                result.getvalue(),
                content_type='application/pdf'
            )
            response['Content-Disposition'] = f'filename=invoice_{invoice.invoice_number}.pdf'
            return response
            
    except Exception as e:
        print(f"PDF generation error: {e}")
        messages.error(request, "Error generating PDF. Please try again.")
    
    return HttpResponse('Error generating PDF', status=400)

def test_pdf(request):
    # For testing PDF generation
    invoice = Invoice.objects.first()
    if not invoice:
        # Create test data if needed
        customer = Customer.objects.create(
            display_name="Test Customer",
            company_name="Test Company"
        )
        invoice = Invoice.objects.create(
            invoice_number="TEST-001",
            customer=customer,
            total_amount=100.00
        )
    
    return generate_pdf(request, invoice.pk)


def payments(request):
    return render(request, 'core/payments.html', {'title': 'Payments Received'})

def expenses(request):
    return render(request, 'core/expenses.html', {'title': 'Expenses'})

def time_tracking(request):
    return render(request, 'core/time_tracking.html', {'title': 'Time Tracking'})

def reports(request):
    return render(request, 'core/reports.html', {'title': 'Reports'})



class ProjectCreateView(CreateView):
    model = Project
    form_class = ProjectForm
    template_name = 'core/project_form.html'
    success_url = reverse_lazy('project_list')

class ProjectUpdateView(UpdateView):
    model = Project
    form_class = ProjectForm
    template_name = 'core/project_form.html'
    success_url = reverse_lazy('project_list')

class ProjectListView(ListView):
    model = Project
    template_name = 'core/project_list.html'
    context_object_name = 'projects'



# Department Views
class DepartmentListView(ListView):
    model = Department
    template_name = 'core/department_list.html'
    context_object_name = 'departments'

class DepartmentCreateView(CreateView):
    model = Department
    form_class = DepartmentForm
    template_name = 'core/department_form.html'
    success_url = reverse_lazy('department_list')

class DepartmentUpdateView(UpdateView):
    model = Department
    form_class = DepartmentForm
    template_name = 'core/department_form.html'
    success_url = reverse_lazy('department_list')

class DepartmentDeleteView(DeleteView):
    model = Department
    template_name = 'core/department_confirm_delete.html'
    success_url = reverse_lazy('department_list')

# Employee Views
class EmployeeListView(ListView):
    model = Employee
    template_name = 'core/employee_list.html'
    context_object_name = 'employees'
    paginate_by = 20

class EmployeeCreateView(CreateView):
    model = Employee
    form_class = EmployeeForm
    template_name = 'core/employee_form.html'
    success_url = reverse_lazy('employee_list')

class EmployeeDetailView(DetailView):
    model = Employee
    template_name = 'core/employee_detail.html'
    context_object_name = 'employee'

class EmployeeUpdateView(UpdateView):
    model = Employee
    form_class = EmployeeForm
    template_name = 'core/employee_form.html'
    success_url = reverse_lazy('employee_list')

class EmployeeDeleteView(DeleteView):
    model = Employee
    template_name = 'core/employee_confirm_delete.html'
    success_url = reverse_lazy('employee_list')

# Attendance Views
class AttendanceCreateView(CreateView):
    model = Attendance
    form_class = AttendanceForm
    template_name = 'core/attendance_form.html'
    success_url = reverse_lazy('attendance_list')

class AttendanceUpdateView(UpdateView):
    model = Attendance
    fields = ['status', 'hours_worked', 'overtime_hours']
    template_name = 'core/attendance_form.html'  # Create this template
    success_url = reverse_lazy('attendance_list')

class AttendanceDeleteView(DeleteView):
    model = Attendance
    template_name = 'core/attendance_confirm_delete.html'  # Create this template
    success_url = reverse_lazy('attendance_list')

class AttendanceListView(ListView):
    template_name = 'core/attendance_list.html'
    context_object_name = 'attendances'
    paginate_by = 30

    def get_queryset(self):
        month = self.request.GET.get('month')
        year = self.request.GET.get('year')
        department = self.request.GET.get('department')
        employee_id = self.request.GET.get('employee')
        employee_monthly = self.request.GET.get('employee_monthly')
        view_type = self.request.GET.get('view_type', 'monthly')

        # Yearly employee view
        if view_type == 'yearly' and employee_id and year:
            return self.get_yearly_employee_data(employee_id, year)
        
        # Monthly department view
        if not month:
            month = timezone.now().strftime('%Y-%m')
        
        year_val, month_val = map(int, month.split('-'))
        start_date = date(year_val, month_val, 1)
        end_date = (start_date.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)

        employees = Employee.objects.all()
        
        # Apply department filter
        if department:
            employees = employees.filter(department__id=department)
            
        # Apply employee filter for monthly view
        if employee_monthly:
            employees = employees.filter(id=employee_monthly)

        results = []
        for emp in employees:
            # Only include dates after employee joining date
            emp_start = emp.joining_date if emp.joining_date else start_date
            effective_start = max(start_date, emp_start)
            
            # Skip if no valid date range
            if effective_start > end_date:
                continue
                
            current_date = effective_start
            while current_date <= end_date:
                att = Attendance.objects.filter(employee=emp, date=current_date).first()
                if att:
                    results.append(att)
                else:
                    # Only create default if after joining date
                    if current_date >= emp.joining_date:
                        results.append(Attendance(
                            employee=emp,
                            date=current_date,
                            status='present',
                            hours_worked=8.0,
                            overtime_hours=0.0
                        ))
                current_date += timedelta(days=1)

        return sorted(results, key=lambda x: x.date, reverse=True)

    def get_yearly_employee_data(self, employee_id, year):
        try:
            employee = Employee.objects.get(id=employee_id)
            year = int(year)
            
            monthly_data = []
            for month in range(1, 13):
                start_date = date(year, month, 1)
                end_date = (start_date.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
                
                # Skip months before joining date
                if employee.joining_date and employee.joining_date > end_date:
                    continue
                    
                # Adjust start date if after joining
                effective_start = max(start_date, employee.joining_date) if employee.joining_date else start_date
                
                # Skip if no valid range
                if effective_start > end_date:
                    continue
                
                # Query for attendance in this month
                attendances = Attendance.objects.filter(
                    employee=employee,
                    date__range=(effective_start, end_date))
                
                # Calculate summaries
                present_count = attendances.filter(status='present').count()
                absent_count = attendances.filter(status='absent').count()
                late_count = attendances.filter(status='late').count()
                total_hours = attendances.aggregate(Sum('hours_worked'))['hours_worked__sum'] or 0
                overtime_hours = attendances.aggregate(Sum('overtime_hours'))['overtime_hours__sum'] or 0
                days_in_period = (end_date - effective_start).days + 1
                
                monthly_data.append({
                    'month': start_date.strftime('%B'),
                    'start_date': start_date,
                    'end_date': end_date,
                    'present': present_count,
                    'absent': absent_count,
                    'late': late_count,
                    'total_hours': total_hours,
                    'overtime_hours': overtime_hours,
                    'days': days_in_period
                })
            
            return monthly_data
        except Employee.DoesNotExist:
            return []

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get filter parameters
        month = self.request.GET.get('month', timezone.now().strftime('%Y-%m'))
        year = self.request.GET.get('year', timezone.now().year)
        department = self.request.GET.get('department')
        employee_id = self.request.GET.get('employee')
        employee_monthly = self.request.GET.get('employee_monthly')
        view_type = self.request.GET.get('view_type', 'monthly')
        
        # Generate list of months for dropdown
        today = timezone.now().date()
        months = []
        for i in range(12):
            d = today - timedelta(days=30*i)
            months.append(d)
        
        # Get all departments and employees for dropdowns
        departments = Department.objects.all()
        employees = Employee.objects.all().order_by('name')
        
        # Calculate yearly summary for yearly view
        yearly_summary = None
        if view_type == 'yearly' and employee_id:
            attendances = context.get('attendances', [])
            total_present = sum(m['present'] for m in attendances)
            total_days = sum(m['days'] for m in attendances)
            total_hours = sum(m['total_hours'] for m in attendances)
            total_overtime = sum(m['overtime_hours'] for m in attendances)
            avg_attendance = (total_present / total_days * 100) if total_days > 0 else 0
            
            yearly_summary = {
                'total_present': total_present,
                'total_days': total_days,
                'total_hours': total_hours,
                'total_overtime': total_overtime,
                'avg_attendance': avg_attendance
            }
        
        # Add to context
        context.update({
            'months': months,
            'departments': departments,
            'employees': employees,
            'selected_month': month,
            'selected_dept': department,
            'selected_employee': int(employee_id) if employee_id else None,
            'selected_employee_monthly': int(employee_monthly) if employee_monthly else None,
            'selected_year': year,
            'view_type': view_type,
            'current_year': timezone.now().year,
            'yearly_summary': yearly_summary
        })
        
        return context


# Payroll Views
class PayrollCreateView(CreateView):
    model = Payroll
    form_class = PayrollForm
    template_name = 'core/payroll_form.html'
    success_url = reverse_lazy('payroll_list')

class PayrollListView(ListView):
    model = Payroll
    template_name = 'core/payroll_list.html'
    context_object_name = 'payrolls'
    paginate_by = 20
    ordering = ['-month']

class PayrollDetailView(DetailView):
    model = Payroll
    template_name = 'core/payroll_detail.html'
    context_object_name = 'payroll'