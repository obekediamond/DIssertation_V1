from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Sum, Avg, Max, Min, Count
from django.contrib.auth.decorators import login_required
from django.views.generic import CreateView, ListView
from django.core.paginator import Paginator
from django.conf import settings
from django.utils.decorators import method_decorator
from accounts.models import User, Student
from institution.models import Session, Trimester
from scores.models import UsersCourses
from accounts.decorators import lecturer_required, student_required, admin_required
from .forms import (ProgramForm, CourseAddForm, CourseAllocationForm, EditCourseAllocationForm, UploadFormFile,
                    UploadFormVideo)
from .models import Program, Course, CourseAllocation, Upload, UploadVideo


# def add_question(request):
#     if request.method == 'POST':
#         form = QuestionForm(request.POST)
#         if form.is_valid():
#             # Create a new quiz
#             quiz = Quiz.objects.create(
#                 title="title",
#                 description="description",
#                 # lecturer=request.user,
#
#                 # title=form.cleaned_data['title'],
#                 # description=form.cleaned_data['description'],
#                 # lecturer=request.user,
#             )
#
#             # Create the first question for the new quiz
#             question = form.save(commit=False)
#             question.quiz = quiz
#             question.save()
#
#             return redirect('quiz_list')
#     else:
#         form = QuestionForm()
#
#     return render(request, 'quiz_app/add_question.html', {'form': form})

@login_required
def view_program(request):
    programs = Program.objects.all()
    program_filter = request.GET.get('program_filter')
    if program_filter:
        programs = Program.objects.filter(title__icontains=program_filter)

    return render(request, 'course/program_list.html', {
        'title': "Programs",
        'programs': programs,
    })


@login_required
@admin_required
def add_program(request):
    if request.method == 'POST':
        form = ProgramForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, request.POST.get('title') + ' program has been created.')
            return redirect('programs')
        else:
            messages.error(request, 'Correct the error(s) and retry')
    else:
        form = ProgramForm()

    return render(request, 'course/add_program.html', {
        'title': "Add Program",
        'form': form,
    })


@login_required
def program_detail(request, pk):
    program = Program.objects.get(pk=pk)
    courses = Course.objects.filter(program_id=pk).order_by('-year')
    credits = Course.objects.aggregate(Sum('credit'))

    paginator = Paginator(courses, 10)
    page = request.GET.get('page')

    courses = paginator.get_page(page)

    return render(request, 'course/program_single.html', {
        'title': program.title,
        'program': program, 'courses': courses, 'credits': credits
    }, )


@login_required
@lecturer_required
def edit_program(request, pk):
    program = Program.objects.get(pk=pk)

    if request.method == 'POST':
        form = ProgramForm(request.POST, instance=program)
        if form.is_valid():
            form.save()
            messages.success(request, str(request.POST.get('title')) + ' program has been updated.')
            return redirect('programs')
    else:
        form = ProgramForm(instance=program)

    return render(request, 'course/add_program.html', {
        'title': "Edit Program",
        'form': form
    })


@login_required
@lecturer_required
def delete_program(request, pk):
    program = Program.objects.get(pk=pk)
    title = program.title
    program.delete()
    messages.success(request, 'Program ' + title + ' deleted.')
    return redirect('programs')


@login_required
def course_view(request, slug):
    course = Course.objects.get(slug=slug)
    files = Upload.objects.filter(course__slug=slug)
    videos = UploadVideo.objects.filter(course__slug=slug)
    lecturers = CourseAllocation.objects.filter(courses__pk=course.id)

    return render(request, 'course/course_view.html', {
        'title': course.title,
        'course': course,
        'files': files,
        'videos': videos,
        'lecturers': lecturers,
        'media_url': settings.MEDIA_ROOT,
    }, )


@login_required
def add_course(request, pk):
    users = User.objects.all()
    if request.method == 'POST':
        form = CourseAddForm(request.POST)
        course_title = request.POST.get('title') + ' ' + request.POST.get('code')
        if form.is_valid():
            form.save()
            messages.success(request, (course_title + ' has been updated.'))
            return redirect('program_detail', pk=request.POST.get('program'))
        else:
            messages.error(request, 'Correct the error(s) and retry')
    else:
        form = CourseAddForm(initial={'program': Program.objects.get(pk=pk)})

    return render(request, 'course/add_course.html', {
        'title': "Add Course",
        'form': form, 'program': pk, 'accounts': users
    }, )


@login_required
@lecturer_required
def edit_course(request, slug):
    course = get_object_or_404(Course, slug=slug)
    if request.method == 'POST':
        form = CourseAddForm(request.POST, instance=course)
        course_title = request.POST.get('title') + ' ' + request.POST.get('code')
        if form.is_valid():
            form.save()
            messages.success(request, (course_title + ' has been updated.'))
            return redirect('program_detail', pk=request.POST.get('program'))
        else:
            messages.error(request, 'Correct the error(s) and retry')
    else:
        form = CourseAddForm(instance=course)

    return render(request, 'course/add_course.html', {
        'title': "Edit Course",
        'form': form
    }, )


@login_required
@lecturer_required
def delete_course(request, slug):
    course = Course.objects.get(slug=slug)
    course.delete()
    messages.success(request, 'Course ' + course.title + ' deleted.')
    return redirect('program_detail', pk=course.program.id)


@method_decorator([login_required], name='dispatch')
class allocate_course(CreateView):
    form_class = CourseAllocationForm
    template_name = 'course/allocate_course.html'

    def get_form_kwargs(self):
        kwargs = super(allocate_course, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        lecturer = form.cleaned_data['lecturer']
        selected_courses = form.cleaned_data['courses']
        courses = ()
        for course in selected_courses:
            courses += (course.pk,)
        a, _ = CourseAllocation.objects.get_or_create(lecturer=lecturer)

        for i in range(0, selected_courses.count()):
            a.courses.add(courses[i])
            a.save()
        return redirect('view_allocated_course')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Assign Course"
        return context


@login_required
def view_allocated_course(request):
    allocated_courses = CourseAllocation.objects.all()
    return render(request, 'course/view_allocated_courses.html', {
        'title': "Course Allocations",
        "allocated_courses": allocated_courses
    })


@login_required
@lecturer_required
def edit_allocated_course(request, pk):
    allocated = get_object_or_404(CourseAllocation, pk=pk)
    if request.method == 'POST':
        form = EditCourseAllocationForm(request.POST, instance=allocated)
        if form.is_valid():
            form.save()
            messages.success(request, 'course assigned has been updated.')
            return redirect('view_allocated_course')
    else:
        form = EditCourseAllocationForm(instance=allocated)

    return render(request, 'course/allocate_course.html', {
        'title': "Edit Course Allocated",
        'form': form, 'allocated': pk
    }, )


@login_required
@lecturer_required
def deallocate_course(request, pk):
    course = CourseAllocation.objects.get(pk=pk)
    course.delete()
    messages.success(request, 'Done!')
    return redirect("view_allocated_course")


@login_required
@lecturer_required
def handle_file_upload(request, slug):
    course = Course.objects.get(slug=slug)
    if request.method == 'POST':
        form = UploadFormFile(request.POST, request.FILES, {'course': course})
        if form.is_valid():
            form.save()
            messages.success(request, (request.POST.get('title') + ' uploaded.'))
            return redirect('course_detail', slug=slug)
    else:
        form = UploadFormFile()
    return render(request, 'upload/upload_file_form.html', {
        'title': "File Upload",
        'form': form, 'course': course
    })


@login_required
@lecturer_required
def handle_file_edit(request, slug, file_id):
    course = Course.objects.get(slug=slug)
    instance = Upload.objects.get(pk=file_id)
    if request.method == 'POST':
        form = UploadFormFile(request.POST, request.FILES, instance=instance)
        if form.is_valid():
            form.save()
            messages.success(request, (request.POST.get('title') + ' updated.'))
            return redirect('course_detail', slug=slug)
    else:
        form = UploadFormFile(instance=instance)
    return render(request, 'upload/upload_file_form.html', {
        'title': instance.title,
        'form': form, 'course': course})


def handle_file_delete(request, slug, file_id):
    file = Upload.objects.get(pk=file_id)
    file.delete()
    messages.success(request, (file.title + ' deleted.'))
    return redirect('course_detail', slug=slug)


@login_required
@lecturer_required
def handle_video_upload(request, slug):
    course = Course.objects.get(slug=slug)
    if request.method == 'POST':
        form = UploadFormVideo(request.POST, request.FILES, {'course': course})
        if form.is_valid():
            form.save()
            messages.success(request, (request.POST.get('title') + ' has been uploaded.'))
            return redirect('course_detail', slug=slug)
    else:
        form = UploadFormVideo()
    return render(request, 'upload/upload_video_form.html', {
        'title': "Video Upload",
        'form': form, 'course': course
    })


@login_required
def handle_video_single(request, slug, video_slug):
    course = get_object_or_404(Course, slug=slug)
    video = get_object_or_404(UploadVideo, slug=video_slug)
    return render(request, 'upload/video_single.html', {'video': video})


@login_required
@lecturer_required
def handle_video_edit(request, slug, video_slug):
    course = Course.objects.get(slug=slug)
    instance = UploadVideo.objects.get(slug=video_slug)
    if request.method == 'POST':
        form = UploadFormVideo(request.POST, request.FILES, instance=instance)
        if form.is_valid():
            form.save()
            messages.success(request, (request.POST.get('title') + ' has been updated.'))
            return redirect('course_detail', slug=slug)
    else:
        form = UploadFormVideo(instance=instance)

    return render(request, 'upload/upload_video_form.html', {
        'title': instance.title,
        'form': form, 'course': course})


def handle_video_delete(request, slug, video_slug):
    video = get_object_or_404(UploadVideo, slug=video_slug)
    video.delete()
    messages.success(request, (video.title + ' deleted.'))
    return redirect('course_detail', slug=slug)


@login_required
@student_required
def student_add_course(request):
    if request.method == 'POST':
        ids = ()
        data = request.POST.copy()
        data.pop('csrfmiddlewaretoken', None)  # remove csrf_token
        for key in data.keys():
            ids = ids + (str(key),)
        for s in range(0, len(ids)):
            student = Student.objects.get(student__pk=request.user.id)
            course = Course.objects.get(pk=ids[s])
            course_object = UsersCourses.objects.create(student=student, course=course)
            course_object.save()
            messages.success(request, 'Courses Registered Successfully!')
        return redirect('student_add_course')
    else:
        student = get_object_or_404(Student, student__id=request.user.id)
        current_trimester = Trimester.objects.get(is_current_trimester=True)

        existing_courses_registered = UsersCourses.objects.filter(student__student__id=request.user.id)
        registered_courses = Course.objects.filter(id__in=existing_courses_registered.values('course__id'))

        available_courses = Course.objects.filter(
            program__pk=student.department.id,
            level=student.level,
            trimester=current_trimester
        ).exclude(id__in=registered_courses.values('id')).order_by('year')

        total_first_trimester_credit = available_courses.filter(trimester='First').aggregate(Sum('credit'))[
            'credit__sum']
        total_sec_trimester_credit = available_courses.filter(trimester='Second').aggregate(Sum('credit'))[
            'credit__sum']
        total_registered_credit = registered_courses.aggregate(Sum('credit'))['credit__sum']

        zero_courses_registered = not registered_courses.exists()
        all_courses_are_registered = available_courses.count() == 0

        context = {
            "is_calender_on": True,
            "all_courses_are_registered": all_courses_are_registered,
            "no_course_is_registered": zero_courses_registered,
            "current_trimester": current_trimester,
            "courses": available_courses,
            "total_first_semester_credit": total_first_trimester_credit or 0,
            "total_sec_trimester_credit": total_sec_trimester_credit or 0,
            "registered_courses": registered_courses,
            "total_registered_credit": total_registered_credit or 0,
            "student": student,
        }
        return render(request, 'course/student_add_course.html', context)


@login_required
@student_required
def student_drop_course(request):
    if request.method == 'POST':
        ids = ()
        data = request.POST.copy()
        data.pop('csrfmiddlewaretoken', None)  # remove csrf_token
        for key in data.keys():
            ids = ids + (str(key),)
        for s in range(0, len(ids)):
            student = Student.objects.get(student__pk=request.user.id)
            course = Course.objects.get(pk=ids[s])
            obj = UsersCourses.objects.get(student=student, course=course)
            obj.delete()
            messages.success(request, 'Successfully Dropped!')
        return redirect('student_add_course')


@login_required
@login_required
def user_course_list(request):
    if request.user.is_lecturer:
        courses = Course.objects.filter(allocated_course__lecturer__pk=request.user.id)
        return render(request, 'course/user_course_list.html', {'courses': courses})
    elif request.user.is_student:
        try:
            student = get_object_or_404(Student, student__id=request.user.id)
            taken_courses = UsersCourses.objects.filter(student__student__id=request.user.id)
            current_trimester = Trimester.objects.get(is_current_trimester=True)
            courses = Course.objects.filter(program__pk=student.department.id, level=student.level,
                                            trimester=current_trimester)
            return render(request, 'course/user_course_list.html', {
                'student': student,
                'taken_courses': taken_courses,
                'courses': courses
            })
        except Student.DoesNotExist:
            pass
    else:
        return render(request, 'course/user_course_list.html')


# def my_template(request):
#     # Your view logic here
#
#     # Example context data
#     context = {
#         'variable1': 'Hello',
#         'variable2': 'World',
#     }
#
#     # Render the HTML page 'my_template.html' with the provided context data
#     return render(request, 'quiz_app/my_template.html', context)
# def execute_code(request):
#     if request.method == 'POST':
#         form = CodeForm(request.POST)
#         if form.is_valid():
#             user_code = form.cleaned_data['code']
#             output = StringIO()
#             error = StringIO()
#             with contextlib.redirect_stdout(output), contextlib.redirect_stderr(error):
#                 try:
#                     exec(user_code)
#                 except Exception as e:
#                     scores = f"Error: {str(e)}"
#                 else:
#                     scores = "Code executed successfully."
#             output_str = output.getvalue()
#             error_str = error.getvalue()
#     else:
#         form = CodeForm()
#         scores = ""
#         output_str = ""
#         error_str = ""
#
#     return render(request, 'quiz_app/execute_code.html', {'form': form, 'scores': scores, 'output': output_str, 'error': error_str})