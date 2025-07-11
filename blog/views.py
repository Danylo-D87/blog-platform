from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)
from django.urls import reverse_lazy
from django.contrib.auth.mixins import (
    LoginRequiredMixin,
    UserPassesTestMixin,
)
from django.db import transaction

from utils.openai_client import generate_article_content
from .models import Article, Photo
from .forms import ArticleForm, PhotoFormSet


class ArticleListView(ListView):
    model = Article
    template_name = "blog/article_list.html"
    context_object_name = "articles"
    paginate_by = 9


class ArticleDetailView(DetailView):
    model = Article
    template_name = "blog/article_detail.html"
    context_object_name = "article"


class ArticleCreateView(LoginRequiredMixin, CreateView):
    model = Article
    form_class = ArticleForm
    template_name = "blog/article_form.html"
    success_url = reverse_lazy("article_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context["photo_formset"] = PhotoFormSet(self.request.POST, self.request.FILES)
        else:
            context["photo_formset"] = PhotoFormSet(queryset=Photo.objects.none())
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        photo_formset = context["photo_formset"]

        form.instance.author = self.request.user

        if photo_formset.is_valid() and form.is_valid():

            # AI
            prompt = form.cleaned_data.get("prompt")
            if prompt and not form.cleaned_data.get("content"):
                try:
                    form.instance.content = generate_article_content(prompt)
                except Exception as e:
                    form.add_error('prompt', f"Помилка генерації: {e}")
                    return self.render_to_response(self.get_context_data(form=form))

            with transaction.atomic():
                self.object = form.save()
                photo_formset.instance = self.object
                photo_formset.save()
            return super().form_valid(form)
        else:
            return self.render_to_response(self.get_context_data(form=form))


class ArticleUpdateView(
    LoginRequiredMixin,
    UserPassesTestMixin,
    UpdateView,
):
    model = Article
    form_class = ArticleForm
    template_name = "blog/article_form.html"
    context_object_name = "article"
    success_url = reverse_lazy("article_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context["photo_formset"] = PhotoFormSet(
                self.request.POST,
                self.request.FILES,
                instance=self.object,
            )
        else:
            context["photo_formset"] = PhotoFormSet(instance=self.object)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        photo_formset = context["photo_formset"]

        if photo_formset.is_valid() and form.is_valid():

            # AI
            prompt = form.cleaned_data.get("prompt")
            if prompt and not form.cleaned_data.get("content"):
                try:
                    form.instance.content = generate_article_content(prompt)
                except Exception as e:
                    form.add_error('prompt', f"Помилка генерації: {e}")
                    return self.render_to_response(self.get_context_data(form=form))

            with transaction.atomic():
                self.object = form.save()
                photo_formset.instance = self.object
                photo_formset.save()
            return super().form_valid(form)
        else:
            return self.render_to_response(self.get_context_data(form=form))

    def test_func(self):
        article = self.get_object()
        return article.author == self.request.user


class ArticleDeleteView(
    LoginRequiredMixin,
    UserPassesTestMixin,
    DeleteView,
):
    model = Article
    template_name = "blog/article_confirm_delete.html"
    context_object_name = "article"
    success_url = reverse_lazy("article_list")

    def test_func(self):
        article = self.get_object()
        return article.author == self.request.user
