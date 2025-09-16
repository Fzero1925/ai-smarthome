---
title: "Fix “Accessory Already Added” and Lost Codes in Apple Home (2025)"
description: "A practical, Apple-aligned playbook for ‘Already added / Can’t add accessory’ and missing HomeKit/Matter codes—where to find codes, how to add previously paired Matter devices, and when to reset."
date: 2025-09-17
lastmod: 2025-09-17
slug: "apple-home-accessory-already-added-lost-code-2025"
draft: false
categories: ["Guides","Apple Home","Matter","Fix"]
tags: ["HomeKit code","Matter","Add accessory","Already added","Reset"]
author: "AI SmartHome Hub Editorial"
---

> **Quick answer** — For **Matter** devices, use **Home → Add Accessory → More options → select the previously paired accessory** (Multi-Admin) instead of factory-resetting. For **classic HomeKit** devices, retrieve the **8-digit code** from the **device/box/manual** or (for some brands) from the **manufacturer app**, and only factory-reset if the accessory is still bound to another home/account.

## Applies to
- Apple **Home** on iOS/iPadOS 18 or newer  
- **Matter** accessories (previously paired) and **HomeKit-coded** accessories

## 10-minute recovery path
1. **If it’s Matter and already paired elsewhere**: in Apple **Home → Add Accessory → More options**, choose the accessory that’s **previously paired** and follow commissioning. (Requires a compatible controller/hub for best results.)  
2. **Find the HomeKit code** (for non-Matter): check the **device sticker**, **box flaps**, **manual**, or the **brand app** (some vendors expose the code digitally).  
3. **Still see “accessory already added”?** Remove it from the **other app/home** first, or perform a **factory reset** using the maker’s instructions, then re-add.  
4. If accessories show **“No Response”**, follow Apple’s reset/restart order (router → hubs/bridges → accessories → phone), then re-add if needed.

## Troubleshooting matrix
| Symptom                                | Likely cause                                          | What to do                                                   |
| -------------------------------------- | ----------------------------------------------------- | ------------------------------------------------------------ |
| “Already added to another home”        | Still bound to prior controller                       | **Remove from old home** or **factory reset**, then add again. |
| Code label missing                     | Code moved to packaging or app                        | Check **box/manual**; some brands show it **in-app** (e.g., LIFX). |
| Matter device won’t appear in Add flow | Not using “More options” for previously paired device | Use **More options**, then select the accessory from the list. |
| Accessory not responding after add     | Hub/network state                                     | Follow Apple’s **restart sequence**; update firmware in the maker app. |

## Common pitfalls
- Scanning QR without trying **More options** for **previously paired Matter** devices.  
- Throwing away boxes/manuals that carry **backup code stickers**.  
- Resetting too early—try proper **de-provisioning** first.

## FAQ
- **Can I recover a lost HomeKit code?**  
  If the brand exposes it **in-app** (e.g., LIFX), yes. Otherwise locate the physical sticker/packaging—or contact the manufacturer.  
- **Do I need a hub?**  
  iOS 18 can add many **Matter** devices without a hub, but a **Home hub** is recommended for automations/remote access.

## References
- Apple Support — *Pair and manage your Matter accessories* (**More options** for previously paired devices).  
- Apple Support — *If your HomeKit or Matter accessory isn’t responding* (restart order; remove/reset guidance).  
- TP-Link — *Where to find the HomeKit code (switch/plug/camera)*.  
- LIFX — *HomeKit Code Recovery* (retrieve code in app).  
- (Background) Media coverage on iOS 18 allowing **Matter add without a hub**.