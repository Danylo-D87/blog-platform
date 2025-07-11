# articles/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db import transaction  # Для атомарних операцій з базою даних

from .models import Article, Photo
from .forms import ArticleForm, PhotoFormSet


# Сторінка перегляду всіх статей
class ArticleListView(ListView):
    model = Article
    template_name = 'blog/article_list.html'
    context_object_name = 'articles'
    paginate_by = 10  # Додаємо пагінацію як "плюс"


# Сторінка перегляду конкретної статті
class ArticleDetailView(DetailView):
    model = Article
    template_name = 'blog/article_detail.html'
    context_object_name = 'article'


# Створення нової статті
class ArticleCreateView(LoginRequiredMixin, CreateView):
    model = Article
    form_class = ArticleForm
    template_name = 'blog/article_form.html'
    success_url = reverse_lazy('article_list')  # Перенаправлення після успішного створення

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            # При POST-запиті ініціалізуємо формсет з даними
            data['photo_formset'] = PhotoFormSet(self.request.POST, self.request.FILES)
        else:
            # При GET-запиті ініціалізуємо порожній формсет
            data['photo_formset'] = PhotoFormSet()
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        photo_formset = context['photo_formset']

        # Використовуємо транзакцію для атомарного збереження:
        # якщо щось піде не так з фото, стаття також не буде збережена.
        with transaction.atomic():
            form.instance.author = self.request.user  # Присвоюємо поточного користувача як автора
            self.object = form.save()  # Зберігаємо статтю

            # Зберігаємо фото, якщо формсет валідний
            if photo_formset.is_valid():
                photo_formset.instance = self.object  # Прив'язуємо фото до щойно створеної статті
                photo_formset.save()
            else:
                # Якщо формсет невалідний, але форма статті валідна,
                # це може бути ознакою того, що є помилки у завантажених фото.
                # Для цього прикладу ми дозволяємо статтю без фото,
                # але ви можете додати додаткову логіку або вивести помилки формсету.
                pass
        return super().form_valid(form)


# Редагування статті
class ArticleUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Article
    form_class = ArticleForm
    template_name = 'blog/article_form.html'
    context_object_name = 'article'
    success_url = reverse_lazy('article_list')

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            # При POST-запиті ініціалізуємо формсет з даними та існуючим об'єктом
            data['photo_formset'] = PhotoFormSet(self.request.POST, self.request.FILES, instance=self.object)
        else:
            # При GET-запиті ініціалізуємо формсет з існуючими фотографіями статті
            data['photo_formset'] = PhotoFormSet(instance=self.object)
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        photo_formset = context['photo_formset']

        with transaction.atomic():
            self.object = form.save()  # Зберігаємо зміни у статті

            if photo_formset.is_valid():
                photo_formset.instance = self.object
                photo_formset.save()  # Зберігаємо зміни у фотографіях (додавання, редагування, видалення)
            else:
                pass  # Обробка помилок формсету, якщо потрібно

        return super().form_valid(form)

    def test_func(self):
        # Перевірка, чи поточний користувач є автором статті
        article = self.get_object()
        return article.author == self.request.user


# Видалення статті
class ArticleDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Article
    template_name = 'blog/article_confirm_delete.html'
    context_object_name = 'article'
    success_url = reverse_lazy('article_list')

    def test_func(self):
        # Перевірка, чи поточний користувач є автором статті
        article = self.get_object()
        return article.author == self.request.user