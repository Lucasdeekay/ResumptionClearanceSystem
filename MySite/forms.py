from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm

from MySite.models import StudentClearanceRequests, DEPARTMENT_CHOICES, FACULTY_CHOICES, HOSTEL_CHOICES, \
    ClearanceDocument, SESSION_CHOICES, SEMESTER_CHOICES

User = get_user_model()


class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Matric Number', 'required': ''}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password', 'required': ''}))

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        self.fields['username'].label = ""
        self.fields['password'].label = ""

    def clean(self):
        cleaned_data = super(LoginForm, self).clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')
        if not username or not password:
            raise forms.ValidationError("Field cannot be empty")


class PasswordChangeForm(PasswordChangeForm):
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'New Password', 'required': ''}))
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm Password', 'required': ''}))

    def clean_new_password(self):
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                self.error_messages['password_mismatch'],
                code='password_mismatch',
            )
        return password2

    def __init__(self, *args, **kwargs):
        super(PasswordChangeForm, self).__init__(*args, **kwargs)
        self.fields['new_password1'].label = ""
        self.fields['new_password2'].label = ""


class StudentClearanceRequestForm(forms.Form):
    faculty = forms.CharField(
        widget=forms.Select(choices=(('', 'Select Faculty'),) + FACULTY_CHOICES,
                            attrs={'class': 'form-control p-3', 'required': ''}))
    department = forms.CharField(widget=forms.Select(choices=(('', 'Select Department'),) + DEPARTMENT_CHOICES,
                                                     attrs={'class': 'form-control p-3', 'required': ''}))
    hostel = forms.CharField(
        widget=forms.Select(choices=(('', 'Select Hostel'),) + HOSTEL_CHOICES,
                            attrs={'class': 'form-control p-3', 'required': ''}))
    session = forms.CharField(
        widget=forms.Select(choices=[('', 'Select Session'), ] + SESSION_CHOICES,
                            attrs={'class': 'form-control p-3', 'required': ''}))
    semester = forms.CharField(
        widget=forms.Select(choices=(('', 'Select Semester'),) + SEMESTER_CHOICES,
                            attrs={'class': 'form-control p-3', 'required': ''}))


class StudentClearanceDocumentForm(forms.Form):
    file = forms.CharField(widget=forms.FileInput(attrs={'class': 'form-control p-3', 'required': ''}))
    description = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control p-3', 'required': '', 'placeholder': 'Type here'}))
    document_type = forms.CharField(
        widget=forms.Select(choices=(
            ('', 'Select Document Type'),
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
            ('others', 'Others'),
        ), attrs={'class': 'form-control p-3', 'required': ''}))
    clearance_type = forms.CharField(
        widget=forms.Select(choices=(
            ('', 'Select Clearance Type'),
            ('department', 'Department'),
            ('faculty', 'Faculty'),
            ('hostel', 'Hostel'),
            ('bursary', 'Bursary'),
        ), attrs={'class': 'form-control p-3', 'required': ''}))
    session = forms.CharField(
        widget=forms.Select(choices=[('', 'Select Session'), ] + SESSION_CHOICES,
                            attrs={'class': 'form-control p-3', 'required': ''}))
    semester = forms.CharField(
        widget=forms.Select(choices=(('', 'Select Semester'),) + SEMESTER_CHOICES, attrs={'class': 'form-control p-3', 'required': ''}))


