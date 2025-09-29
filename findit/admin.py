from django.contrib import admin

from . import models

# Register your models here.

class LostItemAdmin(admin.ModelAdmin):
    # So that the field is shown in the admin page, read only fields arent shown by default
    readonly_fields = ('time_created',)

class UserProfileAdmin(admin.ModelAdmin):
    pass

class FoundItemAdmin(admin.ModelAdmin):
    readonly_fields = ('time_created',)

admin.site.register(models.LostItem,LostItemAdmin)
admin.site.register(models.UserProfile,UserProfileAdmin)
admin.site.register(models.FoundItem,FoundItemAdmin)

