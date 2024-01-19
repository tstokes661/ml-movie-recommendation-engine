from django.contrib import admin

# Register your models here.
from .models import Movie


class MovieAdmin(admin.ModelAdmin):
    search_fields = ['id', 'title']
    list_display = [
        '__str__',
        'calculate_ratings_count',
        'calculate_ratings_avg',
        'rating_last_updated',
        'rating_count',
        'rating_avg',
        'score'
    ]
    readonly_fields = ['rating_avg', 'rating_count', 'rating_avg_display']


admin.site.register(Movie, MovieAdmin)
