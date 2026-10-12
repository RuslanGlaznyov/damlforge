from forge.models import variant
from forge.builtins import no_derive


@no_derive
@variant
class DayOfWeek:
    def Monday(): pass
    def Tuesday(): pass
    def Wednesday(): pass
    def Thursday(): pass
    def Friday(): pass
    def Saturday(): pass
    def Sunday(): pass


@no_derive
@variant
class Month:
    def Jan(): pass
    def Feb(): pass
    def Mar(): pass
    def Apr(): pass
    def May(): pass
    def Jun(): pass
    def Jul(): pass
    def Aug(): pass
    def Sep(): pass
    def Oct(): pass
    def Nov(): pass
    def Dec(): pass
