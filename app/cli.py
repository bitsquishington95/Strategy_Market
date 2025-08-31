import argparse
import sys
from typing import List, Optional

from app.engine.qa import answer_query, format_answers
from app.repository.store import load_repository


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="CEO Knowledgebase CLI")
    sub = parser.add_subparsers(dest="cmd", required=True)

    ask = sub.add_parser("ask", help="Ask a question against the knowledgebase")
    ask.add_argument("query", type=str, help="Your question or situation")
    ask.add_argument(
        "--ceo",
        action="append",
        help="Limit to a specific CEO (repeatable). Example: --ceo 'Steve Jobs'",
    )
    ask.add_argument("--top-k", type=int, default=3, help="Number of answers to return")

    args = parser.parse_args(argv)

    repo = load_repository()

    if args.cmd == "ask":
        results = answer_query(args.query, repo, ceo_filters=args.ceo, top_k=args.top_k)
        print(format_answers(results))
        return 0

    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())


