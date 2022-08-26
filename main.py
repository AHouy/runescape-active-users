from datetime import datetime
import html
import os

from bs4 import BeautifulSoup
import gspread
import requests

LINKS = {
    # "EoC": "https://www.runescape.com/community",
    "EoC": f"https://www.runescape.com/player_count.js?varname=iPlayerCount&callback=jQuery36006573490415341001_1661542575691&_={int(datetime.utcnow().timestamp() * 1000)}",
    "Old School": "https://oldschool.runescape.com/",
    # "Old School - Servers": "https://oldschool.runescape.com/slu",
}

def scrape_website(version, link):
    r = requests.get(link)
    r.raise_for_status()

    soup = BeautifulSoup(r.content, "html.parser")
    timestamp = datetime.utcnow().timestamp()
    if "Servers" in version:
        # We're scraping server list
        if version == "Old School - Servers":
            l = []
            for row in soup.find_all("tr", class_="server-list__row"):
                d = {}
                for entry in row.find_all("td"):
                    text = entry.text
                    if "server-list__row-cell--type" in entry["class"]:
                        if text == "Free":
                            # If the world type is a Free world, then break the for loop
                            # Replace the dictionary so we don't append it
                            d = None
                            break
                        d["type"] = text
                    elif "players" in entry.text:
                        d["players"] = int(text.replace(" players", ""))
                    elif entry.find_all("a"):
                        d["server"] = int(entry.find_all("a")[0].text.split()[-1])

                if d:
                    l.append(d)
            result = [[timestamp, d["players"], d["server"], d["type"]] for d in l]
    else:
        # We're not scraping a server list
        if version == "Old School":
            # There are currently 81,702 people playing!
            player_count = soup.find_all("p", class_="player-count")[0].text.split("There are currently ")[-1].split(" people playing!")[0]
        elif version == "EoC":
            # <span id="playerCount" class="c-responsive-header__player-count" data-test="header-sub-online-count">111,314</span>
            # player_count = soup.find_all("span", id="playerCount")[0].text

            # jQuery36006573490415341001_1661542575691(122045);
            player_count = r.text.split("(")[-1].split(")")[0]
        result = [[timestamp, int(player_count.replace(",", ""))]]

    return result


def main():
    # Open the spreadsheet
    gc = gspread.service_account(filename="service_account.json")
    ss = gc.open_by_key(os.environ.get("GOOGLE_SHEETS_ID"))

    # Iterate through each version of RuneScape
    for version in LINKS:
        # Get the worksheet
        ws = ss.worksheet(version)
        # Scrape website for player count
        data = scrape_website(version, LINKS[version])
        print(version, "---", *data)

        ws.append_rows(data)


if __name__ == "__main__":
    main()
    
