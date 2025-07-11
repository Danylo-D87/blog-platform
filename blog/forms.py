from django import forms
from django.forms import inlineformset_factory
from .models import Article, Photo

class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ['title', 'content']

PhotoFormSet = inlineformset_factory(
    Article,
    Photo,
    fields=['image'],
    extra=1,
    can_delete=True,
    max_num=5,
)