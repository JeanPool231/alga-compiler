#!/usr/bin/env python3

import argparse
import sys
import os

from antlr4 import FileStream

from main import compilar
from vm import VM, AlgaRuntimeError
from vm.values import fmt_value


def run_source(stream, output=print, max_steps=5_000_000, base_dir=None):
    result, tac = compilar(stream, base_dir=base_dir)

    if result["errors"]:
        for error in result["errors"]:
            print(error, file=sys.stderr)
        return 1, None

    machine = VM(tac, output=output, max_steps=max_steps)

    try:
        machine.run()
    except AlgaRuntimeError as error:
        print(error, file=sys.stderr)
        return 1, machine

    return 0, machine


def main(argv=None):
    cli = argparse.ArgumentParser(description="Alga interpreter")

    cli.add_argument("file")
    cli.add_argument(
        "--dump", action="store_true", help="show memory variables at exit"
    )
    cli.add_argument(
        "--max-steps",
        type=int,
        default=5_000_000,
        metavar="N",
        help="max stack depth (def: 5000000)",
    )

    args = cli.parse_args(argv)

    try:
        stream = FileStream(args.file, encoding="utf-8")
    except (OSError, UnicodeError) as error:
        print(f"could not read {args.file}: {error}", file=sys.stderr)
        return 2
    base_dir = os.path.dirname(os.path.abspath(args.file))
    code, machine = run_source(stream, max_steps=args.max_steps, base_dir=base_dir)

    if args.dump and machine is not None:
        print("variables: ")
        for name, value in machine.variables().items():
            print(f"{name} = {fmt_value(value, multiline=False)}")

    return code


if __name__ == "__main__":
    sys.exit(main())
