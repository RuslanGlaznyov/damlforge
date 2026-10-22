
from forge.models import choice, template, view, interface
from forge.builtins import DamlName

struct HoldingView:
    owner: Party

interface Holding(view=HoldingView):
    @view
    def get_view() -> bool:
        pass
