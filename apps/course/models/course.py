from apps.course.models.category import Category
from apps.user.models import User
from common import BaseModel
from django.db import models
from django.utils.text import slugify


class Course(BaseModel):
    cover_img = models.ImageField(upload_to='course/cover_img', blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='course_created_by')
    title = models.CharField(max_length=120)
    desc = models.TextField()
    slug = models.SlugField(max_length=120, unique=True, editable=False, db_index=True)
    base_price = models.PositiveIntegerField()
    discount_price = models.PositiveIntegerField(default=0, blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='course_category')

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1

            while Course.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug

        super().save(*args, **kwargs)

    class Meta:
        db_table = "courses"

    def __str__(self):
        return self.title