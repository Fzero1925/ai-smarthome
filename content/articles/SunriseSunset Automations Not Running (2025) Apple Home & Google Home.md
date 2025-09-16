---
title: "Sunrise/Sunset Automations Not Running (2025): Apple Home & Google Home"
description: "Fix time-of-day and presence automations: Location Services, home hub status, app cache, and known vendor steps to restore reliable triggers."
date: 2025-09-17
lastmod: 2025-09-17
slug: "sunrise-sunset-automations-not-working-2025"
draft: false
categories: ["Guides","Automations"]
tags: ["Apple Home","HomeKit","Google Home","Routines","Location Services","Presence"]
author: "AI SmartHome Hub Editorial"
---

> **Quick answer** — **Apple Home**: confirm **Location Services** for Home are on, your **Home hub (HomePod/Apple TV)** is active, and the automation is **enabled**; power-cycle the hub and re-save the automation. **Google Home**: ensure devices are online, the app is current, and presence/time starters are configured correctly; clear app cache if needed. :contentReference[oaicite:25]{index=25}

## Apple Home: 10-minute recovery
1. **Enable Location Services** for the **Home** app; confirm **Share My Location** for your Apple ID. Re-toggle if it drifted after an update. :contentReference[oaicite:26]{index=26}  
2. **Verify hub status**: Home app → **Home Settings → Home Hubs & Bridges**. Ensure a **HomePod/Apple TV** is connected/primary; power-cycle to rebuild the network if needed. :contentReference[oaicite:27]{index=27}  
3. **Re-enable the automation**: Home app → **Automation → (select) → Enable This Automation**; test manually. :contentReference[oaicite:28]{index=28}  
4. **If devices show “No Response”**, follow Apple’s accessory troubleshooting: restart hubs/bridges and update firmware. :contentReference[oaicite:29]{index=29}

## Google Home: 10-minute recovery
1. **Devices online & app up to date**; verify which devices are included in the Routine/Automation. :contentReference[oaicite:30]{index=30}  
2. **Presence & time starters**: confirm presence is available for the home and that the **sunrise/sunset** starter uses the correct home location. (Use the new Automation editor if available.) :contentReference[oaicite:31]{index=31}  
3. **Clear Home app cache** and **restart phone** if routines fail to trigger. :contentReference[oaicite:32]{index=32}

## Troubleshooting matrix
| Symptom                                         | Likely cause                  | What to do                                                   |
| ----------------------------------------------- | ----------------------------- | ------------------------------------------------------------ |
| Apple sunrise/sunset never fires                | Location permission/hub drift | Re-enable **Location Services**, verify **hub online**, re-save automation. :contentReference[oaicite:33]{index=33} |
| Google automation doesn’t start                 | App state/cache               | **Update app**, **clear cache**, restart device; re-save Routine. :contentReference[oaicite:34]{index=34} |
| Devices respond manually but not in automations | Accessory state vs. triggers  | On Apple, follow **accessory not responding** steps; on Google, check device membership in the routine. :contentReference[oaicite:35]{index=35} |

## FAQ
- **Do sunrise/sunset require internet?**  
  Schedules are cloud-assisted and depend on correct **location & time**; if your hub or phone loses that data, triggers can be missed. (General behavior; see Apple/Google docs above.) :contentReference[oaicite:36]{index=36}  
- **My Google presence starter is missing—why?**  
  Feature availability can vary by account/home configuration; ensure the Home app is current and presence sensing is enabled for the home. :contentReference[oaicite:37]{index=37}

## References
- Apple Support — *Create scenes & automations; enable/disable automations (Home & Shortcuts).*  
- Apple Support — *If accessories aren’t responding in the Home app.*  
- Apple Community — *Sunset/Sunrise triggers fixed by re-enabling Location Services.*  
- Google Nest Help — *Troubleshoot Google Home automations.*  
- Tom’s Guide — *New Google Home automation editor (multi-condition starters).*  