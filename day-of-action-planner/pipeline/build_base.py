import pyarrow.parquet as pq, shapely, json
from shapely.geometry import box, mapping
from shapely.ops import unary_union
BB=box(-4.40,51.30,-3.00,51.90)
def q(geom):  # -> list of rings/lines as flat int arrays (1e-5 deg)
    out=[]
    def ring(cs):
        out.append([v for x,y in cs for v in (round(x*1e5),round(y*1e5))])
    def walk(g):
        t=g.geom_type
        if t=="Polygon":
            ring(g.exterior.coords); [ring(i.coords) for i in g.interiors]
        elif t=="LineString": ring(g.coords)
        elif t.startswith("Multi") or t=="GeometryCollection": [walk(x) for x in g.geoms]
    walk(geom); return out
d=pq.read_table("divareas.parquet").to_pylist()
SWP={"Swansea","Neath Port Talbot","Bridgend","Vale of Glamorgan","Rhondda Cynon Taf","Merthyr Tydfil","Cardiff"}
counties=[(r["names"]["primary"],shapely.from_wkb(r["geometry"])) for r in d if r["subtype"]=="county" and r["region"]=="GB-WLS"]
land=unary_union([g for n,g in counties]).intersection(BB).simplify(0.0004)
force=unary_union([g for n,g in counties if n in SWP]).simplify(0.0004)
la=[]
for n,g in counties:
    if n in SWP:
        c=g.representative_point()
        la.append({"name":n,"lines":q(g.boundary.intersection(BB).simplify(0.0004)),"cx":round(c.x*1e5),"cy":round(c.y*1e5)})
w=pq.read_table("water.parquet").to_pylist()
wpoly=[];wline=[]
for r in w:
    if r["subtype"] in("river","water","reservoir","lake","canal") and r["class"] not in("drain","ditch","wastewater","swimming_pool","fountain"):
        g=shapely.from_wkb(r["geometry"]).intersection(BB)
        if g.is_empty: continue
        if g.geom_type in("Polygon","MultiPolygon"):
            if g.area<2e-6: continue
            wpoly.append(g.simplify(0.00015))
        elif r["class"] in("river","canal"): wline.append(g.simplify(0.0002))
wp=unary_union(wpoly).simplify(0.00015)
l=pq.read_table("land.parquet").to_pylist()
woods=[]
for r in l:
    if r["subtype"] in("forest",) :
        g=shapely.from_wkb(r["geometry"])
        if g.geom_type in("Polygon","MultiPolygon") and g.area>1.2e-5: woods.append(g)
wd=unary_union(woods).intersection(BB).simplify(0.0005)
p=pq.read_table("divpts.parquet").to_pylist()
places=[]
for r in p:
    if r["subtype"] in("locality","macrohood","neighborhood"):
        g=shapely.from_wkb(r["geometry"])
        if not BB.contains(g): continue
        places.append({"n":r["names"]["primary"],"t":r["subtype"],"c":r.get("class"),"pop":r.get("population") or 0,"x":round(g.x*1e5),"y":round(g.y*1e5)})
places.sort(key=lambda x:-x["pop"]); places=[x for x in places if x["pop"]>=1500 or x["t"]!="locality"][:320]
base={"land":q(land),"force":q(force.boundary),"la":la,"water":q(wp),"rivers":q(unary_union(wline)),"woods":q(wd),"places":places}
s=json.dumps(base,separators=(",",":"))
open("base.json","w").write(s)
print(len(s), {k:len(json.dumps(v)) for k,v in base.items()})
print([(x["n"],x["t"],x["pop"]) for x in places[:40]])
