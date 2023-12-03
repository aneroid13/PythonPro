from django.forms import ModelForm, PasswordInput
from django.core.validators import ValidationError
#from django.contrib.auth.models import User
from .models import Question, Answer, CustomUser
from django.forms.fields import CharField

class UserRegistrationForm(ModelForm):
    class Meta:
        model = CustomUser
        fields = ["username", "email", "pict"] ## "first_name", "last_name"

    psw1 = CharField(label="password", widget=PasswordInput)
    psw2 = CharField(label="password confirm", widget=PasswordInput)

    def clean_psw2(self):
        pass1 = self.cleaned_data.get("psw1")
        pass2 = self.cleaned_data.get("psw2")
        if pass1 and pass2 and pass1 == pass2:
            return pass2
        raise ValidationError("Passwords are different")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["psw1"])
        if commit:
            user.save()
        return user

class UserInfo(ModelForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'first_name', 'last_name', 'email', 'pict']

class NewQuestionForm(ModelForm):
    class Meta:
        model = Question
        exclude = ['user', 'date', 'rate']

    def get_initial(self):
        # call super if needed
        return {'tags': self.fields.tags.tag}

class AnswerQuestion(ModelForm):
    class Meta:
        model = Answer
        fields = ["text"]