from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional, Union

from forge.models.decorators import Consuming


@dataclass(frozen=True)
class TypeRef:
    name: str
    args: tuple["TypeRef", ...] = ()


@dataclass(frozen=True)
class Field:
    name: str
    type: Optional[TypeRef]


# ---- expressions ----


@dataclass(frozen=True)
class IRName:
    id: str


@dataclass(frozen=True)
class IRAttribute:
    value: "IRExpr"
    attr: str


@dataclass(frozen=True)
class IRSubscript:
    value: "IRExpr"
    index: "IRExpr"


@dataclass(frozen=True)
class IRCall:
    func: "IRExpr"
    args: tuple["IRExpr", ...] = ()
    keywords: tuple[tuple[str, "IRExpr"], ...] = ()


@dataclass(frozen=True)
class IRConstant:
    value: Any


@dataclass(frozen=True)
class IRList:
    elements: tuple["IRExpr", ...]


@dataclass(frozen=True)
class IRTuple:
    elements: tuple["IRExpr", ...]


@dataclass(frozen=True)
class IRDict:
    keys: tuple["IRExpr", ...]
    values: tuple["IRExpr", ...]


@dataclass(frozen=True)
class IRBinOp:
    op: str
    left: "IRExpr"
    right: "IRExpr"


@dataclass(frozen=True)
class IRBoolOp:
    op: str
    values: tuple["IRExpr", ...]


@dataclass(frozen=True)
class IRUnaryOp:
    op: str
    operand: "IRExpr"


@dataclass(frozen=True)
class IRCompare:
    left: "IRExpr"
    op: str
    right: "IRExpr"


IRExpr = Union[
    IRName,
    IRAttribute,
    IRSubscript,
    IRCall,
    IRConstant,
    IRList,
    IRTuple,
    IRDict,
    IRBinOp,
    IRBoolOp,
    IRUnaryOp,
    IRCompare,
]


# ---- statements ----


@dataclass(frozen=True)
class IRAssert:
    test: IRExpr
    msg: Optional[IRExpr] = None


@dataclass(frozen=True)
class IRAssign:
    target: IRExpr
    value: IRExpr
    type: Optional[TypeRef] = None


@dataclass(frozen=True)
class IRIf:
    test: IRExpr
    body: tuple["IRStmt", ...]
    orelse: tuple["IRStmt", ...] = ()


@dataclass(frozen=True)
class IRFor:
    target: str
    target_type: Optional[TypeRef]
    iter: IRExpr
    body: tuple["IRStmt", ...]


@dataclass(frozen=True)
class IRReturn:
    value: Optional[IRExpr] = None


@dataclass(frozen=True)
class IRPass:
    pass


@dataclass(frozen=True)
class IRExprStmt:
    value: IRExpr


IRStmt = Union[IRAssert, IRAssign, IRIf, IRFor, IRReturn, IRPass, IRExprStmt]


# ---- containers ----


@dataclass(frozen=True)
class IRFunction:
    name: str
    args: tuple[Field, ...]
    return_type: Optional[TypeRef]
    decorators: tuple[str, ...]
    body: tuple[IRStmt, ...]


@dataclass(frozen=True)
class IRChoice:
    name: str
    controller: Optional[IRExpr]
    consuming: Optional[Consuming]
    observer: Optional[IRExpr]
    args: tuple[Field, ...]
    return_type: Optional[TypeRef]
    body: tuple[IRStmt, ...]


@dataclass(frozen=True)
class IRStruct:
    name: str
    fields: tuple[Field, ...]


@dataclass(frozen=True)
class IRFlag:
    name: str
    values: tuple[str, ...]


@dataclass(frozen=True)
class IRInterface:
    name: str
    view: Optional[TypeRef]
    requires: tuple[str, ...]
    keywords: tuple[tuple[str, IRExpr], ...]
    choices: tuple[IRChoice, ...]


@dataclass(frozen=True)
class IRTemplate:
    name: str
    fields: tuple[Field, ...]
    signatory: Optional[IRExpr]
    observer: Optional[IRExpr]
    init: Optional[IRFunction]
    choices: tuple[IRChoice, ...]


@dataclass(frozen=True)
class IRInstance:
    name: str
    bases: tuple[str, ...]
    choices: tuple[IRChoice, ...]


@dataclass(frozen=True)
class IRModule:
    structs: tuple[IRStruct, ...] = ()
    flags: tuple[IRFlag, ...] = ()
    interfaces: tuple[IRInterface, ...] = ()
    templates: tuple[IRTemplate, ...] = ()
    instances: tuple[IRInstance, ...] = ()
    functions: tuple[IRFunction, ...] = ()
