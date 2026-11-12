import json,sys
G="/tmp/claude-0/-home-user-profit-margin-calculator/650c2f93-d72d-5624-ab1a-081f33d26884/scratchpad/geo/"
t=open("template.html").read()
app=open(G+"appdata.json").read().replace("</","<\\/")
base=open(G+"base.json").read().replace("</","<\\/")
def out(path,title,line):
    s=t.replace("__TITLE__",title).replace("__FORCELINE__",line).replace("__APPDATA__",app).replace("__BASEDATA__",base)
    open(path,"w").write(s); print(path,len(s))
out("visit-planner.html","Day of Action Visit Planner","Strategic Public Protection Command · mock-up")
import os
os.makedirs("/home/user/profit-margin-calculator/day-of-action-planner",exist_ok=True)
HEAD='<!doctype html>\n<html lang="en">\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">\n'
def out2(p,ti,l):
    out(p,ti,l); s=open(p).read(); open(p,"w").write(HEAD+s)
out2("/home/user/profit-margin-calculator/day-of-action-planner/index.html","Day of Action Visit Planner","South Wales Police · Heddlu De Cymru · Strategic Public Protection Command · mock-up")
