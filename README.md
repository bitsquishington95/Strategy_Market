# Successful CEOs

A structured, queryable knowledge hub for analyzing CEO decision patterns across 37 fully enriched profiles and 110 situational responses.

## Quickstart (CLI)

1. Create a virtual environment and install dependencies

```powershell
python -m venv .venv
. .venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. Ask questions against the knowledgebase

```powershell
python -m app.cli ask "We missed our quarterly target; how should I address the team?" --top-k 3
python -m app.cli ask "launch failure and PR crisis" --ceo "Steve Jobs"
python -m app.cli ask "hiring philosophy for platform leaders"
```

3. Compare and visualize CEO similarities

```powershell
# Compare a CEO with similar leaders
python -m app.tools.compare_ceos "Elon Musk" --top-k 3

# Generate visualizations
python -m app.tools.visualize_ceos --output visualizations/ceo_clusters.png --type cluster
python -m app.tools.visualize_ceos --output visualizations/ceo_heatmap.png --type heatmap --ceos "Steve Jobs" "Elon Musk" "Jeff Bezos"
```

4. Use the CEO training program

```powershell
# Initialize with a sample trainee
python -m app.training.initialize

# Create your own trainee profile
python -m app.training.cli create "Your Name" "Current Role" "Target CEO Role" --industry "Your Industry"

# Take the skill assessment
python -m app.training.cli assess your_name

# Get a personalized training plan
python -m app.training.cli plan your_name

# Start your first training module
python -m app.training.cli module your_name
```

See [CEO-TRAINING-README.md](CEO-TRAINING-README.md) for complete documentation on the training program.

### Project Structure

- `app/models`: Pydantic models for the schema
- `app/repository`: Repository loader and query functions
- `app/ui`: (Optional) Streamlit UI shell; primary usage is CLI
- `app/engine`: QA engine (ranking + synthesis with fuzzy matching)
- `app/api`: FastAPI service for web UI integration
- `app/db`: Database connection and schema for SQL storage
- `app/training`: CEO training program for skill development
- `app/tools/ingest_csv.py`: Build `data/repository.json` from CSVs
- `app/tools/ingest_markdown.py`: Extract situations from research reports
- `app/tools/compare_ceos.py`: Compare CEOs and find similarities
- `app/tools/visualize_ceos.py`: Generate visualizations of CEO similarities
- `app/tools/migrate_to_db.py`: Migrate data from JSON to SQL database
- `data/repository.json`: Seed data for CEOs and situations
- `data/schema.json`: JSON Schema for validation/reference
- `data/ceos.csv`, `data/situations.csv`: CSV sources for ingestion
- `data/sample_repository.json`: Sample data for testing
- `frontend/`: React frontend for web UI
- `visualizations/`: Generated CEO comparison visualizations

### Knowledgebase Statistics

- **Total CEOs**: 366 (37 fully enriched, 329 placeholders)
- **Total Situations**: 110 across 31 CEOs
- **Industries Represented**: Technology, Retail, Finance, Automotive, Media, Food Service, Manufacturing, and more
- **Top Situation Tags**: competitive_attack (8), product_strategy (5), strategy_refresh (4), talent_management (4)

### Notes
- Tag situations as `situation:*` (e.g., `situation:missed_targets`).
- Extend `repository.json` with more CEOs and situations to enrich results.
- Use fuzzy matching in the QA engine for better query results.

## Data Ingestion from CSV

1. Edit `data/ceos.csv` and `data/situations.csv` (samples below).
2. Build the JSON repository file:

```powershell
python -m app.tools.ingest_csv
```

### Enriched CEOs (37)

1. Steve Jobs
2. Jeff Bezos
3. Satya Nadella
4. Tim Cook
5. Sundar Pichai
6. Elon Musk
7. Jensen Huang
8. Mark Zuckerberg
9. Bill Gates
10. Larry Page
11. Sergey Brin
12. Reed Hastings
13. Andy Grove
14. Marc Benioff
15. Jack Welch
16. Jamie Dimon
17. Sam Walton
18. Howard Schultz
19. Henry Ford
20. John D. Rockefeller
21. Andrew Carnegie
22. Ray Kroc
23. Phil Knight
24. Richard Branson
25. Indra Nooyi
26. Ursula Burns
27. Yvon Chouinard
28. Sara Blakely
29. Oprah Winfrey
30. Tony Hsieh
31. Mary Barra
32. Douglas McMillon
33. Andrew Jassy
34. Darren Woods
35. Timothy Cook
36. Jane Fraser
37. Steve Jobs

### Sample: `data/ceos.csv`

```
name,strategic_philosophy.core_ideology,strategic_philosophy.market_positioning,strategic_philosophy.innovation_engine,strategic_philosophy.competitive_stance,strategic_philosophy.risk_profile,leadership.hiring_philosophy,leadership.cultural_architecture,leadership.motivation_incentives,leadership.communication_style,leadership.talent_management,operational_cadence.meeting_culture,operational_cadence.decision_making_process,operational_cadence.key_metrics,operational_cadence.focus_prioritization,operational_cadence.accountability_framework,personal_ethos.core_principles,personal_ethos.work_ethic,personal_ethos.learning_adaptability,personal_ethos.resilience_mechanism
"Steve Jobs","Build insanely great, integrated products that delight users.","Premium, design-led, end-to-end consumer ecosystem","Secretive, cross-functional teams with rapid prototyping","Confrontational; differentiate through taste and integration","Bold, bet-the-company on a few products","A-players only; passion and intelligence over credentials","High standards; end-to-end ownership; secrecy","Mission-driven excellence; shipping craftsmanship","Keynotes; product reviews; blunt 1:1s","Extreme autonomy for stars; swift exits for underperformance","Small groups; debate; DRI for every outcome","Top-down product taste with data as input","Customer delight, product quality, gross margins","Ruthless focus; kill most projects","DRIs; live demos","Simplicity, taste, end-to-end experience","Hands-on, intense product focus","Observe users; iterate on prototypes","Reframe setbacks into product opportunities"
"Jeff Bezos","Obsess over customers and long-term value creation.","Low-cost, high-convenience platform and cloud infrastructure","Working Backwards (PRFAQ), two-pizza teams, narrative memos","Relentless; compete on speed, selection, price","Calculated big bets with option value","Hire and develop the best; raise the bar","Day 1 culture; frugality; high standards","Ownership mindset; metrics-driven recognition","Narratives over slides; clear, concise writing","Rotate top talent; single-threaded leaders","Short, doc-based meetings; study-hall reading","Disagree and commit; decision velocity","Free cash flow, selection, delivery speed, CSAT","Build flywheels; cut low-ROI distractions","COE; single-thread ownership","Customer obsession, frugality, bias for action","Intense but disciplined; sustainable cadence","Read, write, measure; iterate from data","Learn from metrics; fix processes, not people"
"Elon Musk","Accelerate humanity's transition to sustainable energy and multi-planetary civilization.","Vertically integrated disruptor in auto, energy, and space","First principles thinking; rapid iteration; vertical integration","Disruptive; compete on engineering innovation and cost structure","Existential, bet-the-company on transformative vision","Hire exceptional engineers; no MBAs; first principles thinkers","Hardcore engineering; flat hierarchy; extreme ownership","Mission impact; equity upside; direct contribution to vision","Direct, unfiltered tweets; all-hands; engineering demos","Extreme autonomy for top performers; swift exits for mediocrity","Engineering-focused; data-driven; minimal bureaucracy","CEO as chief engineer; decisive, first principles-based","Production rate, cost per unit, engineering velocity, cash flow","Relentless focus on rate and cost; eliminate distractions","Direct accountability to CEO; public deadlines","Engineering truth; physics-first; sustainability","Extreme work intensity; sleep at factory during crunch","Rapid iteration; learn from failures; physics fundamentals","Face failure directly; pivot fast; double down on first principles"
```

### Sample: `data/situations.csv`

```
ceo,tags,title,response
"Steve Jobs","situation:product_launch_crisis;situation:missed_targets","Address missed targets by refocusing on product","Hold an all-hands, take ownership, and rally around the next great product."
"Jeff Bezos","situation:missed_targets;situation:correction_of_errors","COE: process over blame","Request a written COE doc, fix the process, and reinforce long-term focus."
"Elon Musk","situation:production_crisis;principle:first_principles","Sleep on the factory floor","Relocate to the production line, eliminate constraints through first principles, and drive 24/7 engineering until fixed."
"Bill Gates","situation:competitive_attack;principle:platform_leverage","Platform defense","Strengthen platform integration; accelerate developer tools; leverage ecosystem advantages."
"Warren Buffett","situation:acquisition_opportunity;principle:circle_competence","Circle of competence focus","Evaluate against clear investment criteria; calculate intrinsic value with margin of safety; walk away if uncertain."
```

### Top Situation Tags

1. competitive_attack (8)
2. product_strategy (5)
3. strategy_refresh (4)
4. talent_management (4)
5. operating_system (3)
6. org_restructure (3)
7. regulatory_pressure (3)
8. supply_chain_shock (3)
9. frugality (3)
10. product_launch_crisis (3)

## Data standards (authoritative)

### ceos.csv schema (columns)
- name
- strategic_philosophy.core_ideology
- strategic_philosophy.market_positioning
- strategic_philosophy.innovation_engine
- strategic_philosophy.competitive_stance
- strategic_philosophy.risk_profile
- leadership.hiring_philosophy
- leadership.cultural_architecture
- leadership.motivation_incentives
- leadership.communication_style
- leadership.talent_management
- operational_cadence.meeting_culture
- operational_cadence.decision_making_process
- operational_cadence.key_metrics
- operational_cadence.focus_prioritization
- operational_cadence.accountability_framework
- personal_ethos.core_principles
- personal_ethos.work_ethic
- personal_ethos.learning_adaptability
- personal_ethos.resilience_mechanism

Authoring rules:
- 1–2 sentences per cell, principle-style; avoid biography.
- Quote fields that contain commas.
- Use consistent vocabulary across leaders (e.g., “two-pizza teams”, “DRI”, “OKRs”).

### situations.csv schema (columns)
- ceo
- tags (semicolon- or comma-separated)
- title (short imperative or label)
- response (1–2 sentences; actionable)

Recommended situation tags:
- situation:missed_targets, situation:product_launch_crisis, situation:key_employee_resigning, situation:board_meeting, situation:media_interview, situation:strategy_refresh, situation:org_restructure, situation:pricing_backlash, situation:pr_crisis, situation:competitive_attack, situation:funding_dry_spell, situation:regulatory_pressure, situation:supply_chain_shock

Optional principle tags (prefix):
- principle:day1, principle:operating_system, principle:decision_framework, principle:focus, principle:storytelling, principle:input_metrics, principle:single_threaded_leader, principle:flywheel

Style rules:
- Be concise, present tense, principle-first. Prefer paraphrase over long quotes.
- Tie responses to customer value, inputs vs outputs, ownership and metrics when applicable.

## Research SOP (keep data consistent)

Evidence hierarchy:
- Primary: shareholder letters, founder/CEO memos, long-form talks/interviews.
- Secondary: HBR/FT/WSJ profiles, high-quality books/biographies.
- Tertiary: credible essays and interviews with direct reports.

Collection checklist per CEO:
- Fill all ceos.csv columns with 1–2 sentence principles.
- Add 3–5 situations in situations.csv using recommended tags.
- Keep terminology consistent; prefer reusable patterns (e.g., PRFAQ, COE, DRI, OKRs).

Validation:
- Sanity-check for duplication, conflicting statements, and overuse of fluff words.
- Ensure commas are quoted in CSV cells.

Build/update workflow:
```powershell
# Rebuild repository.json from CSVs
python -m app.tools.ingest_csv

# Ask queries via CLI
python -m app.cli ask "missed targets COE" --ceo "Jeff Bezos"
```

Notes:
- Keep ceos.csv row count and situations.csv entries growing together (coverage per leader).
- If adding new situation or principle tags, reuse existing patterns before inventing new ones; prefer general tags.

