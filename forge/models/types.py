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

from typing import Generic, NewType, TypeVar

from forge.builtins.maps import GenMap, TextMap

__all__ = ("GenMap", "TextMap", "Party", "Text", "Int", "ContractId")

Party = NewType("Party", str)
Text = NewType("Text", str)
Int = NewType("Int", int)

T = TypeVar("T")


class ContractId(Generic[T]):
    pass
