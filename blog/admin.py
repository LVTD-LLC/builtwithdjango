from django.contrib import admin

from .models import Comment, Post, Tag


class ArchiveAdmin(admin.ModelAdmin):
    """Legacy database records are retained for rollback, not publishing."""

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Post)
class PostAdmin(ArchiveAdmin):
    list_display = ("title", "created", "modified")


admin.site.register(Tag, ArchiveAdmin)
admin.site.register(Comment, ArchiveAdmin)
