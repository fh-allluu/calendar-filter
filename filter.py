import os
import re
import sys
import urllib.request

SOURCE_URL = os.environ.get("CALENDAR_SOURCE_URL")
OUTPUT_FILE = "calendar_filtered.ics"
EXCLUDE_KEYWORDS = ["software engineering"]  # add more lowercase keywords here to exclude more

def main():
    if not SOURCE_URL:
        print("ERROR: CALENDAR_SOURCE_URL environment variable is not set.", file=sys.stderr)
        sys.exit(1)

    req = urllib.request.Request(SOURCE_URL, headers={"User-Agent": "Mozilla/5.0"})
    raw = urllib.request.urlopen(req).read().decode("utf-8")

    header, rest = raw.split("BEGIN:VEVENT", 1)
    events_raw = ("BEGIN:VEVENT" + rest).rsplit("END:VCALENDAR", 1)[0]
    footer = "END:VCALENDAR\n"

    events = re.findall(r"BEGIN:VEVENT.*?END:VEVENT", events_raw, re.DOTALL)

    kept = []
    removed = 0
    for ev in events:
        m = re.search(r"^SUMMARY:(.*)$", ev, re.MULTILINE)
        summary = (m.group(1) if m else "").lower()
        if any(kw in summary for kw in EXCLUDE_KEYWORDS):
            removed += 1
            continue
        kept.append(ev)

    output = header + "\n".join(kept) + "\n" + footer

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(output)

    print(f"Kept {len(kept)} events, removed {removed} events matching {EXCLUDE_KEYWORDS}")

if __name__ == "__main__":
    main()
