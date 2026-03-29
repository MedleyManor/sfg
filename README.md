# SFG — Square Foot Garden Planner

Data-driven garden planner for container/tote gardening using Square Foot Gardening principles.

## Quick Links

| Page | URL |
|---|---|
| **Garden Plan** | [medleymanor.github.io/sfg/output/my-garden.html](https://medleymanor.github.io/sfg/output/my-garden.html) |
| **Home** | [medleymanor.github.io/sfg](https://medleymanor.github.io/sfg/) |

## Architecture

```
sfg/
├── data/plants/          # One JSON per plant (spacing, timing, companions)
├── config/garden.json    # Tote assignments, zone, planting dates
├── templates/garden.html # HTML template with injection points
├── generate.py           # Static generator: reads data → outputs HTML
├── output/               # Generated HTML (viewable via GitHub Pages)
└── index.html            # Landing page (future: interactive app)
```

## Usage

```bash
python3 generate.py                      # regenerate plan
open output/my-garden.html               # view locally
```

## Garden Details

- **Zone:** 9a — Bastrop, TX
- **Setup:** 10 totes (27"x17"x12") on wheeled carts, 2 totes per cart
- **Method:** Square Foot Gardening in mobile containers
