# from Will Vincent tutorial -> https://learndjango.com/tutorials/django-markdown-tutorial

import markdown as md
from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()

extension_configs = {
    "markdown.extensions.codehilite": {"css_class": "codehilite", "linenums": False, "guess_lang": False}
}


@register.filter()
@stringfilter
def markdown(value):
    html = md.markdown(
        value,
        extensions=[
            "markdown.extensions.codehilite",
            "markdown.extensions.fenced_code",
            "markdown.extensions.toc",
            "markdown.extensions.admonition",
            "markdown.extensions.tables",
        ],
        extension_configs=extension_configs,
    )

    # Generated code blocks and tables can scroll horizontally on narrow screens.
    # Make them keyboard reachable without changing their semantic elements.
    return html.replace("<pre>", '<pre tabindex="0" aria-label="Code example">').replace(
        "<table>", '<table tabindex="0">'
    )
