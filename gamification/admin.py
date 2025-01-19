

# Register your models here.
from django.contrib import admin
from .models import Gamification

@admin.register(Gamification)
class GamificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'points')
    search_fields = ('user__username',)
