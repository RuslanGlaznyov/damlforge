import pytest

from forge.utils import daml_choice_name


@pytest.mark.parametrize(
    "name,expected",
    [("mint", "Mint"), ("do_mint", "Do_mint"), ("FundingCampaign_Pause", "FundingCampaign_Pause")],
)
def test_daml_choice_name(name, expected):
    assert daml_choice_name(name) == expected
