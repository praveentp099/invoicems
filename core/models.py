from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal, InvalidOperation

class Customer(models.Model):
    CUSTOMER_TYPE_CHOICES = [
        ('business', 'Business'),
        ('individual', 'Individual'),
    ]
    type = models.CharField(max_length=20, choices=CUSTOMER_TYPE_CHOICES, default='business')
    salutation = models.CharField(max_length=10, blank=True, null=True)
    first_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    company_name = models.CharField(max_length=255)
    display_name = models.CharField(max_length=255)
    email = models.EmailField()
    work_phone = models.CharField(max_length=20, blank=True, null=True)
    mobile = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField()
    po_box = models.CharField(max_length=100, blank=True, null=True)

    tin = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[('active', 'Active'), ('inactive', 'Inactive')], default='active')

    def __str__(self):
        return self.display_name

class Quote(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
        ('printed', 'Printed'),
    ]
    quote_number = models.CharField(max_length=100, unique=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    quote_date = models.DateField()
    expiry_date = models.DateField(blank=True, null=True)
    subject = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    created_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True)
    terms = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.quote_number
    
    @property
    def subtotal(self):
        """Calculate total before tax and discounts"""
        return sum(item.amount for item in self.items.all())
    
    @property
    def tax_amount(self):
        """Calculate 5% tax on subtotal"""
        return self.subtotal * Decimal('0.05')
    
    @property
    def total_amount(self):
        """Calculate final total including tax"""
        return self.subtotal + self.tax_amount

class QuoteItem(models.Model):
    UNIT_CHOICES = [
        ('LM', 'LM'),
        ('M2', 'M²'),
        ('LSM', 'LSM'),
        ('NOS', 'Nos'),
        ('UNIT', 'Unit'),
    ]
    
    quote = models.ForeignKey(Quote, related_name='items', on_delete=models.CASCADE)
    description = models.CharField(max_length=255)
    quantity = models.FloatField(default=1.0)
    unit = models.CharField(max_length=10, choices=UNIT_CHOICES, default='UNIT')
    rate = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)

    @property
    def amount(self):
        """Calculate item total after discount"""
        quantity = Decimal(str(self.quantity))
        rate = Decimal(str(self.rate))
        discount = Decimal(str(self.discount))
        
        # Calculate with Decimal arithmetic
        subtotal = quantity * rate
        discount_amount = subtotal * (discount / Decimal('100'))
        return subtotal - discount_amount

class Project(models.Model):
    name = models.CharField(max_length=255)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    target_amount = models.DecimalField(max_digits=10, decimal_places=2)
    achieved_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=[
        ('planning', 'Planning'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('delayed', 'Delayed')
    ], default='planning')
    
    def __str__(self):
        return self.name
    
class Invoice(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('paid', 'Paid'),
        ('overdue', 'Overdue'),
        ('cancelled', 'Cancelled'),
    ]
    
    invoice_number = models.CharField(max_length=100, unique=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    invoice_date = models.DateField(default=timezone.now)
    due_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    created_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True)
    terms = models.TextField(blank=True, null=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)

    def __str__(self):
        return self.invoice_number
    
    def update_total(self):
        self.total_amount = sum(item.total_price for item in self.items.all())
        self.save()

class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, related_name='items', on_delete=models.CASCADE)
    description = models.CharField(max_length=255)
    quantity = models.FloatField(default=1.0)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    tax = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    
    @property
    def total_price(self):
        return self.quantity * self.unit_price * (1 + self.tax/100)
    

class Department(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Employee(models.Model):
    EMPLOYEE_TYPE_CHOICES = [
        ('permanent', 'Permanent'),
        ('daily', 'Daily Wage'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    employee_id = models.CharField(max_length=20, unique=True)
    employee_type = models.CharField(max_length=20, choices=EMPLOYEE_TYPE_CHOICES)
    monthly_salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    daily_wage = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    overtime_rate = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    joining_date = models.DateField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.employee_id})"

class Attendance(models.Model):
    STATUS_CHOICES = (
        ('present', 'Present'),
        ('absent', 'Absent'),
    )
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='present')
    hours_worked = models.DecimalField(max_digits=4, decimal_places=1, default=8.0)
    overtime_hours = models.DecimalField(max_digits=4, decimal_places=1, default=0)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [['employee', 'date']]

    def __str__(self):
        return f"{self.employee.name} - {self.date} - {self.status}"


class Payroll(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    month = models.DateField()  # Stores first day of the month
    total_working_days = models.PositiveSmallIntegerField()
    days_worked = models.PositiveSmallIntegerField()
    total_overtime_hours = models.DecimalField(max_digits=6, decimal_places=1, default=0)
    gross_salary = models.DecimalField(max_digits=10, decimal_places=2)
    deductions = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    net_salary = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField(null=True, blank=True)
    is_paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Payroll for {self.employee.name} - {self.month.strftime('%B %Y')}"