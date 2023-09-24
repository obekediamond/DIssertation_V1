from django.http.response import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.views.generic import CreateView, ListView
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils.decorators import method_decorator
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, PasswordChangeForm
from .decorators import lecturer_required, student_required, admin_required
from course.models import Course
from scores.models import UsersCourses
from institution.models import Session, Trimester
from .forms import LecturerAddForm, StudentAddForm, ProfileUpdateForm
from .models import User, Student
from django.core.mail import send_mail
from django.conf import settings


# def compare_code(instructor_code, student_code):
#     # Step 1: Compare code similarity using difflib
#     code_similarity_ratio = difflib.SequenceMatcher(None, instructor_code, student_code).ratio()
#
#     # Step 2: Run both codes and compare outputs
#     instructor_output = run_code(instructor_code)
#     student_output = run_code(student_code)
#
#     # Step 3: Compare the outputs
#     output_similarity_ratio = difflib.SequenceMatcher(None, instructor_output, student_output).ratio()
#
#     return code_similarity_ratio, output_similarity_ratio

def validate_user(request):
    user = request.GET.get("username", None)
    user_data = {
        "is_taken": User.objects.filter(username__iexact=user).exists()
    }
    return JsonResponse(user_data)


def register(request):
    if request.method == 'POST':
        form = StudentAddForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, f'Account Creation Successful')
        else:
            messages.error(request, f'Please review all fields, correct the errors and retry.')
    else:
        form = StudentAddForm(request.POST)
    return render(request, "registration/register.html", {'form': form})


@login_required
def profile(request):
    # View users profile
    try:
        session = get_object_or_404(Session, is_current_session=True)
        trimester = get_object_or_404(Trimester, is_current_trimester=True, session=session)
    except Trimester.MultipleObjectsReturned and Trimester.DoesNotExist and Session.DoesNotExist:
        raise Http404
    if request.user.is_lecturer:
        courses = Course.objects.filter(allocated_course__lecturer__pk=request.user.id).filter(
            trimester=trimester)
        return render(request, 'accounts/profile.html', {
            'title': request.user.get_full_name,
            "courses": courses,
            'current_session': session,
            'current_trimester': trimester,
        })
    elif request.user.is_student:
        level = Student.objects.get(student__pk=request.user.id)
        courses = UsersCourses.objects.filter(student__student__id=request.user.id, course__level=level.level)
        context = {
            'courses': courses,
            'level': level,
            'current_session': session,
            'title': request.user.get_full_name,
            'current_trimester': trimester,
        }
        return render(request, 'accounts/profile.html', context)
    else:
        admin = User.objects.filter(is_lecturer=True)
        return render(request, 'accounts/profile.html', {
            'title': request.user.get_full_name,
            "staff": admin,
            'current_session': session,
            'current_trimester': trimester,
        })


@login_required
@admin_required
def profile_from_admin(request, id):
    # View other user's profile as an admin
    if request.user.id == id:
        return redirect("/profile/")
    session = get_object_or_404(Session, is_current_session=True)
    trimester = get_object_or_404(Trimester, is_current_trimester=True, session=session)
    user = User.objects.get(pk=id)
    if user.is_lecturer:
        courses = Course.objects.filter(allocated_course__lecturer__pk=id).filter(trimester=trimester)
        context = {
            'title': user.get_full_name,
            "user": user,
            "user_type": "Lecturer",
            "courses": courses,
            'current_session': session,
            'current_trimester': trimester,
        }
        return render(request, 'accounts/profile_from_admin.html', context)
    elif user.is_student:
        student = Student.objects.get(student__pk=id)
        courses = UsersCourses.objects.filter(student__student__id=id, course__level=student.level)
        context = {
            'title': user.get_full_name,
            'user': user,
            "user_type": "student",
            'courses': courses,
            'student': student,
            'current_session': session,
            'current_trimester': trimester,
        }
        return render(request, 'accounts/profile_from_admin.html', context)
    else:
        context = {
            'title': user.get_full_name,
            "user": user,
            "user_type": "superuser",
            'current_session': session,
            'current_trimester': trimester,
        }
        return render(request, 'accounts/profile_from_admin.html', context)


@login_required
@admin_required
def admin_panel(request):
    return render(request, 'setting/admin_panel.html', {})


@login_required
def update_profile(request):
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('profile')
        else:
            messages.error(request, 'Please correct the error(s) below.')
    else:
        form = ProfileUpdateForm(instance=request.user)
    return render(request, 'setting/profile_info_change.html', {
        'title': 'Setting',
        'form': form,
    })


@login_required
def password_change(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Password Change Successful!')
            return redirect('profile')
        else:
            messages.error(request, 'Please correct all errors and try again ')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'setting/password_change.html', {
        'form': form,
    })


@login_required
@admin_required
def lecturer_add_view(request):
    if request.method == 'POST':
        form = LecturerAddForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data.get('first_name')
            last_name = form.cleaned_data.get('last_name')
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            email = form.cleaned_data.get('email')

            # Create the user and send an email
            user = form.save()
            message = "Dear " + first_name + ' ' + last_name + ", your account with username: " + username + \
                      " and password: " + password + " has been created. \n Ensure you change your password upon login."
            send_mail('Account Created', message, 'settings.EMAIL_HOST_USER', [email], fail_silently=False)

            messages.success(request, "Lecturer: " + first_name + ' ' + last_name + " created"
                                                                                    " and credentials sent via mail")
            return redirect("lecturer_list")
    else:
        form = LecturerAddForm()

    context = {
        'title': 'Lecturer Add',
        'form': form,
    }
    return render(request, 'accounts/add_lecturer.html', context)


@login_required
@admin_required
def edit_lecturer(request, pk):
    instance = get_object_or_404(User, is_lecturer=True, pk=pk)
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=instance)
        full_name = instance.get_full_name
        if form.is_valid():
            form.save()

            messages.success(request, 'Lecturer ' + full_name + ' has been updated.')
            return redirect('lecturer_list')
        else:
            messages.error(request, 'Please correct all errors and try again ')
    else:
        form = ProfileUpdateForm(instance=instance)
    return render(request, 'accounts/edit_lecturer.html', {
        'title': 'Edit Lecturer',
        'form': form,
    })


@method_decorator([login_required, admin_required], name='dispatch')
class LecturerListView(ListView):
    queryset = User.objects.filter(is_lecturer=True)
    template_name = "accounts/lecturer_list.html"
    paginate_by = 10
    ordering = ['username']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Lecturers"
        return context


@login_required
@admin_required
def delete_lecturer(request, pk):
    lecturer = get_object_or_404(User, pk=pk)
    full_name = lecturer.get_full_name
    lecturer.delete()
    messages.success(request, 'Lecturer ' + full_name + ' has been deleted.')
    return redirect('lecturer_list')


@login_required
@admin_required
def student_add_view(request):
    if request.method == 'POST':
        form = StudentAddForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data.get('first_name')
            last_name = form.cleaned_data.get('last_name')
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            email = form.cleaned_data.get('email')

            # Create the user and send an email
            user = form.save()
            message = f"Dear {first_name} {last_name}, your account with username: {username} " \
                      f"and password: {password} has been created. \nEnsure you change your password upon login."
            send_mail('Account Created', message, 'settings.EMAIL_HOST_USER', [email], fail_silently=False)

            messages.success(request, f'Account for {first_name} {last_name} has been created'
                                      ' and credentials sent via email')
            return redirect('student_list')
    else:
        form = StudentAddForm()

    return render(request, 'accounts/add_student.html', {
        'title': "Add Student",
        'form': form
    })


@login_required
@admin_required
def edit_student(request, pk):
    instance = get_object_or_404(User, is_student=True, pk=pk)
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=instance)
        full_name = instance.get_full_name
        if form.is_valid():
            form.save()

            messages.success(request, ('Student ' + full_name + ' has been updated.'))
            return redirect('student_list')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = ProfileUpdateForm(instance=instance)
    return render(request, 'accounts/edit_student.html', {
        'title': 'Edit-profile',
        'form': form,
    })


@method_decorator([login_required, admin_required], name='dispatch')
class StudentListView(ListView):
    template_name = "accounts/student_list.html"
    paginate_by = 10  # if pagination is desired
    ordering = ['username']  # Add this line to specify the ordering
    def get_queryset(self):
        queryset = Student.objects.all()
        query = self.request.GET.get('student_id')
        if query is not None:
            queryset = queryset.filter(Q(department=query))
        return queryset
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Students"
        return context


@login_required
@admin_required
def delete_student(request, pk):
    student = get_object_or_404(Student, pk=pk)
    student.delete()
    messages.success(request, 'Student Deleted')
    return redirect('student_list')


# def capture_subprocess(code):
#     try:
#         # Create a subprocess to run the code
#         scores = subprocess.run(['python', '-c', code], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
#                                 timeout=5)
#
#         # Capture the standard output
#         output = scores.stdout
#
#         return output
#     except Exception as e:
#         # Handle any errors (e.g., code that doesn't run)
#         return str(e)
