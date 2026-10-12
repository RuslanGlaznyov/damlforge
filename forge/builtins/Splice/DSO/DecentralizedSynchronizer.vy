from datetime import datetime
from typing import Annotated

from forge.models import GenMap, Optional, variant
from forge.builtins import DamlName
from Splice.CometBft import CometBftConfig, CometBftConfigLimits


PhysicalSynchronizerNodeConfigMap = GenMap[int, PhysicalSynchronizerNodeConfig]


SynchronizerNodeConfigMap = GenMap[str, SynchronizerNodeConfig]


@variant
class SynchronizerState:
    def DS_Bootstrapping(): pass
    def DS_Operational(): pass
    def DS_Decomissioned(): pass
    def ExtSynchronizerState(): pass


struct DsoDecentralizedSynchronizerConfig:
    synchronizers: GenMap[str, SynchronizerConfig]
    last_synchronizer_id: Annotated[str, DamlName("lastSynchronizerId")]
    active_synchronizer_id: Annotated[str, DamlName("activeSynchronizerId")]


struct SynchronizerConfig:
    state: SynchronizerState
    comet_bft_genesis_json: Annotated[str, DamlName("cometBftGenesisJson")]
    acs_commitment_reconciliation_interval: Annotated[Optional[int], DamlName("acsCommitmentReconciliationInterval")]


struct SequencerIdentityConfig:
    sequencer_id: Annotated[str, DamlName("sequencerId")]
    available_after: Annotated[Optional[datetime], DamlName("availableAfter")]


struct SequencerConnectionConfig:
    url: str


struct SequencerConfig:
    migration_id: Annotated[int, DamlName("migrationId")]
    sequencer_id: Annotated[str, DamlName("sequencerId")]
    url: str
    available_after: Annotated[Optional[datetime], DamlName("availableAfter")]


struct LegacySequencerConfig:
    migration_id: Annotated[int, DamlName("migrationId")]
    sequencer_id: Annotated[str, DamlName("sequencerId")]
    url: str


struct MediatorConfig:
    mediator_id: Annotated[str, DamlName("mediatorId")]


struct ScanConfig:
    public_url: Annotated[str, DamlName("publicUrl")]


struct PhysicalSynchronizerNodeConfig:
    sequencer: Optional[SequencerConnectionConfig]


struct SynchronizerNodeConfig:
    comet_bft: Annotated[CometBftConfig, DamlName("cometBft")]
    sequencer: Optional[SequencerConfig]
    mediator: Optional[MediatorConfig]
    scan: Optional[ScanConfig]
    legacy_sequencer_config: Annotated[Optional[LegacySequencerConfig], DamlName("legacySequencerConfig")]
    sequencer_identity: Annotated[Optional[SequencerIdentityConfig], DamlName("sequencerIdentity")]
    physical_synchronizers: Annotated[Optional[GenMap[int, PhysicalSynchronizerNodeConfig]], DamlName("physicalSynchronizers")]


struct SynchronizerNodeConfigLimits:
    comet_bft: Annotated[CometBftConfigLimits, DamlName("cometBft")]


@DamlName("noSynchronizerNodes")
def no_synchronizer_nodes() -> GenMap[str, SynchronizerNodeConfig]:
    pass


@DamlName("emptySynchronizerNodeConfig")
def empty_synchronizer_node_config() -> SynchronizerNodeConfig:
    pass


@DamlName("validSynchronizerNodeConfig")
def valid_synchronizer_node_config(limits: SynchronizerNodeConfigLimits, config: SynchronizerNodeConfig) -> bool:
    pass


@DamlName("defaultSynchronizerNodeConfigLimits")
def default_synchronizer_node_config_limits() -> SynchronizerNodeConfigLimits:
    pass
