import requests

LINKS = {
    "EoC": "https://www.runescape.com/community",
    "Old School": "https://oldschool.runescape.com/",
}

def scrape_website(version, link):
    r = requests.get(link)
    r.raise_for_status()

    if version == "Old School":
        # There are currently 81,702 people playing!
        player_count = r.content.split("There are currently ")[-1].split(" people playing!")[0]
    elif version == "EoC":
        # <span id="playerCount" class="c-responsive-header__player-count" data-test="header-sub-online-count">111,314</span>
        player_count = r.content.split("span id="playerCount")[0].split(">")[0].replace("</span>")
    return int(player_count.replace(",", ""))


def main():
    for link in LINKS:
        player_count = scrape_website(link, LINKS[link])
        
        # TODO: Write to a databse


if __name__ == "__main__":
    main()
    
