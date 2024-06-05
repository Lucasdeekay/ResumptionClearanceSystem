from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.template.loader import render_to_string

from .forms import LoginForm, PasswordChangeForm, StudentClearanceRequestForm, StudentClearanceDocumentForm
from .models import Student, StudentClearanceRequests, Faculty, Department, Hostel, Bursary, ClearanceRequirement, \
    ClearanceDocument


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('student_dashboard')  # Redirect to your home page after successful login
            else:
                messages.error(request, 'Invalid username or password')
                return redirect('login')
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
            messages.error(request, 'User already exists.')
            return redirect('register')
        elif password != confirm_password:
            messages.error(request, 'Password does not match.')
            return redirect('register')
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
            messages.error(request, 'Registration successful.')
            return redirect('login')  # Redirect to your home page after successful registration

    else:
        context = {}
    return render(request, 'register.html', context)


def forgot_password_view(request):
    if request.method == 'POST':
        email = request.POST['email']
        try:
            student = Student.objects.get(email=email)
            current_site = get_current_site(request)
            mail_subject = 'Password reset instructions'
            message = render_to_string('forgot_password_email.html', {
                'student': student.id,
                'domain': current_site.domain,
            })
            email_from = None  # Replace with your email address
            email_to = student.email
            send_mail(mail_subject, message, email_from, [email_to])
            messages.success(request, 'A password reset link has been sent to your email.')
            return redirect('login')
        except User.DoesNotExist:
            messages.success(request, 'Email address not found.')
            return redirect('forgot_password')
    else:
        return render(request, 'forgot_password.html')


def retrieve_password_view(request, reset_uid):
    try:
        student = Student.objects.get(pk=reset_uid)
    except User.DoesNotExist:
        return redirect('login')  # Redirect to login if user not found

    if request.method == 'POST':
        form = PasswordChangeForm(student, request.POST)
        if form.is_valid():
            password = form.clean_new_password()
            student.set_password(password)
            student.save()
            messages.success(request, 'Account password has been successfully reset.')
            return redirect('login')  # Redirect to login after successful password change
    else:
        form = PasswordChangeForm(student)
    context = {'form': form}
    return render(request, 'change_password.html', context)


@login_required
def change_password_view(request):
    student = Student.objects.get(user=request.user)
    if request.method == 'POST':
        old_password = request.POST['old_password']
        new_password = request.POST['new_password']
        confirm_password = request.POST['confirm_password']
        if new_password == confirm_password and student.user.check_password(old_password):
            student.set_password(new_password)
            student.save()
            messages.success(request, "Password successfully changed")
            return redirect('student_dashboard')
        else:
            messages.success(request, "Password does not match")
            return redirect('change_password')
    return render(request, 'change_password.html')


@login_required
def logout_view(request):
    logout(request)
    return redirect('login')  # Redirect to login after successful logout


@login_required
def student_dashboard_view(request):
    if request.user.is_staff or request.user.is_superuser:
        messages.error(request, "User does not have authorized access")
        return redirect('login')  # Redirect staff/superuser to home

    student = Student.objects.get(user=request.user)  # Assuming Student has a user FK
    context = {'student': student}
    return render(request, 'student_dashboard.html', context)


@login_required
def student_clearance_request(request):
    if request.user.is_staff or request.user.is_superuser:
        messages.error(request, "User does not have authorized access")
        return redirect('login')  # Redirect staff/superuser to home

    student = Student.objects.get(user=request.user)  # Assuming Student has a user FK

    if request.method == 'GET':
        form = StudentClearanceRequestForm()
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
                faculty=faculty_clearance,
                department=department_clearance,
                hostel=hostel_clearance,
                bursary=bursary_clearance,
            )
            clearance_request.save()
            messages.error(request, "Clearance request has been successfully submitted")
            return redirect('student_clearance_request')  # Redirect to student dashboard

    context = {'form': form, 'student': student}
    return render(request, 'student_clearance_request.html', context)


@login_required
def student_upload_clearance(request):
    if request.user.is_staff or request.user.is_superuser:
        messages.error(request, "User does not have authorized access")
        return redirect('login')  # Redirect staff/superuser to home

    student = Student.objects.get(user=request.user)  # Assuming Student has a user FK

    if request.method == 'GET':
        form = StudentClearanceDocumentForm()
    else:
        form = StudentClearanceDocumentForm(request.POST, request.FILES)
        if form.is_valid():

            semester = form.cleaned_data['semester']
            session = form.cleaned_data['session']
            clearance_type = form.cleaned_data['clearance_type']
            document_type = form.cleaned_data['document_type']
            description = form.cleaned_data['description']
            file = form.cleaned_data['file']

            # Save uploaded document
            new_document = form.save(commit=False)  # Don't commit yet
            new_document.student = student  # Associate document with student
            new_document.save()

            # Create StudentClearanceRequest object if necessary
            clearance_request, created = StudentClearanceRequests.objects.get_or_create(
                student=student,
                semester=semester,
                session=session,
            )

            clearance_document = ClearanceDocument.objects.create(
                file=file,
                description=description,
                document_type=document_type,
            )

            # Update clearance request based on clearance type
            if clearance_type == 'department':
                department = Department.objects.get_or_create(student=student, status__in=['Pending', 'Incomplete'])
                department.documents.add(clearance_document)

                department.save()

            elif clearance_type == 'faculty':
                faculty = Faculty.objects.get_or_create(student=student, status__in=['Pending', 'Incomplete'])
                faculty.documents.add(clearance_document)

                faculty.save()

            elif clearance_type == 'hostel':
                hostel = Hostel.objects.get_or_create(student=student, status__in=['Pending', 'Incomplete'])
                hostel.documents.add(clearance_document)

                hostel.save()

            elif clearance_type == 'bursary':
                bursary = Bursary.objects.get_or_create(student=student, status__in=['Pending', 'Incomplete'])
                bursary.documents.add(clearance_document)

                bursary.save()

            else:
                # Handle other clearance types if needed
                pass

            clearance_request.save()  # Save clearance request with linked document
            messages.error(request, "Clearance request has been successfully submitted")
            return redirect('student_clearance_request')  # Redirect to student dashboard

    context = {'form': form, 'student': student}
    return render(request, 'student_upload_clearance.html', context)


@login_required
def student_clearance_status(request):
    if request.user.is_staff or request.user.is_superuser:
        messages.error(request, "User does not have authorized access")
        return redirect('login')  # Redirect staff/superuser to home

    student = Student.objects.get(user=request.user)  # Assuming Student has a user FK
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

    context = {
        'department_status': clearance_request.department.status,
        'faculty_status': clearance_request.faculty.status,
        'hostel_status': clearance_request.hostel.status,
        'bursary_status': clearance_request.bursary.status,
        'student': student,
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
