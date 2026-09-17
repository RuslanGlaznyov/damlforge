#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
import sys

from forge.cli import forge_daml, forge_dar, forge_json

if __name__ == "__main__":
    allowed_subcommands = {"--daml": forge_daml, "--dar": forge_dar, "--json": forge_json}

    if len(sys.argv) <= 1 or sys.argv[1] not in allowed_subcommands:
        # default (no args, no switch in first arg): compile .vy -> .daml
        forge_daml._parse_cli_args()
    else:
        # pop switch and forward args to subcommand
        subcommand = sys.argv.pop(1)
        allowed_subcommands[subcommand]._parse_cli_args()
