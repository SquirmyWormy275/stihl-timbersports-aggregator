# STIHL Timbersports Data Scraper

A Python web scraper for collecting Underhand Chop and Standing Block Chop times from the STIHL Timbersports database.

## Features

- ✅ Scrapes Underhand Chop and Standing Block Chop results
- ✅ Extracts: times, dates, competitors, wood species/size, rankings, and more
- ✅ Filter by season (2025, 2024, etc.)
- ✅ Filter by athlete name
- ✅ Exports to Excel with multiple sheets
- ✅ Respectful scraping with configurable delays
- ✅ Detailed athlete summaries

## Installation

1. Install Python 3.8 or higher

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage - Scrape All Events

```bash
python stihl_timbersports_scraper.py
```

This will scrape all available events and save results to `stihl_timbersports_results.xlsx`

### Filter by Season

```bash
# Scrape only 2025 events
python stihl_timbersports_scraper.py --season 2025

# Scrape only 2024 events
python stihl_timbersports_scraper.py --season 2024
```

### Filter by Athlete

```bash
# Get all results for Matthew Cogar
python stihl_timbersports_scraper.py --athlete "Cogar"

# Get all results for Nathaniel Hodges
python stihl_timbersports_scraper.py --athlete "Hodges"

# Get all results for Erin LaVoie
python stihl_timbersports_scraper.py --athlete "LaVoie"
```

### Limit Number of Events

```bash
# Scrape only the 10 most recent events
python stihl_timbersports_scraper.py --limit 10

# Scrape 5 events from 2025 for a specific athlete
python stihl_timbersports_scraper.py --season 2025 --limit 5 --athlete "Hodges"
```

### Custom Output File

```bash
python stihl_timbersports_scraper.py --output my_results.xlsx
```

### Combine Multiple Filters

```bash
# Scrape 2025 events for Nathaniel Hodges, output to custom file
python stihl_timbersports_scraper.py --season 2025 --athlete "Hodges" --output hodges_2025.xlsx

# Get top 20 events from 2024 for athletes with "Matt" in their name
python stihl_timbersports_scraper.py --season 2024 --limit 20 --athlete "Matt"
```

### Adjust Scraping Speed

```bash
# Slower scraping (2 second delay between requests - more polite)
python stihl_timbersports_scraper.py --delay 2.0

# Faster scraping (0.5 second delay - use cautiously)
python stihl_timbersports_scraper.py --delay 0.5
```

## Output Format

The scraper creates an Excel file with multiple sheets:

### Sheet 1: Results
Contains all scraped data with these columns (in this exact order):
1. **Competitor profile URL**: Direct link to athlete's profile
2. **Competitor Name**: Athlete's full name
3. **Discipline**: "SB" (Standing Block Chop) or "UH" (Underhand Chop)
4. **Time**: Competition time in seconds
5. **Size**: Wood diameter in millimeters (converted from cm)
6. **Species**: Wood species (e.g., "WhitePine", "Poplar")
7. **Event Date**: Date of the event
8. **Event Name**: Full event name
9. **Special Markers**: WR (World Record), NR (National Record), PB (Personal Best), SB (Season Best)

### Sheet 2: SB_Results
All Standing Block Chop results with the same columns

### Sheet 3: UH_Results
All Underhand Chop results with the same columns

### Sheet 4: Athlete Summary
Summary showing:
- Competitor Name
- Discipline (SB or UH)
- Best Time
- Number of Events competed

## Command Line Options

```
--season YEAR         Filter by season (e.g., 2025, 2024)
--limit NUMBER        Limit number of events to scrape
--athlete NAME        Filter by athlete name (partial match, case-insensitive)
--output FILENAME     Output Excel filename (default: stihl_timbersports_results.xlsx)
--delay SECONDS       Delay between requests in seconds (default: 1.0)
```

## Examples for Common Use Cases

### Get All Results for a Specific Athlete

```bash
# Get all Nathaniel Hodges results
python stihl_timbersports_scraper.py --athlete "Nathaniel HODGES" --output hodges_all.xlsx
```

### Compare Athletes from 2025

```bash
# Get 2025 results for comparison
python stihl_timbersports_scraper.py --season 2025 --output 2025_comparison.xlsx
```

### Quick Sample of Recent Events

```bash
# Just get the 5 most recent events to see what's available
python stihl_timbersports_scraper.py --limit 5 --output sample.xlsx
```

### Track Specific Athletes Over Time

```bash
# Get all Matt Cogar results
python stihl_timbersports_scraper.py --athlete "Matt COGAR" --output cogar_history.xlsx

# Get all results for athletes named "Matt"
python stihl_timbersports_scraper.py --athlete "Matt" --output matts.xlsx
```

## Using as a Python Module

You can also import and use the scraper in your own Python code:

```python
from stihl_timbersports_scraper import StihlTimberScraper

# Create scraper instance
scraper = StihlTimberScraper(delay=1.0)

# Scrape all 2025 events
df = scraper.scrape_all_events(season="2025")

# Filter for a specific athlete
hodges_df = scraper.scrape_all_events(athlete_filter="Hodges")

# Export to Excel
scraper.export_to_excel(df, "my_results.xlsx")

# Work with the data directly
print(df.head())
print(df['Athlete'].unique())
print(df.groupby('Athlete')['Time'].min())
```

## Data Analysis Examples

Once you have the Excel file, you can perform various analyses:

### Find Best Times by Athlete
Open the "Athlete Summary" sheet to see each athlete's best times

### Track Progress Over Time
Filter the "All Results" sheet by athlete and sort by date

### Compare Wood Species Performance
Filter by wood species/size to see how times vary with different wood types

### Identify World Records
Filter by the "Markers" column for "WR" (World Record)

## Tips

1. **Be Respectful**: The default 1-second delay is reasonable. Don't make it too fast.

2. **Start Small**: Use `--limit 5` first to test before scraping everything.

3. **Athlete Names**: Use partial names for easier matching. "Hodges" will match "Nathaniel HODGES (Nate)"

4. **Check the Output**: The script shows a sample of results before finishing so you can verify the data.

5. **Season Filter**: Use the current year or recent years for the most relevant data.

