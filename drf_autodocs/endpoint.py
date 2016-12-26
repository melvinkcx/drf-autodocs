from rest_framework.serializers import BaseSerializer
from inspect import getdoc
from django.contrib.admindocs.views import simplify_regex
from django.urls import reverse, resolve


class Endpoint:

    def __init__(self, pattern, prefix=None):
        self.pattern = pattern
        self.view = pattern.callback
        self.methods = self._get_allowed_methods()
        self.complete_path = self._get_complete_path(pattern, prefix)
        self.name = pattern.name
        self.input_fields = self._get_serializer_fields(self.view.cls.serializer_class())
        self.docstring = getdoc(self.view.cls)
        if hasattr(self.view.cls, 'response_serializer_class'):
            self.output_fields = self._get_serializer_fields(self.view.cls.response_serializer_class())

    def _get_allowed_methods(self):
        if hasattr(self.view, 'cls'):
            return [m.upper() for m in self.view.cls.http_method_names if hasattr(self.view.cls, m)]
        else:
            return []

    @staticmethod
    def _get_complete_path(pattern, prefix=None):
        return prefix + simplify_regex(pattern._regex)

    def _get_serializer_fields(self, serializer):
        fields = []

        if hasattr(serializer, 'get_fields'):
            for key, field in serializer.get_fields().items():
                to_many_relation = True if hasattr(field, 'many') else False
                sub_fields = []

                if to_many_relation:
                    sub_fields = self._get_serializer_fields(field.child) if isinstance(field, BaseSerializer) else None
                else:
                    sub_fields = self._get_serializer_fields(field) if isinstance(field, BaseSerializer) else None

                fields.append({
                    "name": key,
                    "type": str(field.__class__.__name__),
                    "sub_fields": sub_fields,
                    "required": field.required,
                    "to_many_relation": to_many_relation
                })

        return fields




