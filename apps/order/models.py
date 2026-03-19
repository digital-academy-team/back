from django.db import models
from django.db.models import TextChoices

from apps.course.models.course import Course
from apps.user.models import User
from common import BaseModel


# Create your models here.


class OrderStatus(TextChoices):
    PENDING = 'PENDING', "pending"
    PAID = 'PAID', "paid"
    CANCELED = 'CANCELED', "canceled"


class Order(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    status = models.CharField(max_length=25, choices=OrderStatus.choices, default=OrderStatus.PENDING)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)


    def __str__(self):
        return f'{self.user} - {self.course} - {self.status}'


    class Meta:
        db_table = 'order'
        unique_together = (('user', 'course'),)


