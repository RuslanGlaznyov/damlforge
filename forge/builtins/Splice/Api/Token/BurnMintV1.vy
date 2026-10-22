from typing import Annotated

from forge.models import choice, ContractId, Decimal, Party
from forge.builtins import DamlName
from Splice.Api.Token.HoldingV1 import Holding, InstrumentId
from Splice.Api.Token.MetadataV1 import ChoiceContext, ExtraArgs, Metadata


struct BurnMintFactoryView:
    admin: Party
    meta: Metadata


struct BurnMintFactory_BurnMintResult:
    output_cids: Annotated[list[ContractId[Holding]], DamlName("outputCids")]


struct BurnMintOutput:
    owner: Party
    amount: Decimal
    context: ChoiceContext


interface BurnMintFactory(view=BurnMintFactoryView):
    @choice(controller=actor, consuming="nonconsuming")
    def BurnMintFactory_PublicFetch(self, expected_admin: Annotated[Party, DamlName("expectedAdmin")], actor: Party) -> BurnMintFactoryView:
        pass

    @choice(controller=extra_actors + [view.admin], consuming="nonconsuming")
    def BurnMintFactory_BurnMint(self, expected_admin: Annotated[Party, DamlName("expectedAdmin")], instrument_id: Annotated[InstrumentId, DamlName("instrumentId")], input_holding_cids: Annotated[list[ContractId[Holding]], DamlName("inputHoldingCids")], outputs: list[BurnMintOutput], extra_actors: Annotated[list[Party], DamlName("extraActors")], extra_args: Annotated[ExtraArgs, DamlName("extraArgs")]) -> BurnMintFactory_BurnMintResult:
        pass


@DamlName("burnMintFactory_burnMintImpl", is_ledger_effect=True)
def burn_mint_factory_burn_mint_impl(i: BurnMintFactory, contract_id: ContractId[BurnMintFactory], burn_mint_factory_burn_mint: BurnMintFactory_BurnMint) -> BurnMintFactory_BurnMintResult:
    pass


@DamlName("burnMintFactory_publicFetchImpl", is_ledger_effect=True)
def burn_mint_factory_public_fetch_impl(i: BurnMintFactory, contract_id: ContractId[BurnMintFactory], burn_mint_factory_public_fetch: BurnMintFactory_PublicFetch) -> BurnMintFactoryView:
    pass
