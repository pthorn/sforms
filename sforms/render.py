# coding: utf-8

"""
"""

from htmlgen import Tag, Text, RawText


class Input(object):
    """
    <input type="<type>">
    """

    def __init__(self, type='text'):
        self.type = type

    def render(self, field, rargs):
        if 'type' not in rargs: rargs['type'] = self.type # TODO better design
        return Tag('input', name=field.name, value=field.cvalue, **rargs).render()


class Textarea(object):
    """
    <textarea>
    """

    def render(self, field, rargs):
        return Tag('textarea', field.cvalue, name=field.name, **rargs).render()


class Select(object):
    """
    <select>
      <option>
    </select>
    """

    def __init__(self, options, multiple=False):
        """
        :param options: array of tuples (value, label)
        :param multiple: boolean
        """
        self.multiple = multiple
        self.options = options

    def render(self, field, rargs):
        r_options = [Tag('option', opt[1], value=opt[0], selected=(opt[0] == field.cvalue)) for opt in self.options]
        select = Tag('select', name=field.name, multiple=self.multiple, **rargs).add(r_options)
        return select.render()


class RadioButtons(object):

    def __init__(self, options):
        """
        :param options: array of tuples (value, label)
        """
        self.options = options

    def render(self, field, rargs):
        inputs = [Tag('li').add([Tag('input', type='radio', name=field.name, value=opt[0], checked=(opt[0] == field.cvalue)), Text(opt[1])]) for opt in self.options]
        return Tag('ul', **rargs).add(inputs).render()


class Checkbox(object):
    """
    """

    def render(self, field, rargs):
        return Tag('input', type='checkbox', name=field.name, value=u'true', checked=(field.cvalue == 'true')).render()


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
