#!/usr/bin/env python3
"""Display the current time in local timezone."""

from datetime import datetime

def main():
    # Get current local time
    local_time = datetime.now()

    # Display in different formats
    print(f"Local Time (ISO 8601): {local_time.isoformat()}")
    print(f"Local Time (Readable): {local_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Unix Timestamp:        {local_time.timestamp()}")

if __name__ == "__main__":
    main()
