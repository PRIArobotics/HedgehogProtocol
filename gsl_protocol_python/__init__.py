from gsl.yaml import YAML

from gsl_protocol import proto_target, get_model as _get_model
from gsl_protocol.grammar.HedgehogProtocolVisitor import Oneof, Field


def unique(it):
    items = set()
    for item in it:
        if item not in items:
            items.add(item)
            yield item


def get_model(model_file, py_model_file):
    with open(py_model_file) as f:
        yaml = YAML(typ='safe')
        py_model = yaml.load(f)

    model = _get_model(model_file)

    def get_fields(message):
        for field in message.fields:
            if isinstance(field, Field):
                yield field
            elif isinstance(field, Oneof):
                yield from field.fields

    for message in model.messages:
        full_name = '.'.join(message.qualifiedName.full_name)
        py_fields = py_model.get(full_name, None)
        if py_fields:
            for field in get_fields(message):
                py_field = py_fields.get(field.name, None)
                if py_field:
                    if 'default' not in py_field:
                        py_field.default = None
                    field.python_spec = py_field

    return model


def main():
    from . import python_target

    model = get_model('gsl_protocol/hedgehog_protocol', 'gsl_protocol_python/python.yaml')
    root = '.'
    proto_target.generate_code(model, root)
    python_target.generate_code(model, root)
