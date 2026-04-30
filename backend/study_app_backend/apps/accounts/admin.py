from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, ChildProfile, ParentProfile, ParentChildRelation


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'role', 'is_active', 'created_at']
    list_filter = ['role', 'is_active']
    fieldsets = UserAdmin.fieldsets + (
        ('役割', {'fields': ('role',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('役割', {'fields': ('role',)}),
    )


@admin.register(ChildProfile)
class ChildProfileAdmin(admin.ModelAdmin):
    list_display = ['nickname', 'grade', 'user']
    list_filter = ['grade']


@admin.register(ParentProfile)
class ParentProfileAdmin(admin.ModelAdmin):
    list_display = ['display_name', 'user']


@admin.register(ParentChildRelation)
class ParentChildRelationAdmin(admin.ModelAdmin):
    list_display = ['parent', 'child', 'created_at']
