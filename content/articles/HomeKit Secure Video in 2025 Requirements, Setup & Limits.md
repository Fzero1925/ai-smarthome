---
title: "HomeKit Secure Video in 2025: Requirements, Setup & Limits"
description: "iCloud+ plan tiers, required home hub, which devices work, and how storage, encryption, and notifications actually behave."
date: 2025-08-06
lastmod: 2025-08-06
slug: "homekit-secure-video-requirements-2025"
draft: false
categories: ["Guides","Apple Home","Cameras","Secuity"]
tags: ["HomeKit Secure Video","Apple Home","iCloud+","Home Hub","Cameras"]
author: "AI SmartHome Hub Editorial"
---

> **Quick answer** — To use **HomeKit Secure Video (HKSV)** you need:  
> 1) an **iCloud+ subscription**, and 2) a **home hub** (HomePod mini, HomePod, or Apple TV 4K). Recordings are **end-to-end encrypted** and **don’t count against iCloud storage**; live view and notifications work across your Apple devices. :contentReference[oaicite:23]{index=23}

## Applies to
- Apple **Home** with **iOS/iPadOS 18** or newer  
- Supported cameras with **HomeKit Secure Video** capability  
- Home hubs: **HomePod mini / HomePod / Apple TV 4K** (Thread-enabled models recommended for broader smart-home use). :contentReference[oaicite:24]{index=24}

## 5-minute setup
1. **Check iCloud+** on your Apple ID (Settings → your name → iCloud → *iCloud+*). HKSV requires iCloud+. :contentReference[oaicite:25]{index=25}  
2. Ensure a **home hub** is set up and online at home (HomePod mini/HomePod/Apple TV 4K). :contentReference[oaicite:26]{index=26}  
3. In the **Home app**, add your camera → enable **Recording** and select **When Home/Away** preferences.  
4. Configure **Activity Zones** and **Notifications** to trim false alerts.  
5. Verify remote access on cellular — live view should load, and motion snapshots should arrive.

## What HKSV actually does
- **E2E encryption**: Clips are encrypted and processed for detection in Apple’s architecture; **viewable across your Apple devices**. :contentReference[oaicite:27]{index=27}  
- **Storage math**: Apple states HKSV video **does not count** toward your iCloud storage quota. :contentReference[oaicite:28]{index=28}  
- **Hub requirement**: You need a **home hub** to record and for automations/notifications to be reliable. :contentReference[oaicite:29]{index=29}

## Troubleshooting matrix
| Symptom                         | Likely cause                                | What to do                                                   |
| ------------------------------- | ------------------------------------------- | ------------------------------------------------------------ |
| “Set up a home hub” prompt      | No active HomePod/Apple TV at home          | Plug in and sign into a **home hub**; confirm it shows as **Connected** in Home settings. :contentReference[oaicite:30]{index=30} |
| Live view works, no recordings  | iCloud+ missing or camera not set to record | Check **iCloud+** status and **Recording** options per camera. :contentReference[oaicite:31]{index=31} |
| Motion notifications unreliable | Focus modes / Home status                   | Allow Home notifications; verify **Presence** and **Activity Zones** settings. |

## Common pitfalls
- Assuming a camera marked “Works with Apple Home” automatically supports **HKSV** — many do **Home** only, not **HKSV**. Check the spec sheet.  
- Forgetting that while **iOS 18** lets you add some **Matter** devices without a hub, **HKSV** **still requires a home hub**. :contentReference[oaicite:32]{index=32}

## FAQ
- **Do recordings take up my iCloud storage?**  
  Apple says **no** — HKSV storage doesn’t count against your plan’s space. :contentReference[oaicite:33]{index=33}
- **Which hub should I buy?**  
  **HomePod mini** or **Apple TV 4K (3rd gen, Wi-Fi + Ethernet)** are Thread-enabled and future-proof for broader smart-home roles. :contentReference[oaicite:34]{index=34}
- **Can I add cameras while away from home?**  
  You can view and manage, but first setup usually requires being on the same network; follow the camera maker’s instructions.

## References
- Apple Support — *Set up HomeKit Secure Video on all your devices* (requires iCloud+ and home hub)  
  https://support.apple.com/guide/icloud/set-up-homekit-secure-video-mm7c90d21583/icloud  
- Apple Support — *Store encrypted security camera footage in iCloud with HomeKit Secure Video* (E2E, storage doesn’t count)  
  https://support.apple.com/guide/icloud/icloud-homekit-secure-video-mme054c72692/icloud  
- Apple Support — *Set up HomePod mini or HomePod as a home hub* (hub and Thread notes)  
  https://support.apple.com/en-us/102557