from django import forms
from .models import Customer, Quote, QuoteItem, Project,Invoice, InvoiceItem, Department, Employee, Attendance, Payroll

from django.forms import inlineformset_factory

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = [
            'type', 'salutation', 'first_name', 'last_name',
            'company_name', 'display_name', 'email', 'work_phone',
            'mobile', 'address', 'tin','po_box'
        ]
        widgets = {
            'type': forms.Select(attrs={'class': 'form-control'}),
            'salutation': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'company_name': forms.TextInput(attrs={'class': 'form-control'}),
            'display_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'work_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'mobile': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'tin': forms.TextInput(attrs={'class': 'form-control'}),
            'po_box': forms.TextInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),

        }

class QuoteForm(forms.ModelForm):
    class Meta:
        model = Quote
        fields = ['quote_number', 'customer', 'quote_date', 'expiry_date', 'subject', 'notes', 'terms']
        widgets = {
            'quote_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'expiry_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'terms': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class QuoteItemForm(forms.ModelForm):
    class Meta:
        model = QuoteItem
        fields = ['description', 'quantity', 'unit', 'rate', 'discount']
        widgets = {
            'unit': forms.Select(attrs={'class': 'form-control'}),
        }

QuoteItemFormSet = inlineformset_factory(Quote, QuoteItem, form=QuoteItemForm, extra=1, can_delete=True)

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = '__all__'
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }

class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = ['invoice_number', 'customer', 'invoice_date', 'due_date', 'status', 'notes', 'terms']
        widgets = {
            'invoice_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'due_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'terms': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class InvoiceItemForm(forms.ModelForm):
    class Meta:
        model = InvoiceItem
        fields = ['description', 'quantity', 'unit_price', 'tax']
        
InvoiceItemFormSet = inlineformset_factory(
    Invoice, 
    InvoiceItem, 
    form=InvoiceItemForm, 
    extra=1, 
    can_delete=True
)

Department, Employee, Attendance, Payroll

class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['name', 'description']

class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ['name', 'department', 'employee_id', 'employee_type', 
                  'monthly_salary', 'daily_wage', 'overtime_rate', 
                  'joining_date', 'is_active']
        
        widgets = {'joining_date': forms.DateInput(attrs={'type': 'date','class': 'form-control'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        employee_type = cleaned_data.get('employee_type')
        monthly_salary = cleaned_data.get('monthly_salary')
        daily_wage = cleaned_data.get('daily_wage')
        
        if employee_type == 'permanent' and not monthly_salary:
            raise forms.ValidationError("Monthly salary is required for permanent employees.")
        if employee_type == 'daily' and not daily_wage:
            raise forms.ValidationError("Daily wage is required for daily wage employees.")
        
        return cleaned_data

class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ['employee', 'date', 'status', 'hours_worked', 'overtime_hours','notes']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['status'].initial = 'absent'
        self.fields['status'].disabled = True 

class PayrollForm(forms.ModelForm):
    class Meta:
        model = Payroll
        fields = ['employee', 'month', 'total_working_days', 'days_worked', 
                  'total_overtime_hours', 'gross_salary', 'deductions', 
                  'net_salary', 'payment_date', 'is_paid']