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
        matric_number = request.POST['matric_number'].strip()
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if Student.objects.filter(matric_number=matric_number).exists() or Student.objects.filter(email=email).exists():
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
                first_name=first_name,
                last_name=last_name,
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
            user = User.objects.get(email=email)
            login(request, user)
            return redirect('retrieve_password')
        except User.DoesNotExist:
            messages.success(request, 'Email address not found.')
            return redirect('forgot_password')
    else:
        return render(request, 'forgot_password.html')


def retrieve_password_view(request):
    user = request.user

    if request.method == 'POST':
        new_password1 = request.POST['new_password'].strip()
        new_password2 = request.POST['confirm_password'].strip()
        if new_password1 != new_password2:
            messages.error(request, 'Passwords do not match.')
            return redirect('retrieve_password')
        # Set the new password
        user.set_password(new_password1)
        user.save()
        logout(request)
        messages.success(request, 'Password reset successfully!')
        return redirect('login')
    return render(request, 'password_reset.html')


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
    return render(request, 'change_password.html', {'student': student})


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
                semester=form.cleaned_data['semester'],
                session=form.cleaned_data['session'],
                defaults={'student': student},  # Associate student explicitly
            )
            department_clearance, _ = Department.objects.get_or_create(
                name=form.cleaned_data['department'],
                semester=form.cleaned_data['semester'],
                session=form.cleaned_data['session'],
                defaults={'student': student},  # Associate student explicitly
            )
            hostel_clearance, _ = Hostel.objects.get_or_create(
                name=form.cleaned_data['hostel'],
                semester=form.cleaned_data['semester'],
                session=form.cleaned_data['session'],
                defaults={'student': student},  # Associate student explicitly
            )
            # Bursary object creation logic (example)
            bursary_clearance, _ = Bursary.objects.get_or_create(
                student=student,  # Link bursary to student
                semester=form.cleaned_data['semester'],
                session=form.cleaned_data['session'],
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
                department, is_created = Department.objects.get_or_create(student=student, semester=semester,
                                                                          session=session,
                                                                          status__in=['pending', 'incomplete'])
                department.documents.add(clearance_document)

                department.save()

            elif clearance_type == 'faculty':
                faculty, is_created = Faculty.objects.get_or_create(student=student, semester=semester, session=session,
                                                                    status__in=['pending', 'incomplete'])
                faculty.documents.add(clearance_document)

                faculty.save()

            elif clearance_type == 'hostel':
                hostel, is_created = Hostel.objects.get_or_create(student=student, semester=semester, session=session,
                                                                  status__in=['pending', 'incomplete'])
                hostel.documents.add(clearance_document)

                hostel.save()

            elif clearance_type == 'bursary':
                bursary, is_created = Bursary.objects.get_or_create(student=student, semester=semester, session=session,
                                                                    status__in=['pending', 'incomplete'])
                bursary.documents.add(clearance_document)

                bursary.save()

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

    # Prioritize Omega semester for the current session
    clearance_request = StudentClearanceRequests.objects.filter(
        student=student,
    ).order_by('-semester').first()  # Get most recent (Omega first)

    # If no request found for current session, check Alpha semester
    if clearance_request:
        context = {
            'department_status': clearance_request.department.status,
            'faculty_status': clearance_request.faculty.status,
            'hostel_status': clearance_request.hostel.status,
            'bursary_status': clearance_request.bursary.status,
            'student': student,
        }
    else:
        context = {
            'department_status': 'Unknown',
            'faculty_status': 'Unknown',
            'hostel_status': 'Unknown',
            'bursary_status': 'Unknown',
            'student': student,
        }

    return render(request, 'student_clearance_status.html', context)
