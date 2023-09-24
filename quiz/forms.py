from django import forms
from django.forms.widgets import RadioSelect, Textarea
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.utils.translation import gettext_lazy as _
from django.db import transaction
from django.forms.models import inlineformset_factory
from accounts.models import User
from .models import *


class QuestionForm(forms.Form):
    def __init__(self, question, *args, **kwargs):
        super(QuestionForm, self).__init__(*args, **kwargs)
        choices = [x for x in question.get_choices_list()]
        self.fields["answers"] = forms.ChoiceField(choices=choices, widget=RadioSelect)


class EssayQuestionForm(forms.Form):
    def __init__(self, question, *args, **kwargs):
        super(EssayQuestionForm, self).__init__(*args, **kwargs)
        self.fields["answers"] = forms.CharField(
            label='Sandboxed IDE (RestrictedPython)',
            widget=Textarea(attrs={'style': 'width:100%', 'placeholder': 'Type Answer Here'}),
            required=False)


class EssayForm(forms.ModelForm):
    class Meta:
        model = Essay_Question  # Associate the form with the Essay_Question model
        fields = ['content', 'figure', 'explanation', 'expected_input', 'expected_output']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 7}),  # Set 'rows' attribute to 4
        }


class QuizAddForm(forms.ModelForm):

    class Meta:
        model = Quiz
        exclude = []
        widgets = {
            'assignment_start_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'assignment_due_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    questions = forms.ModelMultipleChoiceField(
        queryset=Question.objects.all().select_subclasses(),
        required=False,
        label=_("Questions"),
        widget=FilteredSelectMultiple(
            verbose_name=_("Questions"),
            is_stacked=False))

    def __init__(self, *args, **kwargs):
        super(QuizAddForm, self).__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['questions'].initial = self.instance.question_set.all().select_subclasses()

    def save(self, commit=True):
        quiz = super(QuizAddForm, self).save(commit=False)
        quiz.save()
        quiz.question_set.set(self.cleaned_data['questions'])
        self.save_m2m()
        return quiz


class MCQuestionForm(forms.ModelForm):
    class Meta:
        model = MCQuestion
        exclude = ()


MCQuestionFormSet = inlineformset_factory(
    MCQuestion, Choice, form=MCQuestionForm, fields=['choice', 'correct'], can_delete=True, extra=5)


# class CodeForm(forms.Form):
#     code = forms.CharField(widget=forms.Textarea(attrs={'style': 'width:100%'}))
#
#
# class SampleQuestionForm(forms.ModelForm):
#     class Meta:
#         model = Question
#         # fields = ['text', 'answer']
