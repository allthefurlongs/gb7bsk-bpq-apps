import sys
import json
from datetime import datetime
import requests

with open('report-to-map.json') as f:
    conf = json.load(f)

lon = None
lat = None
maidenhead = None
randomise = None

# Unless configured otherwise, BPQ sends the user callsign at the start
user_call = sys.stdin.readline().rstrip()
user_call = user_call.upper()

print("")
print("MAP command - report your location to https://nodes.ukpacketradio.network/packet-network-map.html")
print("")
print("Enter /q to quit at any prompt to abort reporting to the map.")
print("")
print("GPS (e.g. 51.59777, 1.34220), or maidenhead grid (eg. IO90ro): ", end="")
sys.stdout.flush()
location = sys.stdin.readline().rstrip()
if location == '/q':
  print("MAP aborted, returning to node.")
  exit()
if ',' in location:
  fields = location.split(',')
  if len(fields) != 2:
    print("Unrecognised GPS coordinates. Expected lat lon format: 51.59777, 1.34220")
    print("MAP aborted, returning to node.")
    exit()
  fields[1] = fields[1].lstrip()
  try:
    lat = float(fields[0])
    lon = float(fields[1])
  except (ValueError, TypeError):
    print("Unrecognised GPS coordinates. Expected format: 51.59777, 1.34220")
    print("MAP aborted, returning to node.")
    exit()
else:
  maidenhead = location
print("Slightly randomise your location on the map [Y/N]: ", end="")
sys.stdout.flush()
while randomise != 'Y' and randomise != 'N' and randomise != '/Q':
  if randomise is not None:
    print("Unrecognised option\nSlightly randomise your location on the map [Y/N]: ", end="")
    sys.stdout.flush()
  randomise = sys.stdin.readline().rstrip()
  randomise = randomise.upper()
if randomise == '/Q':
  print("MAP aborted, returning to node.")
  exit()

now = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
report = {
  "location": {
    "randomised": randomise == 'Y'
  },
  "sysopComment": f"Reported via MAP command on {conf['node_call']}",
  "source": "ReportedByNode",
  "mheard": [
    {
      "callsign": {conf['node_call']},
      "port": "1",
      "packets": 1,
      "firstHeard": now,
      "lastHeard": now,
      "coords": {
        "lat": 51.28215,
        "lon": -1.12489
      }
    }
  ]
}
if maidenhead is not None:
  report['location']['locator'] = maidenhead
elif lat is not None and lon is not None:
  report['location']['coords'] = {
    "lat": lat,
    "lon": lon
  }

try:
    requests.post(f"https://nodes.ukpacketradio.network/api/nodedata/{user_call}", report)
    print("MAP report complete, returning to node.")
except requests.exceptions.RequestException as e:
    print(f"Error submitting map report: {e}")
    print("Returning to node.")
