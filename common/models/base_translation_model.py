from django.db import models
from . import BaseModel


class LanguageChoices(models.TextChoices):
    UZBEK = 'uz', 'Uzbek'
    RUSSIAN = 'ru', 'Russian'
    ENGLISH = 'en', 'English'


class BaseTranslationModel(BaseModel):
    lang_code = models.CharField(
        max_length=2,
        choices=LanguageChoices.choices,
        verbose_name="Language",
        db_index=True
    )

    class Meta:
        abstract = True
