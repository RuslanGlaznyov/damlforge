# Copyright 2026 Noders Team
# Author: Artem Bogomaz <artembogomaz@gmail.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import pytest

from forge.ast.parse import parse_to_ast
from forge.codegen import generate_daml
from forge.daml_versions import DamlCodegenSettings
from forge.ir import lower_module
from forge.models.error_codes import ErrorCodes
from forge.semantics import analyze_module

_SOURCE = """
from typing import Optional

from forge.builtins.daml_lang import exercise_by_key, fetch_by_key, lookup_n_by_key
from forge.models import ContractId, Party, choice, template


struct AccountKey:
    bank: Party
    number: str


@template
class Account:
    bank: Party
    number: str

    signatory: Party = bank
    key: KEY
    maintainer: MAINTAINER

    @choice(controller=bank, consuming="nonconsuming")
    def GetBank(self) -> Party:
        return self.bank

    @choice(controller=bank, consuming="nonconsuming")
    def Probe(self) -> RETURNS:
        BODY
"""

_TUPLE_KEY = ("tuple[Party, str] = (bank, number)", "Party = key[0]")


def _compile(key=_TUPLE_KEY, returns="bool", body="return True", settings=None):
    source = (
        _SOURCE.replace("KEY", key[0])
        .replace("MAINTAINER", key[1])
        .replace("RETURNS", returns)
        .replace("BODY", body)
    )
    module = parse_to_ast(source, module_path="Account.vy", resolved_path="Account.vy")
    analyze_module(module)
    settings = settings or DamlCodegenSettings("3.5.2", ("--target=2.3",))
    return generate_daml(lower_module(module), settings=settings)[0]


@pytest.mark.parametrize(
    "key,returns,body,expected",
    [
        (
            _TUPLE_KEY,
            "bool",
            "return True",
            ["key (bank, number) : (Party, Text)", "maintainer key._1"],
        ),
        (("Party = bank", "list[Party] = [key]"), "bool", "return True", ["key bank : Party"]),
        (
            ("AccountKey = AccountKey(bank=bank, number=number)", "Party = key.bank"),
            "bool",
            "return True",
            ["key (AccountKey with bank = bank, number = number) : AccountKey"],
        ),
        (
            _TUPLE_KEY,
            "Party",
            "pair: tuple[ContractId[Account], Account] = fetch_by_key((self.bank, self.number))\n"
            "        return pair[1].bank",
            ["(pair : (ContractId Account, Account)) <- fetchByKey (self.bank, self.number)"],
        ),
        (
            _TUPLE_KEY,
            "int",
            "rows: list[tuple[ContractId[Account], Account]] = "
            "lookup_n_by_key(1, (self.bank, self.number))\n"
            "        return len(rows)",
            ["import DA.ContractKeys", "lookupNByKey 1 (self.bank, self.number)"],
        ),
        (
            _TUPLE_KEY,
            "Optional[Party]",
            "return exercise_by_key(Account, (self.bank, self.number), Account.GetBank())",
            ["exerciseByKey @Account (self.bank, self.number) (GetBank)", "pure (Some "],
        ),
    ],
    ids=["tuple-key", "party-key", "record-key", "fetch", "lookup-n", "exercise"],
)
def test_contract_key_generates_daml(key, returns, body, expected):
    daml = _compile(key, returns, body)

    assert all(fragment in daml for fragment in expected)


@pytest.mark.parametrize(
    "settings,error",
    [
        (DamlCodegenSettings(), None),
        (DamlCodegenSettings("3.5.2"), "not the default"),
        (DamlCodegenSettings("3.4.11", ("--target=2.3",)), "does not support them"),
    ],
    ids=["no-project", "default-target", "sdk-3.4"],
)
def test_contract_key_requires_supporting_sdk_and_target(settings, error):
    if error is None:
        assert "maintainer key._1" in _compile(settings=settings)
        return
    with pytest.raises(Exception, match=error) as exc_info:
        _compile(settings=settings)
    assert ErrorCodes.DF1234.value in str(exc_info.value)
