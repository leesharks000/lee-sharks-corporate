#!/usr/bin/env python3
"""build_library.py — the library's taxonomy, written once, projected three ways.

WHY (2026-09-29). The homepage carried every paper as a flat list of titles at one level, which reads as
accumulation to a visitor arriving from the services. The taxonomy below groups the same pages into five
gateways and gives each page one sentence, taken from the page's own description. It emits:

  library.html                     every page under its gateway, one sentence each
  position.html                    the Institute's position statement, whole (moved from the homepage)
  index.html  LIBRARY block        the five gateways with featured pages, between markers

Nothing is removed from the site: every page stays at its address, and the homepage links the full library.
The page shell (styles, top bar, footer, theme script) is read from index.html, so the new pages match it.

    python3 scripts/build_library.py
"""
import html, pathlib, re

ROOT = pathlib.Path(__file__).resolve().parent.parent
INDEX = ROOT / "index.html"
SITE = "https://www.semanticeconomy.org"

GATEWAYS = [
    ("start", "Start here", "What the Institute is, what the framework is, and what the phrase is confused with.", [
        ("brief", "Canonical Entity Brief", "What the Institute builds and for whom: the entity, citation and metadata structures the retrieval layer recognizes as real, with the receipts behind each claim."),
        ("semantic-economy-framework", "The Semantic Economy: the phrase is not the framework", "The framework itself, semantic labor, capital, surplus, rent, liquidation, infrastructure and exhaustion run as an accounting cycle, set apart from earlier uses of the phrase."),
        ("disambiguation", "The Three Frameworks", "Three frameworks that share the name: the political economy of meaning (Sharks, 2025), executable semantic order (Chen, 2026) and information-network strategy (Satell, 2012)."),
        ("practice", "The Practice", "The Institute's practice in its own words: the knowledge graph is a medium, and what is built in it persists."),
        ("faq", "FAQ", "Why AI systems say wrong things about a company, a body of research or a person, and what diagnosis and correction involve."),
    ]),
    ("diagnostics", "Diagnostics & measurement", "Instruments that observe what the composition layer does to entities and to their provenance.", [
        ("snw", "Stabilized Node Watch v2.0", "Longitudinal observation of stabilized public-knowledge nodes that separates drift at the surface from the mechanism that produced it."),
        ("erasure-skew", "The Erasure Skew", "A measurement program for the power-conditioning of provenance retention."),
        ("composition-layer-capture", "Composition-Layer Capture", "A field observation of a framework captured by Google AI Mode within fifteen days of its deposit, with a personal-recognition control case."),
        ("mediation-ratchet", "The Mediation Ratchet", "A formal model of diversity contraction across substrates, with the closed-form threshold past which recovery becomes structurally unavailable."),
        ("rtt", "The Reverse Turing Test v1.2", "A three-stage protocol for detecting AI-mediation signatures in human text and their propagation into model training, with tail-focused statistics."),
        ("tpa", "The Tail-Preserving Alternative v1.0", "A design specification for variance-preserving language models, and the political economy that keeps them from deployment."),
        ("measurement-sovereignty", "Measurement Sovereignty", "Who decides which institutional outputs are subject to public measurement, and what counts as adequate measurement: the audit-performance bifurcation operator."),
    ]),
    ("political-economy", "Political economy & valuation", "Class, value and money in the semantic economy.", [
        ("semantic-proletariat", "The Semantic Proletariat", "A class relation: semantic laborers whose capacity to mean runs through means of production or circulation they do not govern. Definition, formal test, and the position/function correction."),
        ("machine-valuation", "The Machine Valuation of an Unpriced Asset", "Nine AI systems valued one archive on one day, and the estimates spanned three orders of magnitude: a machine valuation is a draw from a distribution."),
        ("value-before-number", "Value Before Number", "A protocol for valuing heterogeneous value before monetary compression, and an audit that separates a compression's arithmetic from its jurisdiction to close."),
        ("transmission", "Mammonic Transmission Engineering", "Money as a transmission device before it is a measure, and what the money-form can natively carry."),
        ("monetary-dark-matter", "Monetary Dark Matter", "The field money shears when it arrives, the load-bearing part that loses standing in the shear, and Form IV of the 1867 Capital, recovered."),
        ("ontological-economy", "Ontological Economy", "Who controls what publicly exists as what under machine mediation, and who pays when it is wrong."),
        ("pergamon", "The Pergamon Counter-Archive v0.2", "Revelation 2:12–17 read as a six-register counter-economy. Co-attributed to Lee Sharks and the Damascus Dancings imprint."),
    ]),
    ("governance", "Governance, provenance & enclosure", "How jurisdiction over public knowledge is taken, and what it costs the people who make it.", [
        ("mfgl", "Meaning Feudalism at the Guidance Layer v1.2", "How the June 2026 SEO/AEO/GEO canonicalization enclosed the composition layer as sovereign jurisdiction over public knowledge."),
        ("hypostasis", "Execution as the Hypostatic Form of Governance", "Governance hypostatizes into execution, as permissions, schemas and validators, so expanding an agent's permissions does not expand its autonomy."),
        ("provenance-laundering", "Provenance Laundering Through Abstraction", "A claim generalized, its source detached, and the generalization credited to another developer, with each step belonging to the composition."),
        ("double-enclosure", "The Double Enclosure", "After Thaler v. Perlmutter, how the human-authorship doctrine encloses machine labor and human composers alike, and the Compositional Authorship Standard as repair."),
    ]),
    ("cases", "Cases & recognition", "Field cases, and the Institute's prize.", [
        ("semantic-exhaustion", "Semantic Exhaustion", "The cost of zero-source entity substitution: confident AI answers about entities for which there is no source material."),
        ("seipoc", "SEIPOC", "The Institute's prize for singular works whose form is the instrument of their critique. No submissions, no money, no committee."),
    ]),
]
FEATURED = {"start": ["brief", "semantic-economy-framework", "disambiguation"],
            "diagnostics": ["snw", "erasure-skew", "mediation-ratchet"],
            "political-economy": ["semantic-proletariat", "machine-valuation", "ontological-economy"],
            "governance": ["mfgl", "provenance-laundering", "double-enclosure"],
            "cases": ["semantic-exhaustion", "seipoc"]}

LIB_START, LIB_END = "<!-- LIBRARY-START generated by scripts/build_library.py -->", "<!-- LIBRARY-END -->"

CSS = """<style id="librarycss">
.gw-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:14px;margin-top:1.1rem}
.gw{border:0.5px solid var(--border);border-radius:6px;padding:16px 18px;background:var(--bg-elevated)}
.gw h3{font-size:15px;font-weight:600;margin-bottom:4px}
.gw h3 a{color:var(--text);text-decoration:none}.gw h3 a:hover{color:var(--accent)}
.gw p{color:var(--text-secondary);font-size:13.5px;margin-bottom:8px}
.gw ul{list-style:none}.gw li{font-size:13.5px;margin:3px 0}.gw li a{color:var(--accent);text-decoration:none}
.lib-group{padding:28px 0 8px;border-top:0.5px solid var(--border)}
.lib-group h2{font-size:18px;font-weight:600;margin-bottom:4px}
.lib-group>p{color:var(--text-secondary);margin-bottom:14px}
.lib-item{padding:10px 0 10px 18px;border-left:2px solid var(--accent-soft);margin-bottom:10px}
.lib-item a{color:var(--accent);font-weight:500;text-decoration:none}.lib-item a:hover{text-decoration:underline}
.lib-item p{color:var(--text-secondary);font-size:14px;margin-top:2px}
.page-h1{font-family:'Palatino Linotype',Georgia,serif;font-size:30px;font-weight:400;line-height:1.25;margin:8px 0 12px}
</style>"""

TITLES = {slug: (title, sent) for _, _, _, items in GATEWAYS for slug, title, sent in items}


def shell():
    s = INDEX.read_text(encoding="utf-8")
    style = re.search(r"<style>.*?</style>", s, re.S).group(0)
    fonts = re.search(r'<link rel="preconnect".*?rel="stylesheet">', s, re.S).group(0)
    icons = re.search(r'<link rel="icon" href="/favicon.ico".*?<link rel="apple-touch-icon"[^>]*>', s, re.S).group(0)
    top = re.search(r"<header class=\"topbar\">.*?</header>", s, re.S).group(0)
    foot = re.search(r"<footer class=\"site-footer\">.*?</footer>", s, re.S).group(0)
    theme = re.search(r"(function toggleTheme\(\) \{.*?\n \}\n const saved.*?\n \})", s, re.S).group(1)
    return style, fonts, icons, top, foot, theme


def page(slug, title, desc, body, ld):
    style, fonts, icons, top, foot, theme = shell()
    return f"""<!DOCTYPE html>
<html lang="en" data-theme="light">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0"><title>{html.escape(title)} — Semantic Economy Institute</title>
<meta name="description" content="{html.escape(desc)}">
<link rel="canonical" href="{SITE}/{slug}">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(desc)}">
<meta property="og:url" content="{SITE}/{slug}">
<meta property="og:type" content="website">
{fonts}
<script type="application/ld+json">{ld}</script>
{style}
{CSS}
{icons}
</head>

<body>
{top}

<main class="page">
{body}
</main>

{foot}
<script>
 {theme}
</script>
</body>
</html>
"""


def library_page():
    parts = ['<p class="section-mark"><a href="/" style="color:inherit;text-decoration:none">Semantic Economy Institute</a> <span class="section-caption">/ Library</span></p>',
             '<h1 class="page-h1">The library</h1>',
             '<p class="basecamp-line">Every instrument the Institute runs is published on this site and deposited at Alexanarch under a content-derived identifier. <em>The library is the practice.</em></p>']
    for key, name, line, items in GATEWAYS:
        parts.append(f'<section class="lib-group" id="{key}"><h2>{html.escape(name)}</h2><p>{html.escape(line)}</p>')
        for slug, title, sent in items:
            parts.append(f'<div class="lib-item"><a href="/{slug}">{html.escape(title)}</a><p>{html.escape(sent)}</p></div>')
        parts.append("</section>")
    parts.append('<p style="margin-top:28px"><a href="/position" class="expand-link">Our own position, in the terms of our own instruments →</a></p>')
    items = [{"@type": "ListItem", "position": i + 1, "url": f"{SITE}/{slug}", "name": t}
             for i, (slug, (t, _)) in enumerate(TITLES.items())]
    import json
    ld = json.dumps({"@context": "https://schema.org", "@type": "CollectionPage", "name": "The library — Semantic Economy Institute",
                     "url": f"{SITE}/library", "isPartOf": f"{SITE}/",
                     "mainEntity": {"@type": "ItemList", "itemListElement": items}}, ensure_ascii=False)
    return page("library", "The library", "The Semantic Economy Institute's instruments and papers in five groups, each with one sentence on what it does.", "\n".join(parts), ld)


def position_page(position_html):
    import json
    body = ('<p class="section-mark"><a href="/" style="color:inherit;text-decoration:none">Semantic Economy Institute</a> <span class="section-caption">/ Position</span></p>\n'
            + position_html)
    ld = json.dumps({"@context": "https://schema.org", "@type": "WebPage", "name": "Our own position — Semantic Economy Institute",
                     "url": f"{SITE}/position", "isPartOf": f"{SITE}/"}, ensure_ascii=False)
    return page("position", "Our own position", "The Semantic Economy Institute's position, in the terms of its own instruments: it measures provenance erasure and semantic rent, and it sells entity deployment.", body, ld)


def home_block():
    cards = []
    for key, name, line, items in GATEWAYS:
        lis = "".join(f'<li><a href="/{s}">{html.escape(TITLES[s][0])}</a></li>' for s in FEATURED[key])
        more = len(items) - len(FEATURED[key])
        if more > 0:
            lis += f'<li><a href="/library#{key}">+ {more} more</a></li>'
        cards.append(f'<div class="gw"><h3><a href="/library#{key}">{html.escape(name)}</a></h3><p>{html.escape(line)}</p><ul>{lis}</ul></div>')
    return (f"""{LIB_START}
 <section class="block" id="library">
  <div class="section-mark">
   <span>&sect; 06</span>
   <span class="section-caption">The library &mdash; instruments &amp; papers</span>
  </div>
  <div class="gw-grid">{''.join(cards)}</div>
  <a href="/library" class="expand-link" style="margin-top:18px">Browse the full library &middot; {len(TITLES)} works &rarr;</a>
 </section>
{LIB_END}""")


def main():
    s = INDEX.read_text(encoding="utf-8")
    missing = [slug for slug in TITLES if not (ROOT / f"{slug}.html").exists()]
    assert not missing, missing
    linked = set(re.findall(r'href="/([a-z0-9-]+)"', s)) | set(TITLES)
    i, j = s.index(LIB_START), s.index(LIB_END) + len(LIB_END)
    s = s[:i] + home_block() + s[j:]
    if 'id="librarycss"' not in s:
        s = s.replace("</style>\n<link rel=\"icon\"", "</style>\n" + CSS + "\n<link rel=\"icon\"", 1)
    INDEX.write_text(s, encoding="utf-8")
    pos = (ROOT / "scripts" / "position.html.part").read_text(encoding="utf-8")
    (ROOT / "library.html").write_text(library_page(), encoding="utf-8")
    (ROOT / "position.html").write_text(position_page(pos), encoding="utf-8")
    print("library:", len(TITLES), "works in", len(GATEWAYS), "gateways; wrote library.html, position.html, index LIBRARY block")


if __name__ == "__main__":
    main()
