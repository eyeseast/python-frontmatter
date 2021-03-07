#!/usr/bin/env python
"""
Generate result files for test content. Won't overwrite any that exit.
"""
import json
from pathlib import Path

import frontmatter
from test_files import files, get_result_filename


def main():
    for path in files():
        result = Path(get_result_filename(path))
        if not result.exists():
            post = frontmatter.loads(path.read_text())
            result.write_text(json.dumps(post.to_dict(), indent=2), "utf-8")


if __name__ == "__main__":
    main()