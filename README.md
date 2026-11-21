# Chronanza

**Daily Timeline Puzzle**

Chronanza is a timeline-based trivia and ordering puzzle game where players arrange historical events, pop culture milestones, inventions, and cultural moments in chronological order.

## How to Play

1. **Explore topics and subcategories.** The content plan includes **15 broad topics**: World History, Themed History, Crime & Law, Business & Brands, Nature & Animals, Food, Art & Architecture, Technology, Sports, Music, Literature, Movies, Television, Pop Culture, and Toys & Videogames. Planned subcategories include famous battles, space journeys, court cases, snacks, and consoles. The current daily game selects one topic automatically rather than asking players to choose.
2. **Order the tiles.** Each daily puzzle displays **nine event tiles**, each with a *Tile Name* and an associated historical *Fact*. Arrange the events from earliest to latest according to their *Year*. Years are stored as integers, including negative values for BCE dates (for example, `-2560`).
3. **Lock in and learn.** Submit your timeline to check the order. Correct placements lock into position and reveal their years. At the end of the puzzle, review the historical and cultural facts behind the events.

## Content and Data Structure

The source content was organized in three worksheets in `Chronanza.xlsx`:

| Worksheet | Purpose |
| --- | --- |
| **Topics** | Defines **15 planned top-level topics** and **159 planned subcategories**. |
| **Puzzles** | Contains curated nine-tile puzzle sets, including a *Video Games* timeline from *Pong* (`1972`) to *Nintendo Switch* (`2017`), with ID Number, Tile Name, Year, and Fact fields. |
| **Database** | Contains **306 source rows** spanning populated subcategories and dates from `-2560` to `2022`. Each record includes an ID, topic, subcategory, tile name, year, and fact. |

The JSON import removes nine repeated IDs with matching content, producing **297 unique facts** in the current `puzzles.json` catalog. The 15 topics above describe the **planned content taxonomy**; not all planned topics and subcategories are necessarily populated in the current JSON database.

### Trivia record fields

| Field | Description |
| --- | --- |
| `id` | Stable, human-readable fact identifier, such as `WH-FB-001` or `TVG-CN-001`. |
| `topic` | Broad category used to group the nine events in a daily puzzle. |
| `subcategory` | Editorial classification retained for organization and future content expansion. |
| `label` | Event title shown on a game tile (imported from *Tile Name*). |
| `year` | Historical year as an integer; negative values represent BCE. |
| `fact` | Explanation shown when the timeline is reviewed. |
| `lastUsed` | Most recent date the fact appeared in a daily puzzle, or `null` if never used. |
| `usageHistory` | Dates on which the fact has appeared in a published puzzle. |

## Repository Structure

```text
Chronanza/
├── .github/
│   └── workflows/
│       └── daily-puzzle.yml       # Scheduled GitHub Actions puzzle generation
├── scripts/
│   ├── generate_daily.py          # Selects and records the next daily puzzle
│   ├── import_excel.py            # Converts the Excel Database sheet to JSON
│   └── test_generator.py          # Simulates daily puzzles and validates rules
├── CNAME                         # Custom domain configuration for GitHub Pages
├── daily-archive.json            # Published puzzle history, indexed by date
├── daily.json                    # Current daily puzzle served to the browser
├── index.html                    # Game interface, logic, and JSON loading
├── og-image.jpg                  # Social sharing preview image
├── puzzles.json                  # Trivia catalog and per-fact usage history
└── README.md                     # Project documentation
```

`Chronanza.xlsx` is the original content workbook and is **not required for the deployed website**. It is intentionally omitted from the public repository structure above. If the workbook is used to refresh the JSON catalog, preserve existing usage history before replacing `puzzles.json`; a fresh import initializes `lastUsed` and `usageHistory` to empty values.

## Dynamic Daily Puzzle System

Chronanza separates its content catalog from the game interface. The website reads `daily.json` instead of relying on a manually maintained `DAILY_PUZZLES` JavaScript array.

The generator follows these rules:

1. **One puzzle per Eastern calendar day.** The same dated puzzle is served to all players; the browser does not independently randomize the selection.
2. **Topic rotation.** Topics rotate in a defined sequence, while eligible facts within the selected topic are chosen randomly.
3. **Nine facts from one topic.** Each puzzle contains nine distinct fact IDs, with distinct years so the chronological order is unambiguous. Subcategories may be mixed within the same topic.
4. **90-day cooldown.** A fact is ineligible until at least 90 days have elapsed since its last use. Reuse is allowed in a *different combination* of nine eligible facts; repeating an entire previous puzzle is not the intent.
5. **Skip ineligible topics.** If a topic has fewer than nine eligible facts, the generator tries another topic. If no topic qualifies, generation fails rather than violating the cooldown.
6. **Persistent history.** Published selections are recorded in `daily-archive.json`, and fact usage is updated in `puzzles.json`. Re-running the generator for an already published date must not produce a different puzzle.

### Daily publishing flow

```text
puzzles.json (available facts + usage history)
            |
            v
scripts/generate_daily.py (topic rotation + eligibility)
            |
            +--> daily.json (today's nine events)
            +--> daily-archive.json (published dates)
            +--> puzzles.json (updated lastUsed / usageHistory)
            |
            v
index.html fetches daily.json and renders the existing game
```

The workflow in `.github/workflows/daily-puzzle.yml` runs through GitHub Actions on a UTC schedule and can also be started manually. It commits generated JSON changes when necessary. The schedule includes times intended to cover Eastern daylight and standard time; GitHub Actions schedules can run late, so **exact midnight publication is not guaranteed**. A scheduled workflow must be enabled, have repository write permissions, and run on the repository's default branch to support unattended publishing.

**Content capacity:** With 297 unique facts, the catalog cannot support an unlimited number of daily nine-fact puzzles under a strict 90-day cooldown. Add more facts before inventory is exhausted; the generator is designed to stop rather than silently reuse content early.

## Local Development and Validation

Run the commands from the repository root with a compatible Python installation.

**Generate or refresh the daily puzzle:**

```bash
python scripts/generate_daily.py
```

**Run the puzzle-selection tests:**

```bash
python scripts/test_generator.py
```

**Serve the website locally:**

```bash
python -m http.server 8000
```

Then visit `http://localhost:8000/`. Serving through HTTP is important because `index.html` fetches `daily.json`; opening the HTML directly as a `file://` URL can prevent JSON loading.

**Import content from Excel (editorial maintenance):** `scripts/import_excel.py` reads the `Database` worksheet in `Chronanza.xlsx` and writes `puzzles.json`. This script uses the spreadsheet import dependency included in its implementation and requires the workbook at the repository root when run. **Do not run an import over a live catalog without first preserving or merging its usage history.**

## Deployment Notes

The repository includes a `CNAME` file for the custom domain `chronanza.com`. This supports GitHub Pages configuration but does **not**, by itself, confirm that GitHub Pages is the active host or that the domain's DNS is correctly configured.

Before deploying, verify the actual hosting provider and deployment source. If GitHub Pages serves this repository, generated JSON commits on the publishing branch can become available with subsequent Pages deployments. If Porkbun hosts the website files separately, GitHub commits will **not** automatically update that hosting without an additional deployment process.

Develop and test changes on a feature branch, review them, and merge to the configured publishing branch only after validation. Avoid replacing the current `index.html` with an older copy, as that can overwrite interface changes.
