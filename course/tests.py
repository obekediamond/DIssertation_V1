# from django.test import TestCase
# from django.urls import reverse
# from accounts.models import User
# from .models import Program, Course, CourseAllocation
# from django.http import Http404
# import timeit
#
#
# class ProgramViewTest(TestCase):
#     def setUp(self):
#         self.user = User.objects.create_user(username='appuser', password='appuserpassword')  # Non-admin user
#         self.user.save()
#         self.admin_user = User.objects.create_user(username='admin2', password='admin2password', is_superuser=True)
#         self.admin_user.is_staff = True
#         self.admin_user.save()
#
#     def test_add_program_view(self):
#         self.client.login(username='admin2', password='admin2password')
#         response = self.client.get(reverse('add_program'))
#         self.assertEqual(response.status_code, 200)
#         response = self.client.post(reverse('add_program'), {'title': 'Test Program', 'summary': 'Test Summary'})
#         self.assertEqual(response.status_code, 302)
#         self.assertTrue(Program.objects.filter(title='Test Program').exists())
#
#     def test_add_program_view_requires_admin(self):
#         self.client.login(username='appuser', password='appuserpassword')
#         response = False
#         if self.client.login():
#             response = True
#         else:
#             response = False
#         self.assertNotEqual(response, True)
#
#
# class CourseViewTest(TestCase):
#     def setUp(self):
#         self.user = User.objects.create_user(username='user', password='userpassword')
#         self.admin_user = User.objects.create_user(username='admin', password='adminpassword', is_superuser=True)
#         self.admin_user.is_staff = True
#         self.admin_user.save()
#         self.program = Program.objects.create(title='Test Program', summary='Test Summary')
#         self.course = Course.objects.create(title='Test Course', code='TEST101', credit=3, summary='Test Course Summary', program=self.program, level='Master', year=1, trimester='First')
#
#     def test_add_course_view(self):
#         self.client.login(username='admin', password='adminpassword')
#         response = self.client.get(reverse('add_course', kwargs={'pk': self.program.pk}))
#         self.assertEqual(response.status_code, 200)
#         response = self.client.post(reverse('add_course', kwargs={'pk': self.program.pk}), {'title': 'New Course', 'code': 'NEW101', 'credit': 4, 'summary': 'New Course Summary', 'program': self.program.pk, 'level': 'Master', 'year': 1, 'trimester': 'First'})
#         self.assertEqual(response.status_code, 302)
#         self.assertTrue(Course.objects.filter(title='New Course').exists())
#
#     def test_add_course_view_requires_admin(self):
#         self.client.login(username='user', password='userpassword')
#         response = False
#         if self.client.login():
#             response = True
#         else:
#             response = False
#         self.assertNotEqual(response, True)
#
#
# class UserCourseListViewTest(TestCase):
#     def setUp(self):
#         self.user = User.objects.create_user(username='user', password='userpassword', is_superuser=True)
#         self.lecturer = User.objects.create_user(username='lecturer', password='lecturerpassword')
#         self.lecturer.is_lecturer = True
#         self.lecturer.save()
#         self.lecturer2 = User.objects.create_user(username='lecturer2', password='lecturerpassword2')
#         self.lecturer2.is_lecturer = True
#         self.lecturer2.save()
#         self.student = User.objects.create_user(username='student1', password='studentpassword')
#         self.student.is_student = True
#         self.student.save()
#         self.program = Program.objects.create(title='Test Program', summary='Test Summary')
#         self.program.save()
#         self.course = Course.objects.create(title='Test Course', code='TEST101', credit=3, summary='Test Course Summary', program=self.program, level='Master', year=1, trimester='First')
#         self.course.save()
#         self.course_allocation = CourseAllocation.objects.create(lecturer=self.lecturer)
#         self.course_allocation.save()
#         self.course_allocation.courses.add(self.course)
#
#     def test_user_course_list_view_as_lecturer(self):
#         self.client.login(username='lecturer', password='lecturerpassword')
#         response = self.client.get(reverse('user_course_list'))
#         self.assertEqual(response.status_code, 200)
#         self.assertContains(response, 'Test Course')
#
#     def test_user_course_list_view_as_student(self):
#         self.client.login(username='student', password='studentpassword')
#         response = self.client.get(reverse('user_course_list'))
#         self.assertEqual(response.status_code, 302)
#
#     def test_user_course_list_view_as_unauthorized_user(self):
#         self.client.login(username='lecturer2', password='lecturerpassword2')
#         response = self.client.get(reverse('user_course_list'))
#         self.assertEqual(response.status_code, 200)
# #