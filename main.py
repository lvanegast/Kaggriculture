"""Main entry point for Kaggriculture CLI."""

import sys
from scripts.arena import main as arena_main
from scripts.build_submission import main as build_main


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "build":
        sys.argv.pop(1)
        build_main()
    else:
        if len(sys.argv) > 1 and sys.argv[1] == "arena":
            sys.argv.pop(1)
        arena_main()


if __name__ == "__main__":
    main()
