from gsl import pseudo_tuple
from gsl.antlr import Antlr

from .grammar.HedgehogProtocolLexer import HedgehogProtocolLexer
from .grammar.HedgehogProtocolParser import HedgehogProtocolParser
from .grammar.HedgehogProtocolVisitor import HedgehogProtocolVisitor as _HedgehogProtocolVisitor
from .grammar.HedgehogProtocolVisitor import Field, Oneof, MandatoryParam, RepeatedParam, OptionalParam

Proto = pseudo_tuple('Proto', ('path', 'name', 'messages'))
Module = pseudo_tuple('Module', ('path', 'name', 'messageClasses', 'complexMessages'))


class HedgehogProtocolVisitor(_HedgehogProtocolVisitor):
    def visitField(self, ctx):
        result = super(HedgehogProtocolVisitor, self).visitField(ctx)
        return result

    def visitNumber(self, ctx):
        return int(super(HedgehogProtocolVisitor, self).visitNumber(ctx))

    def visitDocstring(self, ctx):
        return super(HedgehogProtocolVisitor, self).visitDocstring(ctx)[3:-3]

    def visitQualifiedName(self, ctx):
        result = super(HedgehogProtocolVisitor, self).visitQualifiedName(ctx)
        result.path = (*result.path,) if result.path is not None else ()
        result.full_path = (*result.path, result.file)
        result.full_name = (*result.path, result.file, result.name)
        return result

    def visitString(self, ctx):
        return super(HedgehogProtocolVisitor, self).visitString(ctx)[1:-1]


def augment_model(model):
    protos = {}
    model.protos = []

    def add_proto(message):
        q_name = message.qualifiedName
        if q_name.full_path not in protos:
            proto = Proto(q_name.path, q_name.file, [])
            protos[q_name.full_path] = proto
            model.protos.append(proto)
        else:
            proto = protos[q_name.full_path]
        proto.messages.append(message)
        message.proto = proto

    modules = {}
    model.modules = []

    def add_module(messageClass):
        q_name = messageClass.qualifiedName
        if q_name.full_path not in modules:
            mod = Module(q_name.path, q_name.file, [], [])
            modules[q_name.full_path] = mod
            model.modules.append(mod)
        else:
            mod = modules[q_name.full_path]
        mod.messageClasses.append(messageClass)
        messageClass.module = mod

    def fields_dict(message):
        def fields():
            for field in message.fields:
                if isinstance(field, Field):
                    yield field
                elif isinstance(field, Oneof):
                    yield from field.fields
                else:
                    assert False

        return {field.name: field for field in fields()}

    for message in model.messages:
        add_proto(message)
        message.name = message.qualifiedName.name
        fields = fields_dict(message)

        for messageClass in message.messageClasses:
            add_module(messageClass)
            messageClass.name = messageClass.qualifiedName.name
            messageClass.message = message

            for param in messageClass.params:
                if isinstance(param, (MandatoryParam, RepeatedParam)):
                    param.field = fields[param.name]
                elif isinstance(param, OptionalParam):
                    param.fields = [fields[option] for option in param.options]
                else:
                    assert False

        def direction_classes(dirs):
            messageClasses = [messageClass
                              for messageClass in message.messageClasses if messageClass.direction in dirs]
            if len(set(messageClass.qualifiedName.full_path for messageClass in messageClasses)) > 1:
                classNames = ", ".join(".".join(messageClass.qualifiedName.full_name)
                                       for messageClass in messageClasses)
                raise ValueError("all classes must be in the same module: " + classNames)

            return messageClasses

        message.requestClasses = direction_classes({"=>"})
        message.replyClasses = direction_classes({"<-", "<="})

        complex_modules = set()
        if len(message.requestClasses) > 1:
            complex_modules.add(message.requestClasses[0].module)
        if len(message.replyClasses) > 1:
            complex_modules.add(message.replyClasses[0].module)
        for mod in complex_modules:
            mod.complexMessages.append(message)


def get_model(model_file):
    antlr = Antlr(HedgehogProtocolLexer, HedgehogProtocolParser)
    p = antlr.parser(antlr.file_stream(model_file))
    model = p.model().accept(HedgehogProtocolVisitor())

    augment_model(model)
    return model


def main():
    from . import proto_target

    model = get_model('gsl_protocol/hedgehog_protocol')
    root = '.'
    proto_target.generate_code(model, root)
