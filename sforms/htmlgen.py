# coding: utf-8

"""
"""

from markupsafe import escape as html_escape

# TODO see https://github.com/mitsuhiko/markupsafe

singleton_tags = frozenset((
    "area",
    "base", "br",
    "col", "command",
    "embed",
    "hr",
    "img", "input",
    "keygen",
    "link",
    "meta",
    "param",
    "source",
    "track",
    "wbr"
))

boolean_attrs = frozenset((
    "allowfullscreen", "async", "autofocus",
    "checked", "compact",
    "declare", "default", "defer", "disabled",
    "formnovalidate",
    "hidden",
    "inert", "ismap", "itemscope",
    "multiple", "muted",
    "nohref", "noresize", "noshade", "novalidate", "nowrap",
    "open",
    "readonly", "required", "reversed",
    "seamless", "selected", "sortable",
    "truespeed","typemustmatch"
))


class Tag(object):

    def __init__(self, tag, text=None, **attrs):
        self.tag = tag
        self.attrs = attrs
        self.children = []
        if text:
            self.add(Text(text))

    def _render_attrs(self):
        strings = []

        for k, v in self.attrs.iteritems():
            if k.endswith('_'):    # class_='foo'
                k = k.rstrip('_')

            k = k.replace('_', '-')  # e.g. data_foo => data-foo

            if k in boolean_attrs:
                if v:
                    strings.append(html_escape(k))
            else:
                strings.append(u'%s="%s"' % (html_escape(k), html_escape(v)))

        return u'' if len(strings) == 0 else u' ' + u' '.join(strings)

    def add(self, child):
        if isinstance(child, (list, tuple)):
            self.children.extend(child)
        else:
            self.children.append(child)
        return self

    def render(self):
        rendered_children = [child.render() for child in self.children]
        return u'<{tag}{attrs}>{children}{closing_tag}'.format(
            tag = html_escape(self.tag),
            attrs = self._render_attrs(),
            children=u''.join(rendered_children),
            closing_tag = u'' if self.tag in singleton_tags else u'</{0}>'.format(self.tag)
        )


class Text(object):

    def __init__(self, val):
        self.val = unicode(val)

    def render(self):
        return html_escape(self.val)


class RawText(object):

    def __init__(self, val):
        self.val = unicode(val)

    def render(self):
        return self.val
