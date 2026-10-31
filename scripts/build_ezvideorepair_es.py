"""Build Spanish pages from maintained English HTML and a shared translation map."""
from pathlib import Path
import json,re
ROOT=Path(__file__).resolve().parents[1]
def build():
    translations=json.loads((ROOT/'content/ezvideorepair/es-translations.json').read_text())
    pattern=re.compile('|'.join(re.escape(k) for k in sorted(translations,key=len,reverse=True)))
    pages=[('ezvideorepair_en.html','ezvideorepair_es.html'),('ezvideorepair-marketing_en.html','ezvideorepair-marketing_es.html')]
    for source,destination in pages:
        text=(ROOT/source).read_text()
        # Translate exact source strings in one pass so translated words are never translated twice.
        text=pattern.sub(lambda match:translations[match.group()],text)
        text=text.replace('<html lang="en">','<html lang="es-ES">').replace('content="en_US"','content="es_ES"')
        text=text.replace('https://whitelok.github.io/'+source,'https://whitelok.github.io/'+destination)
        text=text.replace('href="ezvideorepair_en.html"','href="ezvideorepair_es.html"').replace('href="ezvideorepair-marketing_en.html"','href="ezvideorepair-marketing_es.html"').replace('href="ezvideorepair-privacy_en.html"','href="ezvideorepair-privacy_es.html"')
        text=re.sub(r'<a class="language".*?</a>', '',text,flags=re.S)
        text=re.sub(r'<div class="locale-links".*?</div>', '',text,flags=re.S)
        zh=destination.replace('_es.html','.html');en=destination.replace('_es.html','_en.html')
        switch=f'<div class="locale-links" aria-label="Idioma"><a class="language" href="{zh}" lang="zh-CN">简体中文</a><a class="language" href="{en}" lang="en">English</a></div>'
        text=text.replace('</nav></header>',switch+'</nav></header>')
        # Preserve the product name in the English interface screenshot alt text.
        text=text.replace('<span>EZVideoRepair</span>','<span>EZ Restaurador de vídeos</span>').replace('<strong>EZVideoRepair</strong>','<strong>EZ Restaurador de vídeos</strong>')
        text=text.replace('<title>EZVideoRepair','<title>EZ Restaurador de vídeos')
        (ROOT/destination).write_text(text)
    # Expose Spanish on existing pages, preserving their original locale links.
    for name in ['ezvideorepair.html','ezvideorepair_en.html','ezvideorepair-marketing.html','ezvideorepair-marketing_en.html']:
        p=ROOT/name;text=p.read_text();es=name.replace('_en.html','_es.html') if '_en.html' in name else name.replace('.html','_es.html')
        if f'href="{es}"' not in text:
            text=text.replace('</nav></header>',f'<a class="language" href="{es}" lang="es-ES">Español</a></nav></header>')
        (p).write_text(text)
    # All locale alternatives must point at the matching language, not a copied canonical.
    for stem in ['ezvideorepair','ezvideorepair-marketing']:
        alternatives=''.join(f'<link rel="alternate" hreflang="{locale}" href="https://whitelok.github.io/{stem}{suffix}.html">' for locale,suffix in [('zh-CN',''),('en','_en'),('es-ES','_es'),('x-default','')])
        for suffix in ['', '_en', '_es']:
            p=ROOT/f'{stem}{suffix}.html';text=p.read_text()
            text=re.sub(r'<link rel="alternate"[^>]*>', '', text)
            text=text.replace('</head>',alternatives+'</head>')
            p.write_text(text)
if __name__=='__main__':build()
