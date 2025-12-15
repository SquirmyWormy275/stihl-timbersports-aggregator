#!/usr/bin/env python3
"""
STIHL Timbersports Data Scraper
Scrapes Underhand Chop and Standing Block Chop times from data.stihl-timbersports.com
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import time
import re
from typing import List, Dict, Optional
import argparse


class StihlTimberScraper:
    """Scraper for STIHL Timbersports results database"""
    
    BASE_URL = "https://data.stihl-timbersports.com"
    
    def __init__(self, delay: float = 1.0):
        """
        Initialize scraper
        
        Args:
            delay: Delay between requests in seconds (be respectful!)
        """
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.delay = delay
        
    def get_page(self, url: str) -> Optional[BeautifulSoup]:
        """Fetch and parse a page"""
        try:
            time.sleep(self.delay)  # Be respectful to the server
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'html.parser')
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return None
    
    def get_events(self, season: Optional[str] = None, seasons_list: Optional[List[str]] = None, 
                   limit: Optional[int] = None) -> List[Dict]:
        """
        Get list of events from the Results page
        
        Args:
            season: Filter by single season (e.g., "2025", "2024")
            seasons_list: List of seasons to scrape (e.g., ["2025", "2024", "2023"])
            limit: Limit number of events to scrape (applies after combining all seasons)
            
        Returns:
            List of event dictionaries
        """
        all_events = []
        
        # If seasons_list provided, scrape each season
        if seasons_list:
            for s in seasons_list:
                print(f"Fetching events for season {s}...")
                events = self._get_events_for_season(s, limit=None)
                all_events.extend(events)
                print(f"  Found {len(events)} events in {s}")
        # If single season provided
        elif season:
            print(f"Fetching events for season {season}...")
            all_events = self._get_events_for_season(season, limit=None)
        # Otherwise get current default view (likely just current year)
        else:
            print("Fetching events (default view - likely current year only)...")
            print("TIP: Use --season or --all-seasons for more complete data")
            all_events = self._get_events_for_season(None, limit=None)
        
        # Apply limit if specified
        if limit and len(all_events) > limit:
            all_events = all_events[:limit]
        
        print(f"Total events to scrape: {len(all_events)}")
        return all_events
    
    def _get_events_for_season(self, season: Optional[str], limit: Optional[int]) -> List[Dict]:
        """Get events for a specific season"""
        url = f"{self.BASE_URL}/Results"
        if season:
            # The website uses season as a query parameter
            url += f"?season={season}"

        soup = self.get_page(url)
        if not soup:
            return []

        events = []
        event_rows = soup.find_all('tr')

        for row in event_rows:
            link = row.find('a', href=re.compile(r'/Event/\d+'))
            if link:
                event_url = self.BASE_URL + link['href']
                event_name = link.text.strip()

                # Get date and location from row
                cells = row.find_all('td')
                date_location = ""
                nation = ""

                if len(cells) >= 2:
                    date_location = cells[0].text.strip()
                    nation = cells[1].text.strip()

                events.append({
                    'name': event_name,
                    'url': event_url,
                    'date_location': date_location,
                    'nation': nation
                })

                if limit and len(events) >= limit:
                    break

        return events

    def detect_all_available_seasons(self, start_year: Optional[int] = None, end_year: Optional[int] = None) -> List[str]:
        """
        Auto-detect all seasons that have events on the website

        Args:
            start_year: Earliest year to check (default: 2000)
            end_year: Latest year to check (default: current year + 1)

        Returns:
            List of season years (as strings) that have events, in descending order
        """
        current_year = datetime.now().year
        start_year = start_year or 2000
        end_year = end_year or (current_year + 1)

        print(f"Auto-detecting available seasons from {start_year} to {end_year}...")
        print("This may take a minute as we check each year...")

        available_seasons = []

        # Check each year in reverse order (newest first)
        for year in range(end_year, start_year - 1, -1):
            # Quick check - just see if there are any events for this year
            events = self._get_events_for_season(str(year), limit=1)
            if events:
                available_seasons.append(str(year))
                print(f"  [OK] {year} - has events")
            else:
                # Don't print for years with no events to reduce noise
                pass

        print(f"\nFound {len(available_seasons)} seasons with events: {', '.join(available_seasons)}")
        return available_seasons
    
    def parse_event_results(self, event_info: Dict) -> List[Dict]:
        """
        Parse results from a single event
        
        Args:
            event_info: Event information dictionary
            
        Returns:
            List of result dictionaries
        """
        print(f"Scraping: {event_info['name']}")
        soup = self.get_page(event_info['url'])
        if not soup:
            return []
        
        results = []
        
        # Extract event date
        date_elem = soup.find('dt', string=re.compile(r'Date'))
        event_date = ""
        if date_elem:
            dd = date_elem.find_next_sibling('dd')
            if dd:
                event_date = dd.text.strip().split('\n')[0].strip()
        
        # Extract location
        location_elem = soup.find('dt', string=re.compile(r'Location'))
        location = ""
        if location_elem:
            dd = location_elem.find_next_sibling('dd')
            if dd:
                location = dd.text.strip()
        
        # Find Underhand Chop section (changed from <a> to any element type)
        underhand_section = soup.find(id='Round1UnderhandChop') or \
                           soup.find(id='Round2UnderhandChop') or \
                           soup.find(id='Round3UnderhandChop')

        if underhand_section:
            results.extend(self._parse_discipline_section(
                underhand_section,
                "Underhand Chop",
                event_info['name'],
                event_date,
                location
            ))

        # Find Standing Block Chop section (changed from <a> to any element type)
        standing_section = soup.find(id='Round1StandingBlockChop') or \
                          soup.find(id='Round2StandingBlockChop') or \
                          soup.find(id='Round3StandingBlockChop')
        
        if standing_section:
            results.extend(self._parse_discipline_section(
                standing_section,
                "Standing Block Chop",
                event_info['name'],
                event_date,
                location
            ))
        
        return results
    
    def _parse_discipline_section(self, section_anchor, discipline_name: str, 
                                  event_name: str, event_date: str, 
                                  location: str) -> List[Dict]:
        """Parse a specific discipline section"""
        results = []
        
        # Find the table after the section header
        table = section_anchor.find_next('table')
        if not table:
            return results
        
        # Get wood species/size from the paragraph before the table
        wood_info = ""
        prev = section_anchor.find_next('p')
        if prev and 'Competition Wood:' in prev.text:
            wood_match = re.search(r'Competition Wood:\s*\*\*([^*]+)\*\*', prev.text)
            if wood_match:
                wood_info = wood_match.group(1).strip()
        
        # Parse table rows
        rows = table.find_all('tr')
        for row in rows[1:]:  # Skip header
            cells = row.find_all('td')
            if len(cells) < 4:
                continue
            
            # Extract rank, name, nation, points, time
            rank = cells[0].text.strip()
            
            # Name and athlete URL
            name_link = cells[1].find('a')
            if name_link:
                athlete_name = name_link.text.strip()
                athlete_url = self.BASE_URL + name_link['href']
            else:
                athlete_name = cells[1].text.strip()
                athlete_url = ""
            
            # Get level (Pro, Rookie, etc.)
            level = ""
            level_span = cells[1].find('span', class_='label')
            if level_span:
                level = level_span.text.strip()
            
            nation = cells[2].text.strip() if len(cells) > 2 else ""
            points = cells[3].text.strip() if len(cells) > 3 else ""
            time = cells[4].text.strip() if len(cells) > 4 else ""
            
            # Check for special markers (WR, NR, PB, SB, etc.)
            markers = []
            if len(cells) > 5:
                markers_cell = cells[5].text.strip()
                if markers_cell:
                    markers.append(markers_cell)
            
            # Abbreviate discipline name
            discipline_abbrev = "SB" if "Standing Block" in discipline_name else "UH"
            
            # Extract wood diameter in CM and convert to MM
            wood_size_mm = ""
            wood_species = ""
            if wood_info:
                # Extract diameter (e.g., "WhitePine (32 cm diameter)" -> 32)
                size_match = re.search(r'(\d+)\s*cm', wood_info)
                if size_match:
                    size_cm = int(size_match.group(1))
                    wood_size_mm = str(size_cm * 10)  # Convert CM to MM
                
                # Extract species name (e.g., "WhitePine (32 cm diameter)" -> "WhitePine")
                species_match = re.search(r'([A-Za-z]+)\s*\(', wood_info)
                if species_match:
                    wood_species = species_match.group(1)
            
            results.append({
                'Competitor profile URL': athlete_url,
                'Competitor Name': athlete_name,
                'Discipline': discipline_abbrev,
                'Time': time,
                'Size': wood_size_mm,
                'Species': wood_species,
                'Event Date': event_date,
                'Event Name': event_name,
                'Special Markers': ', '.join(markers)
            })
        
        return results
    
    def scrape_athlete_profile(self, athlete_name_or_url: str, seasons_to_search: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Scrape ALL results for a specific athlete by searching through multiple seasons

        This is the RELIABLE method - it searches through actual event results rather than
        relying on the athlete's profile page which may not show complete history.

        Args:
            athlete_name_or_url: Either athlete name to search for, or direct URL to profile
            seasons_to_search: List of seasons to search (default: last 10 years)

        Returns:
            DataFrame with all the athlete's SB and UH results from their ENTIRE CAREER
        """
        # If it's a URL, use it directly (advanced usage)
        if athlete_name_or_url.startswith('http'):
            athlete_url = athlete_name_or_url
            print(f"Using athlete profile URL: {athlete_url}")
            # Get athlete name from profile
            soup = self.get_page(athlete_url)
            if not soup:
                return pd.DataFrame()
            h2 = soup.find('h2')
            athlete_name = h2.text.strip() if h2 else "Unknown"
        else:
            # Find the athlete's profile URL by searching recent events
            print(f"Searching for athlete: {athlete_name_or_url}")
            print("Finding athlete profile URL...")

            athlete_url = self._find_athlete_url(athlete_name_or_url)

            if not athlete_url:
                print(f"Could not find athlete matching: {athlete_name_or_url}")
                print("Try:")
                print("  • Check spelling")
                print("  • Use just the last name")
                print("  • Try a different part of the name")
                return pd.DataFrame()

            # Get exact athlete name from profile
            soup = self.get_page(athlete_url)
            if not soup:
                return pd.DataFrame()
            h2 = soup.find('h2')
            athlete_name = h2.text.strip() if h2 else athlete_name_or_url

        print(f"Found athlete: {athlete_name}")
        print(f"Profile URL: {athlete_url}")

        # Default: search last 10 years to ensure complete history
        if seasons_to_search is None:
            current_year = datetime.now().year
            seasons_to_search = [str(year) for year in range(current_year, current_year - 10, -1)]

        print(f"Searching through {len(seasons_to_search)} seasons for complete history...")
        print(f"Seasons: {', '.join(seasons_to_search)}")
        print("This may take a few minutes but ensures all historical data is captured.")
        print()

        all_results = []
        events_with_athlete = 0

        # Scrape each season
        for season in seasons_to_search:
            print(f"Searching season {season}...")
            events = self._get_events_for_season(season, limit=None)

            if not events:
                continue

            # Check each event for this athlete
            for event in events:
                event_results = self._get_athlete_results_from_event(
                    event['url'],
                    event['name'],
                    athlete_name,
                    athlete_url
                )

                if event_results:
                    all_results.extend(event_results)
                    events_with_athlete += 1

            if events_with_athlete > 0:
                print(f"  Found {events_with_athlete} events in {season}")
                events_with_athlete = 0

        df = pd.DataFrame(all_results)

        # Remove duplicates (same event + discipline)
        if not df.empty:
            df = df.drop_duplicates(subset=['Event Name', 'Discipline', 'Time'], keep='first')

        print()
        print("=" * 70)
        print(f"[OK] Found {len(df)} total SB/UH results for {athlete_name}")
        if not df.empty:
            print(f"[OK] Events competed: {df['Event Name'].nunique()}")
            print(f"[OK] Date range: {df['Event Date'].min()} to {df['Event Date'].max()}")
        print("=" * 70)

        return df
    
    def _get_athlete_results_from_event(self, event_url: str, event_name: str, 
                                       athlete_name: str, athlete_url: str) -> List[Dict]:
        """Get specific athlete's results from an event"""
        soup = self.get_page(event_url)
        if not soup:
            return []
        
        results = []
        
        # Get event date
        date_elem = soup.find('dt', string=re.compile(r'Date'))
        event_date = ""
        if date_elem:
            dd = date_elem.find_next_sibling('dd')
            if dd:
                event_date = dd.text.strip().split('\n')[0].strip()
        
        # Find SB and UH sections (changed from <a> to any element type)
        for discipline_name in ['Underhand Chop', 'Standing Block Chop']:
            section = None
            for anchor_id in [f'Round1{discipline_name.replace(" ", "")}',
                            f'Round2{discipline_name.replace(" ", "")}',
                            f'Round3{discipline_name.replace(" ", "")}']:
                section = soup.find(id=anchor_id)
                if section:
                    break
            
            if not section:
                continue
            
            # Get wood info
            wood_info = ""
            prev = section.find_next('p')
            if prev and 'Competition Wood:' in prev.text:
                wood_match = re.search(r'Competition Wood:\s*\*\*([^*]+)\*\*', prev.text)
                if wood_match:
                    wood_info = wood_match.group(1).strip()
            
            # Extract size and species
            wood_size_mm = ""
            wood_species = ""
            if wood_info:
                size_match = re.search(r'(\d+)\s*cm', wood_info)
                if size_match:
                    wood_size_mm = str(int(size_match.group(1)) * 10)
                species_match = re.search(r'([A-Za-z]+)\s*\(', wood_info)
                if species_match:
                    wood_species = species_match.group(1)
            
            # Find the table
            table = section.find_next('table')
            if not table:
                continue
            
            # Parse rows to find our athlete
            rows = table.find_all('tr')
            for row in rows[1:]:
                cells = row.find_all('td')
                if len(cells) < 5:
                    continue
                
                name_link = cells[1].find('a')
                row_athlete_name = name_link.text.strip() if name_link else cells[1].text.strip()
                
                # Check if this is our athlete
                if athlete_name.lower() in row_athlete_name.lower():
                    time = cells[4].text.strip() if len(cells) > 4 else ""
                    markers = cells[5].text.strip() if len(cells) > 5 else ""
                    
                    discipline_abbrev = "SB" if "Standing Block" in discipline_name else "UH"
                    
                    results.append({
                        'Competitor profile URL': athlete_url,
                        'Competitor Name': row_athlete_name,
                        'Discipline': discipline_abbrev,
                        'Time': time,
                        'Size': wood_size_mm,
                        'Species': wood_species,
                        'Event Date': event_date,
                        'Event Name': event_name,
                        'Special Markers': markers
                    })
        
        return results
    
    def _find_athlete_url(self, athlete_name: str) -> Optional[str]:
        """Search for athlete by checking recent events to get their profile URL"""
        # Check a few recent seasons to find the athlete
        seasons = ["2025", "2024", "2023"]
        
        for season in seasons:
            events = self._get_events_for_season(season, limit=10)
            
            # Check first few events
            for event in events[:3]:
                soup = self.get_page(event['url'])
                if not soup:
                    continue
                
                # Find any athlete link that matches
                links = soup.find_all('a', href=re.compile(r'/Athlete/\d+'))
                for link in links:
                    if athlete_name.lower() in link.text.lower():
                        return self.BASE_URL + link['href']
        
        return None
    
    def scrape_all_events(self, season: Optional[str] = None,
                         seasons_list: Optional[List[str]] = None,
                         limit: Optional[int] = None,
                         athlete_filter: Optional[str] = None) -> pd.DataFrame:
        """
        Scrape all events and return DataFrame
        
        Args:
            season: Filter by single season
            seasons_list: List of seasons to scrape
            limit: Limit number of events
            athlete_filter: Filter results by athlete name (case-insensitive partial match)
            
        Returns:
            DataFrame with all results
        """
        events = self.get_events(season=season, seasons_list=seasons_list, limit=limit)
        all_results = []
        
        for event in events:
            event_results = self.parse_event_results(event)
            all_results.extend(event_results)
        
        df = pd.DataFrame(all_results)
        
        # Filter by athlete if specified
        if athlete_filter and not df.empty:
            df = df[df['Competitor Name'].str.contains(athlete_filter, case=False, na=False)]
        
        return df
    
    def export_to_excel(self, df: pd.DataFrame, filename: str):
        """Export DataFrame to Excel"""
        if df.empty:
            print("No results to export!")
            return
        
        print(f"Exporting {len(df)} results to {filename}...")
        
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            # Export main sheet with only the required columns in the correct order
            column_order = [
                'Competitor profile URL',
                'Competitor Name', 
                'Discipline',
                'Time',
                'Size',
                'Species',
                'Event Date',
                'Event Name',
                'Special Markers'
            ]
            
            # Ensure all columns exist and are in the right order
            output_df = df[column_order]
            output_df.to_excel(writer, sheet_name='Results', index=False)
            
            # Create separate sheets for each discipline using abbreviations
            if 'Discipline' in df.columns:
                for discipline in df['Discipline'].unique():
                    discipline_df = df[df['Discipline'] == discipline][column_order]
                    sheet_name = f"{discipline}_Results"
                    discipline_df.to_excel(writer, sheet_name=sheet_name, index=False)
            
            # Create a sheet grouped by athlete
            if 'Competitor Name' in df.columns and not df.empty:
                athlete_summary = df.groupby(['Competitor Name', 'Discipline']).agg({
                    'Time': 'min',
                    'Event Name': 'count'
                }).reset_index()
                athlete_summary.columns = ['Competitor Name', 'Discipline', 'Best Time', 'Events']
                athlete_summary.to_excel(writer, sheet_name='Athlete Summary', index=False)
        
        print(f"Successfully exported to {filename}")


def main():
    """Main function with CLI arguments"""
    parser = argparse.ArgumentParser(
        description='Scrape STIHL Timbersports Underhand and Standing Block Chop results'
    )
    parser.add_argument(
        '--athlete',
        type=str,
        help='Scrape all SB/UH results for specific athlete by name (searches through all events to find complete history)',
        default=None
    )
    parser.add_argument(
        '--athlete-url',
        type=str,
        help='Scrape specific athlete by profile URL (advanced usage)',
        default=None
    )
    parser.add_argument(
        '--season',
        type=str,
        help='Filter by season (e.g., 2025, 2024). Works with both --athlete and event scraping.',
        default=None
    )
    parser.add_argument(
        '--all-seasons',
        action='store_true',
        help='Auto-detect and scrape ALL available seasons from the website. Works with both --athlete and event scraping.'
    )
    parser.add_argument(
        '--seasons',
        type=str,
        help='Comma-separated list of seasons (e.g., "2025,2024,2023"). Works with both --athlete and event scraping.',
        default=None
    )
    parser.add_argument(
        '--limit',
        type=int,
        help='Limit number of events to scrape',
        default=None
    )
    parser.add_argument(
        '--output',
        type=str,
        help='Output Excel filename',
        default='stihl_timbersports_results.xlsx'
    )
    parser.add_argument(
        '--delay',
        type=float,
        help='Delay between requests in seconds',
        default=1.0
    )
    
    args = parser.parse_args()
    
    # Create scraper
    scraper = StihlTimberScraper(delay=args.delay)
    
    print("Starting scraper...")
    print("=" * 60)
    
    # If athlete specified, scrape their profile directly
    if args.athlete or args.athlete_url:
        athlete_id = args.athlete or args.athlete_url
        print(f"Mode: Athlete Profile Scraping (Comprehensive)")
        print(f"Athlete: {athlete_id}")

        # Allow user to specify seasons to search for athlete
        seasons_to_search = None
        if args.all_seasons:
            seasons_to_search = scraper.detect_all_available_seasons()
        elif args.seasons:
            seasons_to_search = args.seasons.split(',')
        elif args.season:
            seasons_to_search = [args.season]
        # else: defaults to last 10 years

        if seasons_to_search:
            print(f"Searching seasons: {', '.join(seasons_to_search)}")
        else:
            print(f"Searching: Last 10 years (default)")
        print("=" * 60)

        df = scraper.scrape_athlete_profile(athlete_id, seasons_to_search=seasons_to_search)
        
    # Otherwise scrape events
    else:
        # Determine seasons to scrape
        seasons_list = None
        if args.all_seasons:
            print("Mode: All Available Seasons Event Scraping")
            seasons_list = scraper.detect_all_available_seasons()
            print(f"Seasons to scrape: {', '.join(seasons_list)}")
        elif args.seasons:
            seasons_list = args.seasons.split(',')
            print("Mode: Multi-Season Event Scraping")
            print(f"Seasons: {', '.join(seasons_list)}")
        elif args.season:
            print("Mode: Single Season Event Scraping")
            print(f"Season: {args.season}")
        else:
            print("Mode: Current Season Event Scraping")
            print("[WARNING] This will only scrape current season (2025)")
            print("[WARNING] For historical data, use --all-seasons or --season YEAR")
        
        print(f"Event Limit: {args.limit or 'No limit'}")
        print("=" * 60)
        
        # Get events
        if seasons_list:
            events = scraper.get_events(seasons_list=seasons_list, limit=args.limit)
        else:
            events = scraper.get_events(season=args.season, limit=args.limit)
        
        # Scrape all events
        all_results = []
        for i, event in enumerate(events, 1):
            print(f"[{i}/{len(events)}] {event['name']}")
            event_results = scraper.parse_event_results(event)
            all_results.extend(event_results)
        
        df = pd.DataFrame(all_results)
    
    if not df.empty:
        print("\n" + "=" * 60)
        print(f"[OK] Scraped {len(df)} results")
        print(f"[OK] Athletes found: {df['Competitor Name'].nunique()}")
        print(f"[OK] Events covered: {df['Event Name'].nunique()}")
        print("=" * 60)

        # Export to Excel
        scraper.export_to_excel(df, args.output)

        # Show sample
        print("\nSample of results:")
        print(df[['Competitor Name', 'Discipline', 'Time', 'Event Name']].head(10).to_string())
        print(f"\n[OK] Complete data saved to: {args.output}")
    else:
        print("\n" + "=" * 60)
        print("[ERROR] No results found!")
        print("\nTroubleshooting:")
        print("  • If searching by athlete, try a shorter name")
        print("  • If searching events, try --all-seasons for historical data")
        print("  • Check your spelling")
        print("=" * 60)


if __name__ == '__main__':
    main()