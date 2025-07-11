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


class ArticleCreateView(LoginRequiredMixin, CreateView):
    """
        View to create a new Article.
        Handles article form and related photo formset.
        Integrates AI content generation if prompt is provided.
    """
    model = Article
    form_class = ArticleForm
    template_name = "blog/article_form.html"
    success_url = reverse_lazy("article_list")

    def get_context_data(self, **kwargs):
        """
            Add photo formset to context for rendering in template.
            Use POST data if present, else provide empty formset.
        """
        context = super().get_context_data(**kwargs)

        if self.request.POST:
            context["photo_formset"] = PhotoFormSet(self.request.POST, self.request.FILES)
        else:
            context["photo_formset"] = PhotoFormSet(queryset=Photo.objects.none())

        return context

    def form_valid(self, form):
        """
            Validate both article form and photo formset.
            If valid, attempt AI content generation if prompt is set and content empty.
            Save all in atomic transaction.
        """
        context = self.get_context_data()
        photo_formset = context["photo_formset"]

        form.instance.author = self.request.user

        if photo_formset.is_valid() and form.is_valid():

            self._try_generate_content(form)

            with transaction.atomic():
                self.object = form.save()
                photo_formset.instance = self.object
                photo_formset.save()

            return super().form_valid(form)

        return self.render_to_response(self.get_context_data(form=form))

    @staticmethod
    def _try_generate_content(form):
        """
            Generate article content using AI if prompt exists and content is empty.
            Attach any error to the form's 'prompt' field.
        """
        prompt = form.cleaned_data.get("prompt")

        if prompt and not form.cleaned_data.get("content"):
            try:
                form.instance.content = generate_article_content(prompt)
            except Exception as e:
                form.add_error("prompt", f"Error: {e}")
                raise


class ArticleUpdateView(
    LoginRequiredMixin,
    UserPassesTestMixin,
    UpdateView,
):
    """
        View to update an existing Article.
        Handles article form and related photo formset.
        Integrates AI content generation similar to create view.
        Restricts access to article author only.
    """
    model = Article
    form_class = ArticleForm
    template_name = "blog/article_form.html"
    context_object_name = "article"
    success_url = reverse_lazy("article_list")

    def get_context_data(self, **kwargs):
        """
            Add photo formset to context for rendering.
            Use POST data if present, else populate with existing photos.
        """
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
        """
            Validate both article form and photo formset.
            Generate content via AI if prompt given and content empty.
            Save all changes atomically.
        """
        context = self.get_context_data()
        photo_formset = context["photo_formset"]

        if photo_formset.is_valid() and form.is_valid():

            self._try_generate_content(form)

            with transaction.atomic():
                self.object = form.save()
                photo_formset.instance = self.object
                photo_formset.save()
            return super().form_valid(form)

        return self.render_to_response(self.get_context_data(form=form))

    @staticmethod
    def _try_generate_content(form):
        """
            Same AI content generation as in create view.
        """
        prompt = form.cleaned_data.get("prompt")

        if prompt and not form.cleaned_data.get("content"):
            try:
                form.instance.content = generate_article_content(prompt)
            except Exception as e:
                form.add_error('prompt', f"Error: {e}")
                raise

    def test_func(self):
        """
            Only allow article author to update.
        """
        article = self.get_object()
        return article.author == self.request.user


class ArticleListView(ListView):
    """
       Display paginated list of articles.
    """
    model = Article
    template_name = "blog/article_list.html"
    context_object_name = "articles"
    paginate_by = 9


class ArticleDetailView(DetailView):
    """
        Show details of a single article.
    """
    model = Article
    template_name = "blog/article_detail.html"
    context_object_name = "article"


class ArticleDeleteView(
    LoginRequiredMixin,
    UserPassesTestMixin,
    DeleteView,
):
    """
        Allow author to delete their article.
    """
    model = Article
    template_name = "blog/article_confirm_delete.html"
    context_object_name = "article"
    success_url = reverse_lazy("article_list")

    def test_func(self):
        """
            Only allow article author to delete.
        """
        article = self.get_object()
        return article.author == self.request.user
