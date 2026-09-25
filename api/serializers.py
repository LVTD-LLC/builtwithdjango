from rest_framework import serializers

from projects.models import Like


class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ("author", "project", "like", "id")
        read_only_fields = ("author", "id")


class LikeSerializerNoId(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ("author", "project", "like")
        read_only_fields = ("author", "project")


class PostSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    author = serializers.IntegerField(read_only=True)
    title = serializers.CharField(read_only=True)
    description = serializers.CharField(read_only=True)
    slug = serializers.CharField(read_only=True)
    tag_list = serializers.JSONField(read_only=True)
    content = serializers.CharField(read_only=True)
    status = serializers.CharField(read_only=True)
    type = serializers.CharField(read_only=True)
    level = serializers.CharField(read_only=True)
    unsplashID = serializers.CharField(read_only=True)
    created = serializers.DateTimeField(read_only=True)
    modified = serializers.DateTimeField(read_only=True)
