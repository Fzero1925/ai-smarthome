---
title: "Link TP-Link Tapo & Kasa to Google Home (2025): Setup & 'Couldn't Reach' Fixes"
description: "Clean account-linking steps for Tapo/Kasa with Google Home, plus reliable ways to re-link, remove, and resync when devices show offline or fail to appear."
date: 2025-09-17
lastmod: 2025-09-17
slug: "tapo-kasa-google-home-linking-2025"
draft: false
categories: ["Guides","Google Home","Integrations"]
tags: ["TP-Link","Tapo","Kasa","Google Home","Account Linking","Troubleshooting"]
author: "AI SmartHome Hub Editorial"
---

> **Quick answer** — Link **from the Tapo/Kasa app** (Third-Party Service → Google Assistant) **or** link **from Google Home** (Add → **Works with Google Home** → search **Tapo**/**Kasa**). If devices don’t show or say *“Couldn’t reach”*, **unlink the service** in Google Home and **link again**; note that unlinking removes **all** devices from that service.

## Two clean ways to link
**Option A — Start in Tapo/Kasa**  
1. Open **Tapo**/**Kasa** app → **Me** → **Third-Party Service** → **Google Assistant**.  
2. Tap **Link from Google Home app** and complete sign-in/consent.  

**Option B — Start in Google Home**  
1. Google Home → **Devices** → **Add** → **Works with Google Home**.  
2. Search **Tapo** or **Kasa** and sign in with your **TP-Link ID** to grant access.  
3. Assign rooms; test voice control.

## Fix devices that won’t appear / go offline
1. **Check cloud status** in Tapo/Kasa app — device must be online there first.  
2. **Unlink & re-link the service** in Google Home: **Settings → Works with Google Home → Linked services → [Tapo/Kasa] → Unlink account**; then link again.  
3. **Resync devices** (voice): “**Hey Google, sync my devices.**”  
4. **Network sanity**: keep device SSIDs simple; 2.4 GHz usually works best for plugs/bulbs; ensure router DNS/firewall allows outbound connections.

## What “unlink” really does
When you **unlink a service** in Google Home, you remove **all** devices for that brand from your account/home and revoke the app’s access; you’ll need to **link again** to restore control.

## Troubleshooting matrix
| Symptom                                      | Likely cause                              | What to do                                                   |
| -------------------------------------------- | ----------------------------------------- | ------------------------------------------------------------ |
| “Service linked successfully” but no devices | Wrong TP-Link account/home, or stale link | Unlink, confirm the correct **TP-Link ID** in Tapo/Kasa, re-link, then **sync devices**. |
| Camera streams fail on Nest display          | Permissions or app state                  | Re-link the service; verify camera works in Tapo first, then try Google display again. |
| Random “Couldn’t reach Tapo/Kasa”            | Cloud token expired / network issues      | Unlink/re-link; power-cycle the device and your router; confirm device online in Tapo/Kasa. |

## FAQ
- **Can I unlink just one Tapo/Kasa device?**  
  No. Google Home **unlinks the entire service**; to remove a single device, delete it in the **Tapo/Kasa app** and then resync in Google.  
- **Does this work with Matter?**  
  Many Tapo/Kasa devices still link via the **cloud service**. Matter devices can pair locally with Google Home if supported, but model coverage varies.

## References
- TP-Link Support — *How to connect my Tapo/Kasa smart device to Google Home* (linking options from either app)  
- Google Nest Help — *Connect third-party smart home devices in the Google Home app* (Works with Google Home; unlink behavior)  
- Google Account Help — *Google Account Linking with third-party apps & services* (how linking works/what access is granted)