from django.shortcuts import render, redirect, get_list_or_404
from django.http.response import HttpResponse
from django.views.generic import CreateView, DetailView, ListView
from .models import Question
from .forms import QuestionForm

def index(request):
    question_list = get_list_or_404(Question.objects.order_by("-date")[:20])
    return render(request, "questions/index.html", {"question_list": question_list})

class index_dv(DetailView):
    template_name = "questions/index.html"
    context_object_name = "question_list"

    def get_queryset(self):
        return Question.objects.order_by("-date")[:20]

class lv(ListView):
    model = Question
    template_name = "questions/index.html"

class question(CreateView):
    model = Question
    #context_object_name = 'form'
    form_class = QuestionForm

    # def get(self, request, *args, **kwargs):
    #     return render(
    #         request,
    #         self.template_name,
    #         {self.context_object_name:
    #             self.form_class()})
    #
    # def post(self, request, *args, **kwargs):
    #     bound_form = self.form_class(request.POST)
    #     if bound_form.is_valid():
    #         new_obj = bound_form.save()
    #         return redirect(new_obj)
    #     return render(
    #         request,
    #         self.template_name,
    #         {self.context_object_name:
    #             bound_form})

def login(request):
    return HttpResponse("Dummy")

def ask(request):
    return HttpResponse("Dummy")

def search(request):
    return HttpResponse("Dummy")

def signup(request):
    return HttpResponse("Dummy")

def tags(request):
    return HttpResponse("Tags")
