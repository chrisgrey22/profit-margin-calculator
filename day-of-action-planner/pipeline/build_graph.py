import pyarrow.parquet as pq, shapely, json, sys, collections, pickle
from shapely.ops import substring
from shapely.geometry import LineString
SRC=sys.argv[1]
CLS={"motorway":0,"trunk":1,"primary":2,"secondary":3,"tertiary":4,"unclassified":5,"residential":6,"living_street":7}
cols=["id","geometry","class","names","connectors","access_restrictions"]
has_routes="routes" in pq.ParquetFile(SRC).schema_arrow.names
if has_routes: cols.append("routes")
t=pq.read_table(SRC,columns=cols)
rows=t.to_pylist()
print("rows",len(rows),flush=True)
names=[""];nidx={"":0}
def ni(s):
    s=s or ""
    if s not in nidx: nidx[s]=len(names);names.append(s)
    return nidx[s]
def motor(a):
    w=a.get("when") or {}
    m=w.get("mode")
    return m is None or any(x in m for x in("motor_vehicle","car","vehicle"))
nodes={}  # connector id -> idx
ncoord=[]
edges=[]
for r in rows:
    c=r["class"]
    if c not in CLS: continue
    if r["geometry"] is None: continue
    oneway=0; skip=False
    for a in (r["access_restrictions"] or []):
        if a.get("between") is not None: continue
        w=a.get("when") or {}
        if a["access_type"]=="denied" and motor(a) and not w.get("using") and not w.get("during"):
            h=w.get("heading")
            if h=="backward": oneway=1
            elif h=="forward": oneway=2
            elif h is None and w.get("vehicle") is None: skip=True
    if skip and CLS[c]>=5: continue
    line=shapely.from_wkb(r["geometry"])
    if line.geom_type!="LineString": continue
    nm=(r["names"] or {}).get("primary") or ""
    ref=""
    if has_routes:
        refs=[x.get("ref") for x in (r["routes"] or []) if x.get("ref") and not x.get("between")]
        refs=[x for x in refs if x[:1] in "MAB" and x[1:2].isdigit()] or refs
        if refs: ref=refs[0]
    con=sorted([(x["at"],x["connector_id"]) for x in (r["connectors"] or [])])
    if len(con)<2: continue
    for (a0,c0),(a1,c1) in zip(con,con[1:]):
        if a1<=a0: continue
        sub=substring(line,a0,a1,normalized=True)
        if sub.geom_type!="LineString" or sub.length==0: continue
        co=list(sub.coords)
        for cid,pt in((c0,co[0]),(c1,co[-1])):
            if cid not in nodes: nodes[cid]=len(ncoord);ncoord.append(pt)
        u=nodes[c0];v=nodes[c1]
        if u==v: continue
        co[0]=ncoord[u];co[-1]=ncoord[v]
        edges.append([u,v,CLS[c],oneway,ni(nm),ni(ref),co])
print("nodes",len(ncoord),"edges",len(edges),flush=True)
# largest component
adj=collections.defaultdict(list)
for i,e in enumerate(edges): adj[e[0]].append(i);adj[e[1]].append(i)
seen={};best=None;comp=0
for s in range(len(ncoord)):
    if s in seen or s not in adj: continue
    stack=[s];seen[s]=comp;cnt=0
    while stack:
        x=stack.pop();cnt+=1
        for ei in adj[x]:
            e=edges[ei];y=e[1] if e[0]==x else e[0]
            if y not in seen: seen[y]=comp;stack.append(y)
    if best is None or cnt>best[1]: best=(comp,cnt)
    comp+=1
edges=[e for e in edges if seen.get(e[0])==best[0]]
print("kept edges",len(edges),flush=True)
# merge degree-2 chains
alive=[True]*len(edges)
inc=collections.defaultdict(list)
for i,e in enumerate(edges): inc[e[0]].append(i);inc[e[1]].append(i)
def rev(e): return [e[1],e[0],e[2],{0:0,1:2,2:1}[e[3]],e[4],e[5],e[6][::-1]]
changed=True;merged=0
for n in list(inc.keys()):
    lst=[i for i in inc[n] if alive[i]]
    if len(lst)!=2: continue
    a,b=lst
    if a==b: continue
    ea,eb=edges[a],edges[b]
    if ea[2:6:1][0]!=eb[2] or ea[4]!=eb[4] or ea[5]!=eb[5]: continue
    # orient ea to end at n, eb to start at n
    if ea[1]!=n: ea=rev(ea)
    if eb[0]!=n: eb=rev(eb)
    if ea[1]!=n or eb[0]!=n: continue
    if ea[3]!=eb[3]: continue
    if ea[0]==eb[1]: continue
    ne=[ea[0],eb[1],ea[2],ea[3],ea[4],ea[5],ea[6]+eb[6][1:]]
    edges[a]=ne;alive[b]=False
    inc[eb[1]]=[a if i==b else i for i in inc[eb[1]]]
    inc[n]=[]
    merged+=1
edges=[e for i,e in enumerate(edges) if alive[i]]
print("after merge",len(edges),flush=True)
for e in edges:
    ls=LineString(e[6]).simplify(0.00003)
    e[6]=list(ls.coords)
used=sorted(set([e[0] for e in edges]+[e[1] for e in edges]))
remap={o:i for i,o in enumerate(used)}
nodes_out=[ncoord[o] for o in used]
for e in edges: e[0]=remap[e[0]];e[1]=remap[e[1]]
pickle.dump({"nodes":nodes_out,"edges":edges,"names":names},open("graph.pkl","wb"))
print("final nodes",len(nodes_out),"edges",len(edges),"pts",sum(len(e[6]) for e in edges))
