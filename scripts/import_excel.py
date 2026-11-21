########################################
# CHRONANZA | EXCEL TRIVIA IMPORTER
########################################
# Script:       import_excel.py
# Version:      1.0.1
# Description:  Imports and validates CEO-maintained Excel trivia into the JSON catalog.
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

import json
from pathlib import Path
from collections import Counter
from artifact_tool import Blob, SpreadsheetFile

########################################
# SOURCE AND DESTINATION
########################################

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'Chronanza.xlsx'
workbook = SpreadsheetFile.import_xlsx(Blob.load(str(SOURCE)))
rows = workbook.worksheets.get_item('Database').get_range('A1:F1000').values

########################################
# VALIDATION AND DEDUPLICATION
########################################

facts = {}
for row in rows[1:]:
    if not row[0] or str(row[0]).strip() == 'ID':
        continue
    fact_id, topic, subcategory, label, year, description = row[:6]
    if not all((fact_id, topic, label, description)) or not isinstance(year, (int, float)):
        raise ValueError(f'Incomplete trivia row: {row[:6]}')
    entry = {'id': str(fact_id).strip(), 'topic': str(topic).strip(), 'subcategory': str(subcategory or '').strip(),
             'label': str(label).strip(), 'year': int(year), 'fact': str(description).strip(),
             'lastUsed': None, 'usageHistory': []}
    if entry['id'] in facts and any(facts[entry['id']][key] != entry[key] for key in ('topic','subcategory','label','year','fact')):
        raise ValueError(f'Conflicting duplicate ID: {entry["id"]}')
    facts[entry['id']] = entry

########################################
# JSON EXPORT
########################################

output = {'schemaVersion': 1, 'reuseCooldownDays': 90, 'facts': list(facts.values())}
(ROOT / 'puzzles.json').write_text(json.dumps(output, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
print(f'Exported {len(facts)} facts across {len(set(f["topic"] for f in facts.values()))} topics')
print('Topic counts:', dict(Counter(f['topic'] for f in facts.values())))
