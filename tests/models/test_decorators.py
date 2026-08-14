import pytest

from forge.models import choice, ledger_effect, view


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
    assert archive_holding.__choice__.consuming is False


@pytest.mark.parametrize(
    "kwargs",
    [
        {"controller": "owner", "consuming": "True"},
        {"controller": "owner", "consuming": 1},
        {"controller": "owner"},
    ],
)
def test_choice_rejects_non_bool_or_missing_consuming(kwargs):
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
