from typing import TypeVar

from forge.models import Optional
from forge.builtins import DamlName
from DA.Internal.Any import TemplateTypeRep
from DA.Internal.Interface.AnyView.Types import AnyView, InterfaceTypeRep

V = TypeVar("V")


@DamlName("fromAnyView")
def from_any_view(any_view: AnyView) -> Optional[V]:
    pass


@DamlName("fromTemplateTypeRep")
def from_template_type_rep(template_type_rep: TemplateTypeRep) -> InterfaceTypeRep:
    pass
