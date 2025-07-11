from django import forms
from .models import Article
from .widgets import MultiFileInput  # створений вище кастомний віджет

class ArticleForm(forms.ModelForm):
    images = forms.FileField(
        widget=MultiFileInput(attrs={'multiple': True}),
        required=False,
        label="Зображення"
    )

    class Meta:
        model = Article
        fields = ['title', 'content']  # або 'content' якщо так називається поле
