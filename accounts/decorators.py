from django.contrib.auth import REDIRECT_FIELD_NAME
from django.http import Http404
from django.contrib.auth.decorators import user_passes_test


def admin_required(function=None, redirect_url=REDIRECT_FIELD_NAME, login_url=Http404):
    """Checks if user is Admin(Superuser)"""
    user_passed = user_passes_test(
        lambda u: u.is_superuser and u.is_active,
        login_url=login_url,
        redirect_field_name=redirect_url
    )
    if function:
        return user_passed(function)
    return user_passed


def lecturer_required(function=None, redirect_url=REDIRECT_FIELD_NAME, login_url=Http404):
    """Checks if user is a Lecturer or Admin(Superuser)"""
    user_passed = user_passes_test(
        lambda u: u.is_active and u.is_lecturer or u.is_superuser,
        login_url=login_url,
        redirect_field_name=redirect_url
    )
    if function:
        return user_passed(function)
    return user_passed


def student_required(function=None, redirect_url=REDIRECT_FIELD_NAME, login_url=Http404):
    """Checks if user is a Student or Admin(Superuser)"""

    user_passed = user_passes_test(
        lambda u: u.is_active and u.is_student or u.is_superuser,
        login_url=login_url,
        redirect_field_name=redirect_url
    )
    if function:
        return user_passed(function)
    return user_passed



