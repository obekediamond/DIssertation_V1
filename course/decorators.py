from coursemanagement.models import CourseSetting
is_calender_on = CourseSetting.objects.filter(add_drop=True).count() > 0