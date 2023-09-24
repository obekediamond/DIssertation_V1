from django import forms
from django.db import transaction
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, PasswordResetForm
from .models import *
from course.models import Program


class LecturerAddForm(UserCreationForm):
    # Form to be presented to the template for adding lecturers
    username = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'type': 'text', 'class': 'form-control', }),
                               label="Username", )
    first_name = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'type': 'text', 'class': 'form-control', }),
                                 label="First Name", )
    last_name = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'type': 'text', 'class': 'form-control', }),
                                label="Last Name", )
    address = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'type': 'text', 'class': 'form-control', }),
                              label="Address", )
    phone = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'type': 'text', 'class': 'form-control', }),
                            label="Mobile No.", )
    email = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'type': 'text', 'class': 'form-control', }),
                            label="Email", )
    password1 = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'type': 'password', 'class': 'form-control', }),
                                label="Password", )
    password2 = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'type': 'password', 'class': 'form-control', }),
                                label="Password Confirmation", )

    class Meta(UserCreationForm.Meta):
        model = User

    @transaction.atomic()
    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_lecturer = True
        user.first_name = self.cleaned_data.get('first_name')
        user.last_name = self.cleaned_data.get('last_name')
        user.phone = self.cleaned_data.get('phone')
        user.address = self.cleaned_data.get('address')
        user.email = self.cleaned_data.get('email')
        if commit:
            user.save()
        return user


class StudentAddForm(UserCreationForm):
    # Form to be presented to the template for adding students
    username = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'type': 'text','class': 'form-control',
                                                                            'id': 'username_id'}),label="Username",)
    address = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'type': 'text','class': 'form-control',}),
                              label="Address",)
    phone = forms.CharField(max_length=50,widget=forms.TextInput(attrs={'type': 'text','class': 'form-control',}),
                            label="Mobile No.",)
    first_name = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'type': 'text','class': 'form-control',}),
                                 label="First name",)
    last_name = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'type': 'text','class': 'form-control',}),
                                label="Last name",)
    level = forms.CharField(widget=forms.Select(choices=LEVEL, attrs={'class': 'browser-default custom-select form-control',}),)
    department = forms.ModelChoiceField(queryset=Program.objects.all(),
                                        widget=forms.Select(attrs={'class': 'browser-default custom-select form-control'}),
                                        label="Department",)
    email = forms.EmailField(widget=forms.TextInput(attrs={'type': 'email','class': 'form-control',}),
                             label="Email Address",)
    password1 = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'type': 'password', 'class': 'form-control', }),
                                label="Password", )
    password2 = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'type': 'password', 'class': 'form-control', }),
                                label="Password Confirmation", )

    class Meta(UserCreationForm.Meta):
        model = User

    @transaction.atomic()
    def save(self):
        user = super().save(commit=False)
        user.is_student = True
        user.first_name = self.cleaned_data.get('first_name')
        user.last_name = self.cleaned_data.get('last_name')
        user.address = self.cleaned_data.get('address')
        user.phone = self.cleaned_data.get('phone')
        user.email = self.cleaned_data.get('email')
        user.save()
        student = Student.objects.create(
            student=user,
            level=self.cleaned_data.get('level'),
            department=self.cleaned_data.get('department')
        )
        student.save()
        return user


class ProfileUpdateForm(UserChangeForm):
    # Form to be presented to the template for updating profiles
    email = forms.EmailField(widget=forms.TextInput(attrs={'type': 'email', 'class': 'form-control', }),
                             label="Email Address",)
    first_name = forms.CharField(widget=forms.TextInput(attrs={'type': 'text', 'class': 'form-control', }),
                                 label="First Name", )
    last_name = forms.CharField(widget=forms.TextInput(attrs={'type': 'text', 'class': 'form-control', }),
                                label="Last Name", )
    phone = forms.CharField(widget=forms.TextInput(attrs={'type': 'text', 'class': 'form-control', }),
                            label="Phone No.", )
    address = forms.CharField(widget=forms.TextInput(attrs={'type': 'text', 'class': 'form-control', }),
                              label="Address / city", )

    class Meta:
        model = User
        fields = ['email', 'phone', 'address', 'picture', 'first_name', 'last_name']


class EmailValidationOnForgotPassword(PasswordResetForm):
    def clean_email(self):
        email = self.cleaned_data['email']
        if not User.objects.filter(email__iexact=email, is_active=True).exists():
            msg = "E-mail address is not found, reconfirm and retry. "
            self.add_error('email', msg)
            return email

