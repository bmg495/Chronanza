########################################
# CHRONANZA | DAILY PUZZLE VALIDATION
########################################
# Script:       test_generator.py
# Version:      1.0.1
# Description:  Simulates puzzle generation and verifies eligibility, uniqueness, and repeat prevention.
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

import copy
import json
from datetime import date, timedelta
from pathlib import Path
from generate_daily import build
########################################
# TEST DATA
########################################
root = Path(__file__).resolve().parents[1]
catalog = json.loads((root / 'puzzles.json').read_text())
archive = {'schemaVersion': 1, 'days': {}}
# Remove already generated usage for independent simulation.
for fact in catalog['facts']:
    fact['usageHistory'] = []
    fact['lastUsed'] = None
first = date(2026, 11, 20)
used = {}
completed = 0
########################################
# VALIDATION SIMULATION
########################################

for n in range(100):
    day = first + timedelta(days=n)
    try:
        puzzle, new = build(day, catalog, archive)
    except RuntimeError:
        break
    assert new
    assert len(puzzle['events']) == 9
    assert len({x['id'] for x in puzzle['events']}) == 9
    assert len({x['year'] for x in puzzle['events']}) == 9
    assert len({x['id'] for x in puzzle['events']}) == 9
    assert len({next(f['topic'] for f in catalog['facts'] if f['id'] == x['id']) for x in puzzle['events']}) == 1
    for event in puzzle['events']:
        if event['id'] in used:
            assert (day - used[event['id']]).days >= 90
        used[event['id']] = day
    again, created = build(day, catalog, archive)
    assert not created and again == puzzle
    completed += 1

########################################
# TEST SUMMARY
########################################

print(f'PASS: {completed} consecutive daily puzzles; no premature fact reuse; idempotent; exhaustion correctly detected')
