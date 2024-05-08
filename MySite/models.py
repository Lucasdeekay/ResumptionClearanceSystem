from django.contrib.auth.models import User
from django.db import models


class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    first_name = models.CharField(max_length=255, blank=False)
    last_name = models.CharField(max_length=255, blank=False)
    middle_name = models.CharField(max_length=255, blank=True)  # Optional middle name
    matric_number = models.CharField(max_length=255, unique=True)
    email = models.EmailField(unique=True)  # Ensure unique email


class ClearanceRequirement(models.Model):
    """
    Base model for clearance requirements
    """
    description = models.TextField()
    document_type = models.CharField(max_length=255, choices=(
        ('course_form_100l_alpha', 'Course Form (100L Alpha Semester)'),
        ('course_form_100l_omega', 'Course Form (100L Omega Semester)'),
        ('course_form_200l_alpha', 'Course Form (200L Alpha Semester)'),
        ('course_form_200l_omega', 'Course Form (200L Omega Semester)'),
        ('course_form_300l_alpha', 'Course Form (300L Alpha Semester)'),
        ('course_form_300l_omega', 'Course Form (300L Omega Semester)'),
        ('course_form_400l_alpha', 'Course Form (400L Alpha Semester)'),
        ('course_form_400l_omega', 'Course Form (400L Omega Semester)'),
        ('bio_data', 'Bio-data'),
        ('local_government_certificate', 'Local Government Certificate'),
        ('birth_certificate', 'Birth Certificate'),
        ('jamb_admission_letter', 'Jamb Admission Letter'),
        ('du_admission_letter', 'DU Admission Letter'),
        ('letter_of_undertaking', 'Letter of Undertaking'),
    ))
    status = models.CharField(max_length=255, choices=(
    ('pending', 'Pending'), ('completed', 'Completed'), ('incomplete', 'Incomplete')))

    class Meta:
        abstract = True


DEPARTMENT_CHOICES = (
    ('computer_science', 'Computer Science'),
    ('software_engineering', 'Software Engineering'),
    ('cyber_security', 'Cyber Security'),
    ('microbiology', 'Microbiology'),
    ('biochemistry', 'Biochemistry'),
    ('industrial_chemistry', 'Industrial Chemistry'),
    ('economics', 'Economics'),
    ('accounting', 'Accounting'),
    ('business_administration', 'Business Administration'),
    ('mass_communication', 'Mass Communication'),
    ('criminology', 'Criminology'),
)

class Department(ClearanceRequirement):
    name = models.CharField(max_length=255, choices=DEPARTMENT_CHOICES, unique=True)




FACULTY_CHOICES = (
    ('computing_and_applied_sciences', 'Computing and Applied Sciences'),
    ('arts_and_management_sciences', 'Arts and Management Sciences'),
)

class Faculty(ClearanceRequirement):
    name = models.CharField(max_length=255, choices=FACULTY_CHOICES, unique=True)



HOSTEL_CHOICES = (
    ('victory_hall', 'Victory Hall'),
    ('faith_hall', 'Faith Hall'),
    ('bishop_hall', 'Bishop Hall'),
    ('new_hall', 'New Hall'),
    ('rehoboth_hall', 'Rehoboth Hall'),
)

class Hostel(models.Model):
    """
    Hostel model inherits from ClearanceRequirement
    """
    name = models.CharField(max_length=255, unique=True)


class Bursary(ClearanceRequirement):
    """
    Bursary model inherits from ClearanceRequirement
    """
    total_amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    total_fees = models.DecimalField(max_digits=10, decimal_places=2)
    outstanding_fees = models.DecimalField(max_digits=10, decimal_places=2)

class StudentClearanceRequests(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    semester = models.CharField(max_length=255)

    SESSION_CHOICES = [(str(y) + '/' + str(y + 1), str(y) + '/' + str(y + 1)) for y in range(2023, 2030)]
    session = models.CharField(max_length=11, choices=SESSION_CHOICES, default=SESSION_CHOICES[0][0])

    # Foreign keys to clearance requirement models (inherited by Faculty, Department, Hostel, Bursary)
    faculty_clearance = models.ForeignKey(Faculty, on_delete=models.CASCADE, blank=True, null=True,
                                          related_name='faculty_clearance_requests')
    department_clearance = models.ForeignKey(Department, on_delete=models.CASCADE, blank=True, null=True,
                                             related_name='department_clearance_requests')
    hostel_clearance = models.ForeignKey(Hostel, on_delete=models.CASCADE, blank=True, null=True,
                                         related_name='hostel_clearance_requests')
    bursary_clearance = models.ForeignKey(Bursary, on_delete=models.CASCADE, blank=True, null=True,
                                          related_name='bursary_clearance_requests')

    def __str__(self):
        return f"{self.student} - {self.semester} ({self.session})"

