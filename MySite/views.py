from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.template.loader import render_to_string

from .forms import LoginForm, PasswordChangeForm, StudentClearanceRequestForm
from .models import Student, StudentClearanceRequests, Faculty, Department, Hostel, Bursary


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')  # Redirect to your home page after successful login
            else:
                form.add_error_message('Invalid username or password')
    else:
        form = LoginForm()
    context = {'form': form}
    return render(request, 'login.html', context)


def register_view(request):
    if request.method == 'POST':
        email = request.POST['email'].strip()
        first_name = request.POST['first_name'].strip()
        last_name = request.POST['last_name'].strip()
        middle_name = request.POST['middle_name'].strip()
        matric_number = request.POST['matric_number'].strip()
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if Student.objects.filter(matric_number=matric_number).exists or not Student.objects.filter(email=email).exists:
            context = {'error': 'User already exists.'}
            return render(request, 'register.html', context)
        elif password != confirm_password:
            context = {'error': 'Password does not match.'}
            return render(request, 'register.html', context)
        else:
            # Create a new User object
            user = User.objects.create_user(username=matric_number, password=password)

            # Create a new Student object associated with the user
            student = Student(
                user=user,
                matric_number=matric_number,
                first_name=first_name,  # Assuming department object exists
                last_name=last_name,
                middle_name=middle_name,
                email=email,
            )
            student.save()

            return redirect('login')  # Redirect to your home page after successful registration

    else:
        context = {}
    return render(request, 'register.html', context)


def forgot_password_view(request):
    if request.method == 'POST':
        email = request.POST['email']
        try:
            user = User.objects.get(email=email)
            current_site = get_current_site(request)
            mail_subject = 'Password reset instructions'
            message = render_to_string('forgot_password_email.html', {
                'user': user,
                'domain': current_site.domain,
            })
            email_from = None  # Replace with your email address
            email_to = user.email
            send_mail(mail_subject, message, email_from, [email_to])
            context = {'message': 'A password reset link has been sent to your email.'}
            return render(request, 'forgot_password_sent.html', context)
        except User.DoesNotExist:
            context = {'error': 'Email address not found.'}
            return render(request, 'forgot_password.html', context)
    else:
        context = {}
    return render(request, 'forgot_password.html', context)


def retrieve_password_view(request, reset_uid):
    try:
        user = User.objects.get(pk=reset_uid)
    except User.DoesNotExist:
        return redirect('login')  # Redirect to login if user not found

    if request.method == 'POST':
        form = PasswordChangeForm(user, request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')  # Redirect to login after successful password change
    else:
        form = PasswordChangeForm(user)
    context = {'form': form}
    return render(request, 'change_password.html', context)


def change_password_view(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            form = PasswordChangeForm(request.user, request.POST)
            if form.is_valid():
                form.save()
                return redirect('login')  # Redirect to login after successful password change
        else:
            form = PasswordChangeForm(request.user)
    else:
        return redirect('login')  # Redirect to login if user is not authenticated
    context = {'form': form}
    return render(request, 'change_password.html', context)


def logout_view(request):
    logout(request)
    return redirect('login')  # Redirect to login after successful logout

@login_required
def student_dashboard_view(request):
    if request.user.is_staff or request.user.is_superuser:
        return redirect('home')  # Redirect staff/superuser to home

    student = Student.objects.get(user=request.user)  # Assuming Student has a user FK
    context = {'student': student}
    return render(request, 'student_dashboard.html', context)

@login_required
def student_clearance_request(request):
    if request.user.is_staff or request.user.is_superuser:
        return redirect('home')  # Redirect staff/superuser to home

    student = request.user.student  # Assuming Student has a user FK

    if request.method == 'GET':
        form = StudentClearanceRequestForm(initial={
            'student': student,
        })
    else:
        form = StudentClearanceRequestForm(request.POST)
        if form.is_valid():
            # Create or retrieve linked clearance requirement objects, explicitly setting student
            faculty_clearance, _ = Faculty.objects.get_or_create(
                name=form.cleaned_data['faculty'],
                defaults={'student': student},  # Associate student explicitly
            )
            department_clearance, _ = Department.objects.get_or_create(
                name=form.cleaned_data['department'],
                defaults={'student': student},  # Associate student explicitly
            )
            hostel_clearance, _ = Hostel.objects.get_or_create(
                name=form.cleaned_data['hostel'],
                defaults={'student': student},  # Associate student explicitly
            )
            # Bursary object creation logic (example)
            bursary_clearance, _ = Bursary.objects.get_or_create(
                student=student,  # Link bursary to student
            )

            # Create student clearance request with linked objects
            clearance_request = StudentClearanceRequests.objects.create(
                student=student,
                semester=form.cleaned_data['semester'],
                session=form.cleaned_data['session'],
                faculty_clearance=faculty_clearance,
                department_clearance=department_clearance,
                hostel_clearance=hostel_clearance,
                bursary_clearance=bursary_clearance,
            )
            return redirect('student_dashboard')  # Redirect to student dashboard

    context = {'form': form}
    return render(request, 'student_clearance_request.html', context)


class StudentClearanceDocumentForm:
    pass


@login_required
def student_upload_clearance(request):
    if request.user.is_staff or request.user.is_superuser:
        return redirect('home')  # Redirect staff/superuser to home

    student = request.user.student  # Assuming Student has a user FK

    if request.method == 'GET':
        form = StudentClearanceDocumentForm(initial={'student': student})
    else:
        form = StudentClearanceDocumentForm(request.POST, request.FILES)
        if form.is_valid():
            # Save uploaded document
            new_document = form.save(commit=False)  # Don't commit yet
            new_document.student = student  # Associate document with student
            new_document.save()

            # Get selected clearance type from form
            clearance_type = form.cleaned_data['clearance_type']

            # Create StudentClearanceRequest object if necessary
            clearance_request, created = StudentClearanceRequests.objects.get_or_create(
                student=student,
                semester=form.cleaned_data['semester'],
                session=form.cleaned_data['session'],
            )

            # Update clearance request based on clearance type
            if clearance_type == 'department':
                clearance_request.department_clearance = new_document
            elif clearance_type == 'faculty':
                clearance_request.faculty_clearance = new_document
            elif clearance_type == 'hostel':
                clearance_request.hostel_clearance = new_document
            elif clearance_type == 'bursary':
                clearance_request.bursary_clearance = new_document
            else:
                # Handle other clearance types if needed
                pass

            clearance_request.save()  # Save clearance request with linked document

            return redirect('student_dashboard')  # Redirect to student dashboard

    context = {'form': form}
    return render(request, 'student_upload_clearance.html', context)


@login_required
def student_clearance_status(request):
    if request.user.is_staff or request.user.is_superuser:
        return redirect('home')  # Redirect staff/superuser to home

    student = request.user.student  # Assuming Student has a user FK
    current_session = get_current_session(student)  # Replace with your logic to get current session

    # Prioritize Omega semester for the current session
    clearance_request = StudentClearanceRequests.objects.filter(
        student=student,
        session=current_session,
    ).order_by('-semester').first()  # Get most recent (Omega first)

    # If no request found for current session, check Alpha semester
    if not clearance_request:
        clearance_request = StudentClearanceRequests.objects.filter(
            student=student,
            session=current_session,
            semester=StudentClearanceRequests.SEMESTER_CHOICES[0][0]  # Alpha
        ).first()

    # Check for clearance status in linked objects (if any)
    department_status = 'N/A'
    faculty_status = 'N/A'
    hostel_status = 'N/A'
    bursary_status = 'N/A'

    if clearance_request:
        if clearance_request.department_clearance:
            department_status = clearance_request.department_clearance.status
        if clearance_request.faculty_clearance:
            faculty_status = clearance_request.faculty_clearance.status
        if clearance_request.hostel_clearance:
            hostel_status = clearance_request.hostel_clearance.status
        if clearance_request.bursary_clearance:
            bursary_status = clearance_request.bursary_clearance.status

    context = {
        'department_status': department_status,
        'faculty_status': faculty_status,
        'hostel_status': hostel_status,
        'bursary_status': bursary_status,
    }

    return render(request, 'student_clearance_status.html', context)

def get_current_session(student):
    left_side = []
    right_side = []

    # Get all sessions from student's clearance requests
    for clearance_request in StudentClearanceRequests.objects.filter(student=student):
        session_string = clearance_request.session
        first, second = session_string.split("/")
        left_side.append(int(first))
        right_side.append(int(second))

    return f"{max(left_side)}/{max(right_side)}"

@login_required
def staff_view_pending_clearances(request):
    if not request.user.is_staff:
        return redirect('home')  # Redirect non-staff users to home

    user_groups = request.user.groups.all()

    # Filter students based on user groups (if any)
    students = Student.objects.all()
    if user_groups:
        clearance_type = None
        if 'hostel' in [group.name.lower() for group in user_groups]:
            clearance_type = Hostel
        elif 'department' in [group.name.lower() for group in user_groups]:
            clearance_type = Department
        elif 'bursary' in [group.name.lower() for group in user_groups]:
            clearance_type = Bursary
        elif 'faculty' in [group.name.lower() for group in user_groups]:
            clearance_type = Faculty

        if clearance_type:
            pending_requests = StudentClearanceRequests.objects.filter(
                student__in=students,
                clearance_type=clearance_type,
                status='pending'
            )
            students = pending_requests.values_list('student', flat=True).distinct()  # Get unique students

    context = {'students': students}
    return render(request, 'staff_view_pending_clearances.html', context)


@login_required
def staff_view_student_clearance_details(request, student_id):
    if not request.user.is_staff:
        return redirect('home')  # Redirect non-staff users to home

    user_groups = request.user.groups.all()
    student = get_object_or_404(Student, pk=student_id)

    # Filter pending requests based on user groups (if any)
    pending_requests = StudentClearanceRequests.objects.filter(
        student=student,
        status='pending'
    )
    if user_groups:
        clearance_type = None
        if 'hostel' in [group.name.lower() for group in user_groups]:
            clearance_type = Hostel
        elif 'department' in [group.name.lower() for group in user_groups]:
            clearance_type = Department
        elif 'bursary' in [group.name.lower() for group in user_groups]:
            clearance_type = Bursary
        elif 'faculty' in [group.name.lower() for group in user_groups]:
            clearance_type = Faculty

        if clearance_type:
            pending_requests = pending_requests.filter(clearance_type=clearance_type)

    context = {
        'student': student,
        'pending_requests': pending_requests,
        'can_send_email': len(user_groups) > 0 and clearance_type is not None,
    }

    if request.method == 'POST' and context['can_send_email']:
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        if subject and message:
            send_mail(
                subject,
                message,
                'staff@yourdomain.com',  # Replace with email sender
                [student.email],  # Recipient email
                fail_silently=False,  # Set to True to hide errors
            )
            return redirect('staff_view_student_clearance_details', student_id=student_id)
        else:
            context['error_message'] = 'Subject and message are required to send email.'

    return render(request, 'staff_view_student_clearance_details.html', context)
