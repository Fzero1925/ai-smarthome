---
title: "Fix Nest Thermostat E73/E74: 'No power to Rc/Rh' (2025)"
description: "A safe, step-by-step playbook to recover from Nest power errors: breakers, drip-pan float switch, wiring inspection, fuse/transformer checks, and when to add a C-wire or the Nest Power Connector."
date: 2025-08-10
lastmod: 2025-08-10
slug: "nest-thermostat-e73-e74-power-fix-2025"
draft: false
categories: ["Guides","HVAC"]
tags: ["Nest","Thermostat","E73","E74","C wire","Nest Power Connector","Rc","Rh"]
author: "AI SmartHome Hub Editorial"
---

> **Quick answer** — **Turn off breakers**, check the **condensate/drip-pan float switch** and **fuse** on the air handler, then inspect/reseat Rc/Rh wiring at the Nest base and HVAC board. If power issues persist, add a **C-wire** or install the **Nest Power Connector** to supply stable 24 VAC.

## What E73/E74 actually mean
- **E73**: *No power to **Rc** wire detected*.  
- **E74**: *No power to **Rh** wire detected*.  
These are Nest **help codes** indicating missing 24 VAC on the R leg feeding your thermostat.

## 15-minute recovery plan (do this order)
1. **Kill power** at HVAC breakers. Remove Nest display.  
2. **Inspect wires** at Nest base: 10–12 mm copper exposed, clean, fully seated.  
3. **Airflow & drip-pan/float switch**: Replace clogged filters; if the pan float is tripped (condensate backup), the system can **cut R** power—clear the drain before proceeding.  
4. **Fuse & transformer** (air handler board): Check the low-voltage fuse; confirm ~24 VAC across **R–C**. Replace blown fuse only after fixing the cause.  
5. **Restore power** and test. If errors return or battery drains, add a **C-wire** or the **Nest Power Connector** at the air handler for stable power.

## Troubleshooting matrix
| Symptom                              | Likely cause                              | What to do                                                   |
| ------------------------------------ | ----------------------------------------- | ------------------------------------------------------------ |
| E73/E74 after hours of cooling       | Drip-pan float switch tripped / iced coil | Clear condensate line, thaw coils, replace filter; restore power. |
| Random reboots / Wi-Fi drops         | Marginal thermostat power                 | Install **C-wire** or **Nest Power Connector**.              |
| Error persists after reseating wires | Open fuse / failed transformer            | Replace fuse; have a pro test/replace transformer as needed. |

## Common pitfalls
- Working live—**always** cut power at the breaker before touching low-voltage wiring.  
- Fixing the symptom but not the cause (e.g., replacing a fuse without clearing the clog that tripped the float).  
- Assuming “power stealing” is enough—many systems **still need C** for stability.

## FAQ
- **Is ‘E73’ always a bad thermostat?**  
  No—most cases are wiring/power path issues (fuse/float switch/transformer).  
- **Do I need a professional?**  
  If you’re not comfortable checking 24 VAC or replacing a fuse, call an HVAC tech.

## References
- Google Nest Help — *Troubleshoot Nest thermostat help codes* (E73/E74 definitions)  
- Google Nest Help — *Troubleshoot thermostat power issues during hot weather* (drip-pan/float switch, wiring steps)  
- Google Nest Help — *Learn about the common or C wire* (when a C-wire is recommended)  
- Google Nest Help — *Nest Power Connector* (stable power when C is missing)