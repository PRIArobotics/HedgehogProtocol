import itertools
import os.path

from gsl import lines, generate
from gsl.strings import case

from .grammar.HedgehogProtocolVisitor import Field, Oneof, MandatoryParam, RepeatedParam, OptionalParam


def generate_code(model, root):
    generate_hedgehog_proto_code(model, root)
    for proto in model.protos:
        generate_message_proto_code(model, proto, root)


def generate_hedgehog_proto_code(model, root):
    out_file = os.path.join(root, 'proto/hedgehog/protocol/proto/hedgehog.proto')
    os.makedirs(os.path.dirname(out_file), exist_ok=True)

    @generate(out_file)
    def code():
        yield from lines(f"""\
syntax = "proto3";

package hedgehog.protocol.proto;

option java_package = "at.pria.hedgehog.protocol.proto";
option java_outer_classname = "HedgehogP";

""")
        for proto in model.protos:
            yield from lines(f"""\
import "hedgehog/protocol/proto/{'/'.join(proto.path + (proto.name,))}.proto";""")
        yield from lines(f"""\

// <default GSL customizable: module-extras />

message HedgehogMessage {{
    oneof payload {{""")
        for proto in model.protos:
            yield from lines(f"""\
        // {proto.name}.proto""")
            for message in proto.messages:
                yield from lines(f"""\
        {message.name} {message.discriminator} = {message.label};""")
        yield from lines(f"""\
    }}
}}""")


def generate_message_proto_code(model, proto, root):
    out_file = os.path.join(root, 'proto/hedgehog/protocol/proto', *proto.path, f'{proto.name}.proto')
    os.makedirs(os.path.dirname(out_file), exist_ok=True)

    @generate(out_file)
    def code():
        def field_code(f):
            def field_str(field):
                return f"{'repeated ' if field.repeated else ''}{field.fieldType} {field.name} = {field.label};"

            if isinstance(f, Field):
                field = f
                yield from lines(f"""\
    {field_str(field)}""")
            elif isinstance(f, Oneof):
                oneof = f
                yield from lines(f"""\
    oneof {oneof.name} {{""")
                for field in oneof.fields:
                    yield from lines(f"""\
        {field_str(field)}""")
                yield from lines(f"""\
    }}""")
            else:
                assert False

        def params_str(params):
            mandatory = (param.name for param in params if isinstance(param, MandatoryParam))
            repeated = (f"*{param.name}" for param in params if isinstance(param, RepeatedParam))
            optional = ("/".join(param.options) for param in params if isinstance(param, OptionalParam))

            optional = f"[{', '.join(optional)}]"
            optional = (optional,) if optional != "[]" else ()

            return f"({', '.join(itertools.chain(mandatory, repeated, optional))})"

        yield from lines(f"""\
syntax = "proto3";

package hedgehog.protocol.proto;

option java_package = "at.pria.hedgehog.protocol.proto";
option java_outer_classname = "{case(snake=proto.name, to='pascal')}P";

// <default GSL customizable: module-extras />
""")
        for message in proto.messages:
            yield from lines(f"""\

""")
            for docstring in lines(message.docstring or ""):
                yield from lines(f"""\
// {docstring}""")
            if message.docstring and message.messageClasses:
                yield from lines(f"""\
//""")
            for messageClass in message.messageClasses:
                yield from lines(f"""\
// {f"{messageClass.direction} {params_str(messageClass.params)}:".ljust(24)}  {messageClass.docstring or ""}""")
            yield from lines(f"""\
message {message.name} {{""")
            for field in message.fields:
                yield from field_code(field)
            yield from lines(f"""\
}}""")
