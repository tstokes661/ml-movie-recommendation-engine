from django.http import HttpResponse
from django.contrib.contenttypes.models import ContentType
from .models import Rating
from django.views.decorators.http import require_http_methods
from .tasks import task_update_movie_ratings


@require_http_methods(['POST'])
def rate_movie_view(request):
    print(request.POST)
    if not request.htmx:
        return HttpResponse("Not Allowed", status=400)
    object_id = request.POST.get('object_id')
    rating_value = request.POST.get('rating_value')
    if object_id is None or rating_value is None:
        response = HttpResponse("Skipping", status=200)
        response['HX-Trigger'] = 'did-skip-movie'
        return response
    user = request.user
    message = "You must login <a href='/accounts/login'>login</a> to rate this"
    if user.is_authenticated:
        message = """<span class='bg-danger text-light px-3 py-1 rounded'>
        An error occured.</span>"""
        ctype = ContentType.objects.get(app_label='movies', model='movie')
        rating_obj = Rating.objects.create(
            content_type=ctype,
            object_id=object_id,
            value=rating_value,
            user=user
        )
        if rating_obj.content_object is not None:
            message = """<span class='bg-success text-light px-3 py-1 rounded'>
            Rating saved</span>"""
            response = HttpResponse(message, status=200)
            response['HX-Trigger-After-Settle'] = 'did-rate-movie'
            task_update_movie_ratings.delay(object_id=object_id)
            return response
    return HttpResponse(message, status=200)
