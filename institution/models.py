from django.db import models
from django.utils import timezone
from django.db.models import Q
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.core.validators import FileExtensionValidator
from django.contrib.auth.models import AbstractUser

NEWS = "News"
EVENTS = "Event"

POST = (
    (NEWS, "News"),
    (EVENTS, "Event"),
)

FIRST = "First"
SECOND = "Second"
THIRD = "Third"

TRIMESTER = (
    (FIRST, "First"),
    (SECOND, "Second"),
    (THIRD, "Third"),
)


class NewPostQuerySet(models.query.QuerySet):

    def search(self, query):
        lookups = (Q(title__icontains=query) | 
                  Q(summary__icontains=query) |
                  Q(posted_as__icontains=query))
        return self.filter(lookups).distinct()


class NewPostMan(models.Manager):
    def get_queryset(self):
        return NewPostQuerySet(self.model, using=self._db)

    def all(self):
        return self.get_queryset()

    def get_by_id(self, id):
        query_set = self.get_queryset().filter(id=id)
        if query_set.count() == 1:
            return query_set.first()
        return None

    def search(self, query):
        return self.get_queryset().search(query)


class NewPost(models.Model):
    # created_by = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_("User"), on_delete=models.CASCADE)
    title = models.CharField(max_length=200, null=True)
    summary = models.TextField(max_length=200, blank=True, null=True)
    posted_as = models.CharField(choices=POST, max_length=10)
    updated_date = models.DateTimeField(auto_now=True, auto_now_add=False, null=True)
    upload_time = models.DateTimeField(auto_now=False, auto_now_add=True, null=True)
    objects = NewPostMan()

    def __str__(self):
        return self.title


class Session(models.Model):
    session = models.CharField(max_length=200, unique=True)
    is_current_session = models.BooleanField(default=False, blank=True, null=True)
    next_session_begins = models.DateField(blank=True, null=True)
    # created_by = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_("User"), on_delete=models.CASCADE)
    time_created = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.session


class Trimester(models.Model):
    trimester = models.CharField(max_length=20, choices=TRIMESTER, blank=True)
    is_current_trimester = models.BooleanField(default=False, blank=True, null=True)
    session = models.ForeignKey(Session, on_delete=models.CASCADE, blank=True, null=True)
    next_trimester_begins = models.DateField(null=True, blank=True)
    # created_by = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_("User"), on_delete=models.CASCADE)
    time_created = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.trimester
