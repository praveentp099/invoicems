from django.urls import path
from . import views
from .views import ProjectCreateView, ProjectUpdateView, ProjectListView

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # Customer URLs
    path('customers/', views.customer_list, name='customer_list'),
    path('customers/new/', views.customer_create, name='customer_create'),
    path('customers/<int:pk>/edit/', views.customer_edit, name='customer_edit'),
    path('customers/<int:pk>/delete/', views.customer_delete, name='customer_delete'),
    
    # Quote URLs
    path('quotes/', views.quote_list, name='quote_list'),
    path('quotes/new/', views.quote_create, name='quote_create'),
    path('quotes/<int:pk>/edit/', views.quote_edit, name='quote_edit'),
    path('quotes/<int:pk>/print/', views.quote_print, name='quote_print'),
    path('quotes/<int:pk>/delete/', views.quote_delete, name='quote_delete'),
    
    # Project URLs
    path('projects/', views.project_list, name='project_list'),
    path('projects/new/', views.project_create, name='project_create'),
    path('projects/<int:pk>/edit/', views.project_edit, name='project_edit'),
    path('projects/<int:pk>/delete/', views.project_delete, name='project_delete'),
    
    # Invoice URLs
    path('invoices/', views.invoice_list, name='invoice_list'),
    path('invoices/new/', views.invoice_create, name='invoice_create'),
    path('invoices/<int:pk>/', views.invoice_detail, name='invoice_detail'),
    path('invoices/<int:pk>/edit/', views.invoice_edit, name='invoice_edit'),
    path('invoices/<int:pk>/delete/', views.invoice_delete, name='invoice_delete'),
    path('invoices/<int:pk>/mark-paid/', views.mark_invoice_paid, name='mark_invoice_paid'),
    path('invoices/<int:pk>/pdf/', views.generate_pdf, name='generate_pdf'),
    path('test-pdf/', views.test_pdf, name='test_pdf'),
    path('payments/', views.payments, name='payments'),
    path('expenses/', views.expenses, name='expenses'),
    path('time-tracking/', views.time_tracking, name='time_tracking'),
    path('reports/', views.reports, name='reports'),

    # Projects
    path('projects/new/', ProjectCreateView.as_view(), name='project_create'),
    path('projects/<int:pk>/edit/', ProjectUpdateView.as_view(), name='project_edit'),
    path('projects/', ProjectListView.as_view(), name='project_list'),

     # Department URLs
    path('departments/', views.DepartmentListView.as_view(), name='department_list'),
    path('departments/create/', views.DepartmentCreateView.as_view(), name='department_create'),
    path('departments/<int:pk>/edit/', views.DepartmentUpdateView.as_view(), name='department_update'),
    path('departments/<int:pk>/delete/', views.DepartmentDeleteView.as_view(), name='department_delete'),
    
    # Employee URLs
    path('employees/', views.EmployeeListView.as_view(), name='employee_list'),
    path('employees/create/', views.EmployeeCreateView.as_view(), name='employee_create'),
    path('employees/<int:pk>/', views.EmployeeDetailView.as_view(), name='employee_detail'),
    path('employees/<int:pk>/edit/', views.EmployeeUpdateView.as_view(), name='employee_update'),
    path('employees/<int:pk>/delete/', views.EmployeeDeleteView.as_view(), name='employee_delete'),
    
    # Attendance URLs
    path('attendance/', views.AttendanceListView.as_view(), name='attendance_list'),
    path('attendance/create/', views.AttendanceCreateView.as_view(), name='attendance_create'),
    path('attendance/update/<int:pk>/', views.AttendanceUpdateView.as_view(), name='attendance_update'),
    path('attendance/delete/<int:pk>/', views.AttendanceDeleteView.as_view(), name='attendance_delete'),

    
    # Payroll URLs
    path('payroll/', views.PayrollListView.as_view(), name='payroll_list'),
    path('payroll/create/', views.PayrollCreateView.as_view(), name='payroll_create'),
    path('payroll/<int:pk>/', views.PayrollDetailView.as_view(), name='payroll_detail'),
]