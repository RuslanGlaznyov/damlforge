
import totally_bogus_nonexistent_module

template Asset:
    owner: Party

    signatory: list[Party] = [owner]

    @choice(controller=owner, consuming=True)
    def transfer(new_owner: Party) -> bool:
        pass
