from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.urls import reverse_lazy
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from accounts.models import User, Student
from institution.models import Session, Trimester
from course.models import Course
from accounts.decorators import lecturer_required, student_required
from .models import UsersCourses, Result
from .models import *


@login_required
@lecturer_required
def provisional_score(request):
    current_session = Session.objects.get(is_current_session=True)
    current_trimester = get_object_or_404(Trimester, is_current_trimester=True, session=current_session)
    courses = Course.objects.filter(allocated_course__lecturer__pk=request.user.id).filter(trimester=current_trimester)
    context = {
        "current_session": current_session,
        "current_trimester": current_trimester,
        "courses": courses,
    }
    return render(request, 'scores/provisional_score.html', context)


@login_required
@lecturer_required
def lecturer_confirm_score(request, id):
    """
    Shows a page where a lecturer will add score for students that are taking courses allocated to him
    in a specific trimester and session
    """
    current_session = Session.objects.get(is_current_session=True)
    current_trimester = get_object_or_404(Trimester, is_current_trimester=True, session=current_session)
    if request.method == 'GET':
        courses = Course.objects.filter(allocated_course__lecturer__pk=request.user.id).filter(
            trimester=current_trimester)
        course = Course.objects.get(pk=id)
        students = UsersCourses.objects.filter(course__allocated_course__lecturer__pk=request.user.id).filter(
            course__id=id).filter(course__trimester=current_trimester)
        context = {
            "title": "Submit Score",
            "courses": courses,
            "course": course,
            "students": students,
            "current_session": current_session,
            "current_trimester": current_trimester,
        }
        return render(request, 'scores/lecturer_confirm_score.html', context)

    if request.method == 'POST':
        ids = ()
        data = request.POST.copy()
        data.pop('csrfmiddlewaretoken', None)  # remove csrf_token
        for key in data.keys():
            ids = ids + (str(key),)  # gather all the all students id (i.e the keys) in a tuple
        for s in range(0, len(ids)):  # iterate over the list of student ids gathered above
            student = UsersCourses.objects.get(id=ids[s])
            courses = Course.objects.filter(level=student.student.level).filter(program__pk=student.student.department.id).filter(
                trimester=current_trimester)
            total_credit_in_trimester = 0
            for i in courses:
                if i == courses.count():
                    break
                else:
                    total_credit_in_trimester += int(i.credit)
            score = data.getlist(ids[s])
            print(score, score[0])
            assignment = score[0]
            obj = UsersCourses.objects.get(pk=ids[s])  # get the current student data
            obj.assignment = assignment  # set current student assignment score
            obj.total = obj.get_score(assignment=assignment)
            obj.grade = obj.get_marked_grade(total=obj.total)
            obj.point = obj.get_point(grade=obj.grade)
            obj.comment = obj.get_comment(grade=obj.grade)
            obj.save()
            try:
                a = Result.objects.get(student=student.student, trimester=current_trimester, session=current_session, level=student.student.level)
                a.score = obj.total
                a.comment = obj.comment
                a.save()
            except:
                Result.objects.get_or_create(student=student.student, comment=obj.comment, trimester=current_trimester,
                                             session=current_session, level=student.student.level)

        messages.success(request, 'Score Updated. ')
        return HttpResponseRedirect(reverse_lazy('lecturer_confirm_score', kwargs={'id': id}))
    return HttpResponseRedirect(reverse_lazy('lecturer_confirm_score', kwargs={'id': id}))


@login_required
@student_required
def provisional_result(request):
    student = Student.objects.get(student__pk=request.user.id)
    assess_courses = UsersCourses.objects.filter(student__student__pk=request.user.id).filter(course__level=student.level)
    assess_results = Result.objects.filter(student__student__pk=request.user.id)

    result_set = set()

    for result in assess_results:
        result_set.add(result.session)

    sorted_result = sorted(result_set)

    total_first_trimester_credit = 0
    total_sec_trimester_credit = 0
    for i in assess_courses:
        if i.course.trimester == "First":
            total_first_trimester_credit += int(i.course.credit)
        if i.course.trimester == "Second":
            total_sec_trimester_credit += int(i.course.credit)

    past_gp = 0
    for i in assess_results:
        past_level = i.level
        try:
            a = Result.objects.get(student__student__pk=request.user.id, level=past_level, trimester="Second")
            past_gp = a.cgpa
            break
        except:
            past_gp = 0

    context = {
        "courses": assess_courses,
        "results": assess_results,
        "sorted_result": sorted_result,
        "student": student,
        'total_first_trimester_credit': total_first_trimester_credit,
        'total_sec_trimester_credit': total_sec_trimester_credit,
        'total_first_and_second_trimester_credit': total_first_trimester_credit + total_sec_trimester_credit,
        "previousCGPA": past_gp,
    }

    return render(request, 'scores/provisional_result.html', context)


@login_required
@student_required
def com_result(request):
    student = Student.objects.get(student__pk=request.user.id)
    assess_courses = UsersCourses.objects.filter(student__student__pk=request.user.id, course__level=student.level)
    assess_result = Result.objects.filter(student__student__pk=request.user.id)

    context = {
        "courses": assess_courses,
        "scores": assess_result,
        "student": student,
    }

    return render(request, 'scores/com_result.html', context)
