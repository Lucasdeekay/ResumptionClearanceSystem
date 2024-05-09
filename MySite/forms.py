from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm,  PasswordChangeForm

from MySite.models import StudentClearanceRequests, Faculty, Department, Hostel, ClearanceDocument

User = get_user_model()

class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        self.fields['username'].label = ""
        self.fields['password'].label = ""


class PasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Old Password'}))
    new_password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'New Password'}))
    new_password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm Password'}))

    def __init__(self, *args, **kwargs):
        super(PasswordChangeForm, self).__init__(*args, **kwargs)
        self.fields['old_password'].label = ""
        self.fields['new_password1'].label = ""
        self.fields['new_password2'].label = ""


class StudentClearanceRequestForm(forms.ModelForm):
    class Meta:
        model = StudentClearanceRequests
        fields = ['faculty', 'department', 'hostel', 'semester', 'session']
        widgets = {
            'faculty': forms.Select(choices=Faculty.objects.all().values_list('name', 'name')),
            'department': forms.Select(choices=Department.objects.all().values_list('name', 'name')),
            'hostel': forms.Select(choices=Hostel.objects.all().values_list('name', 'name')),
            'semester': forms.ChoiceField(choices=StudentClearanceRequests.SEMESTER_CHOICES),
            'session': forms.ChoiceField(choices=StudentClearanceRequests.SESSION_CHOICES),
        }


class StudentClearanceDocumentForm(forms.ModelForm):
    clearance_type = forms.ChoiceField(choices=(
        ('department', 'Department'),
        ('faculty', 'Faculty'),
        ('hostel', 'Hostel'),
        ('bursary', 'Bursary'),
    ))
    semester = forms.ChoiceField(choices=StudentClearanceRequests.SEMESTER_CHOICES)
    session = forms.ChoiceField(choices=StudentClearanceRequests.SESSION_CHOICES)

    class Meta:
        model = ClearanceDocument
        fields = ['file', 'description', 'document_type', 'clearance_type', 'semester', 'session']
