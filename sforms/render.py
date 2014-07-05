# coding: utf-8

"""
"""

from htmlgen import Tag, Text, RawText


class Input(object):

    def __init__(self, type='text'):
        self.type = type

    def render(self, field, rargs):
        if 'type' not in rargs: rargs['type'] = self.type # TODO better design
        return Tag('input', name=field.name, value=field.cvalue, **rargs).render()


class Textarea(object):

    def __init__(self):
        pass

    def render(self, field, rargs):
        return Tag('textarea', type=self.type, name=field.name, value=field.cvalue, **rargs).render()


class Select(object):

    def __init__(self, options, multiple=False):
        self.multiple = multiple
        self.options = options

    def render(self, field, rargs):
        r_options = [Tag('option', opt[1], value=opt[0], selected=(opt[0] == field.cvalue)) for opt in self.options]
        select = Tag('select', name=field.name, multiple=self.multiple, **rargs).add(r_options)
        return select.render()


class RadioButtons(object):
    pass


class Checkbox(object):
    pass


class CheckBoxes(object):
    pass


if __name__ == '__main__':

    class C(object):
        def __init__(self, val, text):
            self.val = val
            self.text = text

    options = [C(1, 'one'), C(2, 'two'), C(3, 'th"r<e>e')]
    current_val = 2

    for x in range(100):
        select = Tag('select', multiple=True).add(
            [Tag('option', opt.text, value=opt.val, selected=opt.val == current_val) for opt in options]
        )

    print select.render()
