---
title: "AC Comes On When You Ask for Heat? Fix the Heat Pump O/B Setting (Nest & ecobee, 2025)"
description: "A vendor-approved playbook to correct reversed heating/cooling on heat pumps by setting the reversing valve (O vs. B) and verifying the fix safely."
date: 2025-09-17
lastmod: 2025-09-17
slug: "heat-pump-reversed-ob-setting-nest-ecobee-2025"
draft: false
categories: ["Guides","HVAC"]
tags: ["Heat pump","Reversing valve","O/B","Nest","ecobee","Wiring"]
author: "AI SmartHome Hub Editorial"
---

> **Quick answer** — If cooling runs when you ask for heat (or vice versa), your thermostat’s **reversing-valve** setting is likely wrong. On **Nest**: **Settings → Equipment → Heat Pump**, then toggle **O ↔ B** and test. On **ecobee**: ensure the **O/B** setting matches your heat pump (energize on **cool** for most brands; some, like Rheem/Ruud, energize on **heat**). Always **cut power** before touching wiring.

## Applies to
- Heat pump systems controlled by **Nest** or **ecobee** thermostats  
- Homes where heating/cooling seems **reversed**

## 10-minute fix
1. **Don’t rewire yet**. On Nest: go to **Equipment → Heat Pump** and flip **O/B** (from **O** to **B** or vice versa). Run **equipment tests** for **heat** and **cool**.  
2. On **ecobee**, open **Equipment → Heat Pump** and confirm **O/B Reversing Valve** orientation—most are **energize on cool**; change if your brand uses **energize on heat**.  
3. If symptoms persist, verify the **O/B wire** is fully seated and the system is indeed a **heat pump** (not conventional A/C + furnace).  
4. Only after settings are correct and tested should you investigate wiring/fuse issues.

## Troubleshooting matrix
| Symptom                      | Likely cause                     | What to do                                                   |
| ---------------------------- | -------------------------------- | ------------------------------------------------------------ |
| AC runs on Heat call         | O/B orientation wrong            | Flip **O ↔ B** in the thermostat’s **heat pump** menu; retest. |
| No heating or cooling at all | Open fuse/transformer or miswire | Check low-voltage fuse at air handler; confirm wiring at **R/Y/O/B/W/C**. |
| Works briefly then flips     | Mixed settings across app/local  | Re-run **equipment setup** and save; restart thermostat.     |

## Common pitfalls
- Assuming **winter/summer** requires manual flips—thermostats handle this automatically when **O/B** is set correctly.  
- Re-wiring before trying the **software orientation** change.  
- Forgetting to **cut power** at the breaker before touching low-voltage wiring.

## FAQ
- **Which brands use B (energize on heat)?**  
  Many **Rheem/Ruud** systems. Always check your unit’s manual or label.  
- **Will changing O/B damage anything?**  
  No—the setting tells the thermostat **when** to energize the reversing valve coil.

## References
- Google Nest Help — *Troubleshoot when heating and cooling are reversed* (Heat Pump O/B toggle steps).  
- Google Nest Help — *Troubleshoot heat pump issues* (reversed operation guidance).  
- ecobee Support — *Getting heat when calling for AC (check O/B reversing valve setting)*.