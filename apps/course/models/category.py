from django.db import models
from django.utils.text import slugify
from common import BaseModel


class Category(BaseModel):

    title = models.CharField(max_length=50, null=False, blank=False)
    slug = models.SlugField(max_length=50, null=False, blank=False, editable=False)

    def __str__(self):
        return self.title


    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1

            while Category.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug

        super().save(*args, **kwargs)


    class Meta:
        db_table = "category"


