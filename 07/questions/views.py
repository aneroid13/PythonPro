from django.shortcuts import reverse, render
from django.urls import reverse_lazy
from django.http.response import HttpResponse
from django.views.generic import CreateView, DetailView, UpdateView, ListView
from django.contrib.auth.views import LoginView, LogoutView
# from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Question, Answer, CustomUser
from .forms import NewQuestionForm, AnswerQuestion, UserRegistrationForm, UserInfo


class IndexView(ListView):
    model = Question
    template_name = "questions/index.html"

    def get_queryset(self):
        return Question.objects.order_by("-date")[:20]

class AskView(LoginRequiredMixin, CreateView):
    model = Question
    context_object_name = 'form'
    form_class = NewQuestionForm

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.save()
        return super().form_valid(form)

class LoginUser(LoginView):
    template_name = "questions/user_login.html"
    redirect_authenticated_user = True

    def get_default_redirect_url(self):
        return reverse("qu:index")

class LogoutUser(LogoutView):
    template_name = "questions/user_logout.html"

    def get_default_redirect_url(self):
        return reverse("qu:index")

class QuestionView(DetailView, CreateView):
    model = Question
    template_name = "questions/question_view.html"
    context_object_name = 'question'
    form_class = AnswerQuestion

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.question_id = self.kwargs['pk']
        form.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["answers_list"] = Answer.objects.filter(question_id=self.kwargs['pk'])
        return context

class SearchView(ListView):
    model = Question
    template_name = "questions/question_search.html"
    context_object_name = 'search_list'
    # queryset = Question.objects.all()

    def post(self, request, *args, **kwargs):
        search_word = request.POST.get('search')
        search = self.get_queryset().filter(header__contains=search_word)
        search2 = self.get_queryset().filter(text__contains=search_word)
        return render(request, self.template_name, {'search_list': search.union(search2)})

class SignUpUser(CreateView):
    model = CustomUser
    context_object_name = 'form'
    form_class = UserRegistrationForm
    template_name = "questions/user_registration.html"

class UserSettingsView(UpdateView):
    model = CustomUser
    context_object_name = 'user'
    form_class = UserInfo
    success_url = reverse_lazy('user')
    template_name = "questions/user_info.html"

    def get_object(self, queryset=None):
        return CustomUser.objects.get(username=self.kwargs['username'])

def tags(request):
    return HttpResponse("Tags")
