import sys
import os
import time

# Add current dir to path to find kademe_scraper
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from kademe_scraper import MatriksKademeScraper

def main():
    if len(sys.argv) < 2:
        print("Usage: python get_kademe_image.py SYMBOL [OUTPUT_PATH]")
        sys.exit(1)
    
    symbol = sys.argv[1].upper()
    
    # Define output path
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_dir = os.path.join(base_dir, "data", "matriks")
    os.makedirs(output_dir, exist_ok=True)
    
    if len(sys.argv) > 2:
        output_path = sys.argv[2]
    else:
        output_path = os.path.join(output_dir, f"{symbol}_kademe.png")
    
    print(f"Starting scraper for {symbol}...")
    scraper = MatriksKademeScraper()
    success = scraper.capture_kademe(symbol, output_path)
    
    if success:
        print(f"SUCCESS:{output_path}")
    else:
        print("FAILED: Window not found or error occurred.")
        sys.exit(1)

if __name__ == "__main__":
    main()
