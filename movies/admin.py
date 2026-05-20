from django.contrib import admin
from .models import TelegramUser, Genre, Movie

admin.site.register(TelegramUser)
admin.site.register(Genre)
admin.site.register(Movie)