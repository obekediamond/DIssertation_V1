from django.contrib import admin
from .models import Session, Trimester, NewPost


admin.site.register(Trimester)
admin.site.register(Session)
admin.site.register(NewPost)
