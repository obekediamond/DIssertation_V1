from django import forms
from .models import NewPost, Session, Trimester, TRIMESTER


class CreateNewEventForm(forms.ModelForm):
    class Meta:
        model = NewPost
        fields = ('title', 'summary', 'posted_as',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].widget.attrs.update({'class': 'form-control'})
        self.fields['summary'].widget.attrs.update({'class': 'form-control'})
        self.fields['posted_as'].widget.attrs.update({'class': 'form-control'})


class SessionForm(forms.ModelForm):
    next_session_begins = forms.DateTimeField(widget=forms.TextInput(attrs={'type': 'date', }), required=True)

    class Meta:
        model = Session
        fields = ['session', 'is_current_session', 'next_session_begins']


class TrimesterForm(forms.ModelForm):
    trimester = forms.CharField(widget=forms.Select(choices=TRIMESTER, attrs={'class': 'browser-default custom-select', }),
                               label="trimester", )
    is_current_trimester = forms.CharField(widget=forms.Select(choices=((True, 'Yes'), (False, 'No')),
                                                              attrs={'class': 'browser-default custom-select', }),
                                          label="is current trimester ?",)
    session = forms.ModelChoiceField(queryset=Session.objects.all(), widget=forms.Select(
        attrs={'class': 'browser-default custom-select', }), required=True)
    next_trimester_begins = forms.DateTimeField(widget=forms.TextInput(attrs={'type': 'date', 'class': 'form-control',}),
                                                required=True)

    class Meta:
        model = Trimester
        fields = ['trimester', 'is_current_trimester', 'session', 'next_trimester_begins']


class CodeForm(forms.Form):
    code = forms.CharField(widget=forms.Textarea)

