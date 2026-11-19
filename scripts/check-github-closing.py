"""Check final messages or every incoming commit for Issue-closing references."""

import sys
sys.dont_write_bytecode = True

from github_closing import main

if __name__ == '__main__':
    raise SystemExit(main())
