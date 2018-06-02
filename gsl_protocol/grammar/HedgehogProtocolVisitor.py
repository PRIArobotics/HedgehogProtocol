from gsl import pseudo_tuple

from gsl.antlr import ParseTreeVisitor
if __name__ is not None and "." in __name__:
    from .HedgehogProtocolParser import HedgehogProtocolParser
else:
    from HedgehogProtocolParser import HedgehogProtocolParser


Model = pseudo_tuple('Model', ('messages',))
Message = pseudo_tuple('Message', ('qualifiedName', 'discriminator', 'label', 'docstring', 'fields', 'messageClasses',))
Field = pseudo_tuple('Field', ('nested', 'repeated', 'fieldType', 'name', 'label',))
Oneof = pseudo_tuple('Oneof', ('name', 'fields',))
MessageClass = pseudo_tuple('MessageClass', ('direction', 'qualifiedName', 'params', 'docstring',))
MandatoryParam = pseudo_tuple('MandatoryParam', ('name',))
RepeatedParam = pseudo_tuple('RepeatedParam', ('name',))
OptionalParam = pseudo_tuple('OptionalParam', ('options',))
QualifiedName = pseudo_tuple('QualifiedName', ('path', 'file', 'name',))


class HedgehogProtocolVisitor(ParseTreeVisitor):
    def visitModel(self, ctx: HedgehogProtocolParser.ModelContext):
        return Model(
            self.visitNodes(self.get_children(ctx, HedgehogProtocolParser.MessageContext)),
        )

    def visitMessage(self, ctx: HedgehogProtocolParser.MessageContext):
        return Message(
            self.visitNode(self.get_child(ctx, HedgehogProtocolParser.QualifiedNameContext)),
            self.visitNode(ctx.discriminator),
            self.visitNode(ctx.label),
            self.visitNode(self.get_child(ctx, HedgehogProtocolParser.DocstringContext)) if self.has_children(ctx, HedgehogProtocolParser.DocstringContext) else None,
            self.visitNodes(self.get_children(ctx, HedgehogProtocolParser.FieldContext, HedgehogProtocolParser.OneofContext)),
            self.visitNodes(self.get_children(ctx, HedgehogProtocolParser.MessageClassContext)),
        )

    def visitField(self, ctx: HedgehogProtocolParser.FieldContext):
        return Field(
            bool(ctx.nested),
            bool(ctx.rep),
            self.visitNode(ctx.fieldType),
            self.visitNode(ctx.name),
            self.visitNode(ctx.label),
        )

    def visitOneof(self, ctx: HedgehogProtocolParser.OneofContext):
        return Oneof(
            self.visitNode(ctx.name),
            self.visitNodes(self.get_children(ctx, HedgehogProtocolParser.FieldContext)),
        )

    def visitMessageClass(self, ctx: HedgehogProtocolParser.MessageClassContext):
        return MessageClass(
            self.visitNode(self.get_child(ctx, HedgehogProtocolParser.DirectionContext)),
            self.visitNode(self.get_child(ctx, HedgehogProtocolParser.QualifiedNameContext)),
            self.visitNode(self.get_child(ctx, HedgehogProtocolParser.ParamListContext)),
            self.visitNode(self.get_child(ctx, HedgehogProtocolParser.DocstringContext)) if self.has_children(ctx, HedgehogProtocolParser.DocstringContext) else None,
        )

    def visitParamList(self, ctx: HedgehogProtocolParser.ParamListContext):
        return self.visitNodes(self.get_children(ctx, HedgehogProtocolParser.MandatoryParamContext, HedgehogProtocolParser.RepeatedParamContext, HedgehogProtocolParser.OptionalParamContext))

    def visitMandatoryParam(self, ctx: HedgehogProtocolParser.MandatoryParamContext):
        return MandatoryParam(
            self.visitNode(self.get_child(ctx, HedgehogProtocolParser.IdentifierContext)),
        )

    def visitRepeatedParam(self, ctx: HedgehogProtocolParser.RepeatedParamContext):
        return RepeatedParam(
            self.visitNode(self.get_child(ctx, HedgehogProtocolParser.IdentifierContext)),
        )

    def visitOptionalParam(self, ctx: HedgehogProtocolParser.OptionalParamContext):
        return OptionalParam(
            self.visitNodes(self.get_children(ctx, HedgehogProtocolParser.IdentifierContext)),
        )

    def visitQualifiedName(self, ctx: HedgehogProtocolParser.QualifiedNameContext):
        return QualifiedName(
            self.visitNode(ctx.path) if ctx.path else None,
            self.visitNode(ctx.fileName),
            self.visitNode(ctx.name),
        )

    def visitQualifiedIdentifier(self, ctx: HedgehogProtocolParser.QualifiedIdentifierContext):
        return self.visitNodes(self.get_children(ctx, HedgehogProtocolParser.IdentifierContext))

    def visitIdentifier(self, ctx: HedgehogProtocolParser.IdentifierContext):
        return self.visitNode(self.get_child(ctx))

    def visitNumber(self, ctx: HedgehogProtocolParser.NumberContext):
        return self.visitNode(self.get_child(ctx))

    def visitDocstring(self, ctx: HedgehogProtocolParser.DocstringContext):
        return self.visitNode(self.get_child(ctx))

    def visitString(self, ctx: HedgehogProtocolParser.StringContext):
        return self.visitNode(self.get_child(ctx))

    def visitDirection(self, ctx: HedgehogProtocolParser.DirectionContext):
        return self.visitNode(self.get_child(ctx))

