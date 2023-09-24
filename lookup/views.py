from django.shortcuts import render
from itertools import chain
from django.views.generic import ListView
from django.db.models import Q
from accounts.models import User, Student
from institution.models import NewPost
from course.models import Program, Course
from quiz.models import Quiz


class LookupPost(ListView):
    template_name = "lookup/lookup_view_s.html"

    def get_context_data(self, *args, **kwargs):
        context = super(LookupPost, self).get_context_data(*args, **kwargs)
        query = self.request.GET.get('q')
        context['query'] = query
        context['obj_counter'] = NewPost.objects.search(query).count()
        return context

    def get_queryset(self, *args, **kwargs):
        request = self.request
        method_dict = request.GET
        query = method_dict.get('q', None)  # lookup method with dictionary object Q
        if query is not None:
            return NewPost.objects.search(query)
        return NewPost.objects.all()


class LookupView(ListView):
    template_name = 'lookup/lookup_view.html'
    paginate_by = 10
    length = 0
    
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['count'] = self.count or 0
        context['query'] = self.request.GET.get('q')
        return context

    def get_queryset(self):
        request = self.request
        query = request.GET.get('q', None)
        
        if query is not None:
            post = NewPost.objects.search(query)
            program = Program.objects.search(query)
            course = Course.objects.search(query)
            quiz = Quiz.objects.search(query)
            # merge the queries
            queryset_chain = chain(post, program, course, quiz)
            query_sets = sorted(queryset_chain, key=lambda instance: instance.pk, reverse=True)
            self.length = len(query_sets)  # count the number of items in the queryset
            return query_sets
        return NewPost.objects.none()  # return an empty query by default
