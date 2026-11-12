# Day of Action Visit Planner (mock-up)

A working mock-up of a tool that shares out Day of Action visits across officers and gives each officer a route and a run sheet, like a paper round. The visits are registered sex offender visits, bail address checks and Clare's Law disclosures.

**All case data is fictional.** No person, visit, address or reference comes from Niche RMS or ViSOR. The "Niche sync" in the header is an animation only. Visit pins are placed on real residential streets so that routing is realistic, but they are not real addresses.

**The map and routing are real.** The road network, coastline, rivers, woodland, local authority boundaries, place names and most police station locations come from OpenStreetMap, via Overture Maps release 2026-10-21. Cockett and Treharris stations are placed by hand and are approximate.

## Files

| File | What it is |
|---|---|
| `index.html` | The branded app. It is one self-contained file of about 2.6 MB: open it in Chrome or Edge, with no server or internet needed (fonts fall back if offline). |
| `visit-planner-unbranded.html` | The same app without the force name. |
| `pipeline/` | Scripts that rebuild the embedded map and road data from Overture Maps. |

## What it does

1. Takes a list of officers, each with a name, base station, team, start time and finish time. Examples are pre-filled and can be cleared.
2. Works out road travel times between every station and every visit, using Dijkstra's algorithm over 72,000 junctions and 85,000 road links (with one-way streets), in the browser.
3. Shares the visits out:
   - Only offender managers (Management of Sexual and Violent Offenders) lead registered sex offender visits.
   - Only the Domestic Abuse Unit gives Clare's Law disclosures.
   - Anyone can do a bail address check.
   - Overdue and higher-risk visits are placed first.
   - The times an applicant has said they can safely be seen are kept.
   - Each shift keeps a write-up period at the end.
4. Optimises each route (cheapest insertion, then 2-opt and relocate moves).
5. Produces a run sheet with arrival times, drive times and miles, and plain-English turn-by-turn directions for each leg, for example "Join M4 heading south-east, 3.6 miles".
6. Lets a supervisor click any pin and give that visit to a named officer, which rebuilds the routes straight away.

## For a production build

- **Routing:** replace the in-browser graph with OSRM, GraphHopper or Valhalla hosted on the force network, or an approved commercial routing API.
- **Base map:** use Ordnance Survey tiles under the Public Sector Geospatial Agreement.
- **Data:** read-only feeds from Niche RMS (bail, Domestic Violence Disclosure Scheme applications) and ViSOR (offender visit schedules), geocoded to AddressBase UPRNs, with an audit log of every view.
- **Security:** role-based access, so addresses are shown only to the allocated crew, and nothing is cached on the device.
- **Rules to keep:** the offender manager is always the named lead on registered sex offender visits, and specialist-only visits stay with two officers from the owning team.

The "Developer notes" button inside the app has the suggested data contract.

## Rebuilding the data

```bash
pip install pyarrow fsspec aiohttp requests shapely
python pipeline/fetch.py seg      # road segments for the force area
python pipeline/fetch.py places   # police stations
python pipeline/fetch.py div; python pipeline/fetch.py divp; python pipeline/fetch.py water; python pipeline/fetch.py land
python pipeline/build_graph.py segments2.parquet
python pipeline/build_base.py
python pipeline/encode.py         # writes appdata.json (graph + fictional visits)
python pipeline/build_page.py     # injects the data into template.html
```

The paths in `build_page.py` point at the original working folders, so adjust them first.

Map data © OpenStreetMap contributors (ODbL), Overture Maps Foundation.
