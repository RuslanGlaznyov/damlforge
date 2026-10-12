from forge.models import Party, template


@template
class AmuletEventLog:
    dso: Party

    signatory: list[Party] = [dso]
