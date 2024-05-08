from django.contrib import admin
from .models import (
    Student, ClearanceRequirement, Department, Faculty, Hostel, Bursary, StudentClearanceRequests
)

class ClearanceRequirementAdmin(admin.ModelAdmin):
    list_display = ["document_type", "status"]  # Display document type and status

class DepartmentAdmin(admin.ModelAdmin):
    list_display = ["name"]  # Display department name

class FacultyAdmin(admin.ModelAdmin):
    list_display = ["name"]  # Display faculty name

class HostelAdmin(admin.ModelAdmin):
    list_display = ["name"]  # Display hostel name

class BursaryAdmin(admin.ModelAdmin):
    list_display = ["total_amount_paid", "total_fees", "outstanding_fees"]  # Display financial details

class StudentAdmin(admin.ModelAdmin):
    list_display = ["user__username", "first_name", "last_name", "matric_number", "email"]  # Display student details

class StudentClearanceRequestsAdmin(admin.ModelAdmin):
    list_display = ["student", "semester", "session"]  # Display student, semester, and session

# Register the models with the admin site
admin.site.register(Student, StudentAdmin)
admin.site.register(ClearanceRequirement, ClearanceRequirementAdmin)
admin.site.register(Department, DepartmentAdmin)
admin.site.register(Faculty, FacultyAdmin)
admin.site.register(Hostel, HostelAdmin)
admin.site.register(Bursary, BursaryAdmin)
admin.site.register(StudentClearanceRequests, StudentClearanceRequestsAdmin)
