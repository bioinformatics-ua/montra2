from django import template
from django.conf import settings
from django.templatetags.static import StaticNode

register = template.Library()


class VersionedStaticNode(StaticNode):
    @classmethod
    def handle_simple(cls, path):
        return super(VersionedStaticNode, cls).handle_simple(path) + "?v={}".format(settings.VERSION)


@register.tag("versioned_static")
def versioned_static(parser, token):
    """
    A variant of the "static" tag which appends "?v={settings.VERSION}" to the url
      so it forces the browser to redownload the file, avoiding it using outdated cached versions of
      static files.
    """
    return VersionedStaticNode.handle_token(parser, token)
