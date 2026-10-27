from forge.builtins.daml_lang import visible_by_key
from forge.models import Party, template


@template
class Token:
    owner: Party

    signatory: Party = owner


def has_token(owner: Party) -> bool:
    return visible_by_key(Token, owner)
