from django.forms import Form
from django.forms.fields import *

class QuestionForm(Form):
    user = CharField()
    email = EmailField()
    psw = CharField()
    pict = ImageField()
    date = DateTimeField()