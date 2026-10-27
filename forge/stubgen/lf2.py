import copy

from dazl.damlast import daml_lf_1 as lf
from dazl.damlast import parse as dazl_parse
from dazl.damlast.parse_factory.pb_v2 import ProtobufParser21


def apply_type(head: lf.Type, arg: lf.Type) -> lf.Type:
    if head.var is not None:
        return lf.Type(var=lf.Type.Var(head.var.var, (*head.var.args, arg)))
    if head.con is not None:
        return lf.Type(con=lf.Type.Con(head.con.tycon, (*head.con.args, arg)))
    if head.prim is not None:
        return lf.Type(prim=lf.Type.Prim(head.prim.prim, (*head.prim.args, arg)))
    if head.syn is not None:
        return lf.Type(syn=lf.Type.Syn(head.syn.tysyn, (*head.syn.args, arg)))
    raise ValueError(f"cannot apply a type argument to {head!r}")


class Parser23(ProtobufParser21):
    def __init__(self, current_package: lf.PackageRef) -> None:
        super().__init__(current_package)
        self.package_imports: list = []
        self.kinds: list = []
        self.exprs: list = []

    def parse_Package(self, pb):
        self.package_imports = list(pb.package_imports.imported_packages)
        self.kinds, self.exprs = list(pb.interned_kinds), list(pb.interned_exprs)
        return super().parse_Package(pb)

    def parse_ModuleId(self, pb):
        if pb.package_id.WhichOneof("Sum") != "package_import_id":
            return super().parse_ModuleId(pb)
        package = lf.PackageRef(self.package_imports[pb.package_id.package_import_id])
        name = lf.DottedName(self.interned_dotted_names[pb.module_name_interned_dname])
        return lf.ModuleRef(package, name)

    def parse_Kind(self, pb):
        if pb.WhichOneof("Sum") == "interned_kind":
            return self.parse_Kind(self.kinds[pb.interned_kind])
        return super().parse_Kind(pb)

    def parse_Expr(self, pb):
        if pb.WhichOneof("Sum") == "interned_expr":
            return self.parse_Expr(self.exprs[pb.interned_expr])
        return super().parse_Expr(pb)

    def parse_Type(self, pb):
        if pb.WhichOneof("Sum") == "tapp":
            return apply_type(self.parse_Type(pb.tapp.lhs), self.parse_Type(pb.tapp.rhs))
        return super().parse_Type(pb)

    def parse_BuiltinLit(self, pb):
        if pb.WhichOneof("Sum") == "failure_category":
            return lf.PrimLit(text=pb.FailureCategory.Name(pb.failure_category))
        return super().parse_BuiltinLit(pb)

    def parse_BuiltinFunction(self, pb):
        try:
            return super().parse_BuiltinFunction(pb)
        except ValueError:
            return pb

    def parse_Update(self, pb):
        return super().parse_Update(pb) if pb.WhichOneof("Sum") else None

    def _copy(self) -> "Parser23":
        return copy.copy(self)


def install() -> None:
    vars(dazl_parse)["ProtobufParser21"] = Parser23
