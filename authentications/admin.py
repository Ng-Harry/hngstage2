from django.contrib import admin
from authentications.models import User
from django.contrib.auth.admin import UserAdmin
from django.forms import TextInput, Textarea, CharField
from django import forms
from django.db import models
from .models import Organisation



class OrganisationAdmin(admin.ModelAdmin):
    list_display = ('orgId','name', 'description')
    search_fields = ('name', 'description')
    filter_horizontal = ('users',)
    list_filter = ('name',)


class UserAdminConfig(UserAdmin):
    model = User
    search_fields = ('userId','email','phone', 'first_name', 'last_name', )
    list_filter = ('is_active', 'is_staff')
    ordering = ('userId',)
    list_display = ('email', 'first_name', 'last_name', 'phone','is_active', 'is_staff')
    fieldsets = (
        (None, {'fields': ('password','email','first_name', 'last_name', 'phone',)}),
        ('Permissions', {'fields': ('is_staff', 'is_active')}),
    )
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 20, 'cols': 60})},
    }
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'phone','password1', 'password2', 'is_active', 'is_staff')}
         ),
    )




admin.site.register(User, UserAdminConfig)
admin.site.register(Organisation, OrganisationAdmin)