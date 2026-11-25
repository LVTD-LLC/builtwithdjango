from django.contrib import admin, messages

from .models import FeaturePurchase, Comment, Like, Project, Technology


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
    list_display = ["title", "url", "logged_in_maker", "active", "published", "maker", "date_added", "might_be_spam"]
    list_filter = ["published"]
    inlines = [CommentInline, LikeInline]
    actions = [unpublish_selected_projects]


admin.site.register(Project, ProjectAdmin)
admin.site.register(Technology)
admin.site.register(Comment)


@admin.register(FeaturePurchase)
class FeaturePurchaseAdmin(admin.ModelAdmin):
    list_display = ("project", "purchased_at", "newsletter_feature_sent")
    list_filter = ("newsletter_feature_sent",)
    readonly_fields = ("project", "session_id", "purchased_at")
