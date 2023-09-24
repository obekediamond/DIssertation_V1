from django.test import TestCase
from django.urls import reverse
from accounts.models import User
from django.utils import timezone
from .models import Quiz, MCQuestion, Essay_Question, Progress, Question, Sitting
from course.models import Program, Course
from .forms import QuizAddForm
from quiz.forms import MCQuestionForm, MCQuestionFormSet, EssayForm, QuestionForm
from quiz.views import MCQuestionCreate
from django.contrib.messages import get_messages
from django.core.exceptions import PermissionDenied
from django.contrib.messages import WARNING
from django.shortcuts import redirect
from datetime import timedelta


class QuizViewTest(TestCase):

    def setUp(self):
        self.admin_user = User.objects.create_user(username='testuser', password='testpassword', is_superuser=True)
        self.admin_user.is_staff = True
        self.admin_user.save()
        self.program = Program.objects.create(title='Test Program', summary='Test Summary')
        self.course = Course.objects.create(title='Test Course', code='TEST101', credit=3,
                                            summary='Test Course Summary', program=self.program, level='Master', year=1,
                                            trimester='First')
        print(self.course.slug)
        self.quiz = Quiz.objects.create(
            cat_q='ess', course=self.course, title='Test Quiz', slug='test-quiz', description='Test Quiz Description',
            assignment_start_date=timezone.now() - timedelta(days=1), assignment_due_date=timezone.now() + timedelta(days=1),
            random_order=True, answers_at_end=True, exam_paper=True, single_attempt=True, pass_mark=60, draft=False,
            timer=2)
        self.quiz.save()
        self.essay_questions = Essay_Question.objects.create(content='Test Essay Question',
                                                             explanation='Explanation for the essay question',
                                                             expected_input='''print('User input code')''',
                                                             expected_output='User input code')
        self.essay_questions.save()
        self.essay_questions.quiz.add(self.quiz)

    def test_code_execution_view(self):
        self.client.login(username='testuser', password='testpassword')
        url = reverse('execute_code', kwargs={'slug': self.quiz.slug, 'pk': self.course.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        code_to_execute = '''print('User input code')'''
        response = self.client.post(url, {'answers': code_to_execute})
        self.assertEqual(response.status_code, 200)


    def test_quiz_create_view(self):
        self.client.login(username='testuser', password='testpassword')
        url = reverse('quiz_create', kwargs={'slug': 'test-course'})
        response = self.client.get(url)
        print(response)
        self.assertEqual(response.status_code, 200)
        form_data = {'cat_q':'mcq', 'course':self.course.id, 'title':'Test Quiz1', 'slug':'test-quiz1',
                     'description':'Test Quiz1 Description', 'assignment_start_date':timezone.now(),
                     'assignment_due_date':timezone.now() + timezone.timedelta(days=1),
                     'random_order':True, 'answers_at_end':True, 'exam_paper':True, 'single_attempt':True,
                     'pass_mark':60, 'draft':False, 'timer':2}
        form = QuizAddForm(data=form_data)  # Create the form with the data
        if form.is_valid():
            print("Form is valid")
        else:
            print("Form errors:", form.errors)  # Print form errors if the form is invalid
        response2 = self.client.post(url, form_data)
        print(response2)
        self.assertEqual(response2.status_code, 302)
        self.assertTrue(Quiz.objects.filter(title='Test Quiz1').exists())

    def test_mc_question_create_view(self):
        self.client.login(username='testuser', password='testpassword')
        url = reverse('mc_create', kwargs={'slug': self.course.slug, 'quiz_id': self.quiz.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        print(response)
        form_data = {
            'content': 'Sample MCQ Question',
            'choice_set-TOTAL_FORMS': 2,
            'choice_set-INITIAL_FORMS': 0,
            'choice_set-MIN_NUM_FORMS': 0,
            'choice_set-MAX_NUM_FORMS': 1000,
            'choice_set-0-choice': 'Option A',
            'choice_set-0-correct': True,
            'choice_set-1-choice': 'Option B',
            'choice_set-1-correct': False,
        }
        form = MCQuestionForm(data=form_data)  # Create the form with the data
        if form.is_valid():
            print("Form is valid")
        else:
            print("Form errors:", form.errors)  # Print form errors if the form is invalid
        response = self.client.post(url, form_data)
        self.assertEqual(response.status_code, 302)  # Expect a redirect
        self.assertTrue(MCQuestion.objects.filter(content='Sample MCQ Question').exists())

    def test_essay_question_create_view(self):
        self.client.login(username='testuser', password='testpassword')
        url = reverse('essay_create', kwargs={'slug': 'test-course', 'quiz_id': self.quiz.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        form_data = {
            'content': 'Test Essay Question',
            # 'figure': None,  # You can set a file here if needed
            'explanation': 'Explanation for the essay question',
            'expected_input': 'Expected input for the essay question',
            'expected_output': 'Expected output for the essay question',
        }
        response = self.client.post(url, form_data)
        self.assertEqual(response.status_code, 302)  # Expect a redirect
        self.assertTrue(Essay_Question.objects.filter(content='Test Essay Question').exists())