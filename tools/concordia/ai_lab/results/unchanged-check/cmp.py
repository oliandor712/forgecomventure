import glob,os,re,sys
R='/tmp/claude-0/uc'
ARM=sys.argv[1] if len(sys.argv)>1 else 'cons'
def res(arm):
    d={}
    for f in glob.glob(f'{R}/{arm}/p*.res'):
        for l in open(f):
            x=l.rstrip('\n').split('\t'); d[x[1]]=x[2:]
    return d
def norm(path):
    out=[]
    for l in open(path,errors='ignore'):
        x=l.rstrip('\n').split('\t')
        if len(x)>2 and x[2].rstrip('*')=='AI_DECISION': continue
        l=re.sub(r' hand: .*','',l)
        out.append(l)
    return out
s,c=res('stock'),res(sys.argv[1] if len(sys.argv)>1 else 'cons')
print('games stock',len(s),'cons',len(c))
same=diffw=difflog=0; first=[]
for g in sorted(set(s)&set(c)):
    if s[g]!=c[g]: diffw+=1; first.append((g,'result',s[g],c[g])); continue
    a,b=norm(f'{R}/stock/logs/{g}.tsv'),norm(f'{R}/{ARM}/logs/{g}.tsv')
    if a==b: same+=1
    else:
        difflog+=1
        for i,(x,y) in enumerate(zip(a,b)):
            if x!=y: first.append((g,i,x.strip()[:150],y.strip()[:150])); break
        else: first.append((g,'length',len(a),len(b)))
print('identical',same,'result differs',diffw,'log differs (same result)',difflog)
for f in first[:10]: print(f)
