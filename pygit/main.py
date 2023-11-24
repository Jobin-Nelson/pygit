from pathlib import Path
from typing import Sequence
import argparse
import logging
import zlib

logging.basicConfig(
    format="[%(asctime)s] %(levelname)s - %(message)s",
    level=logging.INFO,
)

logger = logging.getLogger(__name__)


class Git:
    def __init__(self):
        self.git_dir = Path.cwd().resolve() / ".git"
        self.obj_dir = self.git_dir / "objects"
        self.refs_dir = self.git_dir / "refs"
        self.head = self.git_dir / "HEAD"

    def init(self, args: argparse.Namespace) -> None:
        logger.debug("inside init function")
        if args.bare:
            raise NotImplementedError()

        self.obj_dir.mkdir(parents=True, exist_ok=True)
        self.refs_dir.mkdir(parents=True, exist_ok=True)
        self.head.write_text("ref: refs/heads/master\n")

        logger.info(f"Initialized git directory {self.git_dir}")

    def cat_file(self, args: argparse.Namespace) -> None:
        logger.debug("inside cat_file function")
        obj: Path = self.obj_dir / args.obj[:2] / args.obj[2:]
        with open(obj, mode="rb", buffering=0) as f:
            header, content = zlib.decompress(f.read()).split(b"\x00", 1)
            if args.p:
                print(content.decode("utf-8"), end="")
            elif args.t:
                print(header.split()[0].decode("utf-8"))
            elif args.s:
                print(header.split()[1].decode("utf-8"))


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    subparser = parser.add_subparsers()

    my_git = Git()
    parser_init = subparser.add_parser("init", help="Initialize a git directory")
    parser_init.add_argument(
        "--bare", action="store_true", help="Initialize a bare git directory"
    )
    parser_init.set_defaults(func=my_git.init)

    parser_cat_file = subparser.add_parser(
        "cat-file", help="Check object existence or emit object contents"
    )
    parser_cat_file.add_argument("obj", help="Object to operate on")
    parser_cat_file.add_argument(
        "-p", action="store_true", help="Pretty-print object content"
    )
    parser_cat_file.add_argument("-t", action="store_true", help="Show object type")
    parser_cat_file.add_argument("-s", action="store_true", help="Show object size")
    parser_cat_file.set_defaults(func=my_git.cat_file)

    args = parser.parse_args(argv)
    args.func(args)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
