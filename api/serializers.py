from rest_framework import serializers

from blog.models import Post, Tag
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


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ("id", "name", "slug")
        read_only_fields = ("slug",)


class PostSerializer(serializers.ModelSerializer):
    tags = serializers.CharField(write_only=True, required=False, allow_blank=True)
    tag_list = TagSerializer(many=True, read_only=True, source="tags")

    class Meta:
        model = Post
        fields = (
            "id",
            "title",
            "description",
            "slug",
            "tags",
            "tag_list",
            "content",
            "status",
            "type",
            "created",
            "modified",
        )
        read_only_fields = ("id", "created", "modified", "tag_list")

    def create(self, validated_data):
        from django.contrib.auth import get_user_model

        # Extract tags string if provided
        tags_string = validated_data.pop("tags", "")

        # Set author to first superuser
        User = get_user_model()
        author = User.objects.filter(is_superuser=True).first()
        if not author:
            raise serializers.ValidationError("No superuser found in the system. Please create one first.")

        validated_data["author"] = author

        # Set default level if not provided
        if "level" not in validated_data:
            validated_data["level"] = Post.BEGINNER

        # Create the post
        post = Post.objects.create(**validated_data)

        # Process tags if provided
        if tags_string:
            tag_names = [name.strip() for name in tags_string.split(",") if name.strip()]
            for tag_name in tag_names:
                tag, created = Tag.objects.get_or_create(
                    name=tag_name, defaults={"slug": tag_name.lower().replace(" ", "-")}
                )
                post.tags.add(tag)

        return post
