from django.contrib import admin, messages

from .models import Comment, Like, Project, Technology


class CommentInline(admin.TabularInline):
    model = Comment


class LikeInline(admin.TabularInline):
    model = Like


def unpublish_selected_projects(modeladmin, request, queryset):
    """Admin action to unpublish selected projects."""
    updated = queryset.update(published=False)
    modeladmin.message_user(request, f"Successfully unpublished {updated} project(s).", level=messages.SUCCESS)


unpublish_selected_projects.short_description = "Unpublish selected project(s)"


class ProjectAdmin(admin.ModelAdmin):
    list_display = ["title", "logged_in_maker", "active", "published", "maker", "date_added", "might_be_spam"]
    inlines = [CommentInline, LikeInline]
    actions = [unpublish_selected_projects]


admin.site.register(Project, ProjectAdmin)
admin.site.register(Technology)
admin.site.register(Comment)
