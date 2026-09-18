
@template
class Asset:
    owner: Party

    @choice(controller=owner, consuming=True)
    def transfer(new_owner: Party) -> bool:
        pass
