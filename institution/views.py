from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from accounts.decorators import admin_required, lecturer_required
from .forms import SessionForm, TrimesterForm, CreateNewEventForm
from .models import *
from accounts.models import User
from django.core.mail import send_mail

# Post methods
@login_required
def index_view(request):
    posts = NewPost.objects.all().order_by('-updated_date')
    context = {
        'title': "News & Events",
        'items': posts,
    }
    return render(request, 'institution/index.html', context)

@login_required
def add_post(request):
    if request.method == 'POST':
        form = CreateNewEventForm(request.POST)
        title = request.POST.get('title')
        summary = request.POST.get('summary')
        posted_as = request.POST.get('posted_as')
        email_list = User.objects.exclude(email__isnull=True).exclude(email__exact='').values_list('email', flat=True)
        email_list = list(email_list)
        if form.is_valid():
            form.save()
            messages.success(request, (title + ' created and users notified'))
            message_mail = "Dear User, a new post (" + posted_as + ") has been created. \n Summary: " + summary
            send_mail('New Post Alert', message_mail, 'settings.EMAIL_HOST_USER', email_list)
            return redirect('home')
        else:
            messages.error(request, 'Review the error and retry')
    else:
        form = CreateNewEventForm()
    return render(request, 'institution/add_post.html', {
        'title': 'Add New Post',
        'form': form,
    })

@login_required
def edit_post(request, pk):
    instance = get_object_or_404(NewPost, pk=pk)
    if request.method == 'POST':
        form = CreateNewEventForm(request.POST, instance=instance)
        title = request.POST.get('title')
        if form.is_valid():
            form.save()

            messages.success(request, (title + ' created'))
            return redirect('home')
        else:
            messages.error(request, 'Review the error and retry')
    else:
        form = CreateNewEventForm(instance=instance)
    return render(request, 'institution/add_post.html', {
        'title': 'Edit Post',
        'form': form,
    })
@login_required
@lecturer_required
def delete_post(request, pk):
    post = get_object_or_404(NewPost, pk=pk)
    title = post.title
    post.delete()
    messages.success(request, (title + ' deleted.'))
    return redirect('home')

# Session methods
@login_required
@lecturer_required
def session_list_view(request):
    sessions = Session.objects.all().order_by('-is_current_session', '-session')
    return render(request, 'institution/session_list.html', {"sessions": sessions})

@login_required
@lecturer_required
def session_add_view(request):
    if request.method == 'POST':
        form = SessionForm(request.POST)
        if form.is_valid():
            is_current_session = form.cleaned_data.get('is_current_session')
            if is_current_session:
                Session.objects.update(is_current_session=False)
            form.save()
            messages.success(request, 'Session added successfully.')
            return redirect('session_list')
    else:
        form = SessionForm()
    return render(request, 'institution/session_update.html', {'form': form})

@login_required
@lecturer_required
def session_update_view(request, pk):
    session = Session.objects.get(pk=pk)
    if request.method == 'POST':
        form = SessionForm(request.POST, instance=session)
        if form.is_valid():
            is_current_session = form.cleaned_data.get('is_current_session')
            if is_current_session:
                Session.objects.exclude(pk=session.pk).update(is_current_session=False)
            form.save()
            messages.success(request, 'Session updated successfully.')
            return redirect('session_list')
    else:
        form = SessionForm(instance=session)
    return render(request, 'institution/session_update.html', {'form': form})

@login_required
@lecturer_required
def session_delete_view(request, pk):
    session = get_object_or_404(Session, pk=pk)
    if session.is_current_session:
        messages.error(request, "Cannot delete current session, contact App Support")
        return redirect('session_list')
    else:
        session.delete()
        messages.success(request, "Session deleted")
    return redirect('session_list')


# Trimester Methods
@login_required
@lecturer_required
def trimester_list_view(request):
    trimesters = Trimester.objects.all().order_by('-is_current_trimester', '-trimester')
    return render(request, 'institution/trimester_list.html', {"trimesters": trimesters, })


@login_required
@lecturer_required
def trimester_add_view(request):
    if request.method == 'POST':
        form = TrimesterForm(request.POST)
        if form.is_valid():
            data = form.data.get('is_current_trimester')
            if data == 'True':
                trimester = form.data.get('trimester')
                ss = form.data.get('session')
                session = Session.objects.get(pk=ss)
                try:
                    if Trimester.objects.get(trimester=trimester, session=ss):
                        messages.error(request, trimester + " trimester in " + session.session + " session already exist")
                        return redirect('add_trimester')
                except:
                    trimesters = Trimester.objects.all()
                    sessions = Session.objects.all()
                    if trimesters:
                        for trimester in trimesters:
                            if trimester.is_current_trimester == True:
                                unset_trimester = Trimester.objects.get(is_current_trimester=True)
                                unset_trimester.is_current_trimester = False
                                unset_trimester.save()
                        for session in sessions:
                            if session.is_current_session == True:
                                unset_session = Session.objects.get(is_current_session=True)
                                unset_session.is_current_session = False
                                unset_session.save()

                    new_session = request.POST.get('session')
                    set_session = Session.objects.get(pk=new_session)
                    set_session.is_current_session = True
                    set_session.save()
                    form.save()
                    messages.success(request, 'Trimester added successfully.')
                    return redirect('trimester_list')

            form.save()
            messages.success(request, 'Trimester added successfully. ')
            return redirect('trimester_list')
    else:
        form = TrimesterForm()
    return render(request, 'institution/trimester_update.html', {'form': form})


@login_required
@lecturer_required
def trimester_update_view(request, pk):
    trimester = Trimester.objects.get(pk=pk)
    if request.method == 'POST':
        if request.POST.get('is_current_trimester') == 'True':
            unset_trimester = Trimester.objects.get(is_current_trimester=True)
            unset_trimester.is_current_trimester = False
            unset_trimester.save()
            unset_session = Session.objects.get(is_current_session=True)
            unset_session.is_current_session = False
            unset_session.save()
            new_session = request.POST.get('session')
            form = TrimesterForm(request.POST, instance=trimester)
            if form.is_valid():
                set_session = Session.objects.get(pk=new_session)
                set_session.is_current_session = True
                set_session.save()
                form.save()
                messages.success(request, 'Trimester updated successfully !')
                return redirect('trimester_list')
        else:
            form = TrimesterForm(request.POST, instance=trimester)
            if form.is_valid():
                form.save()
                return redirect('trimester_list')

    else:
        form = TrimesterForm(instance=trimester)
    return render(request, 'institution/trimester_update.html', {'form': form})


@login_required
@lecturer_required
def trimester_delete_view(request, pk):
    trimester = get_object_or_404(Trimester, pk=pk)
    if trimester.is_current_trimester:
        messages.error(request, "You cannot delete current trimester")
        return redirect('trimester_list')
    else:
        trimester.delete()
        messages.success(request, "Trimester successfully deleted")
    return redirect('trimester_list')

@login_required
@admin_required
def dashboard_view(request):
    return render(request, 'institution/dashboard.html')

# def grade_submission(user_code, exercise):
#     try:
#         # Define test cases for the exercise
#         class ExerciseTestCase(unittest.TestCase):
#             def test_code(self):
#                 # Load the exercise-specific data (e.g., inputs and expected outputs)
#                 inputs = exercise.inputs.split('\n')
#                 expected_outputs = exercise.expected_outputs.split('\n')
#
#                 # Evaluate the user's code against each test case
#                 for input_data, expected_output in zip(inputs, expected_outputs):
#                     scores = run_code(user_code, input_data)
#                     self.assertEqual(scores.strip(), expected_output.strip())
#
#         # Create a test suite and run the test cases
#         suite = unittest.TestLoader().loadTestsFromTestCase(ExerciseTestCase)
#         test_result = unittest.TextTestRunner(verbosity=0).run(suite)
#
#         # Calculate the score based on the test results
#         num_passed = test_result.testsRun - len(test_result.failures) - len(test_result.errors)
#         max_score = test_result.testsRun
#         score_percentage = (num_passed / max_score) * 100
#
#         if score_percentage == 100:
#             feedback = "Congratulations! Your code passed all test cases."
#         else:
#             feedback = "Your code did not pass all test cases. Review your code and try again."
#
#         return score_percentage, feedback
#     except Exception as e:
#         # Handle any exceptions (e.g., syntax errors)
#         return 0, str(e)
#
#
# def run_code(user_code, input_data):
#     try:
#         original_stdout = sys.stdout
#         sys.stdout = StringIO()
#         exec(user_code)
#         output = sys.stdout.getvalue()
#         sys.stdout = original_stdout
#         return output
#     except Exception as e:
#         return str(e)