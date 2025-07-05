import re
from rest_framework import serializers

def camel_to_snake(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

def snake_to_camel(word):
    components = word.split('_')
    return components[0] + ''.join(x.title() for x in components[1:])

class BaseSerializer(serializers.ModelSerializer):
    def to_internal_value(self, data):
        new_data = {}
        for key, value in data.items():
            new_key = camel_to_snake(key)
            new_data[new_key] = value
        return super().to_internal_value(new_data)

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        new_ret = {}
        for key, value in ret.items():
            new_key = snake_to_camel(key)
            new_ret[new_key] = value
        return new_ret