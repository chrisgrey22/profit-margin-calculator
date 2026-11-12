import fsspec, pyarrow.parquet as pq, pyarrow as pa, re, requests, sys, os, ssl
B="https://overturemaps-us-west-2.s3.us-west-2.amazonaws.com"
REL="release/2026-10-21.0"
XMIN,YMIN,XMAX,YMAX=-4.35,51.36,-3.05,51.86
def keys(prefix):
    out=[];tok=None
    while True:
        u=f"{B}/?list-type=2&prefix={prefix}"+(f"&continuation-token={requests.utils.quote(tok)}" if tok else "")
        t=requests.get(u).text
        out+=re.findall(r"<Key>([^<]*)</Key>",t)
        m=re.search(r"<NextContinuationToken>([^<]*)",t)
        if not m: break
        tok=m.group(1)
    return [k for k in out if k.endswith(".parquet")]
fs=fsspec.filesystem("https",client_kwargs={"trust_env":True})
def run(theme,typ,cols,outname):
    ks=keys(f"{REL}/theme={theme}/type={typ}/")
    print(typ,len(ks),"files",flush=True)
    tables=[]
    for k in ks:
        f=fs.open(f"{B}/{k}",block_size=2**20)
        pf=pq.ParquetFile(f)
        md=pf.metadata; names=pf.schema_arrow.names
        sch=pf.schema
        # find column indices for bbox leaves
        idx={}
        for i in range(md.num_columns):
            p=md.row_group(0).column(i).path_in_schema
            if p in("bbox.xmin","bbox.xmax","bbox.ymin","bbox.ymax"): idx[p]=i
        rgs=[]
        for r in range(md.num_row_groups):
            rg=md.row_group(r)
            s={p:rg.column(i).statistics for p,i in idx.items()}
            if s["bbox.xmax"].max<XMIN or s["bbox.xmin"].min>XMAX or s["bbox.ymax"].max<YMIN or s["bbox.ymin"].min>YMAX: continue
            rgs.append(r)
        if rgs:
            t=pf.read_row_groups(rgs,columns=cols)
            bb=t.column("bbox").combine_chunks()
            import pyarrow.compute as pc
            xmin=pc.struct_field(bb,"xmin");xmax=pc.struct_field(bb,"xmax");ymin=pc.struct_field(bb,"ymin");ymax=pc.struct_field(bb,"ymax")
            m=pc.and_(pc.and_(pc.greater_equal(xmax,XMIN),pc.less_equal(xmin,XMAX)),pc.and_(pc.greater_equal(ymax,YMIN),pc.less_equal(ymin,YMAX)))
            t=t.filter(m)
            tables.append(t)
        print(k[-60:],md.num_row_groups,len(rgs),sum(x.num_rows for x in tables),flush=True)
    pq.write_table(pa.concat_tables(tables),outname)
if __name__=="__main__":
    w=sys.argv[1]
    if w=="seg": run("transportation","segment",["id","bbox","geometry","subtype","class","names","connectors","access_restrictions","routes"],"segments2.parquet")
    if w=="places": run("places","place",["id","bbox","geometry","names","categories","addresses"],"places.parquet")
    if w=="divp": run("divisions","division",["id","bbox","geometry","names","subtype","class","population"],"divpts.parquet")
    if w=="div": run("divisions","division_area",["id","bbox","geometry","names","subtype","country","region"],"divareas.parquet")
    if w=="water": run("base","water",["id","bbox","geometry","subtype","class","names"],"water.parquet")
    if w=="land": run("base","land",["id","bbox","geometry","subtype","class"],"land.parquet")
