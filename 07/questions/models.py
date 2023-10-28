from django.db import models

class User(models.Model):
    name = models.CharField()
    email = models.EmailField()
    psw = models.CharField()
    pict = models.ImageField()
    date = models.DateTimeField()

class Question(models.Model):
    header = models.CharField()
    text = models.TextField()
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    date = models.DateTimeField()
    tags = models.CharField()

class Answer(models.Model):
    text = models.TextField()
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    date = models.DateTimeField()
    true_answ = models.BooleanField()

class Tag(models.Model):
    name = models.CharField()
