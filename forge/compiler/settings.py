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

import dataclasses
import os
from dataclasses import dataclass
from enum import Enum
from typing import Optional

VYPER_ERROR_CONTEXT_LINES = int(os.environ.get("VYPER_ERROR_CONTEXT_LINES", "1"))
VYPER_ERROR_LINE_NUMBERS = os.environ.get("VYPER_ERROR_LINE_NUMBERS", "1") == "1"


class OptimizationLevel(Enum):
    NONE = 1
    GAS = 2
    CODESIZE = 3
    O2 = 6
    O3 = 7
    Os = 8

    @classmethod
    def from_string(cls, val):
        match val:
            case "none":
                return cls.NONE
            case "O1" | "O2" | "gas":
                return cls.GAS
            case "codesize" | "Os":
                return cls.CODESIZE
            case "O3" | "o3":
                return cls.O3
        raise ValueError(f"unrecognized optimization level: {val}")

    @classmethod
    def default(cls):
        return cls.GAS

    def __str__(self):
        return self._name_ if self._name_.startswith("O") else self._name_.lower()


DEFAULT_ENABLE_DECIMALS = False


@dataclass
class Settings:
    compiler_version: Optional[str] = None
    optimize: Optional[OptimizationLevel] = None
    enable_decimals: Optional[bool] = None
    nonreentrancy_by_default: Optional[bool] = None

    def __post_init__(self):
        if self.optimize is not None:
            assert isinstance(self.optimize, OptimizationLevel)
        if self.enable_decimals is not None:
            assert isinstance(self.enable_decimals, bool)
        if self.nonreentrancy_by_default is not None:
            assert isinstance(self.nonreentrancy_by_default, bool)

    def as_dict(self):
        ret = {}
        for field in dataclasses.fields(self):
            value = getattr(self, field.name)
            if value is None:
                continue
            if field.name == "compiler_version":
                continue
            if field.name == "optimize":
                ret["optimize"] = str(value)
            else:
                ret[field.name] = value
        return ret

    @classmethod
    def from_dict(cls, data):
        data = data.copy()
        if "optimize" in data:
            data["optimize"] = OptimizationLevel.from_string(data["optimize"])
        return cls(**data)
