# from django.test import TestCase
# from django.urls import reverse
# from accounts.models import User
# from django.core import mail
# from .models import NewPost, Session, Trimester
# from .forms import TrimesterForm
# import timeit
#
#
# class InstitutionViewTest(TestCase):
#     def setUp(self):
#         self.user = User.objects.create_user(username='user1', password='password1')
#         self.lecturer = User.objects.create_user(username='lecturer1', password='password2', is_lecturer=True)
#         self.admin_user = User.objects.create_user(username='admin', password='adminpassword', is_superuser=True)
#         self.admin_user.is_staff = True
#         self.admin_user.save()
#
#     def test_add_post_view(self):
#         self.client.login(username='admin', password='adminpassword')
#         response = self.client.get(reverse('add_item'))
#         self.assertEqual(response.status_code, 200)
#         data = {
#             'title': 'Test Post',
#             'summary': 'This is a test post summary',
#             'posted_as': 'News',  # Adjust the value as needed
#         }
#         response = self.client.post(reverse('add_item'), data)
#         self.assertEqual(response.status_code, 302)  # Expect a redirect
#         # Check if the post was created
#         self.assertTrue(NewPost.objects.filter(title='Test Post').exists())
#
#     def test_session_add_view(self):
#         self.client.login(username='admin', password='adminpassword')
#         response = self.client.get(reverse('add_session'))
#         self.assertEqual(response.status_code, 200)
#         data = {
#             'session': 'Test Session',
#             'is_current_session': True,
#             'next_session_begins': '2023-09-20',  # Include session details
#         }
#         response = self.client.post(reverse('add_session'), data)
#         self.assertEqual(response.status_code, 302)  # Expect a redirect
#
#         # Check if the session was created
#         self.assertTrue(Session.objects.filter(session='Test Session').exists())
#
#     def test_trimester_add_view(self):
#         session = Session.objects.create(session='Test Session', is_current_session=True, next_session_begins='2023-09-20')
#         self.client.login(username='admin', password='adminpassword')
#         response = self.client.get(reverse('add_trimester'))
#         self.assertEqual(response.status_code, 200)
#         data = {
#             'trimester': 'First',
#             'is_current_trimester': True,
#             'session': session.pk,
#             'next_trimester_begins': '2023-09-20',  # Adjust the date as needed
#         }
#         form = TrimesterForm(data=data)  # Create the form with the data
#         if form.is_valid():
#             print("Form is valid")
#         else:
#             print("Form errors:", form.errors)  # Print form errors if the form is invalid
#         response = self.client.post(reverse('add_trimester'), data)
#         self.assertEqual(response.status_code, 302)  # Expect a redirect
#         # Check if the trimester was created
#         self.assertTrue(Trimester.objects.filter(trimester='First').exists())
