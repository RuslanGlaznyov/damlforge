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

from forge.models import exception, interface, template, variant


def test_template_preserves_class_identity():
    @template
    class Asset:
        pass

    assert Asset.__name__ == "Asset"


def test_template_marks_class():
    @template
    class Asset:
        pass

    assert Asset.__template__ is True


def test_variant_marks_class():
    @variant
    class Result:
        pass

    assert Result.__variant__ is True


def test_interface_marks_class_with_view_type():
    class HoldingView:
        pass

    @interface(view=HoldingView)
    class Holding:
        pass

    assert Holding.__interface__.view is HoldingView


def test_interface_marks_class_with_required_interfaces():
    class MyInterface:
        pass

    class YourInterface:
        pass

    class HoldingView:
        pass

    @interface(view=HoldingView, requires=(MyInterface, YourInterface))
    class OurInterface:
        pass

    assert OurInterface.__interface__.requires == (MyInterface, YourInterface)


def test_interface_requires_defaults_to_empty_tuple():
    class HoldingView:
        pass

    @interface(view=HoldingView)
    class Holding:
        pass

    assert Holding.__interface__.requires == ()


def test_exception_is_not_supported_yet():
    with pytest.raises(NotImplementedError):

        @exception
        class InsufficientFunds:
            pass
