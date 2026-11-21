from django.contrib import admin

from .models import Company, Job


class JobInline(admin.TabularInline):
    model = Job


class CompanyAdmin(admin.ModelAdmin):
    inlines = [
        JobInline,
    ]


admin.site.register(Company, CompanyAdmin)
@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ["title", "listing_url", "approved", "created_datetime"]
    list_filter = ["approved"]
