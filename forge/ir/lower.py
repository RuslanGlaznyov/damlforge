from pathlib import Path

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
    IRExpr,
    IRExprStmt,
    IREnum,
    IRFor,
    IRFunction,
    IRIf,
    IRInterface,
    IRInterfaceInstance,
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
    IRVariant,
    IRVariantConstructor,
    SourceSpan,
    TypeRef,
)
from forge.builtins import DamlName, choice
from forge.models.decorators import Consuming


def _src(node: vy_ast.VyperNode) -> SourceSpan:
    return SourceSpan(
        lineno=getattr(node, "lineno", None),
        col_offset=getattr(node, "col_offset", None),
        end_lineno=getattr(node, "end_lineno", None),
        end_col_offset=getattr(node, "end_col_offset", None),
    )


_BIN_OPS = {"Add": "+", "Sub": "-", "Mult": "*", "Div": "/", "Mod": "%", "Pow": "**"}

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


def lower_type(node: vy_ast.VyperNode) -> TypeRef:
    if daml_type_name := node._metadata.get("daml_type_name"):
        return TypeRef(daml_type_name)
    if isinstance(node, vy_ast.Name):
        return TypeRef(node.id)
    if isinstance(node, vy_ast.Str):
        return TypeRef(node.value)
    if isinstance(node, vy_ast.NameConstant) and node.value is None:
        return TypeRef("None")
    if isinstance(node, vy_ast.Attribute) and isinstance(node.value, vy_ast.Name):
        return TypeRef(f"{node.value.id}.{node.attr}")
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
    handler = globals().get(f"_lower_expr_{type(node).__name__}")
    if handler is None:
        raise CompilerPanic(f"lower_expr: unsupported expression node {type(node).__name__}")
    return handler(node)


def _lower_expr_Name(node):
    return IRName(node.id)


def _lower_expr_Attribute(node):
    if node._metadata.get("is_enum_value"):
        return IRName(node.attr)
    return IRAttribute(lower_expr(node.value), node.attr)


def _lower_expr_Subscript(node):
    is_list = bool(node._metadata.get("is_list_value"))
    return IRSubscript(lower_expr(node.value), lower_expr(node.slice), is_list=is_list)


def _lower_expr_Call(node):
    if node._metadata.get("datetime_now"):
        return IRCall(IRName("getTime"))
    if "fromtimestamp_argument" in node._metadata:
        argument = node._metadata["fromtimestamp_argument"]
        microseconds = lower_expr(argument)
        if not node._metadata["fromtimestamp_is_microseconds"]:
            microseconds = (
                IRConstant(argument.value * 1_000_000)
                if isinstance(argument, vy_ast.Int)
                else IRBinOp("*", microseconds, IRConstant(1_000_000))
            )
        return IRCall(IRName("fromUnixMicroseconds"), (microseconds,))
    if combine_arguments := node._metadata.get("datetime_combine_arguments"):
        value, hour, minute, second = combine_arguments
        clock = tuple(
            IRConstant(0) if part is None else lower_expr(part) for part in (hour, minute, second)
        )
        return IRCall(IRName("time"), (lower_expr(value), *clock))
    if date_arguments := node._metadata.get("date_arguments"):
        year, month, day = date_arguments
        month_name = node._metadata.get("date_month_name")
        daml_month = (
            IRName(month_name)
            if month_name
            else IRCall(IRName("toEnum"), (IRBinOp("-", lower_expr(month), IRConstant(1)),))
        )
        return IRCall(IRName("date"), (lower_expr(year), daml_month, lower_expr(day)))
    if timedelta_arguments := node._metadata.get("timedelta_arguments"):
        terms = []
        for unit, value_node in timedelta_arguments:
            value = lower_expr(value_node)
            if unit == "weeks":
                value = IRBinOp("*", value, IRConstant(7))
                unit = "days"
            terms.append(IRCall(IRName(unit), (value,)))
        result = terms[0]
        for term in terms[1:]:
            result = IRBinOp("+", result, term)
        return result
    if "timedelta_arguments" in node._metadata:
        return IRCall(IRName("microseconds"), (IRConstant(0),))
    args = tuple(lower_expr(a) for a in node.args)
    keywords = tuple((kw.arg, lower_expr(kw.value)) for kw in node.keywords)
    return IRCall(lower_expr(node.func), args, keywords)


def _lower_expr_literal(node):
    return IRConstant(node.value)


_lower_expr_NameConstant = _lower_expr_literal
_lower_expr_Int = _lower_expr_literal
_lower_expr_Decimal = _lower_expr_literal
_lower_expr_Str = _lower_expr_literal


def _lower_expr_List(node):
    return IRList(tuple(lower_expr(e) for e in node.elements))


def _lower_expr_Tuple(node):
    return IRTuple(tuple(lower_expr(e) for e in node.elements))


def _lower_expr_Dict(node):
    keys = tuple(lower_expr(k) for k in node.keys)
    values = tuple(lower_expr(v) for v in node.values)
    return IRDict(keys, values, kind=node._metadata.get("map_kind"))


def _lower_expr_BinOp(node):
    if node._metadata.get("add_rel_time"):
        return IRCall(IRName("addRelTime"), (lower_expr(node.left), lower_expr(node.right)))
    if node._metadata.get("sub_time"):
        return IRCall(IRName("subTime"), (lower_expr(node.left), lower_expr(node.right)))
    op = _BIN_OPS[type(node.op).__name__]
    return IRBinOp(op, lower_expr(node.left), lower_expr(node.right))


def _lower_expr_BoolOp(node):
    op = _BOOL_OPS[type(node.op).__name__]
    return IRBoolOp(op, tuple(lower_expr(v) for v in node.values))


def _lower_expr_UnaryOp(node):
    op = _UNARY_OPS[type(node.op).__name__]
    return IRUnaryOp(op, lower_expr(node.operand))


def _lower_expr_Compare(node):
    op = _COMPARE_OPS[type(node.op).__name__]
    return IRCompare(lower_expr(node.left), op, lower_expr(node.right))


def lower_stmt(node: vy_ast.VyperNode):
    handler = globals().get(f"_lower_stmt_{type(node).__name__}")
    if handler is None:
        raise CompilerPanic(f"lower_stmt: unsupported statement node {type(node).__name__}")
    return handler(node)


def _lower_stmt_Assert(node):
    msg = lower_expr(node.msg) if node.msg is not None else None
    return IRAssert(lower_expr(node.test), msg, src=_src(node))


def _lower_stmt_AnnAssign(node):
    value = lower_expr(node.value) if node.value is not None else None
    return IRAssign(lower_expr(node.target), value, lower_type(node.annotation), src=_src(node))


def _lower_stmt_Assign(node):
    return IRAssign(lower_expr(node.target), lower_expr(node.value), src=_src(node))


def _lower_stmt_If(node):
    body = tuple(lower_stmt(s) for s in node.body)
    orelse = tuple(lower_stmt(s) for s in node.orelse)
    return IRIf(lower_expr(node.test), body, orelse, src=_src(node))


def _lower_stmt_For(node):
    target = node.target.target
    target_type = lower_type(node.target.annotation) if node.target.annotation else None
    body = tuple(lower_stmt(s) for s in node.body)
    return IRFor(target.id, target_type, lower_expr(node.iter), body, src=_src(node))


def _lower_stmt_Return(node):
    value = lower_expr(node.value) if node.value is not None else None
    return IRReturn(value, src=_src(node))


def _lower_stmt_Pass(node):
    return IRPass(src=_src(node))


def _lower_stmt_Expr(node):
    return IRExprStmt(lower_expr(node.value), src=_src(node))


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
        if isinstance(dec.func, vy_ast.Name) and dec.func.id == choice.__name__:
            return dec
    return None


def _daml_name_override(fn: vy_ast.FunctionDef) -> "str | None":
    for dec in fn.decorator_list:
        if not isinstance(dec, vy_ast.Call):
            continue
        if isinstance(dec.func, vy_ast.Name) and dec.func.id == DamlName.__name__:
            return dec.args[0].value
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
        name=_daml_name_override(fn) or fn.name,
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
        name=_daml_name_override(fn) or fn.name,
        controller=controller,
        consuming=consuming,
        observer=observer,
        args=_lower_args(fn),
        return_type=return_type,
        body=_lower_body(fn.body),
        src=_src(fn),
    )


def _find_signatory(body) -> IRExpr | None:
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


def lower_enum(node: vy_ast.EnumDef) -> IREnum:
    values = []
    for stmt in node.body:
        name = vy_ast.enum_member_name(stmt)
        if name is not None:
            values.append(name)
    return IREnum(node.name, tuple(values), src=_src(node))


def lower_variant(node: vy_ast.VariantDef) -> IRVariant:
    constructors = []
    for fn in node.body:
        if not isinstance(fn, vy_ast.FunctionDef):
            continue
        fields = tuple(
            Field(arg.arg, lower_type(arg.annotation)) for arg in fn.args.args if arg.arg != "self"
        )
        constructors.append(
            IRVariantConstructor(fn.name, fields, record=_has_decorator(fn, "variant_record"))
        )
    return IRVariant(node.name, tuple(constructors), src=_src(node))


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


def _has_decorator(fn: vy_ast.FunctionDef, name: str) -> bool:
    for dec in fn.decorator_list:
        target = dec.func if isinstance(dec, vy_ast.Call) else dec
        if isinstance(target, vy_ast.Name) and target.id == name:
            return True
    return False


def _interface_choice_names(interface_decl: vy_ast.InterfaceDef) -> frozenset:
    return frozenset(
        stmt.name
        for stmt in interface_decl.body
        if isinstance(stmt, vy_ast.FunctionDef) and _choice_call(stmt) is not None
    )


def _interface_view_type_name(interface_decl: vy_ast.InterfaceDef) -> "str | None":
    for kw in interface_decl.keywords:
        if kw.arg == "view" and isinstance(kw.value, vy_ast.Name):
            return kw.value.id
    return None


def _implemented_interfaces(node: vy_ast.TemplateDef) -> tuple:
    from forge.semantics.analysis.types import known_declarations

    declarations = known_declarations([node.module_node])
    result = []
    for base in node.bases:
        if isinstance(base, vy_ast.Name):
            decl = declarations.get(base.id)
            if isinstance(decl, vy_ast.InterfaceDef):
                result.append((base.id, decl))
    return tuple(result)


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

    implemented = _implemented_interfaces(node)
    interface_choice_owner: dict = {}
    interface_view_type: dict = {}
    for iface_name, iface_decl in implemented:
        for choice_name in _interface_choice_names(iface_decl):
            interface_choice_owner[choice_name] = iface_name
        view_type = _interface_view_type_name(iface_decl)
        if view_type is not None:
            interface_view_type[view_type] = iface_name

    init = None
    checked_fetch = None
    own_choices = []
    interface_choices: dict = {name: [] for name, _ in implemented}
    interface_views: dict = {}
    for stmt in node.body:
        if not isinstance(stmt, vy_ast.FunctionDef):
            continue
        if stmt.name == "__init__":
            init = lower_function(stmt)
        elif _has_decorator(stmt, "checked_fetch"):
            checked_fetch = lower_function(stmt)
        elif _has_decorator(stmt, "view") and isinstance(stmt.returns, vy_ast.Name):
            iface_name = interface_view_type.get(stmt.returns.id)
            if iface_name is not None:
                interface_views[iface_name] = lower_function(stmt)
        elif _choice_call(stmt) is not None:
            iface_name = interface_choice_owner.get(stmt.name)
            if iface_name is not None:
                interface_choices[iface_name].append(lower_choice(stmt))
            else:
                own_choices.append(lower_choice(stmt))

    interface_instances = tuple(
        IRInterfaceInstance(
            interface=iface_name,
            view=interface_views.get(iface_name),
            choices=tuple(interface_choices[iface_name]),
        )
        for iface_name, _ in implemented
    )

    return IRTemplate(
        node.name,
        fields,
        signatory,
        observer,
        ensure,
        init,
        tuple(own_choices),
        interface_instances,
        checked_fetch,
        src=_src(node),
    )


_CONSTRUCTOR_DECLARATION_TYPES = (
    vy_ast.StructDef,
    vy_ast.TemplateDef,
    vy_ast.EnumDef,
    vy_ast.VariantDef,
)


def _sibling_constructor_names(node) -> frozenset:
    names = set()
    for info in node._metadata.get("import_infos", ()):
        for decl in info.ast.body:
            if isinstance(decl, _CONSTRUCTOR_DECLARATION_TYPES):
                names.add(decl.name)
            if isinstance(decl, (vy_ast.TemplateDef, vy_ast.InterfaceDef)):
                names.update(
                    _daml_name_override(fn) or fn.name
                    for fn in decl.body
                    if isinstance(fn, vy_ast.FunctionDef) and _choice_call(fn) is not None
                )
    return frozenset(names)


def _lower_imports(body, import_graph=None) -> tuple:
    from forge.builtins import collect_daml_builtins
    from forge.semantics.analysis.imports import ImportsBuilder
    from forge.utils import daml_module_name

    case_accessor_names = frozenset(collect_daml_builtins().case_accessors)

    def _daml_module_ref(module_str: str, node=None) -> str:
        if import_graph is not None:
            is_sibling = module_str in import_graph.sibling_module_strs
        else:
            is_sibling = "." not in module_str
        if not is_sibling:
            return module_str
        if node is not None:
            info = next(
                (
                    info
                    for info in node._metadata.get("import_infos", ())
                    if info.alias == module_str
                ),
                None,
            )
            target_path = getattr(getattr(info, "ast", None), "path", None)
            if target_path:
                path = Path(target_path).with_suffix("")
                return ".".join(daml_module_name(part) for part in path.parts)
        return daml_module_name(module_str)

    imports = []
    for node in body:
        if isinstance(node, vy_ast.ImportFrom):
            names = tuple(
                a.name
                for a in node.names
                if a.name not in case_accessor_names
                and ImportsBuilder.needs_daml_import(node.module, a.name)
            )
            if names:
                constructor_names = frozenset(names) & _sibling_constructor_names(node)
                imports.append(
                    IRImport(_daml_module_ref(node.module, node), names, constructor_names)
                )
        elif isinstance(node, vy_ast.Import):
            for alias in node.names:
                if ImportsBuilder.is_annotation_only_root(alias.name.split(".", 1)[0]):
                    continue
                imports.append(
                    IRImport(_daml_module_ref(alias.name, node), names=None, alias=alias.asname)
                )
    return tuple(imports)


def lower_module(module: vy_ast.Module, import_graph=None) -> IRModule:
    structs = []
    enums = []
    variants = []
    interfaces = []
    templates = []
    functions = []

    for node in module.body:
        if isinstance(node, vy_ast.StructDef):
            structs.append(lower_struct(node))
        elif isinstance(node, vy_ast.EnumDef):
            enums.append(lower_enum(node))
        elif isinstance(node, vy_ast.VariantDef):
            variants.append(lower_variant(node))
        elif isinstance(node, vy_ast.InterfaceDef):
            interfaces.append(lower_interface(node))
        elif isinstance(node, vy_ast.TemplateDef):
            templates.append(lower_template(node))
        elif isinstance(node, vy_ast.FunctionDef):
            functions.append(lower_function(node))

    return IRModule(
        structs=tuple(structs),
        enums=tuple(enums),
        variants=tuple(variants),
        interfaces=tuple(interfaces),
        templates=tuple(templates),
        functions=tuple(functions),
        imports=_lower_imports(module.body, import_graph),
        required_modules=tuple(module._metadata.get("required_daml_modules", ())),
        effect_functions=tuple(module._metadata.get("intrinsic_effect_fns", ())),
    )
