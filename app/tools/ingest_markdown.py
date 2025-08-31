import argparse
import json
import os
from typing import Any, Dict, List, Optional

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
DATA_DIR = os.path.join(ROOT_DIR, "data")
REPO_JSON = os.path.join(DATA_DIR, "repository.json")


def load_text(path: str) -> str:
	with open(path, "r", encoding="utf-8") as f:
		return f.read()


def load_repo() -> Dict[str, Any]:
	with open(REPO_JSON, "r", encoding="utf-8") as f:
		return json.load(f)


def save_repo(repo: Dict[str, Any]) -> None:
	with open(REPO_JSON, "w", encoding="utf-8") as f:
		json.dump(repo, f, ensure_ascii=False, indent=2)


def _has_situation(repo: Dict[str, Any], ceo: str, title: str) -> bool:
	for s in repo.get("situations", []):
		if s.get("ceo") == ceo and s.get("title") == title:
			return True
	return False


def append_situation(repo: Dict[str, Any], ceo: str, title: str, response: str, tags: List[str]) -> None:
	if _has_situation(repo, ceo, title):
		return
	repo.setdefault("situations", []).append({
		"ceo": ceo,
		"title": title,
		"response": response,
		"tags": tags,
	})


def ingest_from_markdown(md_text: str, repo: Dict[str, Any]) -> int:
	"""
	Heuristic extraction for the provided research structure.
	Currently supports Steve Jobs and Jeff Bezos from the report.
	"""
	added = 0
	lower = md_text.lower()

	if "steve jobs" in lower:
		append_situation(
			repo,
			"Steve Jobs",
			"Reality Distortion Field (RDF)",
			"Use charismatic reframing to make teams believe ambitious timelines are possible; set stretch goals that reset perceived constraints.",
			["psychology:rdf", "situation:stretch_goal", "situation:product_crunch"],
		)
		added += 1
		append_situation(
			repo,
			"Steve Jobs",
			"The Filter: ruthless simplification",
			"Collapse diffuse portfolios into a few bets; centralize decision criteria around taste and product clarity.",
			["principle:focus", "situation:turnaround", "situation:product_portfolio"],
		)
		added += 1
		append_situation(
			repo,
			"Steve Jobs",
			"Keynote as vision casting",
			"Use theatrical presentations, simple narratives, and iconic reveals to enroll customers and align the org.",
			["situation:product_launch", "situation:media_interview", "principle:storytelling"],
		)
		added += 1

	if "jeff bezos" in lower or "bezos" in lower:
		append_situation(
			repo,
			"Jeff Bezos",
			"Day 1 mindset",
			"Maintain perpetual startup urgency; frame Day 2 as stasis and decline to sustain long-term focus.",
			["principle:day1", "situation:strategy_refresh", "situation:org_culture"],
		)
		added += 1
		append_situation(
			repo,
			"Jeff Bezos",
			"Six-page memos and two-pizza teams",
			"Replace slides with narrative memos; keep teams small and autonomous to force ownership and clarity.",
			["principle:operating_system", "situation:exec_meeting", "situation:team_structure"],
		)
		added += 1
		append_situation(
			repo,
			"Jeff Bezos",
			"Regret Minimization Framework",
			"Make big career and investment decisions by minimizing lifetime regret and embracing bold attempts.",
			["principle:decision_framework", "situation:career_decision", "situation:big_bet"],
		)
		added += 1

	return added


def main(argv: Optional[List[str]] = None) -> int:
	parser = argparse.ArgumentParser(description="Ingest research markdown into repository.json")
	parser.add_argument("--input", required=True, help="Path to markdown file")
	args = parser.parse_args(argv)

	md_path = args.input
	if not os.path.isabs(md_path):
		md_path = os.path.join(ROOT_DIR, md_path)

	if not os.path.exists(md_path):
		print(f"Input file not found: {md_path}")
		return 2

	repo = load_repo()
	md_text = load_text(md_path)
	added = ingest_from_markdown(md_text, repo)
	save_repo(repo)
	print(f"Added {added} items from {os.path.basename(md_path)}.")
	return 0


if __name__ == "__main__":
	raise SystemExit(main())
