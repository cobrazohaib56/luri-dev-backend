import os

from drf_yasg.generators import OpenAPISchemaGenerator


class EnvVariableNotSet(Exception):
    """Should be raised when an environment variable necessary for setting is not set"""


def required_env_var(var_name):
    var = os.environ.get(var_name)
    if var is None:
        raise EnvVariableNotSet(var_name)
    return var


class BothHttpAndHttpsSchemaGenerator(OpenAPISchemaGenerator):
    def get_schema(self, request=None, public=False):
        schema = super().get_schema(request, public)
        schema.schemes = ["http", "https"]
        return schema
