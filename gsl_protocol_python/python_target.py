import os.path

from gsl import lines, generate

from gsl_protocol.grammar.HedgehogProtocolVisitor import Field, Oneof, MandatoryParam, RepeatedParam, OptionalParam
from . import unique


def generate_code(model, root='.'):
    for mod in model.modules:
        generate_module_code(model, mod, root)


def generate_module_code(model, mod, root):
    out_file = os.path.join(root, 'hedgehog/protocol/messages', *mod.path, f'{mod.name}.py')
    os.makedirs(os.path.dirname(out_file), exist_ok=True)

    @generate(out_file)
    def code():
        def map_params(messageClass, mandatory, repeated, optional, custom=None):
            def has(attr_caller):
                try:
                    attr_caller()
                except AttributeError:
                    return False
                else:
                    return True

            for param in messageClass.params:
                if isinstance(param, MandatoryParam) and has(lambda: param.field.python_spec):
                    yield mandatory(param)
                elif isinstance(param, RepeatedParam) and has(lambda: param.field.python_spec):
                    yield repeated(param)
                elif isinstance(param, OptionalParam) and has(lambda: [field.python_spec for field in param.fields]):
                    for i in range(len(param.options)):
                        yield optional(param, i)
                elif custom:
                    yield custom(param)
                else:
                    raise RuntimeError(f"Unexpected custom parameter: {param}")

        def map_params_code(messageClass, mandatory, repeated, optional, custom=None):
            for generator in map_params(messageClass, mandatory, repeated, optional, custom):
                yield from generator

        def field_names(messageClass):
            return map_params(
                messageClass,
                mandatory=lambda param: param.name,
                repeated=lambda param: param.name,
                optional=lambda param, i: param.options[i],
                custom=lambda param: param.name,
            )

        def message_class_code(messageClass):
            message = messageClass.message
            proto = message.proto

            def message_fields_code():
                def field_str(name, typ, default=None, repeated=False, optional=False):
                    if repeated:
                        return f"    {name}: Sequence[{typ}]"
                    elif default is not None:
                        return f"    {name}: {typ} = {default}"
                    elif optional:
                        return f"    {name}: {typ} = None"
                    else:
                        return f"    {name}: {typ}"

                def mandatory(param):
                    python = param.field.python_spec
                    yield field_str(param.name, python.typ, python.default)

                def repeated(param):
                    python = param.field.python_spec
                    yield field_str(param.name, python.typ, python.default, repeated=True)

                def optional(param, i):
                    python = param.fields[i].python_spec
                    yield field_str(param.options[i], python.typ, python.default, optional=True)

                def custom(param):
                    yield field_str(param.name, 'Any')

                yield from map_params_code(messageClass, mandatory, repeated, optional, custom)

            def message_init_code():
                # only generate an __init__ method if the dataclass __init__ is not enough
                if not any(isinstance(param, RepeatedParam) for param in messageClass.params):
                    return

                def init_param_strs():
                    def param_str(name, typ, default=None, repeated=False, optional=False):
                        if repeated:
                            return f"*{name}: {typ}"
                        elif default is not None:
                            return f"{name}: {typ}={default}"
                        elif optional:
                            return f"{name}: {typ}=None"
                        else:
                            return f"{name}: {typ}"

                    def mandatory(param):
                        python = param.field.python_spec
                        return param_str(param.name, python.typ, python.default)

                    def repeated(param):
                        python = param.field.python_spec
                        return param_str(param.name, python.typ, python.default, repeated=True)

                    def optional(param, i):
                        python = param.fields[i].python_spec
                        return param_str(param.options[i], python.typ, python.default, optional=True)

                    def custom(param):
                        return param.name

                    yield "self"
                    yield from map_params(messageClass, mandatory, repeated, optional, custom)

                yield from lines(f"""\

    def __init__({", ".join(init_param_strs())}) -> None:""")

                for name in field_names(messageClass):
                    yield from lines(f"""\
        object.__setattr__(self, {name!r}, {name})""")

                yield from lines(f"""\
        self.__post_init__()""")

            def message_parse_code():
                def init_param_strs():
                    yield from map_params(
                        messageClass,
                        mandatory=lambda param: param.name,
                        repeated=lambda param: f"*{param.name}",
                        optional=lambda param, i: f"{param.options[i]}={param.options[i]}",
                        custom=lambda param: param.name,
                    )

                yield from lines(f"""\

    @classmethod
    def _parse(cls, msg: {proto.name}_pb2.{message.name}) -> '{messageClass.name}':""")

                yield from map_params_code(
                    messageClass,
                    mandatory=lambda param: lines(f"""\
        {param.name} = msg.{param.name}"""),
                    repeated=lambda param: lines(f"""\
        {param.name} = msg.{param.name}"""),
                    optional=lambda param, i: lines(f"""\
        {param.options[i]} = msg.{param.options[i]}""")
                    if len(param.options) == 1 else lines(f"""\
        {param.options[i]} = msg.{param.options[i]} if msg.HasField('{param.options[i]}') else None"""),
                    custom=lambda param: lines(f"""\
        # <default GSL customizable: {messageClass.name}-parse-{param.name}>
        # TODO parse custom field '{param.name}'
        {param.name} = msg.{param.name}
        # </GSL customizable: {messageClass.name}-parse-{param.name}>"""),
                )

                yield from lines(f"""\
        return cls({", ".join(init_param_strs())})""")

            def message_serialize_code():
                yield from lines(f"""\

    def _serialize(self, msg: {proto.name}_pb2.{message.name}) -> None:""")

                def assignment_str(name, nested=False, repeated=False):
                    if repeated:
                        return f"msg.{name}.extend(self.{name})"
                    elif nested:
                        return f"msg.{name}.CopyFrom(self.{name})"
                    else:
                        return f"msg.{name} = self.{name}"

                if not messageClass.params:
                    yield from lines(f"""\
        msg.SetInParent()""")
                else:
                    yield from map_params_code(
                        messageClass,
                        mandatory=lambda param: lines(f"""\
        {assignment_str(param.name, nested=param.field.nested)}"""),
                        repeated=lambda param: lines(f"""\
        {assignment_str(param.name, nested=param.field.nested, repeated=True)}"""),
                        optional=lambda param, i: lines(f"""\
        {assignment_str(param.options[i], nested=param.fields[i].nested)}""")
                        if len(param.options) == 1 else lines(f"""\
        if self.{param.options[i]} is not None:
            {assignment_str(param.options[i], nested=param.fields[i].nested)}"""),
                        custom=lambda param: lines(f"""\
        # <default GSL customizable: {messageClass.name}-serialize-{param.name}>
        # TODO serialize custom field '{param.name}'
        {assignment_str(param.name)}
        # </GSL customizable: {messageClass.name}-serialize-{param.name}>"""),
                    )

            request = messageClass.direction == "=>"
            is_async = messageClass.direction == "<-"
            complex = len(message.requestClasses if request else message.replyClasses) > 1

            decorator = "protobuf" if complex else "RequestMsg" if request else "ReplyMsg"

            fields_str = ' '.join(f'{field_name!r},' for field_name in field_names(messageClass))

            yield from lines(f"""\


@{decorator}.message({proto.name}_pb2.{message.name}, '{message.discriminator}', fields=({fields_str}))
@dataclass(frozen=True, repr=False)
class {messageClass.name}({"Message" if complex else "SimpleMessage"}):""")

            if is_async:
                yield from lines(f"""\
    is_async = True

""")

            yield from message_fields_code()
            yield from message_init_code()

            yield from lines(f"""\

    def __post_init__(self):
        # <default GSL customizable: {messageClass.name}-init-validation>
        pass
        # </GSL customizable: {messageClass.name}-init-validation>""")

            yield from lines(f"""\

    # <default GSL customizable: {messageClass.name}-extra-members />""")

            if not complex:
                yield from message_parse_code()

            yield from message_serialize_code()

        def complex_parser_code(message, request):
            def init_param_strs(messageClass):
                yield from map_params(
                    messageClass,
                    mandatory=lambda param: param.name,
                    repeated=lambda param: f"*{param.name}",
                    optional=lambda param, i: f"{param.options[i]}={param.options[i]}",
                    custom=lambda param: param.name,
                )

            messageClasses = message.requestClasses if request else message.replyClasses
            proto = message.proto

            decorator = "RequestMsg" if request else "ReplyMsg"
            method_name = f"_parse_{message.discriminator}_{'request' if request else 'reply'}"

            yield from lines(f"""\


@{decorator}.parser('{message.discriminator}')
def {method_name}(msg: {proto.name}_pb2.{message.name}) \
-> Union[{', '.join(messageClass.name for messageClass in messageClasses)}]:""")

            for field in message.fields:
                if isinstance(field, Field):
                    if not field.nested:
                        yield from lines(f"""\
    {field.name} = msg.{field.name}""")
                    else:
                        yield from lines(f"""\
    {field.name} = msg.{field.name} if msg.HasField('{field.name}') else None""")
                elif isinstance(field, Oneof):
                    for field in field.fields:
                        yield from lines(f"""\
    {field.name} = msg.{field.name} if msg.HasField('{field.name}') else None""")
                else:
                    assert False

            yield from lines(f"""\
    # <default GSL customizable: {method_name}-return>
    # TODO return correct message instance""")

            for messageClass in messageClasses:
                yield from lines(f"""\
    #return {messageClass.name}({", ".join(init_param_strs(messageClass))})""")

            yield from lines(f"""\
    return None
    # </GSL customizable: {method_name}-return>""")

        yield from lines(f"""\
from typing import Any, Sequence, Union
from dataclasses import dataclass

from {'.' * (len(mod.path) + 1)} import RequestMsg, ReplyMsg, Message, SimpleMessage""")
        for protoPath, protoName in unique((proto.path, proto.name)
                                           for messageClass in mod.messageClasses
                                           for proto in (messageClass.message.proto,)):
            yield from lines(f"""\
from hedgehog.protocol.proto{'.'.join(('',) + protoPath)} import {protoName}_pb2""")
        yield from lines(f"""\
from hedgehog.utils import protobuf

__all__ = [{', '.join(repr(messageClass.name) for messageClass in mod.messageClasses)}]

# <default GSL customizable: module-header />""")
        for messageClass in mod.messageClasses:
            yield from message_class_code(messageClass)
        for message in mod.complexMessages:
            if len(message.requestClasses) > 1:
                yield from complex_parser_code(message, request=True)
            if len(message.replyClasses) > 1:
                yield from complex_parser_code(message, request=False)
