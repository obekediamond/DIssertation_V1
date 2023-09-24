from django.contrib.auth.decorators import login_required, permission_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, render, redirect
from django.utils.decorators import method_decorator
from django.views.generic import DetailView, ListView, TemplateView, FormView, CreateView, DeleteView, UpdateView
from django.contrib import messages
import datetime
from django.utils import timezone
from django.urls import reverse_lazy
from django.db import transaction
from django.forms import inlineformset_factory
from django.http import HttpResponseRedirect
from scores.models import UsersCourses
from accounts.decorators import student_required, lecturer_required
from .models import *
from .forms import *
from io import StringIO
import contextlib
from .sandbox import Sandbox
from RestrictedPython.PrintCollector import PrintCollector
from RestrictedPython import compile_restricted
from RestrictedPython import safe_globals, safe_builtins
from RestrictedPython.Eval import default_guarded_getiter,default_guarded_getitem
from RestrictedPython.Guards import guarded_iter_unpack_sequence,safer_getattr
import math, matplotlib, numpy, numba, pandas, random, datetime, difflib


def _import(name, globals=None, locals=None, fromlist=(), level=0):
    safe_modules = ["math", "matplotlib", "numpy", "numba", "pandas", "random", "datetime", "tkinter", "matplotlib.pyplot"]
    if name in safe_modules:
       globals[name] = __import__(name, globals, locals, fromlist, level)
    else:
        raise Exception("This module incorrect or not allowed: {0}".format(name))


def custom_inplacevar(op, x, y):
    globs = {'x': x, 'y': y}
    exec('x' + op + 'y', globs)
    return globs['x']


safe_builtins['__import__'] = _import # Must be a part of builtins
safe_builtins['_inplacevar_'] = custom_inplacevar # Must be a part of builtins
safe_globals['_inplacevar_'] = custom_inplacevar
safe_globals['_print_'] = PrintCollector
safe_globals['_getattr_'] = safer_getattr
safe_globals['_getitem_'] = default_guarded_getitem
safe_globals['_getiter_'] = default_guarded_getiter
safe_globals['dir'] = dir
safe_globals['math'] = math
safe_globals['_iter_unpack_sequence_'] = guarded_iter_unpack_sequence
safe_globals['matplotlib'] = matplotlib
safe_globals['numpy'] = numpy
safe_globals['numba'] = numba
safe_globals['pandas'] = pandas
safe_globals['random'] = random
safe_globals['datetime'] = datetime
safe_globals['__builtins__'] = safe_builtins
safe_globals['__metaclass__'] = type

@method_decorator([login_required, lecturer_required], name='dispatch')
class QuizCreateView(CreateView):
    model = Quiz
    form_class = QuizAddForm

    def get_context_data(self, *args, **kwargs):
        context = super(QuizCreateView, self).get_context_data(**kwargs)
        context['course'] = Course.objects.get(slug=self.kwargs['slug'])
        if self.request.POST:
            context['form'] = QuizAddForm(self.request.POST)
            # context['quiz'] = self.request.POST.get('quiz')
        else:
            context['form'] = QuizAddForm(initial={'course': Course.objects.get(slug=self.kwargs['slug'])})
        return context

    def form_valid(self, form, **kwargs):
        context = self.get_context_data()
        form = context['form']
        with transaction.atomic():
            self.object = form.save()
            if form.is_valid():
                form.instance = self.object
                self.object.cat_q = 'mcq'
                form.save()
                return redirect('mc_create', slug=self.kwargs['slug'], quiz_id=form.instance.id)
        return super(QuizCreateView, self).form_invalid(form)


@method_decorator([login_required, lecturer_required], name='dispatch')
class QuizUpdateView(UpdateView):
    model = Quiz
    form_class = QuizAddForm
    template_name = 'quiz/quiz_form.html'

    def get_object(self, queryset=None):
        return get_object_or_404(Quiz, pk=self.kwargs['pk'], course__slug=self.kwargs['slug'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['course'] = self.object.course
        return context

    def form_valid(self, form):
        with transaction.atomic():
            if form.is_valid():
                form.instance = self.object
                if self.object.cat_q == 'mcq':
                    self.object.cat_q = 'mcq'
                    self.object.save()
                    form.save()
                elif self.object.cat_q == 'ess':
                    self.object.cat_q = 'ess'
                    self.object.save()
                    form.save()
        course_slug = self.object.course.slug
        return redirect('quiz_index', slug=course_slug)


@login_required
@lecturer_required
def quiz_delete(request, slug, pk):
    quiz = Quiz.objects.get(pk=pk)
    course = Course.objects.get(slug=slug)
    quiz.delete()
    messages.success(request, f'successfuly deleted.')
    return redirect('quiz_index', quiz.course.slug)


@method_decorator([login_required, lecturer_required], name='dispatch')
class MCQuestionCreate(CreateView):
    model = MCQuestion
    form_class = MCQuestionForm

    def get_context_data(self, **kwargs):
        context = super(MCQuestionCreate, self).get_context_data(**kwargs)
        context['course'] = Course.objects.get(slug=self.kwargs['slug'])
        context['quiz_obj'] = Quiz.objects.get(id=self.kwargs['quiz_id'])
        context['quizQuestions'] = Question.objects.filter(quiz=self.kwargs['quiz_id']).count()
        if self.request.POST:
            context['form'] = MCQuestionForm(self.request.POST)
            context['formset'] = MCQuestionFormSet(self.request.POST)
        else:
            context['form'] = MCQuestionForm(initial={'quiz': self.kwargs['quiz_id']})
            context['formset'] = MCQuestionFormSet()

        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']
        course = context['course']
        with transaction.atomic():
            form.instance.question = self.request.POST.get('content')
            self.object = form.save()
            if formset.is_valid():
                formset.instance = self.object
                formset.save()
                if "another" in self.request.POST:
                    return redirect('mc_create', slug=self.kwargs['slug'], quiz_id=self.kwargs['quiz_id'])
                return redirect('quiz_index', course.slug)
        return super(MCQuestionCreate, self).form_invalid(form)


@login_required
def quiz_list(request, slug):
    quizzes = Quiz.objects.filter(course__slug=slug).order_by('-timestamp')
    course = Course.objects.get(slug=slug)
    return render(request, 'quiz/quiz_list.html', {'quizzes': quizzes, 'course': course})


@method_decorator([login_required, lecturer_required], name='dispatch')
class QuizMarkerMixin(object):
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(QuizMarkerMixin, self).dispatch(*args, **kwargs)


class SittingFilterTitleMixin(object):
    def get_queryset(self):
        queryset = super(SittingFilterTitleMixin, self).get_queryset()
        quiz_filter = self.request.GET.get('quiz_filter')
        if quiz_filter:
            queryset = queryset.filter(quiz__title__icontains=quiz_filter)
        return queryset


@method_decorator([login_required], name='dispatch')
class QuizUserProgressView(TemplateView):
    template_name = 'progress.html'

    def dispatch(self, request, *args, **kwargs):
        return super(QuizUserProgressView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(QuizUserProgressView, self).get_context_data(**kwargs)
        progress, c = Progress.objects.get_or_create(user=self.request.user)
        context['cat_scores'] = progress.list_all_cat_scores
        context['exams'] = progress.show_exams()
        context['exams_counter'] = progress.show_exams().count()
        return context


@method_decorator([login_required, lecturer_required], name='dispatch')
class QuizMarkingList(QuizMarkerMixin, SittingFilterTitleMixin, ListView):
    model = Sitting
    def get_queryset(self):
        if self.request.user.is_superuser:
            queryset = super(QuizMarkingList, self).get_queryset().filter(complete=True)
        else:
            queryset = super(QuizMarkingList, self).get_queryset().filter(
                quiz__course__allocated_course__lecturer__pk=self.request.user.id).filter(complete=True)
        user_filter = self.request.GET.get('user_filter')
        if user_filter:
            queryset = queryset.filter(user__username__icontains=user_filter)

        return queryset


@method_decorator([login_required, lecturer_required], name='dispatch')
class QuizMarkingDetail(QuizMarkerMixin, DetailView):
    model = Sitting

    def post(self, request, *args, **kwargs):
        sitting = self.get_object()

        q_to_toggle = request.POST.get('qid', None)
        if q_to_toggle:
            q = Question.objects.get_subclass(id=int(q_to_toggle))
            if int(q_to_toggle) in sitting.get_incorrect_questions:
                sitting.remove_incorrect_question(q)
            else:
                sitting.add_incorrect_question(q)

        return self.get(request)

    def get_context_data(self, **kwargs):
        context = super(QuizMarkingDetail, self).get_context_data(**kwargs)
        context['questions'] = context['sitting'].get_questions(with_answers=True)
        return context


@method_decorator([login_required], name='dispatch')
class QuizTake(FormView):
    form_class = QuestionForm
    template_name = 'question.html'
    result_template_name = 'result.html'
    start_time = timezone.now()

    def dispatch(self, request, *args, **kwargs):
        self.start_time = timezone.now()
        self.quiz = get_object_or_404(Quiz, slug=self.kwargs['slug'])
        # if timezone.now() == (self.start_time + datetime.timedelta(minutes=self.quiz.timer)):
        #     return self.final_result_user()
        self.course = get_object_or_404(Course, pk=self.kwargs['pk'])
        quizQuestions = Question.objects.filter(quiz=self.quiz).count()
        course = get_object_or_404(Course, pk=self.kwargs['pk'])
        if quizQuestions <= 0:
            messages.warning(request, f'Question set of the quiz is empty. try later!')
            return redirect('quiz_index', self.course.slug)
        if self.quiz.draft and not request.user.has_perm('quiz.change_quiz'):
            raise PermissionDenied
        self.sitting = Sitting.objects.user_sitting(request.user, self.quiz, self.course)
        if self.sitting is False:
            messages.info(request, f'You have exhausted your trials for this Quiz')
            return redirect('quiz_index', self.course.slug)
        current_datetime = timezone.now()
        if current_datetime < self.quiz.assignment_start_date:
            messages.info(request, f'This Quiz will be available on {self.quiz.assignment_start_date}')
            return redirect('quiz_index', self.course.slug)
        if current_datetime > self.quiz.assignment_due_date:
            messages.info(request, f'This Quiz was due on {self.quiz.assignment_due_date}')
            return redirect('quiz_index', self.course.slug)
        return super(QuizTake, self).dispatch(request, *args, **kwargs)

    def get_form(self, *args, **kwargs):
        self.question = self.sitting.get_first_question()
        self.progress = self.sitting.progress()

        if self.question.__class__ is Essay_Question:
            form_class = EssayForm
        else:
            form_class = self.form_class

        return form_class(**self.get_form_kwargs())

    def get_form_kwargs(self):
        kwargs = super(QuizTake, self).get_form_kwargs()

        return dict(kwargs, question=self.question)

    def form_valid(self, form):
        self.form_valid_user(form)
        if self.sitting.get_first_question() is False:
            return self.final_result_user()
        current_time = timezone.now()
        elapsed_time = current_time - self.start_time
        quiz_duration = datetime.timedelta(minutes=self.quiz.timer)
        # if timezone.now() == (self.start_time + self.quiz.timer):
        #     return self.final_result_user()
        self.request.POST = {}
        return super(QuizTake, self).get(self, self.request)

    def get_context_data(self, **kwargs):
        context = super(QuizTake, self).get_context_data(**kwargs)
        context['question'] = self.question
        context['quiz'] = self.quiz
        context['course'] = get_object_or_404(Course, pk=self.kwargs['pk'])
        if hasattr(self, 'previous'):
            context['previous'] = self.previous
        if hasattr(self, 'progress'):
            context['progress'] = self.progress
        return context

    def form_valid_user(self, form):
        progress, c = Progress.objects.get_or_create(user=self.request.user)
        guess = form.cleaned_data['answers']
        is_correct = self.question.check_if_correct(guess)

        if is_correct is True:
            self.sitting.add_to_score(1)
            progress.update_score(self.question, 1, 1)
        else:
            self.sitting.add_incorrect_question(self.question)
            progress.update_score(self.question, 0, 1)

        if self.quiz.answers_at_end is not True:
            self.previous = {
                'previous_answer': guess,
                'previous_outcome': is_correct,
                'previous_question': self.question,
                'answers': self.question.get_choices(),
                'question_type': {self.question.__class__.__name__: True}
            }
        else:
            self.previous = {}

        self.sitting.add_user_answer(self.question, guess)
        self.sitting.remove_first_question()


    def final_result_user(self):
        results = {
            'course': get_object_or_404(Course, pk=self.kwargs['pk']),
            'quiz': self.quiz,
            'score': self.sitting.get_current_score,
            'max_score': self.sitting.get_max_score,
            'percent': self.sitting.get_percent_correct,
            'sitting': self.sitting,
            'previous': self.previous,
            'course': get_object_or_404(Course, pk=self.kwargs['pk'])
        }

        self.sitting.mark_quiz_complete()

        if self.quiz.answers_at_end:
            results['questions'] = self.sitting.get_questions(with_answers=True)
            results['incorrect_questions'] = self.sitting.get_incorrect_questions

        if self.quiz.exam_paper is False or self.request.user.is_superuser or self.request.user.is_lecturer :
            self.sitting.delete()

        return render(self.request, self.result_template_name, results)


@method_decorator([login_required, lecturer_required], name='dispatch')
class QuizCreateViewEssay(CreateView):
    model = Quiz
    form_class = QuizAddForm

    def get_context_data(self, *args, **kwargs):
        context = super(QuizCreateViewEssay, self).get_context_data(**kwargs)
        context['course'] = Course.objects.get(slug=self.kwargs['slug'])
        if self.request.POST:
            context['form'] = QuizAddForm(self.request.POST)
            Quiz.cat_q = 'ess'
        else:
            context['form'] = QuizAddForm(initial={'course': Course.objects.get(slug=self.kwargs['slug'])})
        return context

    def form_valid(self, form, **kwargs):
        context = self.get_context_data()
        form = context['form']
        with transaction.atomic():
            self.object = form.save(commit=False)
            if form.is_valid():
                self.object.cat_q = 'ess'
                self.object.save()
                return redirect('essay_create', slug=self.kwargs['slug'], quiz_id=form.instance.id)
        return super(QuizCreateViewEssay, self).form_invalid(form)


@method_decorator(login_required, name='dispatch')
class EssayQuestionCreate(CreateView):
    model = Essay_Question
    form_class = EssayForm

    def get_context_data(self, **kwargs):
        context = super(EssayQuestionCreate, self).get_context_data(**kwargs)
        context['course'] = Course.objects.get(slug=self.kwargs['slug'])
        context['quiz_obj'] = Quiz.objects.get(id=self.kwargs['quiz_id'])
        context['quizQuestions'] = Question.objects.filter(quiz=self.kwargs['quiz_id']).count()

        if self.request.POST:
            context['form'] = EssayForm(self.request.POST)
        else:
            context['form'] = EssayForm(initial={'quiz': self.kwargs['quiz_id']})

        return context

    def form_valid(self, form):
        context = self.get_context_data()
        quiz_obj = context['quiz_obj']
        course = context['course']
        essay_question = form.save(commit=False)
        essay_question.save()
        essay_question.quiz.set([quiz_obj])
        essay_question.save()

        if "another" in self.request.POST:
            return redirect('essay_create', slug=self.kwargs['slug'], quiz_id=self.kwargs['quiz_id'])
        else:
            return redirect('quiz_index', course.slug)

    def form_invalid(self, form):
        return super(EssayQuestionCreate, self).form_invalid(form)


@method_decorator(login_required, name='dispatch')
class CodeExecutionView(FormView):
    form_class = EssayQuestionForm
    template_name = 'quiz/execute_code.html'
    result_template_name = 'result.html'

    def dispatch(self, request, *args, **kwargs):
        self.start_time = timezone.now()
        self.quiz = get_object_or_404(Quiz, slug=kwargs['slug'])
        self.course = get_object_or_404(Course, pk=kwargs['pk'])
        self.sitting = Sitting.objects.user_sitting(request.user, self.quiz, self.course)
        quiz_questions = Question.objects.filter(quiz=self.quiz)
        quizQuestions = Question.objects.filter(quiz=self.quiz).count()
        self.questions = list(quiz_questions)
        if not self.questions:
            messages.warning(request, 'There are no questions available for this quiz.')
            return redirect('quiz_index', slug=self.course.slug)
        if self.quiz.draft and not request.user.has_perm('quiz.change_quiz'):
            raise PermissionDenied
        if self.sitting is False:
            messages.info(request, f'You have exhausted your trials for this Quiz')
            return redirect('quiz_index', self.course.slug)
        current_datetime = timezone.now()
        if current_datetime < self.quiz.assignment_start_date:
            messages.info(request, f'This Quiz will be available on {self.quiz.assignment_start_date}')
            return redirect('quiz_index', self.course.slug)
        if current_datetime > self.quiz.assignment_due_date:
            messages.info(request, f'This Quiz was due on {self.quiz.assignment_due_date}')
            return redirect('quiz_index', self.course.slug)
        return super().dispatch(request, *args, **kwargs)

    def get_form(self, *args, **kwargs):
        self.question = self.sitting.get_first_question()
        self.progress = self.sitting.progress()
        form_class = self.form_class
        return form_class(**self.get_form_kwargs())

    def get_form_kwargs(self):
        kwargs = super(CodeExecutionView, self).get_form_kwargs()
        return dict(kwargs, question=self.question)

    def form_valid(self, form):
        self.form_valid_user(form)
        if self.sitting.get_first_question() is False:
            return self.final_result_user()
        # current_time = timezone.now()
        # elapsed_time = current_time - self.start_time
        # quiz_duration = datetime.timedelta(minutes=self.quiz.timer)
        # print('The start', timezone.now(), '\n', current_time, '\n', elapsed_time, '\n', quiz_duration)
        #
        # if timezone.now() == (self.start_time + self.quiz.timer):
        #     return self.final_result_user()
        self.request.POST = {}
        return super(CodeExecutionView, self).get(self, self.request)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['quiz'] = self.quiz
        context['questions'] = self.question
        context['course'] = get_object_or_404(Course, pk=self.kwargs['pk'])
        if hasattr(self, 'previous'):
            context['previous'] = self.previous
        if hasattr(self, 'progress'):
            context['progress'] = self.progress
        return context

    def form_valid_user(self, form):
        output = StringIO()
        error = StringIO()
        score = 0
        progress, c = Progress.objects.get_or_create(user=self.request.user)
        guess = form.cleaned_data['answers']
        try:
            loc = {}
            u_code = guess + '\nscores = printed'
            user_cc = compile_restricted(u_code, '<inline>', 'exec')
            exec(user_cc, safe_globals, loc)
            printed = loc['scores']
            iloc = {}
            i_code = self.question.expected_input + '\nscores = printed'
            inst_cc = compile_restricted(i_code, '<inline>', 'exec')
            exec(inst_cc, safe_globals, iloc)
            iprinted = iloc['scores']
            code_similarity_ratio = difflib.SequenceMatcher(None, self.question.expected_input, guess).ratio()
            output_similarity_ratio = difflib.SequenceMatcher(None, iprinted, printed).ratio()
            score = code_similarity_ratio * output_similarity_ratio
            print(score)
            if printed:
                guess = f"Code executed successfully. Output:\n{printed}"
            else:
                guess = "Code executed successfully. (No output)"
        except Exception as e:
            guess = f"Error: {str(e)}"
        output_str = output.getvalue()
        error_str = error.getvalue()
        if score > 0.95:
            is_correct = True
        else:
            is_correct = False
        if is_correct is True:
            self.sitting.add_to_score(1)
            progress.update_score(self.question, 1, 1)
        else:
            self.sitting.add_incorrect_question(self.question)
            progress.update_score(self.question, 0, 1)

        if self.quiz.answers_at_end is not True:
            self.previous = {
                'previous_answer': guess,
                'previous_outcome': is_correct,
                'previous_question': self.question,
                'answers': guess,
                'output_str': output_str,
                'error_str': error_str,
                'question_type': {self.question.__class__.__name__: True}
            }
        else:
            self.previous = {}

        self.sitting.add_user_answer(self.question, guess)
        self.sitting.remove_first_question()

    def final_result_user(self):
        results = {
            'course': get_object_or_404(Course, pk=self.kwargs['pk']),
            'quiz': self.quiz,
            'score': self.sitting.get_current_score,
            'max_score': self.sitting.get_max_score,
            'percent': self.sitting.get_percent_correct,
            'sitting': self.sitting,
            'previous': self.previous,
        }

        self.sitting.mark_quiz_complete()

        if self.quiz.answers_at_end:
            results['questions'] = self.sitting.get_questions(with_answers=True)
            results['incorrect_questions'] = self.sitting.get_incorrect_questions

        if self.quiz.exam_paper is False or self.request.user.is_superuser or self.request.user.is_lecturer:
            self.sitting.delete()

        return render(self.request, self.result_template_name, results)


def quiz_completion(request, course_pk, quiz_slug):
    return render(request, 'result.html')


# def submit_code(request, exercise_id):
#     exercise = Exercise.objects.get(pk=exercise_id)
#     feedback = None
#
#     if request.method == 'POST':
#         user_code = request.POST.get('code')
#         # Perform code grading
#         score_percentage, feedback = grade_submission(user_code, exercise)
#
#         # Save the submission and grade to the database (you'll need to define Submission model)
#         # Create a Submission instance and save it to the database here
#
#         # Redirect to a scores page with feedback
#         return render(request, 'quiz_app/result_page.html',
#                       {'exercise': exercise, 'score_percentage': score_percentage, 'feedback': feedback})
#
#     return render(request, 'quiz_app/submit_code.html', {'exercise': exercise})
# def quiz_list(request):
#     quizzes = Quiz.objects.all()
#     return render(request, 'quiz_app/quiz_list.html', {'quizzes': quizzes})
#
#
# def quiz_detail(request, quiz_id):
#     quiz = get_object_or_404(Quiz, pk=quiz_id)
#     questions = Question.objects.filter(quiz=quiz)
#
#     # Get all student answers for questions related to this quiz
#     student_answers = StudentAnswer.objects.filter(question__in=questions)
#
#     # Create a list of dictionaries to store student answers for each question
#     student_answers_list = []
#
#     for question in questions:
#         student_answer = student_answers.filter(question=question).first()
#         if student_answer:
#             student_answers_list.append({
#                 'question_text': question.text,
#                 'correct_answer': question.answer,
#                 'student_answer': student_answer.student_answer,
#                 'score': student_answer.score,
#             })
#         else:
#             student_answers_list.append({
#                 'question_text': question.text,
#                 'correct_answer': question.answer,
#                 'student_answer': None,
#                 'score': 0,
#             })
#
#     return render(request, 'quiz_app/quiz_detail.html', {
#         'quiz': quiz,
#         'student_answers_list': student_answers_list,
#     })
# def submit_answer(request, question_id):
#     question = get_object_or_404(Question, pk=question_id)
#
#     if request.method == 'POST':
#         student_answer = request.POST.get('student_answer')
#
#         # Compare student's answer with the correct answer using SequenceMatcher
#         similarity_ratio = SequenceMatcher(None, student_answer, question.answer).ratio()
#
#         # Assign scores based on similarity ratio
#         if similarity_ratio == 1.0:
#             score = 100
#         elif similarity_ratio >= 0.7:
#             score = 50
#         else:
#             score = 0
#
#         # Create a StudentAnswer instance with the calculated score
#         student_answer_instance = StudentAnswer.objects.create(
#             question=question,
#             student_answer=student_answer,
#             # student=request.user,
#             score=score
#         )
#
#         student_answer_instance.save()
#
#         return redirect('quiz_detail', quiz_id=question.quiz.id)
#
#     return render(request, 'quiz_app/submit_answer.html', {'question': question})