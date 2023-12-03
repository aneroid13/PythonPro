from django.db import models
from django.shortcuts import reverse
from django.contrib.auth.models import User

class CustomUser(User):
    pict = models.ImageField("Your image")

    def set_password(self, psw_verifyed):
        self.set_password(psw_verifyed)

    def get_absolute_url(self):
        return reverse('qu:user', kwargs={'pk': self.id})


class Tag(models.Model):
    name = models.CharField("Tag")

class QuestionRate(models.Model):
    question = models.ForeignKey('Question', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    rate = models.IntegerField()

class Question(models.Model):
    header = models.CharField("Question object")
    text = models.TextField("Question text")
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    date = models.DateTimeField(auto_now=True)
    tags = models.ManyToManyField(Tag)

    @property
    def rate(self):
        return QuestionRate.objects.filter(question=self.id).aggregate(models.Sum('rate'))

    def rate_increase(self, current_user):
        rate_obj = self.get_rate(current_user)
        rate_obj = 1 if rate_obj else ""

    def rate_decrease(self, current_user):
        if self.get_rate(current_user):
            self.get_rate(current_user).rate = -1

    def get_rate(self, current_user):
        return QuestionRate.objects.filter(question=self.id, user=current_user)

    def get_absolute_url(self):
        return reverse('qu:question', kwargs={'pk': self.id})


class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    text = models.TextField("Answer")
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    date = models.DateTimeField(auto_now=True)
    true_answ = models.BooleanField(default=False)

    def get_absolute_url(self):
        return reverse('qu:question', kwargs={'pk': self.question.id})
