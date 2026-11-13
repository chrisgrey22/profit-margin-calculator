# Joint Visit Planner (mock-up)

## The problem

Several teams in the Strategic Public Protection Command visit offenders' home addresses, and each team plans its own visits:

- MOSOVO visits registered sex offenders.
- The Online Investigation Team checks devices under Sexual Harm Prevention Orders.
- The Domestic Abuse Unit gives Clare's Law disclosures and checks protection orders.
- Integrated Offender Management visits its cohort.
- BCU officers check bail addresses.

Because the teams plan in silos, separate crews go down the same streets, sometimes to the same front door, on the same day.

## What this tool does

It brings all of that demand into one plan:

- It pairs officers from different teams into **crews of two**. Nobody goes out alone.
- The specialist from the owning team always leads their own visit. Specialist-only offender visits need two MOSOVO officers.
- Bail checks are picked up along any crew's route.
- When several teams need the same address, the planner tries to send one crew that can cover all of it. The app shows how many shared addresses were done in a single trip.
- Each crew gets the most efficient road route from its station, with a turn-by-turn run sheet.

**All case data is fictional.** There are 113 invented records across six visit types, and 13 addresses are wanted by more than one team. None of it comes from Niche, ViSOR or any IOM system, and the "sync" is an animation only. Visit pins sit on real residential streets so the routing is realistic, but they are not real addresses.

**The map and routing are real.** The roads, coastline, boundaries, place names and most police stations come from OpenStreetMap via Overture Maps (release 2026-10-21). Cockett and Treharris stations are placed by hand and are approximate.

| Visit type | Owning team, who leads | Average time on site |
|---|---|---|
| Registered sex offender visit | MOSOVO | 1 hour |
| Device check (Sexual Harm Prevention Order) | Online Investigation Team | 45 min |
| Clare's Law disclosure | Domestic Abuse Unit | 30 min |
| Protection order compliance check | Domestic Abuse Unit | 20 min |
| Integrated Offender Management visit | Integrated Offender Management | 30 min |
| Bail address check | BCU officer | 10 min |

All the times on site can be changed on the day.

## Files

| File | What it is |
|---|---|
| `index.html` | The branded app (Joint Visit Planner). It is one self-contained file of about 2.6 MB: open it in Chrome or Edge, with no server or internet needed (fonts fall back if offline). |
| `visit-planner-unbranded.html` | The same app without the force name. |
| `pipeline/` | Scripts that rebuild the embedded map and road data from Overture Maps. |

## How it plans

1. **Travel times.** Dijkstra's shortest-path search runs over 72,000 road junctions, with one-way streets, from every station and every visit, in the browser.
2. **Crews.** A supervisor's own pairings come first. Anyone without a partner gets no visits.
3. **Priority.** Visits are sorted with device checks, shared addresses, overdue and higher-risk visits first, and safe time windows kept.
4. **Allocation.** Each visit goes to the eligible crew and position that adds the least time, with a strong preference for a crew already visiting that address. Each route is then improved with 2-opt and relocate moves.
5. **Supervisor control.** A supervisor can move any visit to a named crew, or re-pair officers, and the plan rebuilds immediately.

## For a production build

- **Routing:** replace the in-browser graph with OSRM, GraphHopper or Valhalla hosted on the force network, or an approved commercial routing API.
- **Base map:** use Ordnance Survey tiles under the Public Sector Geospatial Agreement.
- **Data:** read-only feeds from ViSOR (offender visits, device checks), Niche RMS (bail, Clare's Law applications, protection orders) and the IOM cohort. All are geocoded to AddressBase UPRNs so the same address is matched across teams, with an audit log of every view.
- **Security:** role-based access, so addresses are shown only to the allocated crew, and nothing is cached on the device.
- **Rules to keep:** every visit has two officers, with no lone visits. The MOSOVO officer is always the named lead on registered sex offender visits, and specialist-only visits stay with two officers from the owning team.

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
