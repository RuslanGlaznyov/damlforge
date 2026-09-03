from forge.ast import nodes as vy_ast
from forge.exceptions import CompilerPanic
from forge.ir.nodes import (
    Field,
    IRAssert,
    IRAssign,
    IRAttribute,
    IRBinOp,
    IRBoolOp,
    IRCall,
    IRChoice,
    IRCompare,
    IRConstant,
    IRDict,
    IRExprStmt,
    IRFlag,
    IRFor,
    IRFunction,
    IRIf,
    IRInstance,
    IRInterface,
    IRList,
    IRImport,
    IRModule,
    IRName,
    IRPass,
    IRReturn,
    IRStruct,
    IRSubscript,
    IRTemplate,
    IRTuple,
    IRUnaryOp,
    SourceSpan,
    TypeRef,
)
from forge.models.decorators import Consuming


def _src(node: vy_ast.VyperNode) -> SourceSpan:
    return SourceSpan(
        lineno=getattr(node, "lineno", None),
        col_offset=getattr(node, "col_offset", None),
        end_lineno=getattr(node, "end_lineno", None),
        end_col_offset=getattr(node, "end_col_offset", None),
    )

_BIN_OPS = {
    "Add": "+",
    "Sub": "-",
    "Mult": "*",
    "Div": "/",
    "Mod": "%",
    "Pow": "**",
}

_BOOL_OPS = {"And": "and", "Or": "or"}

_UNARY_OPS = {"Not": "not", "USub": "-"}

_COMPARE_OPS = {
    "Eq": "==",
    "NotEq": "!=",
    "Is": "==",
    "IsNot": "!=",
    "Lt": "<",
    "LtE": "<=",
    "Gt": ">",
    "GtE": ">=",
    "In": "in",
    "NotIn": "not in",
}

CHOICE_DECORATOR = "choice"


def lower_type(node: vy_ast.VyperNode) -> TypeRef:
    if isinstance(node, vy_ast.Name):
        return TypeRef(node.id)
    if isinstance(node, vy_ast.Str):
        return TypeRef(node.value)
    if isinstance(node, vy_ast.NameConstant) and node.value is None:
        return TypeRef("None")
    if isinstance(node, vy_ast.Subscript):
        base = lower_type(node.value)
        if isinstance(node.slice, vy_ast.Tuple):
            args = tuple(lower_type(e) for e in node.slice.elements)
        else:
            args = (lower_type(node.slice),)
        return TypeRef(base.name, args)
    raise CompilerPanic(f"lower_type: unsupported type expression {type(node).__name__}")


def lower_expr(node: vy_ast.VyperNode):
    result = _lower_expr_inner(node)
    if node._metadata.get("needs_some_wrap"):
        result = IRCall(IRName("Some"), (result,))
    if node._metadata.get("needs_from_some_unwrap"):
        result = IRCall(IRName("from_some"), (result,))
    return result


def _lower_expr_inner(node: vy_ast.VyperNode):
    if isinstance(node, vy_ast.Name):
        return IRName(node.id)
    if isinstance(node, vy_ast.Attribute):
        if node._metadata.get("is_flag_value"):
            return IRName(node.attr)
        return IRAttribute(lower_expr(node.value), node.attr)
    if isinstance(node, vy_ast.Subscript):
        is_list = bool(node._metadata.get("is_list_value"))
        return IRSubscript(lower_expr(node.value), lower_expr(node.slice), is_list=is_list)
    if isinstance(node, vy_ast.Call):
        args = tuple(lower_expr(a) for a in node.args)
        keywords = tuple((kw.arg, lower_expr(kw.value)) for kw in node.keywords)
        return IRCall(lower_expr(node.func), args, keywords)
    if isinstance(node, vy_ast.NameConstant):
        return IRConstant(node.value)
    if isinstance(node, (vy_ast.Int, vy_ast.Decimal, vy_ast.Str)):
        return IRConstant(node.value)
    if isinstance(node, vy_ast.List):
        return IRList(tuple(lower_expr(e) for e in node.elements))
    if isinstance(node, vy_ast.Tuple):
        return IRTuple(tuple(lower_expr(e) for e in node.elements))
    if isinstance(node, vy_ast.Dict):
        keys = tuple(lower_expr(k) for k in node.keys)
        values = tuple(lower_expr(v) for v in node.values)
        return IRDict(keys, values)
    if isinstance(node, vy_ast.BinOp):
        op = _BIN_OPS[type(node.op).__name__]
        return IRBinOp(op, lower_expr(node.left), lower_expr(node.right))
    if isinstance(node, vy_ast.BoolOp):
        op = _BOOL_OPS[type(node.op).__name__]
        return IRBoolOp(op, tuple(lower_expr(v) for v in node.values))
    if isinstance(node, vy_ast.UnaryOp):
        op = _UNARY_OPS[type(node.op).__name__]
        return IRUnaryOp(op, lower_expr(node.operand))
    if isinstance(node, vy_ast.Compare):
        op = _COMPARE_OPS[type(node.op).__name__]
        return IRCompare(lower_expr(node.left), op, lower_expr(node.right))
    raise CompilerPanic(f"lower_expr: unsupported expression node {type(node).__name__}")


def lower_stmt(node: vy_ast.VyperNode):
    if isinstance(node, vy_ast.Assert):
        msg = lower_expr(node.msg) if node.msg is not None else None
        return IRAssert(lower_expr(node.test), msg, src=_src(node))
    if isinstance(node, vy_ast.AnnAssign):
        value = lower_expr(node.value) if node.value is not None else None
        return IRAssign(lower_expr(node.target), value, lower_type(node.annotation), src=_src(node))
    if isinstance(node, vy_ast.Assign):
        return IRAssign(lower_expr(node.target), lower_expr(node.value), src=_src(node))
    if isinstance(node, vy_ast.If):
        body = tuple(lower_stmt(s) for s in node.body)
        orelse = tuple(lower_stmt(s) for s in node.orelse)
        return IRIf(lower_expr(node.test), body, orelse, src=_src(node))
    if isinstance(node, vy_ast.For):
        target = node.target.target
        target_type = lower_type(node.target.annotation) if node.target.annotation else None
        body = tuple(lower_stmt(s) for s in node.body)
        return IRFor(target.id, target_type, lower_expr(node.iter), body, src=_src(node))
    if isinstance(node, vy_ast.Return):
        value = lower_expr(node.value) if node.value is not None else None
        return IRReturn(value, src=_src(node))
    if isinstance(node, vy_ast.Pass):
        return IRPass(src=_src(node))
    if isinstance(node, vy_ast.Expr):
        return IRExprStmt(lower_expr(node.value), src=_src(node))
    raise CompilerPanic(f"lower_stmt: unsupported statement node {type(node).__name__}")


def _lower_body(body) -> tuple:
    return tuple(lower_stmt(s) for s in body if not isinstance(s, vy_ast.DocStr))


def _lower_args(fn: vy_ast.FunctionDef) -> tuple:
    fields = []
    for a in fn.args.args:
        if a.arg == "self":
            continue
        arg_type = lower_type(a.annotation) if a.annotation is not None else None
        fields.append(Field(a.arg, arg_type))
    return tuple(fields)


def _decorator_names(fn: vy_ast.FunctionDef) -> tuple:
    names = []
    for dec in fn.decorator_list:
        target = dec.func if isinstance(dec, vy_ast.Call) else dec
        if isinstance(target, vy_ast.Name):
            names.append(target.id)
    return tuple(names)


def _choice_call(fn: vy_ast.FunctionDef):
    for dec in fn.decorator_list:
        if not isinstance(dec, vy_ast.Call):
            continue
        if isinstance(dec.func, vy_ast.Name) and dec.func.id == CHOICE_DECORATOR:
            return dec
    return None


def _lower_consuming(node) -> Consuming:
    if isinstance(node, vy_ast.NameConstant) and isinstance(node.value, bool):
        return Consuming.CONSUMING if node.value else Consuming.NON_CONSUMING
    if isinstance(node, vy_ast.Str):
        return Consuming(node.value)
    raise CompilerPanic(f"lower_consuming: unsupported consuming literal {type(node).__name__}")


def lower_function(fn: vy_ast.FunctionDef) -> IRFunction:
    return_type = lower_type(fn.returns) if fn.returns is not None else None
    return IRFunction(
        name=fn.name,
        args=_lower_args(fn),
        return_type=return_type,
        decorators=_decorator_names(fn),
        body=_lower_body(fn.body),
        src=_src(fn),
    )


def lower_choice(fn: vy_ast.FunctionDef) -> IRChoice:
    call = _choice_call(fn)
    controller = None
    consuming = None
    observer = None
    if call is not None:
        kwargs = {kw.arg: kw.value for kw in call.keywords}
        if "controller" in kwargs:
            controller = lower_expr(kwargs["controller"])
        if "consuming" in kwargs:
            consuming = _lower_consuming(kwargs["consuming"])
        if "observer" in kwargs:
            observer = lower_expr(kwargs["observer"])

    return_type = lower_type(fn.returns) if fn.returns is not None else None
    return IRChoice(
        name=fn.name,
        controller=controller,
        consuming=consuming,
        observer=observer,
        args=_lower_args(fn),
        return_type=return_type,
        body=_lower_body(fn.body),
        src=_src(fn),
    )


def _find_signatory(body) -> "IRExpr | None":
    for stmt in body:
        target = None
        value = None
        if isinstance(stmt, (vy_ast.AnnAssign, vy_ast.Assign)):
            target = stmt.target
            value = stmt.value
        if isinstance(target, vy_ast.Name) and target.id == "signatory" and value is not None:
            return lower_expr(value)
    return None


def _find_observer(body):
    for stmt in body:
        target = None
        value = None
        if isinstance(stmt, (vy_ast.AnnAssign, vy_ast.Assign)):
            target = stmt.target
            value = stmt.value
        if isinstance(target, vy_ast.Name) and target.id == "observer" and value is not None:
            return lower_expr(value)
    return None


def _find_ensure(body):
    for stmt in body:
        target = None
        value = None
        if isinstance(stmt, (vy_ast.AnnAssign, vy_ast.Assign)):
            target = stmt.target
            value = stmt.value
        if isinstance(target, vy_ast.Name) and target.id == "ensure" and value is not None:
            return lower_expr(value)
    return None


def lower_struct(node: vy_ast.StructDef) -> IRStruct:
    fields = tuple(
        Field(stmt.target.id, lower_type(stmt.annotation))
        for stmt in node.body
        if isinstance(stmt, vy_ast.AnnAssign)
    )
    return IRStruct(node.name, fields, src=_src(node))


def lower_flag(node: vy_ast.FlagDef) -> IRFlag:
    values = tuple(stmt.value.id for stmt in node.body if isinstance(stmt, vy_ast.Expr))
    return IRFlag(node.name, values, src=_src(node))


def lower_interface(node: vy_ast.InterfaceDef) -> IRInterface:
    view = None
    keywords = []
    for kw in node.keywords:
        if kw.arg == "view":
            view = lower_type(kw.value)
        else:
            keywords.append((kw.arg, lower_expr(kw.value)))

    requires = tuple(base.id for base in node.bases)
    choices = tuple(
        lower_choice(stmt) for stmt in node.body if isinstance(stmt, vy_ast.FunctionDef)
    )
    return IRInterface(node.name, view, requires, tuple(keywords), choices, src=_src(node))


def lower_template(node: vy_ast.TemplateDef) -> IRTemplate:
    fields = tuple(
        Field(stmt.target.id, lower_type(stmt.annotation))
        for stmt in node.body
        if isinstance(stmt, vy_ast.AnnAssign)
        and isinstance(stmt.target, vy_ast.Name)
        and stmt.target.id not in ("signatory", "observer", "key", "maintainer", "ensure")
    )
    signatory = _find_signatory(node.body)
    observer = _find_observer(node.body)
    ensure = _find_ensure(node.body)

    init = None
    choices = []
    for stmt in node.body:
        if not isinstance(stmt, vy_ast.FunctionDef):
            continue
        if stmt.name == "__init__":
            init = lower_function(stmt)
        elif _choice_call(stmt) is not None:
            choices.append(lower_choice(stmt))

    return IRTemplate(
        node.name, fields, signatory, observer, ensure, init, tuple(choices), src=_src(node)
    )


def lower_instance(node: vy_ast.InstanceDef) -> IRInstance:
    bases = tuple(base.id for base in node.bases)
    choices = tuple(
        lower_choice(stmt) for stmt in node.body if isinstance(stmt, vy_ast.FunctionDef)
    )
    return IRInstance(node.name, bases, choices, src=_src(node))


_CONSTRUCTOR_DECLARATION_TYPES = (vy_ast.StructDef, vy_ast.TemplateDef, vy_ast.FlagDef)


def _sibling_constructor_names(node) -> frozenset:
    names = set()
    for info in node._metadata.get("import_infos", ()):
        for decl in info.ast.body:
            if isinstance(decl, _CONSTRUCTOR_DECLARATION_TYPES):
                names.add(decl.name)
    return frozenset(names)


def _lower_imports(body, import_graph=None) -> tuple:
    from forge.builtins import collect_daml_builtins
    from forge.semantics.analysis.imports import ImportsBuilder
    from forge.utils import daml_module_name

    case_accessor_names = frozenset(collect_daml_builtins().case_accessors)

    def _daml_module_ref(module_str: str) -> str:
        if import_graph is not None:
            is_sibling = module_str in import_graph.sibling_module_strs
        else:
            is_sibling = "." not in module_str
        return daml_module_name(module_str) if is_sibling else module_str

    imports = []
    for node in body:
        if isinstance(node, vy_ast.ImportFrom):
            names = tuple(
                a.name
                for a in node.names
                if a.name not in case_accessor_names and ImportsBuilder.needs_daml_import(node.module, a.name)
            )
            if names:
                constructor_names = frozenset(names) & _sibling_constructor_names(node)
                imports.append(IRImport(_daml_module_ref(node.module), names, constructor_names))
        elif isinstance(node, vy_ast.Import):
            for alias in node.names:
                if alias.asname is not None:
                    continue
                if ImportsBuilder.is_annotation_only_root(alias.name.split(".", 1)[0]):
                    continue
                imports.append(IRImport(_daml_module_ref(alias.name), names=None))
    return tuple(imports)


def lower_module(module: vy_ast.Module, import_graph=None) -> IRModule:
    structs = []
    flags = []
    interfaces = []
    templates = []
    instances = []
    functions = []

    for node in module.body:
        if isinstance(node, vy_ast.StructDef):
            structs.append(lower_struct(node))
        elif isinstance(node, vy_ast.FlagDef):
            flags.append(lower_flag(node))
        elif isinstance(node, vy_ast.InterfaceDef):
            interfaces.append(lower_interface(node))
        elif isinstance(node, vy_ast.TemplateDef):
            templates.append(lower_template(node))
        elif isinstance(node, vy_ast.InstanceDef):
            instances.append(lower_instance(node))
        elif isinstance(node, vy_ast.FunctionDef):
            functions.append(lower_function(node))

    return IRModule(
        structs=tuple(structs),
        flags=tuple(flags),
        interfaces=tuple(interfaces),
        templates=tuple(templates),
        instances=tuple(instances),
        functions=tuple(functions),
        imports=_lower_imports(module.body, import_graph),
    )
