from django import forms
from django.forms import inlineformset_factory
from .models import Article, Photo


class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ['title', 'content']


class PhotoForm(forms.ModelForm):
    class Meta:
        model = Photo
        fields = ['image']

PhotoFormSet = inlineformset_factory(
    Article,
    Photo,
    form=PhotoForm,
    fields=['image'],
    extra=0,
    can_delete=True,
    max_num=5,
)