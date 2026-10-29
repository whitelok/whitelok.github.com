"""Build only the independent EZVideoRepair pages; preserve the personal homepage."""
from pathlib import Path
from html import escape
import json
from string import Template
ROOT = Path(__file__).resolve().parents[1]
SOURCE = "https://github.com/whitelok/EZVideoRepair"
MODEL = "https://huggingface.co/whitelok/seedvr2-hybricprecision-3b"
def build():
    data = {lang: json.loads((ROOT / f"content/ezvideorepair/{lang}.json").read_text()) for lang in ["zh", "en"]}
    assert data["zh"].keys() == data["en"].keys(), "Language keys differ"
    for lang, d in data.items():
        for name in ["features", "workflow", "requirements", "faq"]:
            assert len(d[name]) == len(data["zh"][name]), f"Language structure differs: {name}"
        values = {key: escape(value, quote=True) for key, value in d.items() if isinstance(value, str)}
        values.update(source_url=SOURCE, model_url=MODEL, file="ezvideorepair.html" if lang == "zh" else "ezvideorepair_en.html", asset_locale=lang)
        values["headline"] = "<br>".join(escape(x) for x in d["headline"])
        values["features"] = "".join(f'<article class="feature"><span class="number">{escape(n)}</span><h3>{escape(t)}</h3><p>{escape(b)}</p></article>' for n,t,b in d["features"])
        values["workflow"] = "".join(f'<li><span class="step-number">0{i+1}</span><h3>{escape(t)}</h3><p>{escape(b)}</p></li>' for i,(t,b) in enumerate(d["workflow"]))
        values["requirements"] = "".join(f'<div><dt>{escape(t)}</dt><dd>{escape(b)}</dd></div>' for t,b in d["requirements"])
        values["faq"] = "".join(f'<details><summary>{escape(q)}</summary><p>{escape(a)}</p></details>' for q,a in d["faq"])
        html = Template((ROOT / "templates/ezvideorepair/page.html").read_text()).substitute(values)
        (ROOT / values["file"]).write_text(html)
if __name__ == "__main__":
    build()
    print("Built ezvideorepair.html and ezvideorepair_en.html")
