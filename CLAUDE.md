# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A Python web scraper that extracts competition data (Underhand Chop and Standing Block Chop times) from the STIHL Timbersports official database (https://data.stihl-timbersports.com) and exports to Excel with a specific 9-column format.

## Core Architecture

### Main Components

**[TimbersportsScraper.py](TimbersportsScraper.py)** - Core scraper module
- `StihlTimberScraper` class handles all web scraping logic
- Uses `requests.Session` for HTTP with 1-second respectful delay between requests
- BeautifulSoup for HTML parsing
- pandas for data aggregation and Excel export via openpyxl

**[InteractiveMenu.PY](InteractiveMenu.PY)** - User-friendly CLI interface
- Imports and uses `StihlTimberScraper` from TimbersportsScraper module
- Menu-driven interaction (no command-line args needed)
- Wrapper around the core scraper functionality

### Key Design Patterns

**Two Scraping Modes:**
1. **Event-based scraping** (Reliable, Recommended)
   - Scrapes by season/year via `get_events()` and `parse_event_results()`
   - Processes event list from Results page
   - Iterates through each event extracting SB/UH data

2. **Athlete-based scraping** (Unreliable, Known Issue)
   - Scrapes athlete profile pages via `scrape_athlete_profile()`
   - Has navigation/completeness issues (documented in README)
   - Users should use season scraping + Excel filtering instead

**Data Flow:**
```
Web Page → BeautifulSoup → dict/list → pandas DataFrame → Excel (multiple sheets)
```

### Critical Data Transformations

The scraper performs specific transformations required by downstream tools:

1. **Discipline abbreviation**: "Standing Block Chop" → "SB", "Underhand Chop" → "UH"
2. **Size conversion**: CM to MM (multiply by 10)
3. **Column ordering**: Exact 9-column format (see Output Format below)

### Output Format

Excel files must have exactly these 9 columns in this order:
1. Competitor profile URL
2. Competitor Name
3. Discipline (SB or UH only)
4. Time
5. Size (in MM)
6. Species
7. Event Date
8. Event Name
9. Special Markers (WR, NR, PB, SB)

Multiple sheets created:
- `Results` - All data
- `SB_Results` - Standing Block only
- `UH_Results` - Underhand only
- `Athlete Summary` - Aggregated best times

## Development Commands

### Run the scraper

**Interactive mode (easiest):**
```bash
python InteractiveMenu.PY
```

**Command line - scrape by season (recommended):**
```bash
python TimbersportsScraper.py --season 2024
python TimbersportsScraper.py --seasons "2024,2023,2022"
python TimbersportsScraper.py --all-seasons
```

**Command line - quick test:**
```bash
python TimbersportsScraper.py --limit 5
```

**Command line - custom output:**
```bash
python TimbersportsScraper.py --season 2024 --output my_data.xlsx
```

### Dependencies

The README references `requirements.txt` but it's not present in the repository. Based on the code, required packages are:
- requests
- beautifulsoup4
- pandas
- openpyxl (for Excel writing)

## Important Implementation Details

### Web Scraping Strategy

**Base URL and Patterns:**
- Base: `https://data.stihl-timbersports.com`
- Results page: `/Results?season={year}`
- Event pages: `/Event/{id}`
- Athlete profiles: `/Athlete/{id}`

**HTML Parsing Approach:**
- Discipline sections identified by anchor IDs: `Round1UnderhandChop`, `Round1StandingBlockChop`, etc.
- Competition wood info extracted via regex from paragraphs: `Competition Wood: **{species} ({size} cm diameter)**`
- Results tables parsed row-by-row (skip header row)
- Special markers in 6th table column

**Rate Limiting:**
- 1 second delay between requests (`time.sleep(self.delay)`)
- Do NOT reduce below 1.0 seconds (documented in README as ethical requirement)

### Known Issues and Workarounds

**Athlete Direct Search Unreliable:**
- `scrape_athlete_profile()` has completeness issues
- Profile pages have complex navigation that makes comprehensive scraping difficult
- **Workaround**: Use `scrape_all_events(season="2024")` then filter in Excel

**Duplicate Code:**
- Lines 540-638 in TimbersportsScraper.py appear to be duplicate/dead code from `_find_athlete_url()` method
- Should be cleaned up in future refactoring

### Excel Export Implementation

Located in `export_to_excel()` method:
- Uses `pd.ExcelWriter` with openpyxl engine
- Enforces strict column order via `column_order` list
- Creates filtered sheets by discipline using DataFrame filtering
- Athlete Summary sheet uses `groupby` aggregation (min time, event count)

## Code Patterns to Maintain

### When adding new scraping functionality:

1. **Always use the session object** (`self.session.get()`) not raw `requests.get()`
2. **Always call `self.get_page(url)`** which includes delay and error handling
3. **Return empty list/DataFrame on errors** rather than raising exceptions
4. **Parse wood info consistently** using the regex patterns established
5. **Convert CM to MM** for size measurements (multiply by 10)
6. **Use discipline abbreviations** SB/UH in output data

### When modifying data extraction:

The 9-column output format is non-negotiable - it's required by downstream tools. Any changes to column order, names, or count will break integrations.

## Testing Strategy

The README documents specific testing approaches:

**Quick validation:**
```bash
python TimbersportsScraper.py --limit 5 --output test.xlsx
```

**Season validation:**
```bash
python TimbersportsScraper.py --season 2024 --limit 10 --output test_2024.xlsx
```

**Expected timing:**
- 5 events: ~30 seconds
- Single season: 10-15 minutes
- Multiple seasons: 30-60 minutes

## Critical Context from README

The README emphasizes these points repeatedly:
- Season scraping is the reliable method
- Athlete search has known issues
- Use Excel for filtering athletes after scraping
- Respect rate limits (1.0 second delay minimum)
- Output format is designed for integration with other programs (exact 9 columns)

When making changes, remember the scraper is part of a larger workflow - users scrape data then use it in other analysis tools that expect the specific column format.
