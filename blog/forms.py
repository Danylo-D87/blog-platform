from django import forms
from django.forms import inlineformset_factory
from .models import Article, Photo


class ArticleForm(forms.ModelForm):
    """
    Form for Article model with extra 'prompt' field
    for AI content generation input (optional).
    """
    prompt = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"placeholder": "Prompt for content generation..."}),
        label="Content generation prompt"
    )

    class Meta:
        model = Article
        fields = ["title", "content"]


class PhotoForm(forms.ModelForm):
    """
    Simple form for uploading a Photo (image field).
    """
    class Meta:
        model = Photo
        fields = ["image"]


PhotoFormSet = inlineformset_factory(
    Article,
    Photo,
    form=PhotoForm,
    fields=["image"],
    extra=0,
    can_delete=True,
    max_num=5
)

