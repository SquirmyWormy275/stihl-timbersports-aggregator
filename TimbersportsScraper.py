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
    
    def get_events(self, season: Optional[str] = None, limit: Optional[int] = None) -> List[Dict]:
        """
        Get list of events from the Results page
        
        Args:
            season: Filter by season (e.g., "2025", "2024")
            limit: Limit number of events to scrape
            
        Returns:
            List of event dictionaries
        """
        print("Fetching events list...")
        url = f"{self.BASE_URL}/Results"
        if season:
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
        
        print(f"Found {len(events)} events")
        return events
    
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
        
        # Find Underhand Chop section
        underhand_section = soup.find('a', id='Round1UnderhandChop') or \
                           soup.find('a', id='Round2UnderhandChop') or \
                           soup.find('a', id='Round3UnderhandChop')
        
        if underhand_section:
            results.extend(self._parse_discipline_section(
                underhand_section, 
                "Underhand Chop",
                event_info['name'],
                event_date,
                location
            ))
        
        # Find Standing Block Chop section
        standing_section = soup.find('a', id='Round1StandingBlockChop') or \
                          soup.find('a', id='Round2StandingBlockChop') or \
                          soup.find('a', id='Round3StandingBlockChop')
        
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
    
    def get_athlete_results(self, athlete_url: str) -> List[Dict]:
        """
        Get all results for a specific athlete
        
        Args:
            athlete_url: URL to athlete's profile page
            
        Returns:
            List of athlete's best times
        """
        soup = self.get_page(athlete_url)
        if not soup:
            return []
        
        results = []
        
        # Get athlete name
        h2 = soup.find('h2')
        athlete_name = h2.text.strip() if h2 else "Unknown"
        
        # Find "Best Discipline Results" section
        best_results_section = soup.find('h3', string=re.compile(r'Best Discipline Results'))
        if not best_results_section:
            return results
        
        table = best_results_section.find_next('table')
        if not table:
            return results
        
        rows = table.find_all('tr')
        for row in rows[1:]:  # Skip header
            cells = row.find_all('td')
            if len(cells) < 3:
                continue
            
            discipline_link = cells[0].find('a')
            discipline = discipline_link.text.strip() if discipline_link else cells[0].text.strip()
            
            # Only include Underhand Chop and Standing Block Chop
            if 'Underhand Chop' not in discipline and 'Standing Block Chop' not in discipline:
                continue
            
            time = cells[1].text.strip()
            
            event_link = cells[2].find('a')
            event = event_link.text.strip() if event_link else cells[2].text.strip()
            
            marker = cells[3].text.strip() if len(cells) > 3 else ""
            
            results.append({
                'Athlete': athlete_name,
                'Discipline': discipline,
                'Best Time': time,
                'Event': event,
                'Marker': marker
            })
        
        return results
    
    def scrape_all_events(self, season: Optional[str] = None, 
                         limit: Optional[int] = None,
                         athlete_filter: Optional[str] = None) -> pd.DataFrame:
        """
        Scrape all events and return DataFrame
        
        Args:
            season: Filter by season
            limit: Limit number of events
            athlete_filter: Filter results by athlete name (case-insensitive partial match)
            
        Returns:
            DataFrame with all results
        """
        events = self.get_events(season=season, limit=limit)
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
        '--season',
        type=str,
        help='Filter by season (e.g., 2025, 2024)',
        default=None
    )
    parser.add_argument(
        '--limit',
        type=int,
        help='Limit number of events to scrape',
        default=None
    )
    parser.add_argument(
        '--athlete',
        type=str,
        help='Filter by athlete name (partial match)',
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
    
    # Scrape data
    print("Starting scraper...")
    print(f"Season: {args.season or 'All'}")
    print(f"Event Limit: {args.limit or 'No limit'}")
    print(f"Athlete Filter: {args.athlete or 'All athletes'}")
    print("-" * 50)
    
    df = scraper.scrape_all_events(
        season=args.season,
        limit=args.limit,
        athlete_filter=args.athlete
    )
    
    if not df.empty:
        print(f"\nScraped {len(df)} results")
        print(f"Athletes found: {df['Competitor Name'].nunique()}")
        print(f"Events covered: {df['Event Name'].nunique()}")
        
        # Export to Excel
        scraper.export_to_excel(df, args.output)
        
        # Show sample
        print("\nSample of results:")
        print(df.head(10).to_string())
    else:
        print("No results found!")


if __name__ == '__main__':
    main()