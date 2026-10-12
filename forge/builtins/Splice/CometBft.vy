from typing import Annotated

from forge.models import GenMap
from forge.builtins import DamlName


struct CometBftNodeConfig:
    validator_pub_key: Annotated[str, DamlName("validatorPubKey")]
    voting_power: Annotated[int, DamlName("votingPower")]


struct GovernanceKeyConfig:
    pub_key: Annotated[str, DamlName("pubKey")]


struct SequencingKeyConfig:
    pub_key: Annotated[str, DamlName("pubKey")]


struct CometBftConfig:
    nodes: GenMap[str, CometBftNodeConfig]
    governance_keys: Annotated[list[GovernanceKeyConfig], DamlName("governanceKeys")]
    sequencing_keys: Annotated[list[SequencingKeyConfig], DamlName("sequencingKeys")]


struct CometBftConfigLimits:
    max_num_comet_bft_nodes: Annotated[int, DamlName("maxNumCometBftNodes")]
    max_num_governance_keys: Annotated[int, DamlName("maxNumGovernanceKeys")]
    max_num_sequencing_keys: Annotated[int, DamlName("maxNumSequencingKeys")]
    max_node_id_length: Annotated[int, DamlName("maxNodeIdLength")]
    max_pub_key_length: Annotated[int, DamlName("maxPubKeyLength")]


@DamlName("emptyCometBftConfig")
def empty_comet_bft_config() -> CometBftConfig:
    pass


@DamlName("defaultCometBftConfigLimits")
def default_comet_bft_config_limits() -> CometBftConfigLimits:
    pass


@DamlName("validCometBftConfig")
def valid_comet_bft_config(limits: CometBftConfigLimits, config: CometBftConfig) -> bool:
    pass


@DamlName("validCometBftNodeConfig")
def valid_comet_bft_node_config(limits: CometBftConfigLimits, tuple_value: tuple[str, CometBftNodeConfig]) -> bool:
    pass


@DamlName("totalVotingPower")
def total_voting_power(config: CometBftConfig) -> int:
    pass
