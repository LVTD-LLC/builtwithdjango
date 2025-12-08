from django.contrib.syndication.views import Feed
from django.template.defaultfilters import truncatewords

from .models import Post


class BlogFeed(Feed):
    title = "Built with Django"
    link = "https://builtwithdjango.com/blog/"
    description = "Articles about Django."

    def items(self):
        return Post.objects.filter(status=Post.PUBLISHED).order_by("-created")

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return truncatewords(item.content, 50)

    def item_pubdate(self, item):
        return item.created
