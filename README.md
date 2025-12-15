# STIHL Timbersports Data Scraper

## PURPOSE

This Python web scraper extracts competition data from the STIHL Timbersports official database (https://data.stihl-timbersports.com). It specifically focuses on two disciplines:
- **Underhand Chop (UH)**
- **Standing Block Chop (SB)**

The scraper collects times, competitors, wood specifications, event details, and special markers (world records, personal bests, etc.) and exports everything to Excel files formatted for use in other programs.

## WHAT PROBLEM DOES THIS SOLVE?

The STIHL Timbersports website has competition data, but:
- No easy way to export data
- No way to filter by specific athletes
- No way to analyze trends across seasons
- Data is spread across hundreds of individual event pages

This scraper solves that by:
- Automatically collecting data from multiple events
- Organizing it into structured Excel files
- Filtering by season or athlete
- Providing clean, ready-to-use data with specific column format

## WHAT YOU GET

### Excel Output Format
The scraper creates Excel files with **exactly 9 columns** in this order:

1. **Competitor profile URL** - Direct link to athlete's profile
2. **Competitor Name** - Full athlete name
3. **Discipline** - "SB" (Standing Block Chop) or "UH" (Underhand Chop)
4. **Time** - Competition time in seconds
5. **Size** - Wood diameter in millimeters (converted from centimeters)
6. **Species** - Wood type (e.g., "WhitePine", "Poplar")
7. **Event Date** - Date of competition
8. **Event Name** - Full event name
9. **Special Markers** - WR (World Record), NR (National Record), PB (Personal Best), SB (Season Best)

### Multiple Sheets
Each Excel file contains:
- **Results** - All data
- **SB_Results** - Only Standing Block Chop
- **UH_Results** - Only Underhand Chop
- **Athlete Summary** - Best times per athlete/discipline

## HOW TO USE IT

### Installation

1. **Install Python 3.8 or higher**
   - Download from https://python.org
   - Make sure to check "Add Python to PATH" during installation

2. **Install required packages**
   ```bash
   pip install -r requirements.txt
   ```

### Two Ways to Run

#### METHOD 1: Interactive Mode (Easiest)
```bash
python interactive_scraper.py
```
Follow the on-screen menus. No command line knowledge needed.

#### METHOD 2: Command Line
```bash
python stihl_timbersports_scraper.py [options]
```

## WHAT WORKS RELIABLY

### ✅ Scraping by Season (RECOMMENDED)

**Get all 2024 competitions:**
```bash
python stihl_timbersports_scraper.py --season 2024
```

**Get all 2023 competitions:**
```bash
python stihl_timbersports_scraper.py --season 2023
```

**Get multiple seasons:**
```bash
python stihl_timbersports_scraper.py --seasons "2024,2023,2022"
```

**Get last 5 years:**
```bash
python stihl_timbersports_scraper.py --all-seasons
```

**Then filter in Excel** by athlete name - this is the most reliable method.

### ✅ Quick Testing

**Test with 5 recent events:**
```bash
python stihl_timbersports_scraper.py --limit 5
```

**Test with 10 events from 2024:**
```bash
python stihl_timbersports_scraper.py --season 2024 --limit 10
```

### ✅ Custom Output Filename

```bash
python stihl_timbersports_scraper.py --season 2024 --output my_data.xlsx
```

## WHAT DOESN'T WORK RELIABLY

### ⚠️ Direct Athlete Search (Known Issue)

The `--athlete "NAME"` option is **not currently reliable**. 

**Why:** The athlete profile pages have complex navigation structures that make it difficult to scrape all historical results consistently.

**Workaround:** Use season scraping instead:
1. Scrape the season(s) you want
2. Open the Excel file
3. Filter by athlete name in Excel

**Example:**
```bash
# Get all 2024 data
python stihl_timbersports_scraper.py --season 2024 --output 2024_all.xlsx

# Then in Excel:
# - Open 2024_all.xlsx
# - Click "Competitor Name" column
# - Use Excel filter to show only "Hodges" or "Cogar"
# - Copy filtered results to new file if needed
```

## COMMAND LINE OPTIONS

```
--season YEAR              Single season (e.g., 2024, 2023, 2016)
--seasons "YEAR,YEAR"      Multiple seasons (e.g., "2024,2023")
--all-seasons              Last 5 years (2025,2024,2023,2022,2021)
--limit NUMBER             Limit number of events to scrape
--output FILENAME          Custom output filename (.xlsx)
--delay SECONDS            Delay between requests (default: 1.0)
```

## TYPICAL USE CASES

### Use Case 1: Track Athlete Performance Over Time

**Goal:** Get all of Matthew Cogar's 2024 results

**Steps:**
1. Scrape 2024 season: `python stihl_timbersports_scraper.py --season 2024 --output 2024_data.xlsx`
2. Open `2024_data.xlsx` in Excel
3. Filter "Competitor Name" column for "COGAR"
4. Analyze his times, see progression, identify personal bests

### Use Case 2: Compare Athletes in a Season

**Goal:** Compare top athletes in 2024

**Steps:**
1. Scrape 2024: `python stihl_timbersports_scraper.py --season 2024`
2. Open in Excel
3. Use pivot tables or filters to compare times
4. Sort by Time column to see fastest performances

### Use Case 3: Build Historical Database

**Goal:** Create complete database of recent years

**Steps:**
1. Scrape multiple years: `python stihl_timbersports_scraper.py --all-seasons --output complete_db.xlsx`
2. Wait 30-60 minutes (this scrapes a lot of data)
3. Get comprehensive dataset for analysis

### Use Case 4: Quick Sample for Testing

**Goal:** See what the data looks like

**Steps:**
1. Quick test: `python stihl_timbersports_scraper.py --limit 5 --output test.xlsx`
2. Wait ~30 seconds
3. Open `test.xlsx` to see sample data

## HOW LONG DOES IT TAKE?

- **5 events:** ~30 seconds
- **Single season (50-70 events):** 10-15 minutes
- **Multiple seasons:** 10-15 minutes per season
- **Last 5 years (--all-seasons):** 30-60 minutes

The delay is intentional to be respectful to the server. Don't reduce it below 1.0 seconds.

## TROUBLESHOOTING

### "No results found"
- **Check season year:** Make sure that year has events (2024, 2023 definitely work)
- **Try with --limit 5:** Test with small sample first
- **Check internet connection:** Scraper needs stable internet

### "Taking too long"
- **This is normal:** Event scraping takes time due to respectful delays
- **Use --limit:** Test with smaller samples first
- **Be patient:** A full season takes 10-15 minutes

### "Can't find athlete"
- **Use season scraping:** `--season 2024` then filter in Excel
- **Don't use --athlete flag:** This feature is not reliable currently

### "pip is not recognized"
- **Try:** `pip3 install -r requirements.txt`
- **Or:** Reinstall Python with "Add to PATH" checked

### "python is not recognized"
- **Try:** `python3 interactive_scraper.py`
- **Or:** Add Python to system PATH

## INTERACTIVE MODE

For easier use without command line arguments:

```bash
python interactive_scraper.py
```

You'll get a menu:
```
1. Scrape specific athlete's complete history
2. Scrape multiple athletes
3. Scrape a single season
4. Scrape multiple seasons
5. Scrape last 5 years (2021-2025)
6. Quick test (5 recent events)
7. Exit
```

**Note:** Option 1 & 2 (athlete search) have known reliability issues. Use option 3 (season scraping) instead.

## TECHNICAL DETAILS

### How It Works

1. **Fetches event list** from Results page (filtered by season if specified)
2. **Visits each event page** one at a time
3. **Finds Underhand and Standing Block sections** in each event
4. **Extracts table data:** times, athletes, wood specs, rankings
5. **Converts measurements:** CM to MM for wood size
6. **Abbreviates disciplines:** "Standing Block Chop" → "SB", "Underhand Chop" → "UH"
7. **Exports to Excel** with multiple sheets

### What Makes This Different

- **Specific format:** Outputs exactly 9 columns needed for your other program
- **Clean data:** Automatic conversion (CM to MM), abbreviation (SB/UH)
- **Multiple sheets:** Organized by discipline for easy access
- **No extra columns:** Only essential data, nothing extraneous

### Limitations

- **Only SB and UH:** Other disciplines (Stock Saw, Single Buck, etc.) are not included
- **Text data only:** Times are stored as text, not calculated values
- **Website dependent:** If the STIHL website changes structure, scraper may break
- **Rate limited:** 1 second delay between requests (can't be faster)

## BEST PRACTICES

1. **Always test first**
   ```bash
   python stihl_timbersports_scraper.py --season 2024 --limit 5
   ```

2. **Use season scraping, not athlete search**
   - Season scraping is reliable
   - Filter in Excel afterwards

3. **Be patient**
   - Full seasons take 10-15 minutes
   - This is normal and expected

4. **Save different files for different queries**
   ```bash
   python stihl_timbersports_scraper.py --season 2024 --output 2024.xlsx
   python stihl_timbersports_scraper.py --season 2023 --output 2023.xlsx
   ```

5. **Start with recent seasons**
   - 2024, 2023 have the most data
   - Older years may have fewer events

## ETHICAL USE

- **Be respectful:** Don't reduce the delay below 1.0 seconds
- **Personal use:** This is for personal analysis and research
- **Data belongs to STIHL:** This scraper just helps you access it
- **No server overload:** The built-in delays prevent this

## EXAMPLES THAT WORK

### Example 1: Get 2024 Season
```bash
python stihl_timbersports_scraper.py --season 2024 --output 2024_complete.xlsx
```
**Result:** All 2024 events with SB/UH times

### Example 2: Get Recent History
```bash
python stihl_timbersports_scraper.py --seasons "2024,2023,2022" --output recent_3years.xlsx
```
**Result:** Three years of competition data

### Example 3: Quick Test
```bash
python stihl_timbersports_scraper.py --limit 5 --output sample.xlsx
```
**Result:** 5 recent events as a test

### Example 4: Specific Year
```bash
python stihl_timbersports_scraper.py --season 2016 --output 2016_data.xlsx
```
**Result:** 2016 events (if available)

## NEED HELP?

1. **Read START_HERE.md** - Quickest way to get started
2. **Read INTERACTIVE_GUIDE.md** - For interactive mode help
3. **Read SAMPLE_OUTPUT_FORMAT.md** - See what the Excel looks like
4. **Check troubleshooting section** - Common issues above

## FILES INCLUDED

- **stihl_timbersports_scraper.py** - Main scraper (command line)
- **interactive_scraper.py** - Interactive menu version
- **requirements.txt** - Python packages needed
- **run_scraper.bat** - Windows launcher
- **run_scraper.sh** - Mac/Linux launcher
- **START_HERE.md** - Quick start guide
- **INTERACTIVE_GUIDE.md** - Interactive mode guide
- **SAMPLE_OUTPUT_FORMAT.md** - Shows Excel format
- **README.md** - This file

## HONEST ASSESSMENT

### What Works Great ✅
- Scraping by season
- Scraping multiple seasons
- Excel export with exact format needed
- Interactive menus
- Quick testing

### What Needs Work⚠️
- Direct athlete search (use season + Excel filter instead)
- Very old events (some may have different formats)

### Recommended Workflow
1. Scrape by season: `--season 2024`
2. Filter in Excel by athlete name
3. Export filtered results if needed

This is the most reliable method currently.

## VERSION HISTORY

- **Current Version:** Fixed output format (9 columns, SB/UH abbreviations, MM sizes)
- **Known Issues:** Athlete direct search unreliable - use season scraping instead

## LICENSE

For personal, educational, and research use. Data belongs to STIHL Timbersports.

---

**Bottom Line:** Use season scraping (`--season 2024`), then filter in Excel. This works reliably and gives you exactly what you need.