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

from forge.utils import daml_choice_name


@pytest.mark.parametrize(
    "name,expected",
    [("mint", "Mint"), ("do_mint", "Do_mint"), ("FundingCampaign_Pause", "FundingCampaign_Pause")],
)
def test_daml_choice_name(name, expected):
    assert daml_choice_name(name) == expected
