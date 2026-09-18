
from forge.models import choice, ledger_effect, template, view, interface
from forge.builtins import DamlName

struct HoldingView:
    owner: Party

interface Holding(view=HoldingView):
    @view
    def get_view() -> bool:
        pass
