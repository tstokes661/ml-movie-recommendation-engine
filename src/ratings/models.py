from django.conf import settings
from django.db import models
from django.db.models import Avg
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

User = settings.AUTH_USER_MODEL


class RatingChoice(models.IntegerChoices):
    ONE = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    __empty__ = 'Rate this'


class RatingsQuerySet(models.QuerySet):
    def avg(self):
        return self.aggregate(average=Avg('value'))['average']


class RatingManager(models.Manager):
    def get_queryset(self):
        return RatingsQuerySet(self.model, using=self._db)

    def avg(self):
        return self.get_queryset().avg()


class Rating(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    value = models.IntegerField(
        null=True,
        blank=True,
        choices=RatingChoice.choices
    )
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE
    )
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")
    active = models.BooleanField(default=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    objects = RatingManager()