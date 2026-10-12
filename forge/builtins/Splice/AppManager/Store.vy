from typing import Annotated

from forge.models import Party, template
from forge.builtins import DamlName


@template
class AppConfiguration:
    validator_operator: Annotated[Party, DamlName("validatorOperator")]
    provider: Party
    version: int
    json: str

    signatory: list[Party] = [validator_operator]


@template
class AppRelease:
    validator_operator: Annotated[Party, DamlName("validatorOperator")]
    provider: Party
    version: str
    json: str

    signatory: list[Party] = [validator_operator]


@template
class RegisteredApp:
    validator_operator: Annotated[Party, DamlName("validatorOperator")]
    provider: Party

    signatory: list[Party] = [validator_operator]


@template
class InstalledApp:
    validator_operator: Annotated[Party, DamlName("validatorOperator")]
    provider: Party
    app_url: Annotated[str, DamlName("appUrl")]

    signatory: list[Party] = [validator_operator]


@template
class ApprovedReleaseConfiguration:
    validator_operator: Annotated[Party, DamlName("validatorOperator")]
    provider: Party
    configuration_version: Annotated[int, DamlName("configurationVersion")]
    json: str
    json_hash: Annotated[str, DamlName("jsonHash")]

    signatory: list[Party] = [validator_operator]
