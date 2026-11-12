import pickle, base64, json, random, math
g=pickle.load(open("graph.pkl","rb"))
nodes,edges,names=g["nodes"],g["edges"],g["names"]
buf=bytearray()
def uv(n):
    while True:
        b=n&0x7f;n>>=7
        if n: buf.append(b|0x80)
        else: buf.append(b);return
def sv(n): uv((n<<1) if n>=0 else ((-n<<1)-1))
Q=[(round(x*1e5),round(y*1e5)) for x,y in nodes]
uv(len(Q));px=py=0
for x,y in Q: sv(x-px);sv(y-py);px,py=x,y
uv(len(edges))
for u,v,c,ow,nm,rf,co in edges:
    uv(u);sv(v-u);buf.append(c|(ow<<4));uv(nm);uv(rf)
    inner=co[1:-1];uv(len(inner))
    px,py=Q[u]
    for x,y in inner:
        x=round(x*1e5);y=round(y*1e5);sv(x-px);sv(y-py);px,py=x,y
b64=base64.b64encode(bytes(buf)).decode()
print("graph bytes",len(buf),"b64",len(b64))
# ---------- stations
ST=[
 dict(id="CKT",name="Cockett",lat=51.6372,lon=-3.9858,approx=True,teams=["MOSOVO","DAU"],hub="W",role="Western hub"),
 dict(id="SWC",name="Swansea Central",lat=51.62211,lon=-3.94604,approx=False,teams=["MOSOVO"],hub="W",role="Feeds Western hub"),
 dict(id="TRH",name="Treharris",lat=51.6655,lon=-3.3040,approx=True,teams=["MOSOVO","DAU"],hub="N",role="Central North hub"),
 dict(id="BGD",name="Bridgend",lat=51.50483,lon=-3.57514,approx=False,teams=["MOSOVO","POLIT"],hub="S",role="Central South hub"),
 dict(id="CFC",name="Cardiff Central",lat=51.48517,lon=-3.1807,approx=False,teams=["MOSOVO"],hub="E",role="Eastern hub"),
 dict(id="CFB",name="Cardiff Bay",lat=51.46473,lon=-3.17046,approx=False,teams=["DAU"],hub="E",role="Feeds Eastern hub"),
]
import collections
deg=collections.Counter()
resid=set()
for u,v,c,ow,nm,rf,co in edges:
    deg[u]+=1;deg[v]+=1
    if c in(6,7,5): resid.add(u);resid.add(v)
def dm(a,b):  # metres between (lon,lat)
    return math.hypot((a[0]-b[0])*69400,(a[1]-b[1])*111200)
def nearest(lon,lat,pool=None):
    best=None
    for i,(x,y) in enumerate(nodes):
        if pool is not None and i not in pool: continue
        d=dm((x,y),(lon,lat))
        if best is None or d<best[0]: best=(d,i)
    return best
for s in ST:
    d,i=nearest(s["lon"],s["lat"]);s["node"]=i;s["snap_m"]=round(d)
rnd=random.Random(20261120)
AREAS={
 "W":[("Townhill",51.632,-3.962,"Swansea"),("Morriston",51.668,-3.928,"Swansea"),("Gorseinon",51.668,-4.042,"Swansea"),("Sketty",51.618,-3.983,"Swansea"),("Bonymaen",51.643,-3.913,"Swansea"),("Penlan",51.648,-3.951,"Swansea"),("St Thomas",51.624,-3.928,"Swansea"),("Clydach",51.693,-3.903,"Swansea"),("Killay",51.616,-4.013,"Swansea"),("Mumbles",51.572,-3.999,"Swansea"),("Neath",51.663,-3.806,"Neath Port Talbot"),("Briton Ferry",51.632,-3.820,"Neath Port Talbot"),("Sandfields",51.585,-3.810,"Neath Port Talbot"),("Pontardawe",51.722,-3.852,"Neath Port Talbot"),("Skewen",51.659,-3.846,"Neath Port Talbot")],
 "N":[("Gurnos",51.762,-3.379,"Merthyr Tydfil"),("Dowlais",51.761,-3.350,"Merthyr Tydfil"),("Aberdare",51.713,-3.445,"Rhondda Cynon Taf"),("Mountain Ash",51.681,-3.378,"Rhondda Cynon Taf"),("Treorchy",51.659,-3.506,"Rhondda Cynon Taf"),("Ferndale",51.660,-3.447,"Rhondda Cynon Taf"),("Porth",51.613,-3.408,"Rhondda Cynon Taf"),("Pontypridd",51.602,-3.342,"Rhondda Cynon Taf"),("Treharris",51.665,-3.307,"Merthyr Tydfil"),("Abercynon",51.645,-3.327,"Rhondda Cynon Taf")],
 "S":[("Bridgend town",51.506,-3.577,"Bridgend"),("Wildmill",51.515,-3.576,"Bridgend"),("Brackla",51.508,-3.555,"Bridgend"),("Pencoed",51.524,-3.505,"Bridgend"),("Porthcawl",51.483,-3.700,"Bridgend"),("Pyle",51.528,-3.698,"Bridgend"),("Maesteg",51.610,-3.657,"Bridgend"),("Caerau",51.627,-3.659,"Bridgend"),("Tonypandy",51.621,-3.452,"Rhondda Cynon Taf"),("Tonyrefail",51.584,-3.433,"Rhondda Cynon Taf"),("Talbot Green",51.540,-3.380,"Rhondda Cynon Taf")],
 "E":[("Ely",51.481,-3.248,"Cardiff"),("Caerau (Cardiff)",51.473,-3.245,"Cardiff"),("Splott",51.477,-3.155,"Cardiff"),("Adamsdown",51.484,-3.163,"Cardiff"),("Grangetown",51.468,-3.185,"Cardiff"),("Butetown",51.465,-3.170,"Cardiff"),("St Mellons",51.524,-3.110,"Cardiff"),("Llanrumney",51.522,-3.130,"Cardiff"),("Trowbridge",51.519,-3.116,"Cardiff"),("Pentwyn",51.531,-3.140,"Cardiff"),("Llanishen",51.530,-3.183,"Cardiff"),("Cathays",51.490,-3.180,"Cardiff"),("Fairwater",51.490,-3.235,"Cardiff"),("Barry",51.403,-3.270,"Vale of Glamorgan"),("Penarth",51.436,-3.177,"Vale of Glamorgan"),("Llantwit Major",51.408,-3.484,"Vale of Glamorgan")],
}
COUNTS={"W":(9,6,5),"N":(6,4,4),"S":(6,5,4),"E":(10,7,6)}
FIRST=list("ABCDEGHJKLMNPRSTW")
FLAGS_RSO=["Dog at address","Lives with partner, partner aware of conviction","Shift worker, usually home before 13:00","Internet-enabled devices to examine (Police Online Investigation Team)","Known to be hostile to police","Second address declared","Recent change of vehicle not yet notified","Requested a female officer","Uses Welsh as first language"]
FLAGS_BAIL=["Condition: live and sleep at this address","Condition: not to contact the complainant","Condition: curfew 19:00 to 07:00","Condition: report to the police station weekly","Address supplied by the defence, not yet verified"]
FLAGS_DVDS=["Right to Ask (applicant asked for information)","Right to Know (police decided to disclose)","Partner works days, applicant safe to see 10:00 to 14:00","Applicant prefers a female officer","Children under 5 at the address","Interpreter needed: Polish","Independent Domestic Violence Adviser to attend"]
visits=[];used=set();seq={"rso":4100,"bail":7200,"dvds":5300}
TY=["rso","bail","dvds"]
def pick(area,hub):
    nm,lat,lon,la=area
    cand=[i for i,(x,y) in enumerate(nodes) if i in resid and deg[i]>=2 and dm((x,y),(lon,lat))<900]
    rnd.shuffle(cand)
    for i in cand:
        if all(dm(nodes[i],nodes[j])>250 for j in used):
            used.add(i);return i
    return None
for hub,(a,b,c) in COUNTS.items():
    types=["rso"]*a+["bail"]*b+["dvds"]*c
    areas=AREAS[hub]
    for k,t in enumerate(types):
        area=areas[(k*7+3)%len(areas)] if k>=len(areas) else areas[k]
        i=pick(area,hub)
        if i is None: continue
        seq[t]+=rnd.randint(3,40)
        v=dict(id=f"{hub}{len([x for x in visits if x['hub']==hub])+1:02d}",type=t,hub=hub,area=area[0],la=area[3],node=i,
               lon=round(nodes[i][0],5),lat=round(nodes[i][1],5),initials=rnd.choice(FIRST)+"."+rnd.choice(FIRST)+".")
        if t=="rso":
            v["ref"]=f"VISOR-MOCK-{seq[t]:05d}";v["risk"]=rnd.choices(["Low","Medium","High","Very high"],[3,5,3,1])[0]
            v["mins"]=60
            v["overdue"]=rnd.random()<0.25;v["spec"]=v["risk"] in("High","Very high") and rnd.random()<0.7
            v["lastVisit"]=f"{rnd.randint(1,28):02d}/{rnd.choice(['06','07','08','09'])}/2026"
            v["flags"]=rnd.sample(FLAGS_RSO,2)
            v["team"]="Management of Sexual and Violent Offenders"
            if rnd.random()<0.2: v["window"]=[540,780]
        elif t=="bail":
            v["ref"]=f"NICHE-MOCK-OCC-{seq[t]:06d}";v["mins"]=10;v["overdue"]=False;v["spec"]=False
            v["flags"]=rnd.sample(FLAGS_BAIL,2);v["team"]="Custody and case progression";v["risk"]=""
            v["bailTo"]=f"{rnd.randint(1,28):02d}/{rnd.choice(['12','01'])}/202{rnd.choice(['6','7'])}"
        else:
            v["ref"]=f"DVDS-MOCK-{seq[t]:05d}";v["mins"]=30;v["overdue"]=rnd.random()<0.2;v["spec"]=False;v["risk"]=""
            f=rnd.sample(FLAGS_DVDS,2);v["flags"]=f;v["team"]="Domestic Abuse Unit"
            if any("10:00 to 14:00" in x for x in f): v["window"]=[600,840]
            v["route"]="Right to Know" if any("Right to Know" in x for x in f) else "Right to Ask"
            v["flags"]=[x for x in f if not x.startswith("Right to")] or [f[0]]
            v["applied"]=f"{rnd.randint(1,28):02d}/10/2026"
        visits.append(v)
print(len(visits),collections.Counter((v["hub"],v["type"]) for v in visits))
data={"graph":b64,"names":names,"stations":ST,"visits":visits}
json.dump(data,open("appdata.json","w"),separators=(",",":"))
for s in ST: print(s["name"],s["snap_m"])
