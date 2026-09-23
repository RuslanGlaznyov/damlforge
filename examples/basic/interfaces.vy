from forge.models import Party, choice

struct SimpleTemplateView:
    platform: Party
    comment: str


interface SimpleTemplateInterface(view=SimpleTemplateView):
    @choice(controller=actors, consuming="nonconsuming")
    def interface_test(self, actors: list[Party]) -> bool:
        pass