"""月次レポートの Word 原稿（.docx）を report.html に変換する。

使い方（リポジトリ直下で実行）:
    python tools/docx_to_report.py 原稿.docx

行うこと:
  1. 原稿の本文・表・図版を、順序を変えずに HTML へ写す（文言は一切変えない）
  2. 図版と写真を assets/img/ へ無加工で取り出す
  3. report.html を上書きする
  4. 原稿の全文字が HTML に同じ順序で含まれるかを照合し、結果を表示する

前提とする原稿の書式（2026年9月号 v2.2 と同じ型）:
  - 章見出し: 13pt（sz=26）で「1　表題」の形
  - 節見出し: 段落全体が太字、または 9.5pt（sz=19）
  - 注記・出典: 8pt（sz=16）
  - 要点の段落: 「—」で始まる
  - 数字のカード: 17pt（sz=34）の数字を含む表
書式が違う原稿では見出しの判定がずれる。照合が「一致」でも、必ず画面で目視する。

必要なもの: python-docx（pip install python-docx）
"""
import docx,html,re,sys,os,zipfile
if len(sys.argv)!=2: sys.exit(__doc__)
DOCX=sys.argv[1]
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W='{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
R='{http://schemas.openxmlformats.org/officeDocument/2006/relationships}'
d=docx.Document(DOCX)
rel={k:v.target_ref.split('/')[-1] for k,v in d.part.rels.items() if 'image' in v.reltype}
def runs(p):
    out=[]
    for r in p.iter(W+'r'):
        t=''.join(x.text or '' for x in r.iter(W+'t'))
        rp=r.find(W+'rPr'); b=False; sz=None
        if rp is not None:
            be=rp.find(W+'b'); b= be is not None and be.get(W+'val') not in ('0','false')
            s=rp.find(W+'sz'); sz=int(s.get(W+'val')) if s is not None else None
        if t: out.append((t,b,sz))
    return out
def imgs(p): return [rel[b.get(R+'embed')] for b in p.iter('{http://schemas.openxmlformats.org/drawingml/2006/main}blip')]
def inline(rs):
    s=''
    for t,b,_ in rs:
        e=html.escape(t)
        s+=f'<b>{e}</b>' if b else e
    return s.replace('</b><b>','')
def info(p):
    rs=runs(p); txt=''.join(t for t,_,_ in rs)
    szs=[z for t,_,z in rs if z]; sz=max(szs) if szs else None
    allb=bool(rs) and all(b for t,b,_ in rs if t.strip())
    return rs,txt,sz,allb
out=[];toc=[];cover=[];n=0;seen_h2=False
def table(t):
    rows=[[ [info(p) for p in c.iter(W+'p')] for c in r.findall(W+'tc')] for r in t.findall(W+'tr')]
    if any(i[2]==34 for r in rows for c in r for i in c):
        o=['<div class="cards">']
        for r in rows:
            for c in r:
                ps=[i for i in c if i[1].strip()]
                if not ps: continue
                cls=['l','n','d']
                o.append('<div class="card">'+''.join(f'<p class="{cls[min(k,2)]}">{html.escape(i[1])}</p>' for k,i in enumerate(ps))+'</div>')
        o.append('</div>'); return '\n'.join(o)
    o=['<div class="tscroll"><table>']
    for k,r in enumerate(rows):
        head = k==0 and all(i[3] for c in r for i in c if i[1].strip())
        cells=[]
        for j,c in enumerate(r):
            body='<br>'.join(html.escape(i[1]) for i in c if i[1].strip())
            tag='th' if head else 'td'
            if not head and j==0: body=f'<b>{body}</b>' if all(i[3] for i in c if i[1].strip()) and body else body
            cells.append(f'<{tag}>{body}</{tag}>')
        o.append('<tr>'+''.join(cells)+'</tr>')
    o.append('</table></div>'); return '\n'.join(o)
for el in d.element.body.iterchildren():
    if el.tag==W+'tbl': out.append(table(el)); continue
    if el.tag!=W+'p': continue
    rs,txt,sz,allb=info(el)
    for im in imgs(el): out.append(f'<figure><img src="/assets/img/{im}" alt="図版（{im}）" loading="lazy"></figure>')
    if not txt.strip(): continue
    e=html.escape(txt)
    if sz==26 and re.match(r'\d+\u3000',txt):
        seen_h2=True;n+=1;toc.append((n,e));out.append(f'<h2 id="sec-{n}">{e}</h2>');continue
    if not seen_h2: cover.append((e,sz));continue
    if sz==19 or (allb and sz is None and not txt.startswith('「')): out.append(f'<h3>{e}</h3>')
    elif allb and txt.startswith('「'): out.append(f'<p class="quote">{e}</p>')
    elif sz==16: out.append(f'<p class="note">{inline(rs)}</p>')
    elif txt.startswith('—'): out.append(f'<p class="point">{inline(rs)}</p>')
    elif txt.startswith('2026年10月') and len(txt)<12 or txt.startswith('日本信達株式会社　代表取締役'): out.append(f'<p class="sign">{e}</p>')
    else: out.append(f'<p>{inline(rs)}</p>')
c=[x for x,_ in cover]
while len(c)<7: c.append('')
body=f'''<div class="cover">
<p class="eyebrow">MONTHLY REPORT</p>
<h1>{c[0]}　{c[1]}</h1>
<p class="issue">{c[2]}</p>
<p class="note">{c[3]}<br>{c[4]}　{c[5]}　{c[6]}</p>
</div>
<nav aria-label="目次"><ol class="toc" style="list-style:none;padding-left:0">'''+''.join(f'<li><a href="#sec-{k}">{t}</a></li>' for k,t in toc)+'</ol></nav>\n'+'\n'.join(out)+'\n'
page=f'''<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex,nofollow">
<title>月次レポート｜日本信達 株主専用ポータル</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Zen+Old+Mincho:wght@400;700&family=Noto+Sans+JP:wght@400;700&family=Inter:wght@400;600;700&display=swap">
<link rel="stylesheet" href="/assets/style.css">
</head>
<body>
<header id="site-head"></header>
<main class="narrow">
{body}</main>
<footer id="site-foot"></footer>
<script src="/assets/site.js"></script>
</body>
</html>
'''
open(os.path.join(ROOT,'report.html'),'w',encoding='utf-8').write(page)
os.makedirs(os.path.join(ROOT,'assets','img'),exist_ok=True)
with zipfile.ZipFile(DOCX) as z:
    for n in z.namelist():
        if n.startswith('word/media/'):
            open(os.path.join(ROOT,'assets','img',os.path.basename(n)),'wb').write(z.read(n))
src=''.join(t.text or '' for t in d.element.body.iter(W+'t'))
m=re.sub(r'<nav.*?</nav>','',body,flags=re.S); m=re.sub(r'<p class="eyebrow">.*?</p>','',m); m=re.sub(r'alt="[^"]*"','',m)
txt=html.unescape(re.sub(r'<[^>]+>','',m))
n=lambda s:re.sub(r'\s+','',s)
a,b=n(src),n(txt)
print(f'章 {len(toc)}／表紙の行 {len(cover)}／図版 {len(rel)}')
print('原文との照合:', '一致' if a==b else '不一致（下の箇所を確認すること）')
if a!=b:
    i=next((k for k in range(min(len(a),len(b))) if a[k]!=b[k]),min(len(a),len(b)))
    print(' 原稿:',a[max(0,i-20):i+30]); print(' HTML:',b[max(0,i-20):i+30]); sys.exit(1)
