from pathlib import Path
from html.parser import HTMLParser
import json
import xml.etree.ElementTree as ET
from urllib.parse import urlparse
root=Path(__file__).resolve().parents[1]
base="https://nanasnestcare.com"
class Page(HTMLParser):
    def __init__(self):
        super().__init__(); self.canon=[]; self.h1=0; self.schema=False; self.buf=""
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=="link" and a.get("rel")=="canonical": self.canon.append(a.get("href"))
        if tag=="h1": self.h1+=1
        if tag=="script" and a.get("type")=="application/ld+json": self.schema=True; self.buf=""
    def handle_data(self,data):
        if self.schema: self.buf+=data
    def handle_endtag(self,tag):
        if tag=="script" and self.schema: json.loads(self.buf); self.schema=False
urls=ET.parse(root/"sitemap.xml").findall(".//{*}loc")
assert len(urls)>=28
seen=set()
for loc in urls:
    url=loc.text
    assert url.startswith(base+"/") and url not in seen, url
    seen.add(url)
    path=urlparse(url).path
    file=root/(path.lstrip("/") + ("index.html" if path.endswith("/") else ""))
    html=file.read_text()
    p=Page(); p.feed(html)
    assert p.canon==[url], (file,p.canon,url)
    assert p.h1==1,(file,p.h1)
    assert "YOUR_FORM_ID" not in html,file
assert "Sitemap: "+base+"/sitemap.xml" in (root/"robots.txt").read_text()
print(f"{len(urls)} sitemap pages passed canonical, H1 and JSON-LD checks")
