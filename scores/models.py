from django.db import models
from django.urls import reverse
from accounts.models import Student
from institution.models import Session, Trimester
from course.models import Course
from django.utils import timezone


YEARS = (
        (1, '1'),
    )

MASTER_DEGREE = "Masters Program"

LEVEL = (
    (MASTER_DEGREE, "Masters Program"),
)

FIRST = "First"
SECOND = "Second"
THIRD = "Third"

TRIMESTER = (
    (FIRST, "First"),
    (SECOND, "Second"),
    (THIRD, "Third"),
)

Distinction = "Distinction"
Merit = "Merit"
Pass = "Pass"
Fail = "Fail"


GRADE = (
        (Distinction, "Distinction"),
        (Merit, "Merit"),
        (Pass, "Merit"),
        (Fail, "Fail"),
)

PASS = "PASS"
FAIL = "FAIL"

COMMENT = (
    (PASS, "PASS"),
    (FAIL, "FAIL"),
)


class UsersCoursesManager(models.Manager):
    def new_or_get(self, request):
        cart_id = request.session.get("cart_id", None)
        query_set = self.get_queryset().filter(id=cart_id)
        if query_set.count() == 1:
            new_obj = False
            cart_obj = query_set.first()
            if request.user.is_authenticated() and cart_obj.user is None:
                cart_obj.user = request.user
                cart_obj.save()
        else:
            cart_obj = Cart.objects.new(user=request.user)
            new_obj = True
            request.session['cart_id'] = cart_obj.id
        return cart_obj, new_obj

    def new(self, user=None):
        user_obj = None
        if user is not None:
            if user.is_authenticated():
                user_obj = user
        return self.model.objects.create(user=user_obj)


class UsersCourses(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='taken_courses')
    assignment = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    total = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    grade = models.CharField(choices=GRADE, max_length=11, blank=True)
    point = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    comment = models.CharField(choices=COMMENT, max_length=200, blank=True)
    time_created = models.DateTimeField(default=timezone.now)

    def get_absolute_url(self):
        return reverse('course_detail', kwargs={'slug': self.course.slug})

    def __str__(self):
        return "{0} ({1})".format(self.course.title, self.course.code)

    def get_score(self, assignment):
        return float(assignment)

    def get_marked_grade(self, total):
        if total >= 70:
            grade = Distinction
        elif total >= 60:
            grade = Merit
        elif total >= 50:
            grade = Pass
        else:
            grade = Fail
        return grade

    def get_comment(self, grade):
        if grade == Fail:
            comment = FAIL
        else:
            comment = PASS
        return comment

    def get_point(self, grade):
        initial_point = 0
        credit = self.course.credit
        if self.grade == Distinction:
            point = 5
        elif self.grade == Merit:
            point = 4
        elif self.grade == Pass:
            point = 3
        else:
            point = 0
        initial_point += int(credit) * point
        return initial_point


class Result(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    score = models.FloatField(null=True)
    trimester = models.CharField(max_length=100, choices=TRIMESTER)
    comment = models.CharField(max_length=100, choices=COMMENT)
    session = models.CharField(max_length=100, blank=True, null=True)
    level = models.CharField(max_length=25, choices=LEVEL, null=True)
