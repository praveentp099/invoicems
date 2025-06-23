# templatetags/attendance_tags.py (create this file)
from django import template
from ..models import Employee

register = template.Library()

@register.filter
def get_employee(queryset, employee_id):
    try:
        return queryset.get(id=employee_id)
    except Employee.DoesNotExist:
        return None