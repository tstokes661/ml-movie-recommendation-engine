import random
import time
import datetime

from django.db.models import Avg, Count
from celery import shared_task
from movies.models import Movie
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from .models import Rating, RatingChoice
from django.utils import timezone


User = get_user_model()


@shared_task(name='generate_fake_reviews_task')
def generate_fake_reviews(count=100, users=10, null_avg=False):
    user_s = User.objects.first()
    user_e = User.objects.last()
    random_user_ids = random.sample(range(user_s.id, user_e.id), users)
    users = User.objects.filter(
        id__in=random_user_ids
    )
    # movie_ctype = ContentType.objects.get_for_model(Movie)

    movies = Movie.objects.all().order_by("?")[:count]

    if null_avg:
        movies = Movie.objects.filter(
            rating_avg__isnull=False
        ).order_by("?")[:count]
    n_ratings = movies.count()
    rating_choices = [x for x in RatingChoice.values if x is not None]
    user_ratings = [random.choice(rating_choices) for _ in range(0, n_ratings)]

    new_ratings = []
    for movie in movies:
        rating_obj = Rating.objects.create(
            content_object=movie,
            # content_type=movie_ctype,
            # object_id=movie.id,
            value=user_ratings.pop(),
            user=random.choice(users)
        )
        new_ratings.append(rating_obj.id)
    return new_ratings


@shared_task(name='task_update_movie_ratings')
def task_update_movie_ratings(object_id=None):
    start_time = time.time()
    ctype = ContentType.objects.get_for_model(Movie)
    agg_ratings = Rating.objects.filter(
        content_type=ctype
    )
    if object_id is not None:
        agg_ratings = agg_ratings.filter(
            object_id=object_id
        )
    agg_ratings = agg_ratings.values(
        'object_id'
    ).annotate(
        average=Avg('value'),
        count=Count('object_id')
    )
    for agg_rate in agg_ratings:
        id = agg_rate['object_id']
        rating_avg = agg_rate['average']
        rating_count = agg_rate['count']
        qs = Movie.objects.filter(
            id=id
        )

        qs.update(
            rating_avg=rating_avg,
            rating_count=rating_count,
            rating_last_updated=timezone.now()
        )
    total_time = time.time() - start_time
    delta = datetime.timedelta(seconds=int(total_time))
    print(f"Rating update took: {delta}({total_time}s)")
