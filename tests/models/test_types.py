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

from decimal import Decimal as PyDecimal

from forge.models import ContractId, Decimal, GenMap, Int, Party, TextMap


def test_party_wraps_and_returns_underlying_value():
    assert Party("Alice") == "Alice"


def test_int_wraps_and_returns_underlying_value():
    assert Int(5) == 5


def test_decimal_is_python_decimal():
    assert Decimal is PyDecimal


def test_contract_id_is_subscriptable_with_a_template_type():
    class Asset:
        pass

    assert ContractId[Asset] is not None


def test_text_map_is_subscriptable():
    assert TextMap[int] is not None


def test_gen_map_is_subscriptable():
    assert GenMap[str, int] is not None
