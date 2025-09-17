---
title: "Share a Matter Device with Multiple Apps (2025): Google Home, Apple Home, and Alexa"
description: "The correct multi-admin flow to add one Matter device to several ecosystems—what a Matter hub is, where to find the 11-digit pairing code, and how to fix common errors."
date: 2025-08-30
lastmod: 2025-08-30
slug: "matter-multi-admin-share-device-2025"
draft: false
categories: ["Guides","Matter","Interoperability","Smart Hub"]
tags: ["Matter","Multi-Admin","Google Home","Apple Home","Alexa"]
author: "AI SmartHome Hub Editorial"
---

> **Quick answer** — Use Matter’s **Multi-Admin**. In the **Alexa** app, open the device → **Other Assistants & Apps → Add another** to generate an **11-digit pairing code**. In **Google Home** or **Apple Home**, choose **Add accessory/device** and **enter that code**. You need a compatible **Matter hub** in the target ecosystem (e.g., Nest Hub/Chromecast for Google; HomePod/Apple TV recommended for Apple). :contentReference[oaicite:0]{index=0}

## Before you start
- **Confirm a Matter hub** is available in each ecosystem you want to add (e.g., Nest Hub/Nest Wifi Pro/Chromecast with Google TV; HomePod/Apple TV; many Echo models act as controllers). :contentReference[oaicite:1]{index=1}  
- **Multi-Admin ≠ auto-sync**: you **add** the same device to each platform; it won’t appear everywhere automatically. :contentReference[oaicite:2]{index=2}

## Add an already-paired device to another app
### From Alexa → to Google Home or Apple Home
1. Alexa app → your **Matter device** → **Other Assistants & Apps** → **Add another**. Copy the **11-digit code**. :contentReference[oaicite:3]{index=3}  
2. In the target app:  
   - **Google Home**: **Add → New device → Matter** (have a Google-compatible hub). Enter the code. :contentReference[oaicite:4]{index=4}  
   - **Apple Home**: **Home → “+” → Add Accessory → More options** (select the **previously paired** accessory). Enter code if prompted. A Home hub is recommended for best results. :contentReference[oaicite:5]{index=5}

### From a manufacturer app → to Google Home
- When finishing setup in the manufacturer app, **accept the prompt to share** with Google Home; or later, follow the brand’s “Share with Google Home” instructions. :contentReference[oaicite:6]{index=6}

## Troubleshooting matrix
| Symptom                                                    | Likely cause                         | What to do                                                   |
| ---------------------------------------------------------- | ------------------------------------ | ------------------------------------------------------------ |
| Device doesn’t show in Google Home after pairing elsewhere | Not shared to Google Home            | In the manufacturer app, **enable sharing** to Google Home; verify you have a **Google Matter hub**. :contentReference[oaicite:7]{index=7} |
| Target app rejects QR/doesn’t scan                         | Need **11-digit** “Add another” code | Use Alexa’s **Other Assistants & Apps → Add another** to generate and enter the code. :contentReference[oaicite:8]{index=8} |
| Control flaky/offline                                      | No local controller / hub missing    | Ensure an eligible hub is online; Matter enables **local** control with supported hubs. :contentReference[oaicite:9]{index=9} |

## FAQ
- **Can one code be reused across apps?**  
  Multi-Admin uses per-share commissioning; you’ll **add once per platform** (codes are generated for that flow). :contentReference[oaicite:10]{index=10}
- **Do I need to reset to share?**  
  No—use the in-app **share/add another** flow first. Factory reset is last resort.

## References
- Google Nest Help — *Set up / manage Matter; share with Google Home.*  
- Apple Support — *Pair & manage Matter accessories; add previously paired accessory.*  
- Amazon Help — *Set up an Alexa-connected Matter device to another voice service* (11-digit code).  
- Silicon Labs Docs — *Using Multi-Admin (“Other Assistants & Apps → Add Another”).*  
- Google Nest Help — *Prepare your smart home for Matter* (hub requirements; cross-platform control).  