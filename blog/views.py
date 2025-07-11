from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from .models import Article, Photo
from .forms import ArticleForm


class ArticleListView(ListView):
    model = Article
    template_name = 'blog/article_list.html'
    context_object_name = 'articles'


class ArticleDetailView(DetailView):
    model = Article
    template_name = 'blog/article_detail.html'
    context_object_name = 'article'


class ArticleCreateView(LoginRequiredMixin, CreateView):
    model = Article
    form_class = ArticleForm
    template_name = 'blog/article_form.html'
    success_url = reverse_lazy('article_list')

    def form_valid(self, form):
        form.instance.author = self.request.user
        response = super().form_valid(form)

        # handle images
        for file in self.request.FILES.getlist('images'):
            Photo.objects.create(article=self.object, image=file)

        return response


class ArticleUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Article
    form_class = ArticleForm
    template_name = 'blog/article_form.html'
    success_url = reverse_lazy('article_list')

    def form_valid(self, form):
        response = super().form_valid(form)

        if self.request.FILES:
            self.object.images.all().delete()
            for file in self.request.FILES.getlist('images'):
                Photo.objects.create(article=self.object, image=file)

        return response

    def test_func(self):
        article = self.get_object()
        return article.author == self.request.user


class ArticleDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Article
    template_name = 'blog/article_confirm_delete.html'
    success_url = reverse_lazy('article_list')

    def test_func(self):
        article = self.get_object()
        return article.author == self.request.user
