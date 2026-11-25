from django.db.models import BooleanField, Count, Exists, OuterRef, Q, Value

from django.db.models.functions import Now

from .models import Like


def with_like_metadata(queryset, user):
    user_has_liked = Value(False, output_field=BooleanField())
    if user and user.is_authenticated:
        user_has_liked = Exists(Like.objects.filter(author=user, project=OuterRef("pk"), like=True))

    return queryset.annotate(
        is_featured=Q(sponsored=True) | Q(featured_until__isnull=False, featured_until__gt=Now()),
        like_count=Count("like", filter=Q(like__like=True), distinct=True),
        user_has_liked=user_has_liked,
    )
