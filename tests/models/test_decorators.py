import pytest

from forge.models import Consuming, choice, ledger_effect, view


def test_choice_preserves_function_behavior():
    @choice(controller="owner", consuming=True)
    def transfer(new_owner):
        return new_owner

    assert transfer("alice") == "alice"


def test_choice_attaches_inspectable_metadata():
    @choice(controller="owner", consuming=False)
    def archive_holding():
        pass

    assert archive_holding.__choice__.controller == "owner"
    assert archive_holding.__choice__.consuming is Consuming.NON_CONSUMING


@pytest.mark.parametrize(
    "consuming,expected",
    [
        (True, Consuming.CONSUMING),
        (False, Consuming.NON_CONSUMING),
        ("consuming", Consuming.CONSUMING),
        ("nonconsuming", Consuming.NON_CONSUMING),
        ("preconsuming", Consuming.PRE_CONSUMING),
        ("postconsuming", Consuming.POST_CONSUMING),
        (Consuming.PRE_CONSUMING, Consuming.PRE_CONSUMING),
        (Consuming.POST_CONSUMING, Consuming.POST_CONSUMING),
    ],
)
def test_choice_accepts_all_four_daml_consuming_modes(consuming, expected):
    @choice(controller="owner", consuming=consuming)
    def transfer(new_owner):
        pass

    assert transfer.__choice__.consuming is expected


def test_choice_accepts_optional_observer():
    @choice(controller="owner", consuming=True, observer="issuer")
    def transfer(new_owner):
        pass

    assert transfer.__choice__.observer == "issuer"


def test_choice_observer_defaults_to_none():
    @choice(controller="owner", consuming=True)
    def transfer(new_owner):
        pass

    assert transfer.__choice__.observer is None


@pytest.mark.parametrize(
    "kwargs",
    [
        {"controller": "owner", "consuming": "True"},
        {"controller": "owner", "consuming": 1},
        {"controller": "owner"},
    ],
)
def test_choice_rejects_invalid_or_missing_consuming(kwargs):
    with pytest.raises(TypeError):
        choice(**kwargs)


@pytest.mark.parametrize("decorator", [ledger_effect, view])
def test_bare_marker_decorators_preserve_function_behavior(decorator):
    @decorator
    def fn(x):
        return x * 2

    assert fn(3) == 6


def test_ledger_effect_marks_function():
    @ledger_effect
    def replace():
        pass

    assert replace.__ledger_effect__ is True


def test_view_marks_function():
    @view
    def get_view():
        pass

    assert get_view.__view__ is True
