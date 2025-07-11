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

from .models import Article
from .forms import ArticleForm, PhotoFormSet


class ArticleListView(ListView):
    model = Article
    template_name = 'blog/article_list.html'
    context_object_name = 'articles'
    paginate_by = 10


class ArticleDetailView(DetailView):
    model = Article
    template_name = 'blog/article_detail.html'
    context_object_name = 'article'


class ArticleCreateView(LoginRequiredMixin, CreateView):
    model = Article
    form_class = ArticleForm
    template_name = 'blog/article_form.html'
    success_url = reverse_lazy('article_list')

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data['photo_formset'] = PhotoFormSet(self.request.POST, self.request.FILES)
        else:
            data['photo_formset'] = PhotoFormSet()
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        photo_formset = context['photo_formset']

        with transaction.atomic():
            form.instance.author = self.request.user
            self.object = form.save()

            if photo_formset.is_valid():
                photo_formset.instance = self.object
                photo_formset.save()
            else:
                pass
        return super().form_valid(form)


class ArticleUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Article
    form_class = ArticleForm
    template_name = 'blog/article_form.html'
    context_object_name = 'article'
    success_url = reverse_lazy('article_list')

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data['photo_formset'] = PhotoFormSet(self.request.POST, self.request.FILES, instance=self.object)
        else:
            data['photo_formset'] = PhotoFormSet(instance=self.object)
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        photo_formset = context['photo_formset']

        with transaction.atomic():
            self.object = form.save()

            if photo_formset.is_valid():
                photo_formset.instance = self.object
                photo_formset.save()
            else:
                pass

        return super().form_valid(form)

    def test_func(self):
        article = self.get_object()
        return article.author == self.request.user


# Видалення статті
class ArticleDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Article
    template_name = 'blog/article_confirm_delete.html'
    context_object_name = 'article'
    success_url = reverse_lazy('article_list')

    def test_func(self):
        article = self.get_object()
        return article.author == self.request.user
