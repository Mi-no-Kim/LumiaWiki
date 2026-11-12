"""Read-only project skill/hook inventory check for work, index or a commit."""

import sys
sys.dont_write_bytecode = True

import argparse
import json
import subprocess
import harness_inventory as inventory


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--candidate', default='index')
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--describe', action='store_true', help='Print actual source paths/digests; never writes')
    mode.add_argument('--render', action='store_true', help='Print the summary table; never writes')
    args = parser.parse_args()
    try:
        value = inventory.inspect(inventory.Candidate(args.candidate), args.describe, args.render)
        if value is not None:
            print(json.dumps(value, ensure_ascii=False, indent=2) if args.describe else value)
        return 0
    except (ValueError, OSError, KeyError, TypeError, UnicodeError, subprocess.SubprocessError) as error:
        reason = str(error).splitlines()[0][:1000]
        print('Inventory unverified: ' + reason + '\nNext: update the matching inventory entry and stage the exact verified candidate.', file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
