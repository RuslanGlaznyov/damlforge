from datetime import datetime
from typing import Annotated

from forge.models import choice, ContractId, Optional, Party, template
from forge.builtins import DamlName, no_derive
from Splice.Amulet import Amulet
from Splice.AmuletRules import PaymentTransferContext, TransferInput
from Splice.DecentralizedSynchronizer import MemberTraffic


struct BuyTrafficRequestTrackingInfo:
    tracking_id: Annotated[str, DamlName("trackingId")]
    end_user_party: Annotated[Party, DamlName("endUserParty")]


@no_derive
struct BuyTrafficRequest_CompleteResult:
    purchased_traffic: Annotated[ContractId[MemberTraffic], DamlName("purchasedTraffic")]
    tracking_info: Annotated[BuyTrafficRequestTrackingInfo, DamlName("trackingInfo")]
    sender_change_amulet: Annotated[Optional[ContractId[Amulet]], DamlName("senderChangeAmulet")]


@no_derive
struct BuyTrafficRequest_CancelResult:
    tracking_info: Annotated[BuyTrafficRequestTrackingInfo, DamlName("trackingInfo")]


@no_derive
struct BuyTrafficRequest_ExpireResult:
    tracking_info: Annotated[BuyTrafficRequestTrackingInfo, DamlName("trackingInfo")]


@template
class BuyTrafficRequest:
    dso: Party
    end_user_party: Annotated[Party, DamlName("endUserParty")]
    expires_at: Annotated[datetime, DamlName("expiresAt")]
    tracking_id: Annotated[str, DamlName("trackingId")]
    traffic_amount: Annotated[int, DamlName("trafficAmount")]
    member_id: Annotated[str, DamlName("memberId")]
    synchronizer_id: Annotated[str, DamlName("synchronizerId")]
    migration_id: Annotated[int, DamlName("migrationId")]

    signatory: list[Party] = [end_user_party]

    @choice(controller=[end_user_party, wallet_provider], consuming=True)
    def BuyTrafficRequest_Complete(self, inputs: list[TransferInput], context: PaymentTransferContext, wallet_provider: Annotated[Party, DamlName("walletProvider")]) -> BuyTrafficRequest_CompleteResult:
        pass

    @choice(controller=end_user_party, consuming=True)
    def BuyTrafficRequest_Cancel(self, reason: str) -> BuyTrafficRequest_CancelResult:
        pass

    @choice(controller=end_user_party, consuming=True)
    def BuyTrafficRequest_Expire(self) -> BuyTrafficRequest_ExpireResult:
        pass
