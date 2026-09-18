
from Splice.AppTransferContext import AppTransferContext as AppTContext

template Asset:
    owner: Party

    signatory: list[Party] = [owner]

    @choice(controller=owner, consuming=True)
    def transfer(new_owner: Party, app_context: AppTContext) -> bool:
        pass
