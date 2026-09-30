from datetime import datetime
from typing import Optional

from forge.builtins import DamlName
from forge.builtins.daml_lang import exercise
from forge.models import ContractId, Party, choice, template
from Splice.Amulet import Amulet
from Splice.AmuletRules import (
    AmuletRules_BuyMemberTraffic,
    PaymentTransferContext,
    TransferInput,
)
from Splice.DecentralizedSynchronizer import MemberTraffic


struct BuyTrafficRequestTrackingInfo:
    trackingId: str
    endUserParty: Party


struct BuyTrafficRequest_CompleteResult:
    purchasedTraffic: ContractId[MemberTraffic]
    trackingInfo: BuyTrafficRequestTrackingInfo
    senderChangeAmulet: Optional[ContractId[Amulet]]


struct BuyTrafficRequest_CancelResult:
    trackingInfo: BuyTrafficRequestTrackingInfo


struct BuyTrafficRequest_ExpireResult:
    trackingInfo: BuyTrafficRequestTrackingInfo


@template
class BuyTrafficRequest:
    dso: Party
    endUserParty: Party
    expiresAt: datetime
    trackingId: str
    trafficAmount: int
    memberId: str
    synchronizerId: str
    migrationId: int

    signatory: Party = endUserParty

    @DamlName("BuyTrafficRequest_Complete")
    @choice(controller=[endUserParty, walletProvider], consuming=True)
    def complete(
        self,
        inputs: list[TransferInput],
        context: PaymentTransferContext,
        walletProvider: Party,
    ) -> BuyTrafficRequest_CompleteResult:
        now = datetime.now()
        assert now < self.expiresAt, "BuyTrafficRequest has not expired"
        result = exercise(
            context.amulet_rules,
            AmuletRules_BuyMemberTraffic(
                inputs=inputs,
                context=context.context,
                provider=walletProvider,
                member_id=self.memberId,
                synchronizer_id=self.synchronizerId,
                migration_id=self.migrationId,
                traffic_amount=self.trafficAmount,
                expected_dso=self.dso,
            ),
        )
        return BuyTrafficRequest_CompleteResult(
            purchasedTraffic=result.purchased_traffic,
            trackingInfo=BuyTrafficRequestTrackingInfo(
                trackingId=self.trackingId, endUserParty=self.endUserParty
            ),
            senderChangeAmulet=result.sender_change_amulet,
        )

    @DamlName("BuyTrafficRequest_Cancel")
    @choice(controller=endUserParty, consuming=True)
    def cancel(self, reason: str) -> BuyTrafficRequest_CancelResult:
        now = datetime.now()
        assert now < self.expiresAt, "BuyTrafficRequest has not expired"
        return BuyTrafficRequest_CancelResult(
            trackingInfo=BuyTrafficRequestTrackingInfo(
                trackingId=self.trackingId, endUserParty=self.endUserParty
            )
        )

    @DamlName("BuyTrafficRequest_Expire")
    @choice(controller=endUserParty, consuming=True)
    def expire(self) -> BuyTrafficRequest_ExpireResult:
        now = datetime.now()
        assert self.expiresAt <= now, "BuyTrafficRequest has expired"
        return BuyTrafficRequest_ExpireResult(
            trackingInfo=BuyTrafficRequestTrackingInfo(
                trackingId=self.trackingId, endUserParty=self.endUserParty
            )
        )
