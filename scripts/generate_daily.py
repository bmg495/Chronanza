########################################
# CHRONANZA | DAILY PUZZLE GENERATOR
########################################
# Script:       generate_daily.py
# Version:      1.0.1
# Description:  Generates a shared daily puzzle with topic rotation and a 90-day fact cooldown.
# Author:       Chronanza Development Team
# Maintainer:   Chronanza Development Team
# Email:        Not specified (retain original author contact when provided)
# Copyright:    Copyright (c) 2026 Chronanza. All rights reserved.
#
# Revision History:
# 1.0.1 | 2026-11-20 | Standardized documentation, section structure, and naming presentation.
#
########################################
# IMPORTS
########################################

import argparse
import hashlib
import json
import random
from collections import defaultdict
from datetime import date, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

########################################
# CONFIGURATION
########################################

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / 'puzzles.json'
DAILY = ROOT / 'daily.json'
ARCHIVE = ROOT / 'daily-archive.json'
ANCHOR = date(2026, 11, 19)

########################################
# FILE UTILITIES
########################################

def read_json(path, default):
    """Read a JSON file, returning the provided default if the file is missing.

    Args:
        path: Path to the JSON file.
        default: Value returned when the file does not exist.

    Returns:
        The decoded JSON value or default.
    """
    return json.loads(path.read_text(encoding='utf-8')) if path.exists() else default

########################################
# DAILY PUZZLE SELECTION
########################################

def build(day, catalog, archive):
    """Build one shared daily puzzle without repeating facts inside 90 days.

    Args:
        day: Eastern calendar date to generate.
        catalog: Mutable trivia catalog containing facts and usage history.
        archive: Mutable collection of previously published puzzles.

    Returns:
        Tuple of (daily puzzle dictionary, newly_created boolean).

    Raises:
        ValueError: When attempting to create an unpublished past puzzle.
        RuntimeError: When no topic contains nine eligible distinct years.
    """
    key = day.isoformat()
    if key in archive['days']:
        return archive['days'][key], False
    if archive['days'] and key < max(archive['days']):
        raise ValueError('Cannot generate a new past date; previous archive entries must remain immutable')
    by_topic = defaultdict(list)
    for fact in catalog['facts']:
        if any((day - date.fromisoformat(d)).days < 90 for d in fact['usageHistory']):
            continue
        by_topic[fact['topic']].append(fact)
    topics = sorted(set(f['topic'] for f in catalog['facts']))
    start = max(0, (day - ANCHOR).days) % len(topics)
    selected_topic = next((topics[(start + i) % len(topics)] for i in range(len(topics)) if len(by_topic[topics[(start + i) % len(topics)]]) >= 9), None)
    if selected_topic is None:
        raise RuntimeError(f'No topic has nine eligible facts for {key}; add trivia before publishing')
    rng = random.Random(int.from_bytes(hashlib.sha256(f'chronanza:{key}:{selected_topic}'.encode()).digest()[:8], 'big'))
    # Each selected year must be unique: the game scores an unambiguous 1–9 timeline.
    year_groups = defaultdict(list)
    for fact in by_topic[selected_topic]:
        year_groups[fact['year']].append(fact)
    if len(year_groups) < 9:
        # Try other topics rather than publishing an ambiguous timeline.
        for i in range(1, len(topics)):
            alternative = topics[(start + i) % len(topics)]
            groups = defaultdict(list)
            for fact in by_topic[alternative]:
                groups[fact['year']].append(fact)
            if len(groups) >= 9:
                selected_topic, year_groups = alternative, groups
                break
        else:
            raise RuntimeError(f'No topic has nine eligible distinct years for {key}')
    years = rng.sample(sorted(year_groups), 9)
    chosen = sorted((rng.choice(year_groups[y]) for y in years), key=lambda f: f['year'])
    number = (day - ANCHOR).days + 1
    puzzle = {'date': key, 'puzzleNumber': number, 'id': f'{key}-{selected_topic.lower().replace(" ", "-")}',
              'theme': selected_topic, 'events': [{k: f[k] for k in ('id','label','year','fact')} for f in chosen]}
    for fact in chosen:
        fact['usageHistory'].append(key)
        fact['lastUsed'] = key
    archive['days'][key] = puzzle
    return puzzle, True

########################################
# COMMAND LINE EXECUTION
########################################

def main():
    """Parse command-line options, generate the puzzle, and persist JSON files."""
    parser = argparse.ArgumentParser()
    parser.add_argument('--date', help='Override Eastern date YYYY-MM-DD (for testing)')
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    day = date.fromisoformat(args.date) if args.date else datetime.now(ZoneInfo('America/New_York')).date()
    catalog = read_json(CATALOG, None)
    archive = read_json(ARCHIVE, {'schemaVersion': 1, 'days': {}})
    puzzle, created = build(day, catalog, archive)
    print(f'{puzzle["date"]}: {puzzle["theme"]}: {len(puzzle["events"])} facts ({"new" if created else "existing"})')
    if not args.dry_run:
        CATALOG.write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        ARCHIVE.write_text(json.dumps(archive, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        DAILY.write_text(json.dumps(puzzle, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

########################################
# ENTRY POINT
########################################
if __name__ == '__main__':
    main()
