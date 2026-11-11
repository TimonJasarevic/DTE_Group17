"""Render the MetroPT ontology as an interactive, color-coded physical-asset graph.
"""
from pathlib import Path
from html import escape
import re

from rdflib import Graph, RDF, RDFS, Namespace
from pyvis.network import Network

BASE = Path("data")
EX = Namespace("https://example.org/metropt/")

graph = Graph()
graph.parse(BASE / "apu.ttl", format="turtle")

net = Network(
    height="750px", width="100%", directed=True,
    bgcolor="#ffffff", font_color="#222222", cdn_resources="in_line",
)
net.barnes_hut(gravity=-3000, central_gravity=0.3, spring_length=100, spring_strength=0.05)

TYPES = {
    EX.Train: "Train",
    EX.APU: "APU",
    EX.Component: "Component",
    EX.AnalogSignal: "Analog",
    EX.DigitalSignal: "Digital",
    EX.GPSField: "GPS",
}

# The colors are used for both graph nodes and the HTML legend.
COLORS = {
    "Train": "#CC79A7",      # Purple/pink
    "APU": "#0072B2",        # Blue
    "Component": "#009E73",  # Green
    "Analog": "#56B4E9",     # Light blue
    "Digital": "#E69F00",    # Orange
    "GPS": "#D55E00",        # Vermilion
    "Other": "#999999",      # Grey
}


def name(term):
    return str(term).split("/")[-1]


UNIT_LABELS = {"degC": "°C", "m3/h": "m³/h", "degrees": "°"}


def add_node(term):
    kind = TYPES.get(graph.value(term, RDF.type), "Other")
    unit = graph.value(term, EX.unit)
    encoding = graph.value(term, EX.valueEncoding)
    column = graph.value(term, EX.csvColumn)
    description = graph.value(term, RDFS.comment)

    # Surface units on sensor nodes, with full metadata on hover.
    display_unit = UNIT_LABELS.get(str(unit), str(unit)) if unit else None
    label = name(term) + (f"\n({display_unit})" if display_unit else "")
    details = [f"<b>{escape(name(term))}</b>", f"Type: {escape(kind)}"]
    if column is not None:
        details.append(f"CSV column: {escape(str(column))}")
    if display_unit:
        details.append(f"Unit: {escape(display_unit)}")
    elif kind == "Digital":
        details.append("Unit: none (binary 0/1)")
    elif kind == "GPS":
        details.append("Unit: not specified in the source")
    if encoding is not None:
        details.append(f"Encoding: {escape(str(encoding))}")
    if description is not None:
        details.append(escape(str(description)))

    net.add_node(
        str(term),
        label=label,
        title="<br>".join(details),
        group=kind,
        color=COLORS[kind],
    )


nodes_added = set()
for subj, prop, obj in graph:
    if prop not in (EX.hasPart, EX.hasField):
        continue
    for term in (subj, obj):
        if str(term) not in nodes_added:
            add_node(term)
            nodes_added.add(str(term))
    net.add_edge(str(subj), str(obj), label=name(prop), title=name(prop))

output = BASE / "metropt_ontology_graph.html"
net.write_html(str(output))

# Add a visible, responsive legend above the graph without hiding any nodes.
legend_items = "".join(
    f'<span class="metropt-legend-item">'
    f'<span class="metropt-swatch" style="background:{escape(color)}"></span>'
    f'{escape(category)}</span>'
    for category, color in COLORS.items()
    if category != "Other" or any(
        TYPES.get(graph.value(s, RDF.type), "Other") == "Other"
        for s in graph.subjects()
        if (s, EX.hasPart, None) in graph or (s, EX.hasField, None) in graph
    )
)

legend = f"""
<style>
  .metropt-legend {{
    display: flex; flex-wrap: wrap; align-items: center; gap: 10px 18px;
    padding: 14px 18px; margin: 10px 12px;
    background: #f8fafc; border: 1px solid #e2e8f0;
    border-radius: 10px; font: 14px system-ui, sans-serif;
  }}
  .metropt-legend-title {{ font-weight: 700; margin-right: 6px; }}
  .metropt-legend-item {{ display: inline-flex; align-items: center; gap: 7px; }}
  .metropt-swatch {{
    display: inline-block; width: 14px; height: 14px;
    border-radius: 50%; border: 1px solid #475569;
    flex-shrink: 0;
  }}
</style>
<div class="metropt-legend" role="group" aria-label="Node color legend">
  <span class="metropt-legend-title">Node colors</span>
  {legend_items}
</div>
"""

html = output.read_text(encoding="utf-8")
body_open = re.search(r"<body\b[^>]*>", html, flags=re.IGNORECASE)
if not body_open:
    raise RuntimeError("Could not find HTML <body> to insert the legend")
html = html[:body_open.end()] + legend + html[body_open.end():]
output.write_text(html, encoding="utf-8")

print(f"Created {output}")
