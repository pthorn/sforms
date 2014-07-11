# coding: utf-8

"""
form = SmallForm()
Field(form, 'name', ...)

form.from_object(obj)
form.from_submitted(request.POST.items())
if c.form.valid:
    form.to_object(obj)

<input type="text" name="contact_name"
    value="${c.form.contact_name.cvalue}"
    class="${c.form.contact_name.iclass('invalid')}">

% if not c.form.field.valid:
    ${c.form.contact_name.errors}
% endif

"""


import datetime

import colander
import peppercorn

from .render import Input, Textarea, Select

import logging
log = logging.getLogger(__name__)


class _Nothing(object):
    pass

_nothing = _Nothing()


def _colander_args(name=_nothing, default=_nothing, missing=_nothing, validators=_nothing):
    args = dict()

    if name != _nothing:
        args['name'] = name
    if default != _nothing:
        args['default'] = default
    if missing != _nothing:
        args['missing'] = missing
    if validators != _nothing:
        args['validator'] = colander.All(*validators)

    return args


class SmallForm(object):  # TODO csrf http://docs.pylonsproject.org/projects/pyramid/en/latest/narr/sessions.html

    def __init__(self, validators=None, request=None, check_csrf=True):
        self._fields = dict()
        self._fields_list = []
        self._schema = colander.SchemaNode(colander.Mapping(), **_colander_args(validators=validators or _nothing))
        self._cstruct = dict()
        self._appstruct = dict()
        self._errors = dict()
        self._request = request
        self._check_csrf = check_csrf

    def from_object(self, obj=None, **kwargs):
        if not obj:
            obj = kwargs

        self._appstruct = dict()

        for name, field in self._fields.iteritems():
            if isinstance(obj, dict):
                try:
                    val = obj[name]
                except KeyError:
                    self._appstruct[name] = colander.null
                    continue
            else: # object with attributes
                try:
                    val = getattr(obj, name)
                except AttributeError:
                    self._appstruct[name] = colander.null
                    continue

            # do not shield errors that happen in child._value_from_object()
            self._appstruct[name] = field._from_object(val)

        self._cstruct = self._schema.serialize(self._appstruct)

        #print '---- Form.from_object(): appstruct =', self.appstruct, 'cstruct =', self.cstruct
        return self

    def to_object(self, obj):
        for field in self._fields.itervalues():
            field._to_object(obj)

    def from_submitted(self, data, debug_submission=False):
        """
        my_form = my_form.from_submitted(request.POST.items())
        or
        my_form = my_form.from_submitted(request.json_body)

        consider using from_request() instead
        """

        def to_hierarchy(d):
            for k in d.keys():
                if '.' in k:
                    new_k, rest = k.split('.', 1)
                    if new_k not in d:
                        d[new_k] = dict()
                    d[new_k][rest] = d[k]
                    del d[k]
            for k, v in d.iteritems():
                if isinstance(v, dict):
                    to_hierarchy(v)

        if isinstance(data, list):
            # request.POST.items()
            self._cstruct = peppercorn.parse(data)
        elif isinstance(data, dict):
            # request.json_body
            self._cstruct = data
        else:
            raise RuntimeError('expected list or dict')

        if self._check_csrf and not self._request:
            log.warn('check_csrf is True but no request has been passed to the form')

        if self._check_csrf and self._request:
            if self._cstruct.get('csrf_token') != self._request.session.get_csrf_token():
                from pyramid.httpexceptions import HTTPBadRequest
                raise HTTPBadRequest()

        try:
            self._appstruct = self._schema.deserialize(self._cstruct)
            self._errors = dict()
        except colander.Invalid as e:
            self._errors = e.asdict()
            # TODO hack
            for k, v in self._errors.iteritems():
                if v == u'Required':
                    self._errors[k] = u'Обязательное поле'
            to_hierarchy(self._errors)

        if debug_submission:
            print '------ from_submitted(): params    =', data
            print '------ from_submitted(): cstruct   =', self._cstruct
            print '------ from_submitted(): appstruct =', self._appstruct
            print '------ from_submitted(): errors    =', self._errors

        return self

    def from_request(self, request, debug_submission=False):
        """
        my_form = my_form.from_request(request)
        Pyramid only
        """
        if request.content_type.startswith('application/json'):
            body = request.json_body  # TODO possible exceptions
        else:
            body = request.POST.items()

        return self.from_submitted(body, debug_submission)

    @property
    def valid(self):
        return not self._errors

    @property
    def error(self):
        """
        :return: form's own error (generated by a validator attached to the form itself)
        """
        if not self.valid:
            return self._errors.get('')
        else:
            return None

    @property
    def errors(self):
        """
        :return: dict of validation errors (for json)
        """
        return self._errors or dict()

    @property
    def fields(self):
        return self._fields_list

    def render_csrf_field(self):
        """
        <form>
            ${c.form.render_csrf_field() | n}
        </form
        Note: will throw an exception if request was not passed to the constructor
        """
        token = self._request.session.get_csrf_token()
        return u'<input type="hidden" name="csrf_token" value="%s">' % token

    def _add_field(self, field):
        self._fields[field.name] = field
        self._fields_list.append(field)
        self._schema.add(field._schema)

    def __getattr__(self, item):
        try:
            return self._fields[item]
        except KeyError:
            raise AttributeError(item)


class Field(object):

    def __init__(self, form, name,
                 colander_type, default, missing, validators,
                 renderer): #, **kwargs): TODO 1) Renderer(args) 2) Field(kwargs) 3) field.render(args)
        """
        default - cvalue to serialize if none is supplied
        missing - value if none is entered by the user (_nothing means field is required)
        """
        self._form = form
        self._name = name

        self.renderer = renderer
        #self.rargs = kwargs

        self._schema = colander.SchemaNode(colander_type, **_colander_args(name, default, missing, validators or _nothing))

        form._add_field(self) # after schema object is constructed

    @property
    def name(self):
        return self._name

    @property
    def valid(self):
        return self._name not in self._form._errors

    @property
    def cvalue(self):
        """
        :return: serialized value (as used in HTML and submitted by client)
        """
        return self._form._cstruct.get(self._name, u'') # TODO u'' is needed for radio inputs if none is selected

    @property
    def value(self):
        """
        :return: deserialized value
        """
        return self._form._appstruct[self._name]

    @property
    def error(self):
        return self._form._errors.get(self._name)

    def iclass(self, invalid_class, valid_class=u''):
        return valid_class if self.valid else invalid_class

    def render(self, **kwargs):
        return self.renderer.render(self, kwargs)

    def _from_object(self, val):
        # colander.null means colander will use 'default'
        return val if val is not None else colander.null

    def _to_object(self, obj):
        setattr(obj, self._name, self.value)


class StringField(Field):

    def __init__(self, form, name, required=False, validators=None, renderer=None):
        super(StringField, self).__init__(
            form,
            name,
            colander.String(),
            u'',  # default
            _nothing if required else u'',  # missing
            validators,
            renderer or Input()
        )


class IntegerField(Field):

    def __init__(self, form, name, required=False, validators=None):
        super(IntegerField, self).__init__(
            form,
            name,
            colander.Int(),
            u'',  # default
            _nothing if required else None,  # missing
            validators,
            Input()
        )
