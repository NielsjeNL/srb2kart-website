# SRB2Kart Website
This repo contains the SRB2Kart website hosted on https://srb2kart.aqua.fyi.
It is tailored to fit the needs of the Aqua's Karthouse community.

To give the website your own style, fork the repo and customize the files to your needs.

### Running the website
First install the necessary requirements:
```Python
pip install -r requirements.txt
```
Then setup `config.json` inside the `srb2kartwebsite` folder. There's an example file that can help you.

When ready, launch the code as follows in a testing environment:
```
srb2kartwebsite> python kartsite.py
```
In production, use gunicorn instead:
```
python3 -m gunicorn --bind 0.0.0.0:5000 wsgi:app
```

### JSON Data sources
The website can use some JSON data sources to enrich information on the website. Below you'll find an explanation of the used data sources with the key-value pairs used in the JSON files.

The `examples` folder contains empty JSON files you can start filling yourself. JSON files with the `filled` suffix contain some real-world data to help you understand how the JSON files are filled.

#### `allmaps.json`
| **Key** | **Description** |
|---|---|
| `packs` | A dict of all map packs in use on your server. Every key contains a dict value detailing all maps with their SOC information. See the filled example for more info. |
| `customSOCs` | An optional list of custom SOCs. If a custom SOC exists for a map from a map pack in `packs`, it's info will be overwritten with info from this dict. |
| `ranks` | An optional dict of [Aqua's Map Ranking Script](https://mb.srb2.org/addons/aquas-map-ranking-script.4902/) scores. |
| `totalPacks` | Total map packs on your server. |
| `totalMaps` | Total amount of individual maps on your server. |
| `raceMaps` | Amount of maps that are race maps. |
| `battleMaps` | Amount of maps that are battle maps. |
| `hiddenMaps` | Amount of maps that are hidden from gameplay (`TypeOfLevel = SinglePlayer`) |
| `customRaceMaps` | Not used. |
| `customBattleMaps` | Not used. |
| `customSinglePlayerMaps` | Amount of custom SOCs that have `TypeOfLevel = Singleplayer` defined. |
| `customHiddenMaps` | Amount of custom SOCs that have `Hidden = True` defined. |
| `customLaps` | Amount of custom SOCs that change the default number of laps. |
| `leaderboard` | An optional dict containing data from [!Not's Time Attack Leaderboard](https://mb.srb2.org/addons/time-attack-leaderboard.3742/). Every key in the dict is a map with it's value being a list of data from the leaderboard. |
| `statTrackerMapData` | An optional dict containing data from [Onyo's StatTracker](https://mb.srb2.org/addons/stattracker.3992/). Every key in the dict is a map with it's values being how often a race finished and how often a race was RTV'd. |
| `players` | An optional dict containing the amount of records a player has from the Time Attack Leaderboard. First value is the amount of first places, second value amount of second places, third value amount of third places and last value total amount of records. |

#### `kartusers.json`
| **Key** | **Description** |
|---|---|
| `kartUsers` | A dict where a key is a Discord user's ID with it's values being their SRB2Kart netgame name and their Discord username. Discriminators are not stored or used. |
| `kartUserRequests` | Not used. |

#### `skininfo.json`
| **Key** | **Description** |
|---|---|
| `[skin's realname]` | Every key in this JSON file is a SRB2Kart skin's realname. It's value is a dict containing all values from the skin's definition (read from their PK3/WAD) and the name of the file. |