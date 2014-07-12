#coding: utf-8

import colander


class Date(object):

    def __init__(self, format=u"%d.%m.%Y"):
        self.format = format

    def serialize(self, node, appstruct):
        if not appstruct:
            return colander.null

        if isinstance(appstruct, datetime.datetime):
            appstruct = appstruct.date()

        if not isinstance(appstruct, datetime.date):
            raise colander.Invalid(node, 'not a date object')

        return appstruct.strftime(self.format)

    def deserialize(self, node, cstruct):
        if not cstruct:
            return colander.null

        try:
            return datetime.datetime.strptime(cstruct, self.format).date()
        except ValueError:
            raise colander.Invalid(node, u"Неправильный формат даты")


class DateTime(object):

    def __init__(self, format=u"%d.%m.%Y %H:%M:%S"):
        self.format = format

    def serialize(self, node, appstruct):
        if not appstruct:
            return colander.null

        if not isinstance(appstruct, datetime.datetime):
            raise colander.Invalid(node, 'not a datetime object')

        return appstruct.strftime(self.format)

    def deserialize(self, node, cstruct):
        if not cstruct:
            return colander.null

        try:
            return datetime.datetime.strptime(cstruct, self.format)
        except ValueError:
            raise colander.Invalid(node, u"Неправильный формат даты/времени")


class File(object):

    def __init__(self):
        pass

    def serialize(self, node, appstruct):
        return colander.null

    def deserialize(self, node, cstruct):
        # cgi.FieldStorage seems to be always false. however, when user
        # doesn't select a file cstructs seems to be u'' so test for that
        if cstruct is colander.null or (isinstance(cstruct, basestring) and not cstruct):
            return colander.null
        import cgi
        if not isinstance(cstruct, cgi.FieldStorage):
            raise colander.Invalid(node, u"expected FieldStorage (how about some enctype?)")
        return cstruct
