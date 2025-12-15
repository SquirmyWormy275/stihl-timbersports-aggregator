#!/usr/bin/env python3
"""
STIHL Timbersports Interactive Scraper
User-friendly menu interface - no command line needed!
"""

import sys
import os
from TimbersportsScraper import StihlTimberScraper
import pandas as pd


def clear_screen():
    """Clear the terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')


def print_header():
    """Print the application header"""
    print("=" * 70)
    print(" " * 15 + "STIHL TIMBERSPORTS DATA SCRAPER")
    print(" " * 20 + "Interactive Mode")
    print("=" * 70)
    print()


def print_section(title):
    """Print a section title"""
    print("\n" + "-" * 70)
    print(f"  {title}")
    print("-" * 70)


def get_input(prompt, default=None, valid_options=None):
    """Get user input with optional validation"""
    while True:
        if default:
            user_input = input(f"{prompt} [{default}]: ").strip()
            if not user_input:
                return default
        else:
            user_input = input(f"{prompt}: ").strip()
        
        if valid_options:
            if user_input.lower() in [opt.lower() for opt in valid_options]:
                return user_input
            else:
                print(f"Invalid input. Please choose from: {', '.join(valid_options)}")
        else:
            if user_input:
                return user_input
            elif not default:
                print("This field is required. Please enter a value.")


def confirm(message):
    """Ask for yes/no confirmation"""
    response = get_input(f"{message} (y/n)", "y", ["y", "n", "yes", "no"])
    return response.lower() in ["y", "yes"]


def main_menu():
    """Display and handle the main menu"""
    clear_screen()
    print_header()
    
    print("Welcome! This scraper will help you extract competition data.")
    print()
    print("Choose what you want to scrape:")
    print()
    print("  ATHLETE DATA (Recommended - Fast & Complete):")
    print("    1. Scrape specific athlete's complete history")
    print("    2. Scrape multiple athletes")
    print()
    print("  EVENT DATA (Comprehensive but Slower):")
    print("    3. Scrape a single season")
    print("    4. Scrape multiple seasons")
    print("    5. Scrape ALL available seasons (auto-detect)")
    print()
    print("  OTHER:")
    print("    6. Quick test (5 recent events)")
    print("    7. Exit")
    print()
    
    choice = get_input("Enter your choice (1-7)", valid_options=["1", "2", "3", "4", "5", "6", "7"])
    return choice


def scrape_single_athlete():
    """Interactive flow for scraping a single athlete"""
    print_section("Scrape Single Athlete")

    print("\nThis will get ALL SB and UH results for the athlete from their entire career.")
    print("Examples: 'Hodges', 'Cogar', 'LaVoie', 'Slingerland'")
    print()

    athlete_name = get_input("Enter athlete name (or part of name)")

    # Get output filename
    default_filename = f"{athlete_name.lower().replace(' ', '_')}_results.xlsx"
    output_file = get_input("Output filename", default_filename)
    if not output_file.endswith('.xlsx'):
        output_file += '.xlsx'

    # Confirm
    print()
    print("Ready to scrape:")
    print(f"  Athlete: {athlete_name}")
    print(f"  Output: {output_file}")
    print()

    if not confirm("Start scraping?"):
        return False

    # Scrape with auto-detection of all available seasons
    print()
    print("=" * 70)
    print("Step 1: Auto-detecting all available seasons...")
    print("=" * 70)
    scraper = StihlTimberScraper(delay=1.0)
    seasons_to_search = scraper.detect_all_available_seasons()

    print()
    print("=" * 70)
    print(f"Step 2: Searching for {athlete_name} in {len(seasons_to_search)} seasons...")
    print("=" * 70)
    df = scraper.scrape_athlete_profile(athlete_name, seasons_to_search=seasons_to_search)
    
    if not df.empty:
        scraper.export_to_excel(df, output_file)
        print("=" * 70)
        print()
        print(f"[OK] SUCCESS! Found {len(df)} results")
        print(f"[OK] Saved to: {output_file}")
        print()
        print("Preview:")
        print(df[['Competitor Name', 'Discipline', 'Time', 'Event Name']].head(10).to_string())
    else:
        print("=" * 70)
        print()
        print("[ERROR] No results found!")
        print("Try:")
        print("  • Check spelling")
        print("  • Use a shorter/partial name")
        print("  • Try just the last name")
    
    return True


def scrape_multiple_athletes():
    """Interactive flow for scraping multiple athletes"""
    print_section("Scrape Multiple Athletes")
    
    print("\nYou can scrape several athletes at once.")
    print("Each athlete will get their own Excel file.")
    print()
    
    athletes = []
    while True:
        athlete_name = get_input(f"Enter athlete name #{len(athletes)+1} (or press Enter to finish)")
        if not athlete_name:
            if len(athletes) == 0:
                print("You need to enter at least one athlete name!")
                continue
            break
        athletes.append(athlete_name)
        print(f"  Added: {athlete_name}")
    
    # Confirm
    print()
    print(f"Ready to scrape {len(athletes)} athletes:")
    for i, athlete in enumerate(athletes, 1):
        print(f"  {i}. {athlete}")
    print()
    
    if not confirm("Start scraping?"):
        return False

    # Auto-detect all available seasons once
    print()
    print("=" * 70)
    print("Step 1: Auto-detecting all available seasons...")
    print("=" * 70)
    scraper = StihlTimberScraper(delay=1.0)
    seasons_to_search = scraper.detect_all_available_seasons()

    # Scrape each athlete
    successful = 0

    for i, athlete_name in enumerate(athletes, 1):
        print()
        print("=" * 70)
        print(f"Step 2.{i}: Scraping athlete {i}/{len(athletes)}: {athlete_name}")
        print(f"Searching {len(seasons_to_search)} seasons...")
        print("=" * 70)

        output_file = f"{athlete_name.lower().replace(' ', '_')}_results.xlsx"
        df = scraper.scrape_athlete_profile(athlete_name, seasons_to_search=seasons_to_search)
        
        if not df.empty:
            scraper.export_to_excel(df, output_file)
            print(f"[OK] Found {len(df)} results - saved to {output_file}")
            successful += 1
        else:
            print(f"[ERROR] No results found for {athlete_name}")
    
    print()
    print("=" * 70)
    print(f"Completed! Successfully scraped {successful}/{len(athletes)} athletes")
    print("=" * 70)
    
    return True


def scrape_single_season():
    """Interactive flow for scraping a single season"""
    print_section("Scrape Single Season")
    
    print("\nThis will scrape all events from a specific year.")
    print("Note: This can take 10-20 minutes for a full year!")
    print()
    
    season = get_input("Enter season year (e.g., 2024, 2023, 2016)", "2024")
    
    # Ask about limit
    use_limit = confirm("\nDo you want to limit the number of events? (recommended for testing)")
    
    if use_limit:
        limit = int(get_input("How many events to scrape?", "10"))
    else:
        limit = None
        print("\n[WARNING] This will scrape ALL events from that year (may take a while)")
    
    # Get output filename
    default_filename = f"season_{season}_results.xlsx"
    output_file = get_input("Output filename", default_filename)
    if not output_file.endswith('.xlsx'):
        output_file += '.xlsx'
    
    # Confirm
    print()
    print("Ready to scrape:")
    print(f"  Season: {season}")
    print(f"  Limit: {limit if limit else 'None (all events)'}")
    print(f"  Output: {output_file}")
    print()
    
    if not confirm("Start scraping?"):
        return False
    
    # Scrape
    print()
    print("=" * 70)
    scraper = StihlTimberScraper(delay=1.0)
    df = scraper.scrape_all_events(season=season, limit=limit)
    
    if not df.empty:
        scraper.export_to_excel(df, output_file)
        print()
        print("=" * 70)
        print(f"[OK] SUCCESS! Found {len(df)} results from {df['Event Name'].nunique()} events")
        print(f"[OK] Saved to: {output_file}")
    else:
        print()
        print("=" * 70)
        print("[ERROR] No results found!")
    
    return True


def scrape_multiple_seasons():
    """Interactive flow for scraping multiple seasons"""
    print_section("Scrape Multiple Seasons")
    
    print("\nThis will scrape all events from multiple years.")
    print("[WARNING] This can take 30+ minutes depending on how many years!")
    print()
    
    seasons = []
    print("Enter the years you want to scrape (one at a time):")
    while True:
        season = get_input(f"Year #{len(seasons)+1} (or press Enter to finish)")
        if not season:
            if len(seasons) == 0:
                print("You need to enter at least one year!")
                continue
            break
        seasons.append(season)
        print(f"  Added: {season}")
    
    # Ask about limit
    use_limit = confirm("\nDo you want to limit the number of events per season?")
    
    if use_limit:
        limit = int(get_input("How many events per season?", "10"))
    else:
        limit = None
    
    # Get output filename
    default_filename = f"seasons_{'_'.join(seasons)}_results.xlsx"
    output_file = get_input("Output filename", default_filename)
    if not output_file.endswith('.xlsx'):
        output_file += '.xlsx'
    
    # Confirm
    print()
    print("Ready to scrape:")
    print(f"  Seasons: {', '.join(seasons)}")
    print(f"  Limit per season: {limit if limit else 'None (all events)'}")
    print(f"  Output: {output_file}")
    print()
    
    if not confirm("Start scraping?"):
        return False
    
    # Scrape
    print()
    print("=" * 70)
    scraper = StihlTimberScraper(delay=1.0)
    df = scraper.scrape_all_events(seasons_list=seasons, limit=limit)
    
    if not df.empty:
        scraper.export_to_excel(df, output_file)
        print()
        print("=" * 70)
        print(f"[OK] SUCCESS! Found {len(df)} results from {df['Event Name'].nunique()} events")
        print(f"[OK] Saved to: {output_file}")
    else:
        print()
        print("=" * 70)
        print("[ERROR] No results found!")
    
    return True


def scrape_last_5_years():
    """Quick option for all available seasons"""
    print_section("Scrape ALL Available Seasons (Auto-Detect)")

    print("\n[WARNING] This will auto-detect and scrape ALL years with data!")
    print("First, we'll detect what seasons are available on the website.")
    print("This can take 30-60+ minutes depending on how much historical data exists.")
    print()

    # Ask about limit for testing
    test_mode = confirm("Do you want to run in TEST MODE first? (limits to 10 events per year)")

    if test_mode:
        limit = 10
        output_file = "test_all_seasons.xlsx"
        print("\n[OK] Test mode enabled - will scrape 10 events per year")
    else:
        limit = None
        output_file = get_input("Output filename", "all_seasons_complete.xlsx")
        if not output_file.endswith('.xlsx'):
            output_file += '.xlsx'

    # Auto-detect seasons
    print()
    print("=" * 70)
    print("Step 1: Auto-detecting available seasons...")
    print("=" * 70)
    scraper = StihlTimberScraper(delay=1.0)
    seasons_list = scraper.detect_all_available_seasons()

    if not seasons_list:
        print("\n[ERROR] Could not detect any available seasons!")
        return False

    # Confirm
    print()
    print("Ready to scrape:")
    print(f"  Seasons detected: {', '.join(seasons_list)}")
    print(f"  Total seasons: {len(seasons_list)}")
    print(f"  Mode: {'TEST (10 events/year)' if test_mode else 'FULL (all events)'}")
    print(f"  Output: {output_file}")
    print()

    if not confirm("Start scraping?"):
        return False

    # Scrape
    print()
    print("=" * 70)
    print("Step 2: Scraping events from all seasons...")
    print("=" * 70)
    df = scraper.scrape_all_events(seasons_list=seasons_list, limit=limit)
    
    if not df.empty:
        scraper.export_to_excel(df, output_file)
        print()
        print("=" * 70)
        print(f"[OK] SUCCESS! Found {len(df)} results from {df['Event Name'].nunique()} events")
        print(f"[OK] Saved to: {output_file}")
    else:
        print()
        print("=" * 70)
        print("[ERROR] No results found!")
    
    return True


def quick_test():
    """Quick test with 5 recent events"""
    print_section("Quick Test (5 Recent Events)")
    
    print("\nThis will scrape just 5 recent events as a quick test.")
    print("Good for seeing how the scraper works before doing a full scrape.")
    print()
    
    if not confirm("Start quick test?"):
        return False
    
    # Scrape
    print()
    print("=" * 70)
    scraper = StihlTimberScraper(delay=1.0)
    df = scraper.scrape_all_events(limit=5)
    
    if not df.empty:
        output_file = "quick_test_results.xlsx"
        scraper.export_to_excel(df, output_file)
        print()
        print("=" * 70)
        print(f"[OK] SUCCESS! Found {len(df)} results from {df['Event Name'].nunique()} events")
        print(f"[OK] Saved to: {output_file}")
        print()
        print("Preview:")
        print(df[['Competitor Name', 'Discipline', 'Time', 'Event Name']].head(15).to_string())
    else:
        print()
        print("=" * 70)
        print("[ERROR] No results found!")
    
    return True


def main():
    """Main application loop"""
    while True:
        choice = main_menu()
        
        if choice == "1":
            scrape_single_athlete()
        elif choice == "2":
            scrape_multiple_athletes()
        elif choice == "3":
            scrape_single_season()
        elif choice == "4":
            scrape_multiple_seasons()
        elif choice == "5":
            scrape_last_5_years()
        elif choice == "6":
            quick_test()
        elif choice == "7":
            print("\nGoodbye!")
            sys.exit(0)
        
        # Ask if user wants to continue
        print()
        if not confirm("\nDo you want to scrape more data?"):
            print("\nThank you for using STIHL Timbersports Scraper!")
            print("Your Excel files are ready to use.")
            break


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nScraping cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n\nError: {e}")
        print("Please report this error if it persists.")
        sys.exit(1)