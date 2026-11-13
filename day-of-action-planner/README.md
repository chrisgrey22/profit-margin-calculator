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

## In the mock-up as well

- **Signed in as (simulated).** A switch in the header shows the difference between a supervisor, who sees every crew, and an officer, who sees only their own crew's visits on the map and list.
- **Phone sat nav.** "Open phone sat nav" on any crew opens the crew's phone screen. A simulated drive follows the real road route, giving turn-by-turn directions with distance to the next turn and time to arrival. Each stop shows:
  - who the crew is going to see;
  - warning markers;
  - conditions (registration requirements, Sexual Harm Prevention Order, bail, licence, protection order);
  - what to look out for;
  - an on-scene checklist.

  The crew then moves on to the next stop and finally back to base.
- **Joint working dashboard.** The header button opens it. It shows:
  - visits planned against demand;
  - shared addresses done in one trip;
  - officer driving hours and miles saved against each team planning alone. The "alone" figures replan the same visits with same-team crews from each team's own stations;
  - crew trips;
  - FTE released and the value of that time a year, from editable assumptions: days a year, hours per FTE, manual planning hours and cost per hour;
  - how each crew's shift is used (on site, driving, waiting, spare);
  - demand by team;
  - the capacity gap;
  - an illustrative usage trend for the pilot.
- **Roster sync (simulated).** The header shows a sync from GRS (who is on duty) alongside Niche and ViSOR.

## For a production build

| Need | How |
|---|---|
| Who is working today | Read the day's duty roster from GRS or FIRMS: officer, team, station, shift times, skills and vehicles. Abstractions and sickness drop out automatically. |
| What needs doing | Read-only feeds from ViSOR (offender visits, device checks), Niche RMS (bail, Clare's Law applications, protection orders) and the IOM cohort. Addresses are matched by AddressBase UPRN. |
| Locked down | Force sign-in (Microsoft Entra ID) with roles. Supervisors see their area. Officers see only their own crew's visits, released at shift start and withdrawn at shift end. Every view and change is audited. DPIA, MoPI-compliant retention and force security accreditation are needed before go-live. |
| Sat nav on the phone | An app on force-managed phones under mobile device management. It uses GPS for turn-by-turn directions, re-routes, and moves on to the next visit automatically. Nothing is stored on the device after the shift. |
| Briefing at the door | Subject, PNC and Niche warning markers, current conditions, what to look out for, and an on-scene checklist. Results are written back to ViSOR or Niche. |
| Dashboard on live data | The same measures from real outcomes: visits completed rather than planned, actual miles from vehicle telematics, time on site from the phone app, and trends over weeks for the Senior Management Team. |
| Live view for supervisors | Each crew's position and progress, so visits can be moved if a crew is pulled to an incident. |
| Routing and mapping | A routing engine (OSRM, GraphHopper or Valhalla) hosted on the force network, with Ordnance Survey mapping under the Public Sector Geospatial Agreement. |

**Rules to keep:** every visit has two officers, with no lone visits. The officer from the owning team leads, and specialist-only offender visits stay with two MOSOVO officers.

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
