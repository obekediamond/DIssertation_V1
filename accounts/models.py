from django.db.models import Q
from PIL import Image
from course.models import Program
from .validators import ASCIIUsernameValidator
from django.db import models
from django.urls import reverse
from django.contrib.auth.models import AbstractUser, UserManager
from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


MASTER_DEGREE = "Master"

LEVEL = ((MASTER_DEGREE, "Masters Program"),)


class UserManager(UserManager):
    # Method to enable searching for users within specific contexts and fields
    def search(self, query=None):
        query_set = self.get_queryset()
        if query is not None:
            or_lookup = (Q(username__icontains=query) |
                         Q(first_name__icontains=query) |
                         Q(last_name__icontains=query) |
                         Q(email__icontains=query))
            query_set = query_set.filter(or_lookup).distinct()
        return query_set


class User(AbstractUser):
    # Model for the User which is adopted and customized from Django's Abstract User Template
    # created_by = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_("User"), on_delete=models.CASCADE)
    time_created = models.DateTimeField(default=timezone.now, blank=True, null=True)
    created_by = models.CharField(max_length=80, blank=True, null=True, default='Admin')
    is_student = models.BooleanField(default=False)
    is_lecturer = models.BooleanField(default=False)
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.CharField(max_length=80, blank=True, null=True)
    picture = models.ImageField(upload_to='pictures/%y/%m/%d/', default='profile_default.png', null=True)
    email = models.EmailField(blank=False, null=False)
    username_validator = ASCIIUsernameValidator()
    objects = UserManager()

    @property
    def get_full_name(self):
        f_name = self.username
        if self.first_name and self.last_name:
            f_name = self.first_name + " " + self.last_name
        return f_name

    def __str__(self):
        return '{} ({})'.format(self.username, self.get_full_name)

    @property
    def get_role(self):
        if self.is_superuser:
            return "Admin"
        elif self.is_student:
            return "Student"
        elif self.is_lecturer:
            return "Lecturer"

    def get_pict(self):
        try:
            return self.picture.url
        except:
            no_picture = settings.MEDIA_URL + 'profile_default.png'
            return no_picture

    def get_absolute_url(self):
        return reverse('profile_from_admin', kwargs={'id': self.id})

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        try:
            image = Image.open(self.picture.path)
            if image.height > 278 or image.width > 278:
                output_size = (278, 278)
                image.thumbnail(output_size)
                image.save(self.picture.path)
        except:
            pass

    def delete(self, *args, **kwargs):
        if self.picture.url != settings.MEDIA_URL + 'profile_default.png':
            self.picture.delete()
        super().delete(*args, **kwargs)


class StudentMan(models.Manager):
    def search(self, query=None):
        query_set = self.get_queryset()
        if query is not None:
            or_lookup = (Q(level__icontains=query) |
                         Q(department__icontains=query)
                        )
            query_set = query_set.filter(or_lookup).distinct()
        return query_set


class Student(models.Model):
    student = models.OneToOneField(User, on_delete=models.CASCADE)
    level = models.CharField(max_length=25, choices=LEVEL, null=True)
    department = models.ForeignKey(Program, on_delete=models.CASCADE, null=True)
    objects = StudentMan()

    def __str__(self):
        return self.student.get_full_name

    def get_absolute_url(self):
        return reverse('profile_from_admin', kwargs={'id': self.id})

    def delete(self, *args, **kwargs):
        self.student.delete()
        super().delete(*args, **kwargs)


class Exercise(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    initial_code = models.TextField()


class Submission(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    code = models.TextField()
    submission_date = models.DateTimeField(auto_now_add=True)