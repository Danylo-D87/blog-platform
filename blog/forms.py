# articles/forms.py
from django import forms
from django.forms import inlineformset_factory
from .models import Article, Photo

class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ['title', 'content'] # 'author' буде встановлено автоматично у view

# Формсет для фотографій
# extra=1 означає, що за замовчуванням буде одне порожнє поле для завантаження нового фото
# can_delete=True дозволяє видаляти існуючі фотографії
# max_num=5 обмежує кількість фото до 5 (можна змінити)
PhotoFormSet = inlineformset_factory(
    Article,
    Photo,
    fields=['image'],
    extra=1, # Завжди показувати хоча б одне порожнє поле для нового фото
    can_delete=True, # Дозволити видаляти існуючі фото
    max_num=5, # Максимальна кількість фото на статтю
)