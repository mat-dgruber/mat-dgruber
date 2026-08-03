import json
import os
import re
import requests
from bs4 import BeautifulSoup

def fetch_contributions(username: str = "mat-dgruber", output_json: str = "data/contributions.json") -> dict:
    url = f"https://github.com/users/{username}/contributions"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    days = []

    # Find elements with data-date attribute
    day_elements = soup.find_all(attrs={"data-date": True})
    for el in day_elements:
        date_str = el.get("data-date")
        level = int(el.get("data-level", 0))
        count = 0

        # Try tool-tip element associated by for="id"
        el_id = el.get("id")
        tooltip = soup.find("tool-tip", attrs={"for": el_id}) if el_id else None
        tooltip_text = tooltip.get_text(strip=True) if tooltip else el.get("aria-label", "")

        if tooltip_text:
            match = re.search(r"(\d+)\s+contribution", tooltip_text)
            if match:
                count = int(match.group(1))
            elif "no contribution" in tooltip_text.lower():
                count = 0
        elif el.get("data-count"):
            count = int(el.get("data-count"))

        days.append({
            "date": date_str,
            "count": count,
            "level": level
        })

    total_contributions = 0
    h2 = soup.find("h2")
    if h2:
        h2_text = h2.get_text(strip=True)
        match = re.search(r"([\d,]+)\s+contribution", h2_text)
        if match:
            total_contributions = int(match.group(1).replace(",", ""))

    if total_contributions == 0 and days:
        total_contributions = sum(d["count"] for d in days)

    result = {
        "username": username,
        "total_contributions": total_contributions,
        "days": days
    }

    dir_name = os.path.dirname(output_json)
    if dir_name:
        os.makedirs(dir_name, exist_ok=True)

    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

    return result

if __name__ == "__main__":
    fetch_contributions("mat-dgruber")
