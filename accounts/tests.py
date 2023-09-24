# from institution.models import Session
# from unittest.mock import patch, Mock
# from django.test import TestCase, RequestFactory
# from django.contrib.auth import get_user_model
# from django.http import JsonResponse, HttpResponse
# from unittest.mock import Mock
# from .views import validate_user, register, profile  # Import your view functions
# from pytz import timezone as pytz_timezone
# from django.utils import timezone
# from .forms import StudentAddForm
# from course.models import Program  # Import Program model from your app's models
# from django.urls import reverse
# from .models import User  # Import your custom User model
# from django.core import mail
# from .forms import LecturerAddForm
# import timeit
#
#
# desired_timezone = pytz_timezone('Europe/London')
# current_time_in_uk_timezone = timezone.now().astimezone(desired_timezone)
#
#
# class YourTestCase(TestCase):
#     def setUp(self):
#         self.factory = RequestFactory()
#
#     def test_validate_user(self):
#         def perform_request():
#             request = self.factory.get('/ajax/validate-username/', {'username': 'testuser'})
#             response = validate_user(request)
#             self.assertIsInstance(response, JsonResponse)
#             self.assertEqual(response.status_code, 200)
#
#         # Measure the time taken to perform the request
#         execution_time = timeit.timeit(perform_request, number=10)  # Adjust the number of iterations as needed
#
#         # Print the execution time
#         print(f"Execution time for 10 requests: {execution_time} seconds")
#
#     def test_register(self):
#         data = {'field1': 'value1', 'field2': 'value2'}
#         request = self.factory.post('/register/', data)
#         request._messages = Mock()
#         response = register(request)
#         self.assertEqual(response.status_code, 200)  # Check for the correct status code
#
#     def test_profile(self):
#         mock_session = Mock(is_current_session=True)
#         with patch('accounts.views.get_object_or_404', return_value=mock_session):
#             username = f'testuser_{current_time_in_uk_timezone}'  # Unique username
#             user = User.objects.create_user(username=username, password='testpass')
#             request = self.factory.get('/profile/')
#             request.user = user
#             response = profile(request)
#             self.assertIsInstance(response, HttpResponse)  # Check for HttpResponse
#
#     def test_password_change(self):
#         username = f'testuser_{current_time_in_uk_timezone}'  # Unique username
#         user = User.objects.create_user(username=username, password='testpass')
#         self.client.login(username=username, password='testpass')
#         data = {
#             'old_password': 'testpass',
#             'new_password1': 'newpassword123',
#             'new_password2': 'newpassword123',
#         }
#         response = self.client.post(reverse('password_change'), data)
#         self.assertRedirects(response, reverse('password_change_done'))
#
#
# class LecturerAddViewTest(TestCase):
#     def setUp(self):
#         self.url = reverse('add_lecturer')
#         self.admin_user = User.objects.create_user(username='admin', password='adminpass', is_superuser=True)
#         self.client.login(username='admin', password='adminpass')
#
#     def test_lecturer_add_form_submission(self):
#         form_data = {
#             'username': 'newlecturer',
#             'first_name': 'John',
#             'last_name': 'Doe',
#             'address': '123 Main St',
#             'phone': '1234567890',
#             'email': 'john@example.com',
#             'password1': 'testpassword',
#             'password2': 'testpassword',
#         }
#
#         response = self.client.post(self.url, form_data)
#         self.assertEqual(response.status_code, 302)  # Check for a successful redirect
#
#         # Check if a new user was created
#         self.assertTrue(User.objects.filter(username='newlecturer').exists())
#
#         # Check if an email was sent
#         self.assertEqual(len(mail.outbox), 1)
#         self.assertEqual(mail.outbox[0].subject, 'Account Created')
#         self.assertIn('Dear John Doe, your account with username: newlecturer', mail.outbox[0].body)
#
#     def test_invalid_lecturer_add_form_submission(self):
#         # Submit an invalid form without required fields
#         form_data = {}
#         response = self.client.post(self.url, form_data)
#         self.assertEqual(response.status_code, 200)  # Check for a form validation error
#         self.assertEqual(len(mail.outbox), 0)
#
#     def test_get_lecturer_add_form(self):
#         response = self.client.get(self.url)
#         self.assertEqual(response.status_code, 200)
#         self.assertIsInstance(response.context['form'], LecturerAddForm)
#
#     def test_authenticated_user_required(self):
#         self.client.logout()  # Log out the user
#         response = self.client.get(self.url)
#         self.assertEqual(response.status_code, 302)
#         self.assertRedirects(response, '/accounts/login/?next=' + self.url)
#
#
# class StudentAddViewTest(TestCase):
#     def setUp(self):
#         self.url = reverse('add_student')
#         self.admin_user = User.objects.create_user(username='admin', password='adminpass', is_superuser=True)
#         self.client.login(username='admin', password='adminpass')
#
#     def test_student_add_form_submission(self):
#         program = Program.objects.create(  # Create a new Program instance
#             title="Test Program",
#             summary="Test Summary")
#
#         form_data = {
#             'username': 'newstudent',
#             'address': '456 Elm St',
#             'phone': '9876543210',
#             'first_name': 'Alice',
#             'last_name': 'Smith',
#             'level': 'Master',
#             'department': program.id,  # Use the ID of the created Program
#             'email': 'alice@example.com',
#             'password1': 'testpassword',
#             'password2': 'testpassword',
#         }
#         print(form_data, '\n')  # Print form data to help with debugging
#
#         form = StudentAddForm(data=form_data)  # Create the form with the data
#         if form.is_valid():
#             print("Form is valid")
#         else:
#             print("Form errors:", form.errors)  # Print form errors if the form is invalid
#
#         response = self.client.post(self.url, form_data)
#         self.assertEqual(response.status_code, 302)  # Check for a successful response
#         print(form_data, '\n', response)
#
#         # Check if a new user was created
#         self.assertTrue(User.objects.filter(username='newstudent').exists())
#
#         # Check if an email was sent
#         self.assertEqual(len(mail.outbox), 1)
#         self.assertEqual(mail.outbox[0].subject, 'Account Created')
#         self.assertIn('Dear Alice Smith, your account with username: newstudent', mail.outbox[0].body)
#
#     def test_invalid_student_add_form_submission(self):
#         # Submit an invalid form without required fields
#         form_data = {}
#         response = self.client.post(self.url, form_data)
#         self.assertEqual(response.status_code, 200)  # Check for a form validation error
#         self.assertContains(response, 'This field is required.')
#
#     def test_get_student_add_form(self):
#         response = self.client.get(self.url)
#         self.assertEqual(response.status_code, 200)
#         self.assertIsInstance(response.context['form'], StudentAddForm)
#
#     def test_authenticated_user_required(self):
#         self.client.logout()  # Log out the user
#         response = self.client.get(self.url)
#         self.assertEqual(response.status_code, 302)
#         self.assertRedirects(response, '/accounts/login/?next=' + self.url)
