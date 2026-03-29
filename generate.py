#!/usr/bin/env python3
"""SFG Garden Plan Generator — reads config + plant data, outputs HTML."""
import json, os, sys
from pathlib import Path

ROOT = Path(__file__).parent
PLANT_DIR = ROOT / "data" / "plants"
CONFIG = ROOT / "config" / "garden.json"
TEMPLATE = ROOT / "templates" / "garden.html"
OUTPUT = ROOT / "output" / "my-garden.html"

def load_plants():
    plants = {}
    for f in PLANT_DIR.glob("*.json"):
        p = json.loads(f.read_text())
        plants[p["id"]] = p
    return plants

def load_config():
    return json.loads(CONFIG.read_text())

def plant_card(plant):
    zone = plant.get("zone_9a", {})
    friends = ", ".join(plant.get("companions", {}).get("friends", []))
    foes = ", ".join(plant.get("companions", {}).get("foes", []))
    return f"""<div class="plant-card">
  <h3>{plant['name']}</h3>
  <p class="variety">{plant.get('variety_note','')}</p>
  <table>
    <tr><td>Per sqft</td><td>{plant['per_sqft']}</td></tr>
    <tr><td>Height</td><td>{plant.get('height','—')}</td></tr>
    <tr><td>Min depth</td><td>{plant.get('min_depth_inches','—')}"</td></tr>
    <tr><td>Weeks to harvest</td><td>{plant.get('weeks_to_harvest','continuous')}</td></tr>
    <tr><td>Season type</td><td>{plant['season_type']}</td></tr>
    <tr><td>Start from</td><td>{plant.get('start_from','—')}</td></tr>
    <tr><td>Spring plant</td><td>{zone.get('spring_plant','—')}</td></tr>
    <tr><td>Fall plant</td><td>{zone.get('fall_plant','—')}</td></tr>
    <tr><td>Harvest window</td><td>{zone.get('harvest_window','—')}</td></tr>
  </table>
  <p class="friends"><strong>Friends:</strong> {friends or 'none listed'}</p>
  <p class="foes"><strong>Foes:</strong> {foes or 'none listed'}</p>
  <p class="notes">{plant.get('pest_notes','')}</p>
  <p class="notes">{plant.get('container_notes','')}</p>
</div>"""

def tote_block(tote, plants):
    tid = tote["id"]
    sq1 = tote.get("sq1", {})
    sq2 = tote.get("sq2", {})
    p1 = plants.get(sq1.get("plant",""), {})
    p2 = plants.get(sq2.get("plant",""), {})
    name1 = p1.get("name", "Open") if sq1.get("plant") else "Open"
    name2 = p2.get("name", "Open") if sq2.get("plant") else "Open"
    c1 = f" x{sq1['count']}" if sq1.get("count") else ""
    c2 = f" x{sq2['count']}" if sq2.get("count") else ""
    full = tote.get("full_tote", False)
    note = tote.get("note", tote.get("full_tote_note", ""))
    rot = tote.get("fall_rotation")
    rot_html = ""
    if rot:
        rp = plants.get(rot["plant"], {})
        rname = rp.get("name", rot["plant"])
        rot_html = f'<p class="rotation">Fall rotation: <strong>{rname}</strong> x{rot["count"]} (plant {rot["plant_date"]})</p>'
    if full:
        return f"""<div class="tote">
  <div class="tote-header">{tid}</div>
  <div class="tote-grid full"><div class="sq full-sq">{name1}{c1}</div></div>
  <p class="tote-note">{note}</p>{rot_html}
</div>"""
    return f"""<div class="tote">
  <div class="tote-header">{tid}</div>
  <div class="tote-grid"><div class="sq">{name1}{c1}</div><div class="sq">{name2}{c2}</div></div>
  <p class="tote-note">{note}</p>{rot_html}
</div>"""

def harvest_calendar():
    months = [
        ("May", "Cilantro (before bolt), radishes"),
        ("Jun", "Cherry tomatoes, basil, dill, squash/zucchini start"),
        ("Jul", "Regular tomatoes, all peppers, cucumber, squash/zucchini peak, cabbage (spring)"),
        ("Aug", "Tomatoes, peppers, cucumber; squash/zucchini winding down"),
        ("Sep", "Tomatoes, peppers; plant fall crops (carrots, beets, lettuce, cabbage)"),
        ("Oct", "Lettuce R4, plant garlic cloves, replant cilantro"),
        ("Nov", "Lettuce R5, carrots ready, beets ready"),
        ("Dec", "Lettuce R6, continued carrot/beet harvest"),
        ("Jan", "Lettuce R7, cabbage (fall), plant potatoes"),
        ("Feb", "Potato growing, plan new summer cycle"),
        ("Mar", "Garlic harvest, start new summer transplants"),
        ("Apr", "New summer cycle begins"),
    ]
    rows = "".join(f"<tr><td>{m}</td><td>{h}</td></tr>" for m, h in months)
    return f"<table class='calendar'><tr><th>Month</th><th>Harvesting</th></tr>{rows}</table>"

def generate():
    config = load_config()
    plants = load_plants()
    template = TEMPLATE.read_text()

    # Build cart sections
    carts_html = ""
    for cart in config["carts"]:
        totes_html = "".join(tote_block(t, plants) for t in cart["totes"])
        station = cart.get("station_note", cart.get("station", ""))
        carts_html += f"""<div class="cart">
  <h2>Cart {cart['id']} — {cart['name']}</h2>
  <p class="station">{station}</p>
  <div class="totes">{totes_html}</div>
</div>"""

    # Build plant cards
    used_ids = set()
    for cart in config["carts"]:
        for tote in cart["totes"]:
            for sq in ["sq1", "sq2"]:
                pid = tote.get(sq, {}).get("plant")
                if pid: used_ids.add(pid)
            rot = tote.get("fall_rotation")
            if rot: used_ids.add(rot["plant"])
    cards_html = "".join(plant_card(plants[pid]) for pid in sorted(used_ids) if pid in plants)

    # Inject into template
    html = template.replace("{{GARDEN_NAME}}", config["garden_name"])
    html = html.replace("{{ZONE}}", config["zone"])
    html = html.replace("{{LOCATION}}", config["location"])
    html = html.replace("{{CARTS}}", carts_html)
    html = html.replace("{{PLANT_CARDS}}", cards_html)
    html = html.replace("{{HARVEST_CALENDAR}}", harvest_calendar())

    OUTPUT.parent.mkdir(exist_ok=True)
    OUTPUT.write_text(html)
    print(f"Generated: {OUTPUT}")

if __name__ == "__main__":
    generate()
