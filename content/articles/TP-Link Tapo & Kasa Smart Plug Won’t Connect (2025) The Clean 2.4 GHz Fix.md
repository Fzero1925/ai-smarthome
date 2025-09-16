---
title: "TP-Link Tapo & Kasa Smart Plug Won’t Connect (2025): The Clean 2.4 GHz Fix"
description: "Vendor-backed steps to onboard Tapo/Kasa smart plugs: 2.4 GHz only, avoid WPA3-only, force your phone onto 2.4 GHz, and when to reset or create a temporary IoT SSID."
date: 2025-09-17
lastmod: 2025-09-17
slug: "tapo-kasa-smart-plug-wont-connect-2025"
draft: false
categories: ["Guides","Wi-Fi","Plugs","Security"]
tags: ["TP-Link","Tapo","Kasa","2.4 GHz","WPA3","Onboarding"]
author: "AI SmartHome Hub Editorial"
---

> **Quick answer** — Tapo/Kasa smart plugs connect to **2.4 GHz only**. Put your **phone** on 2.4 GHz during setup, **avoid WPA3-only** security, and keep the plug within a few meters of the router. If the SSID doesn’t appear, **disable 5 GHz temporarily** or create a **2.4 GHz-only guest/IoT SSID**, complete onboarding, then restore your normal settings.

## Applies to
- TP-Link **Tapo** and **Kasa** smart plugs and similar 2.4 GHz-only devices.

## 10-minute, vendor-aligned checklist
1. **Confirm 2.4 GHz**: Tapo/Kasa plugs do **not** support 5 GHz.  
2. **Phone on 2.4 GHz**: If your router uses a single SSID for 2.4/5 GHz, temporarily **turn off 5 GHz** or create a **2.4 GHz guest** so your phone joins 2.4 GHz.  
3. **Security mode**: Avoid **WPA3-only**; use **WPA2-PSK** during setup.  
4. **SSID & password hygiene**: Use simple names; avoid unusual characters while testing.  
5. **Signal & distance**: Place the plug within ~2–3 m of the router for pairing; you can relocate after it’s online.  
6. **Config mode & reset**: Ensure the plug’s LED indicates **setup/config mode**; if not, perform a factory **reset** per model guide.  
7. **IoT SSID (optional)**: Keep a dedicated **2.4 GHz IoT network** for plugs/bulbs if your household uses band steering or mesh.

## Troubleshooting matrix
| Symptom                          | Likely cause                          | What to do                                                   |
| -------------------------------- | ------------------------------------- | ------------------------------------------------------------ |
| SSID list shows nothing relevant | Phone is on 5 GHz / steering to 5 GHz | Temporarily disable 5 GHz; connect phone to 2.4 GHz or a 2.4 GHz guest SSID; retry scan. |
| “Incorrect password” loop        | WPA3-only or special chars issue      | Switch router to **WPA2-PSK**; use a simpler test password; try another phone. |
| Connects then drops              | Weak signal / roaming                 | Keep width at **20 MHz** on 2.4 GHz; reduce distance; consider an IoT SSID closer to the plug. |
| Can’t enter setup                | Not in config mode                    | Reset the plug; confirm LED pattern for config mode, then reattempt onboarding. |

## Common pitfalls
- Expecting 5 GHz support or **WPA3-only** compatibility.  
- Setting up while your **phone** is stubbornly on 5 GHz (band steering).  
- Hiding SSIDs or using complex passwords during the **first** pairing attempt.

## FAQ
- **Can I re-enable 5 GHz after pairing?**  
  Yes. Once the plug is onboarded to 2.4 GHz, you can turn 5 GHz back on.  
- **Do Tapo/Kasa support WPA3?**  
  Many models **don’t** pair on WPA3-only. Use **WPA2-PSK** during setup, then test WPA3 transition later if your router supports it.

## References
- TP-Link — *Fail to configure Tapo smart plug (2.4 GHz only; move closer; reset)*  
- TP-Link — *Fail to configure Kasa device (config mode; password; signal)*  
- TP-Link — *Fail to configure Tapo devices (2.4 GHz only; hidden SSID; rescan)*  
- TP-Link Community — *WPA3-only and special characters can block setup; force 2.4 GHz*  
- TP-Link Community — *Phone on 5 GHz prevents setup; disable 5 GHz temporarily*  