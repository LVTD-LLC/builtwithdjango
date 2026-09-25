from django.contrib.syndication.views import Feed
from django.template.defaultfilters import truncatewords

from .content import published_posts


class BlogFeed(Feed):
    title = "Built with Django"
    link = "https://builtwithdjango.com/blog/"
    description = "Articles about Django."

    def items(self):
        return published_posts()

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return truncatewords(item.content, 50)

    def item_pubdate(self, item):
        return item.created
