# Astroarch Interface

> **Controllo remoto completo di un osservatorio astronomico AstroArch da smartphone Android.**
> Clone mobile-friendly di KStars/Ekos con tutte le funzioni essenziali per una sessione di astrofotografia.

[![Version](https://img.shields.io/badge/version-0.2.12-f5a623?style=flat-square)](https://github.com/Johannes1979I/astroarch-interface/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](LICENSE)
[![Platform](https://img.shields.io/badge/Android-8.0%2B-green?style=flat-square&logo=android)](#)
[![Backend](https://img.shields.io/badge/Backend-Python%203.11%2B-blue?style=flat-square&logo=python)](#)

**Sviluppatore**: Zarletti-Osservatorio Jupiter
**Targets**: AstroArch (Arch Linux ARM) su Raspberry Pi 5 + smartphone Android

---

## Cos'è

Astroarch Interface è composta da due parti:

| | |
|---|---|
| 🖥️ **Backend** (`backend/astroarch_bridge`) | Daemon Python (FastAPI + WebSocket) installato sul Raspberry Pi 5. Si connette a INDI server, PHD2 e Ekos via DBus, esponendo una REST API + due stream WebSocket. **Zero modifiche** al setup di Ekos. |
| 📱 **App Android** (`android_app`) | App Flutter con 14 schermate dedicate ai vari moduli Ekos clonati per uso mobile. Comunica con il backend via Tailscale. |

L'app **NON sostituisce Ekos**: lo affianca. Ekos resta operativo sul desktop AstroArch, l'app legge i suoi stati via DBus e INDI, e invia comandi che Ekos esegue come al solito. Quando in Ekos viene scattata un'immagine, l'app la riceve in tempo reale via INDI BLOB intercept (parallelo, non invasivo).

---

## Funzionalità complete

### 📊 Dashboard
- Stato connessione live (INDI · PHD2 · WebSocket state · WebSocket frames)
- Coordinate target attivo (RA/Dec) con stato mount
- **Anteprima ultima immagine** auto-stretchata con HFR e star count
- 4 card live: Mount tracking · Camera temp/cooler · Guide RMS · Focuser pos
- Telemetria osservatorio: meteo, dome, weather safe

### 🔭 Mount
- Coordinate live RA/Dec aggiornate via WebSocket
- **Search SIMBAD** integrato (digita "M 31" → RA/Dec automatici via astropy)
- GoTo + Track / Slew / Sync con un tap
- Joypad slew manuale N/S/E/W con selezione rate (Guide / Centering / Find / Max)
- Park / Unpark / Sync / Stop di emergenza
- Tracking mode chips: Sidereal / Lunar / Solar / Off
- Pier side, accuratezza, settle time

### 🎯 Align (Plate Solve + Polar Align)
**Plate Solve** — clone esatto del modulo Ekos Align:
- Anteprima FITS live (zoom pinch) **stretchata identica a Ekos** (algoritmo ZScale + MTF asinh)
- Tempo, Gain, Binning configurabili — vengono applicati alla camera prima del solve
- Solver action: GoTo / Sync / Slew to target / Niente
- Modalità solver: StellarSolver / Remote (INDI)
- Coordinate telescopio + soluzione live (AR · DEC · Err · AP · Pix scale · FOV · Focal length · F/)
- Storia ultimi solve con dAR/dDEC colorati (verde<50″, giallo<150″, rosso oltre)
- **Plot target** stile Ekos con cerchi concentrici 50/100/150″
- Log Ekos Align espandibile

**Polar Align** — routine drift-based 3-step:
- Capture + plate solve in 3 posizioni RA diverse
- Calcolo errore AZ/ALT dalla deriva in Dec
- Suggerimenti di correzione viti

### 📷 Capture (Ekos-style)
- **Sequencer multi-job persistente** — modello Ekos completo
- Ogni job: filter, count, exposure, gain, offset, binning, frame type, transfer format (FITS/NATIVE/XISF), capture format (RAW/RGB), delay, dither flag, target name
- Lista jobs con drag-and-drop riordinabile, edit/duplica/rimuovi
- **Save/Load preset JSON** locali (es. "M31 LRGB notte 1")
- 3 modalità di esecuzione:
  - ⭐ **OSSERVAZIONE COMPLETA** — pipeline pre-flight 10 fasi (resolve target → slew → tracking → plate solve → sync → autofocus → guide calibrate → guide start → capture)
  - **VIA EKOS** — i job vengono caricati in Ekos Capture queue via DBus + start
  - **DIRETTO** — comandi diretti al driver INDI (no Ekos)

### 🎯 Guide (PHD2)
- RMS Total · SNR · RMS RA · RMS DEC live
- Grafico errore inseguimento RA/DEC (storico ultimi 120 sample)
- Bottoni: Start / Stop / Dither / Find Star / Calibrate / Clear cal / Pause
- Equipaggiamento PHD2 (versione, pixel scale, calibrato, settling)

### 🎛️ Focus
- Movimento manuale ±10/100/1000 step
- Posizione assoluta con campo numerico
- **Autofocus iterativo** lato bridge: N step × ±step_size, scatta exp_sec, calcola HFR, trova minimo, sposta sul best
- **Plot V-curve** live con punti colorati e linea verticale sul best position

### 🌡️ Cooler
- Toggle ON/OFF con stato visivo (verde se ON, neutro se OFF)
- Temperatura target editabile, sensore live
- Power % cooler con barra di progresso
- Auto-detection driver bloccato (es. ToupTek toupbase) con bottone **RICONNETTI DRIVER** per recuperare

### 🌐 Observatory
- Card meteo con tutti i parametri (temp, umidità, vento, cielo)
- Dome shutter open/close (compatibile sia DOME_SHUTTER standard sia DOME_PARK scripting/roll-off)
- Dust cap park/unpark
- Flat panel toggle + slider intensità 0-255
- Driver candidati con bottoni CONNECT/DISCONNECT inline

### 📅 Scheduler
- Card sky-state con fase twilight (day/civil/nautical/astronomical/night)
- Altitudine sole/luna live (lat/lon auto-rilevati dal mount via INDI)
- Lista jobs persistenti multi-target
- Form **+ NUOVO JOB** con risoluzione SIMBAD automatica
- Verifica condizioni live (twilight required, altitudine target, weather safe)

### ⚙️ Setup / Profili
- Lettura profili Ekos da `~/.local/share/kstars/userdb.sqlite`
- Lista driver INDI attivi con toggle Connect/Disconnect

### 🎛️ INDI Panel
**Clone esatto** della INDI Control Panel di KStars/Ekos:
- Lista di tutti i device connessi
- Tap su un device → tutte le sue properties raggruppate per Group
- Switch / Number / Text editabili in tempo reale
- Light read-only con stato colorato
- Cambiamenti propagati live in entrambe le direzioni (modifichi qui → Ekos lo vede; modifichi in Ekos → qui appare)

### 📁 Files
- Browser dei FITS in `~/Pictures/Ekos/`
- Lista file recenti con thumbnail auto-stretchata
- Tap → preview a schermo intero con zoom pinch
- **Selezione multipla** con long-press
- **Cancellazione batch** con conferma (libera spazio sul RPi senza occupare il telefono)
- Card storage RPi: barra GB usati/totali colorata, conteggio FITS

### 📈 Analyze
- Counters sessione: WS events, properties totali, devices
- Last frame info (object, filter, exposure, HFR, stars, size)
- Grafico storico RMS PHD2 (RA/DEC)
- Stream messaggi INDI

### 🔬 Activity Log
- **Tutte le chiamate API** dell'app al backend con timestamp ms, status code colorato, durata, body
- Tap per dettaglio + copia → debug rapidissimo

---

## Architettura

```
       App Android                 Tailscale (WireGuard)         Raspberry Pi 5 (AstroArch)
   ┌─────────────────┐                                       ┌──────────────────────────────┐
   │                 │ ─────HTTPS / WSS───────────────────► │  astroarch-bridge :8765      │
   │  Astroarch      │                                       │   ├─ REST   /api/*           │
   │  Interface      │ ◄────── live snapshots ──────────── │   ├─ WS     /ws/state        │
   │  (Flutter)      │                                       │   └─ WS     /ws/frames       │
   │                 │                                       │                              │
   │  14 schermate   │                                       │   ┌─ INDI client TCP :7624  │
   │  Provider       │                                       │   │  + enableBLOB (parallelo│
   │  WebSocket      │                                       │   │    a Ekos, no invadenza) │
   │                 │                                       │   ├─ PHD2 client TCP :4400  │
   │                 │                                       │   ├─ Ekos via DBus          │
   └─────────────────┘                                       │   └─ FITS watcher           │
                                                             │                              │
                                                             │  KStars/Ekos (intatto)       │
                                                             │  PHD2 (intatto)              │
                                                             │  ~/Pictures/Ekos/            │
                                                             └──────────────────────────────┘
```

**Caratteristica chiave**: il bridge è un *secondo client INDI* che non modifica nulla del setup di Ekos. Riceve i BLOB delle camere via `enableBLOB Also` in parallelo a Ekos, processa in memoria, invia alle app — **zero file su disco**, **zero interferenze con il workflow Ekos**.

---

## Installazione

Vedi [DEPLOY.md](DEPLOY.md) per istruzioni complete.

**Quick start**:

```bash
# 1. Sul Raspberry Pi
scp -r backend/ astronaut@RPI_IP:/tmp/
ssh astronaut@RPI_IP
cd /tmp/backend
sudo bash deploy/install.sh --user astronaut
# stampa URL e token

# 2. Scarica APK dalla pagina Releases di GitHub e installa sul cellulare
# https://github.com/Johannes1979I/astroarch-interface/releases/latest

# 3. Apri l'app, tap "SCAN QR DALLA DASHBOARD" e inquadra il QR sul desktop AstroArch
#    (oppure inserisci host/porta/token manualmente)
```

---

## Documentazione

- 📄 [Manuale utente PDF](AstroarchInterface_Manuale.pdf) — guida completa stampabile (13 pagine)
- 🔧 [DEPLOY.md](DEPLOY.md) — istruzioni installazione passo-passo
- 🎨 [mockups.html](mockups.html) — preview interfaccia (apri nel browser)

---

## Stack tecnologico

| | |
|---|---|
| **Backend** | Python 3.11+, FastAPI, uvicorn, WebSocket, asyncio |
| | astropy (FITS, SIMBAD, AltAz), Pillow, numpy, watchdog |
| | INDI XML protocol custom parser (incremental) |
| | PHD2 JSON-RPC, Ekos DBus (qdbus6) |
| **App** | Flutter 3.32 / Dart 3.5 |
| | provider, http, web_socket_channel, fl_chart, mobile_scanner |
| **Deploy** | systemd user service, install.sh, PKGBUILD opzionale |
| **Connettività** | Tailscale (WireGuard) — niente apertura porte sul router |

---

## Limitazioni note

- iOS non supportato (solo Android, scelta progettuale)
- Plate solving richiede `solve-field` (astrometry.net) installato sul RPi
- Il polar alignment è una routine "drift-based" semplificata (3 step), non sostituisce strumenti dedicati come SharpCap Polar Align

---

## Roadmap

- [ ] Mosaic planner
- [ ] Notifiche push (frame finito, sequenza completata, weather alert)
- [ ] Eventuale donazione codice come integrazione ufficiale al progetto [devDucks/astroarch](https://github.com/devDucks/astroarch)

---

## Licenza

[MIT](LICENSE) — feel free to use, modify, distribute. Mantieni l'attribuzione a Zarletti-Osservatorio Jupiter.

---

## Crediti

- **AstroArch** — distribuzione ArchLinux ARM per astrofotografia [github.com/devDucks/astroarch](https://github.com/devDucks/astroarch)
- **KStars / Ekos** — il software di riferimento per l'astrofotografia open source [edu.kde.org/kstars](https://edu.kde.org/kstars/)
- **PHD2** — autoguider [openphdguiding.org](https://openphdguiding.org/)
- **astrometry.net** — plate solving offline [astrometry.net](https://astrometry.net/)

---

🌙 **Buone osservazioni!** — Zarletti-Osservatorio Jupiter
