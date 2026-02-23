from tvDatafeed import TvDatafeed, Interval
import sys

try:
    print("Connecting to TvDatafeed...")
    tv = TvDatafeed()
    print("Attempting to fetch THYAO from BIST...")
    data = tv.get_hist(symbol='THYAO', exchange='BIST', interval=Interval.in_daily, n_bars=1)
    if data is not None:
        print("Success!")
        print(data)
    else:
        print("Failed: Data is None")
except Exception as e:
    print(f"Error: {e}")
