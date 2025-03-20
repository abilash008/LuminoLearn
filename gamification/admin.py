

# Register your models here.
from django.contrib import admin
from .models import Badge, Point, UserBadge


@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display = ('name', 'criteria_type', 'criteria_threshold')
    search_fields = ('name', 'criteria_type')

@admin.register(UserBadge)
class UserBadgeAdmin(admin.ModelAdmin):
    list_display = ('user', 'badge', 'date_earned')
    list_filter = ('badge', 'date_earned')

@admin.register(Point)
class PointAdmin(admin.ModelAdmin):
    list_display = ('user', 'points', 'reason', 'date_awarded')
    list_filter = ('reason', 'date_awarded')