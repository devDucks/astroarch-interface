"""Genera il manuale PDF di Astroarch Interface.

Sviluppatore: Zarletti-Osservatorio Jupiter
"""
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer,
                                 PageBreak, Table, TableStyle, KeepTogether,
                                 ListFlowable, ListItem)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.pdfgen import canvas as canvas_module
from datetime import datetime

OUTPUT = r"C:/Users/Zarletti/Desktop/AstroarchInterface_Manuale.pdf"

# Palette
ACCENT = colors.HexColor("#c98612")
ACCENT_LIGHT = colors.HexColor("#f5a623")
TEXT_DARK = colors.HexColor("#1a1d24")
MUTED = colors.HexColor("#6b7280")
PANEL = colors.HexColor("#f6f7fa")
LINE = colors.HexColor("#e0e3e8")
OK = colors.HexColor("#1f8b62")
ERR = colors.HexColor("#b3303f")

styles = getSampleStyleSheet()

# Custom styles
def make_styles():
    styles.add(ParagraphStyle(
        name="DocTitle", fontSize=28, leading=32, alignment=TA_CENTER,
        textColor=TEXT_DARK, spaceAfter=8, fontName="Helvetica-Bold"))
    styles.add(ParagraphStyle(
        name="DocSubtitle", fontSize=14, leading=18, alignment=TA_CENTER,
        textColor=MUTED, spaceAfter=4, fontName="Helvetica"))
    styles.add(ParagraphStyle(
        name="ChapterTitle", fontSize=20, leading=26, textColor=ACCENT,
        spaceBefore=18, spaceAfter=10, fontName="Helvetica-Bold",
        borderPadding=(0, 0, 6, 0)))
    styles.add(ParagraphStyle(
        name="SectionTitle", fontSize=14, leading=18, textColor=TEXT_DARK,
        spaceBefore=12, spaceAfter=6, fontName="Helvetica-Bold"))
    styles.add(ParagraphStyle(
        name="SubSection", fontSize=12, leading=15, textColor=ACCENT,
        spaceBefore=8, spaceAfter=4, fontName="Helvetica-Bold"))
    styles.add(ParagraphStyle(
        name="Body", fontSize=10, leading=14, textColor=TEXT_DARK,
        alignment=TA_JUSTIFY, spaceAfter=6, fontName="Helvetica"))
    styles.add(ParagraphStyle(
        name="Mono", fontSize=9, leading=12, textColor=TEXT_DARK,
        fontName="Courier", backColor=PANEL, borderColor=LINE,
        borderWidth=0.5, borderPadding=6, spaceAfter=8))
    styles.add(ParagraphStyle(
        name="Note", fontSize=9.5, leading=13, textColor=TEXT_DARK,
        backColor=colors.HexColor("#fff7e6"),
        borderColor=ACCENT_LIGHT, borderWidth=0.6, borderPadding=8,
        leftIndent=0, rightIndent=0, spaceBefore=6, spaceAfter=8,
        fontName="Helvetica"))
    styles.add(ParagraphStyle(
        name="Warning", fontSize=9.5, leading=13, textColor=TEXT_DARK,
        backColor=colors.HexColor("#fff0f3"),
        borderColor=ERR, borderWidth=0.6, borderPadding=8,
        leftIndent=0, rightIndent=0, spaceBefore=6, spaceAfter=8,
        fontName="Helvetica"))


def page_layout(canvas, doc):
    """Header/footer su ogni pagina."""
    canvas.saveState()
    w, h = A4
    # Footer
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(MUTED)
    canvas.drawString(2 * cm, 1 * cm, "Astroarch Interface - Manuale utente")
    canvas.drawCentredString(w / 2, 1 * cm, "Zarletti-Osservatorio Jupiter")
    canvas.drawRightString(w - 2 * cm, 1 * cm, f"Pag. {doc.page}")
    # Header line (skip on cover)
    if doc.page > 1:
        canvas.setStrokeColor(LINE)
        canvas.line(2 * cm, h - 1.5 * cm, w - 2 * cm, h - 1.5 * cm)
        canvas.setFont("Helvetica-Bold", 8)
        canvas.setFillColor(ACCENT)
        canvas.drawString(2 * cm, h - 1.2 * cm, "ASTROARCH INTERFACE")
        canvas.setFillColor(MUTED)
        canvas.setFont("Helvetica", 8)
        canvas.drawRightString(w - 2 * cm, h - 1.2 * cm, "v0.2.4")
    canvas.restoreState()


def cover_layout(canvas, doc):
    """Cover speciale con sfondo gradient."""
    canvas.saveState()
    w, h = A4
    # Sfondo dark
    canvas.setFillColor(colors.HexColor("#0a0d12"))
    canvas.rect(0, 0, w, h, stroke=0, fill=1)
    # Banda accent in alto
    canvas.setFillColor(ACCENT_LIGHT)
    canvas.rect(0, h - 0.8 * cm, w, 0.8 * cm, stroke=0, fill=1)
    # Titolo
    canvas.setFont("Helvetica-Bold", 38)
    canvas.setFillColor(colors.white)
    canvas.drawCentredString(w / 2, h - 6 * cm, "Astroarch")
    canvas.setFillColor(ACCENT_LIGHT)
    canvas.drawCentredString(w / 2, h - 7.5 * cm, "Interface")
    # Sottotitolo
    canvas.setFont("Helvetica", 14)
    canvas.setFillColor(colors.HexColor("#8a93a6"))
    canvas.drawCentredString(w / 2, h - 9 * cm,
                              "Controllo remoto osservatorio AstroArch da smartphone Android")
    # Logo decorativo (cerchio)
    canvas.setStrokeColor(ACCENT_LIGHT)
    canvas.setLineWidth(2)
    canvas.circle(w / 2, h - 13 * cm, 1.8 * cm, stroke=1, fill=0)
    canvas.setFont("Helvetica-Bold", 28)
    canvas.setFillColor(ACCENT_LIGHT)
    canvas.drawCentredString(w / 2, h - 13.4 * cm, "*")
    # Footer cover
    canvas.setFont("Helvetica", 11)
    canvas.setFillColor(colors.HexColor("#e6eaf2"))
    canvas.drawCentredString(w / 2, 4 * cm, "Manuale Utente e Installazione")
    canvas.setFont("Helvetica", 10)
    canvas.setFillColor(colors.HexColor("#8a93a6"))
    canvas.drawCentredString(w / 2, 3.3 * cm, "Versione 0.2.4")
    canvas.drawCentredString(w / 2, 2.7 * cm, "Sviluppatore: Zarletti-Osservatorio Jupiter")
    canvas.drawCentredString(w / 2, 2.1 * cm,
                              datetime.now().strftime("%d %B %Y"))
    # Banda accent in basso
    canvas.setFillColor(ACCENT_LIGHT)
    canvas.rect(0, 0, w, 0.8 * cm, stroke=0, fill=1)
    canvas.restoreState()


make_styles()


def H1(t): return Paragraph(t, styles["ChapterTitle"])
def H2(t): return Paragraph(t, styles["SectionTitle"])
def H3(t): return Paragraph(t, styles["SubSection"])
def P(t): return Paragraph(t, styles["Body"])
def CODE(t):
    safe = t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    safe = safe.replace("\n", "<br/>")
    return Paragraph(f'<font face="Courier">{safe}</font>', styles["Mono"])
def NOTE(t): return Paragraph(f"<b>Nota:</b> {t}", styles["Note"])
def WARN(t): return Paragraph(f"<b>Attenzione:</b> {t}", styles["Warning"])


def kv_table(rows, widths=None):
    widths = widths or [4 * cm, 12 * cm]
    t = Table(rows, colWidths=widths, hAlign="LEFT")
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), PANEL),
        ("TEXTCOLOR", (0, 0), (0, -1), MUTED),
        ("FONT", (0, 0), (0, -1), "Helvetica-Bold", 9),
        ("FONT", (1, 0), (1, -1), "Helvetica", 9.5),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LINEBELOW", (0, 0), (-1, -2), 0.5, LINE),
        ("BOX", (0, 0), (-1, -1), 0.5, LINE),
    ]))
    return t


def grid_table(header, rows, col_widths=None):
    data = [header] + rows
    t = Table(data, colWidths=col_widths, hAlign="LEFT")
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), ACCENT_LIGHT),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#1a1305")),
        ("FONT", (0, 0), (-1, 0), "Helvetica-Bold", 9),
        ("FONT", (0, 1), (-1, -1), "Helvetica", 9),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LINEBELOW", (0, 0), (-1, -1), 0.4, LINE),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, PANEL]),
        ("BOX", (0, 0), (-1, -1), 0.5, LINE),
    ]))
    return t


# ----------------------------------------------------------------------------
# COSTRUZIONE DOCUMENTO
# ----------------------------------------------------------------------------

story = []

# COVER (rendered via cover_layout, content vuoto qui)
story.append(Spacer(1, 24 * cm))
story.append(PageBreak())

# ============================================================================
# 1. INTRODUZIONE
# ============================================================================
story.append(H1("1. Introduzione"))
story.append(P(
    "<b>Astroarch Interface</b> è un'applicazione Android che permette di controllare "
    "in modo completo un osservatorio astronomico basato sulla distribuzione "
    "<b>AstroArch</b> (Arch Linux per RaspberryPi con KStars/Ekos/INDI) installata "
    "su un Raspberry Pi 5. L'app si collega via Tailscale al RaspberryPi e replica "
    "in tempo reale tutte le funzioni di Ekos in formato mobile-friendly."))
story.append(P(
    "Il progetto è composto da due parti:"))
story.append(ListFlowable([
    ListItem(P("<b>Backend astroarch-bridge</b>: daemon Python (FastAPI + WebSocket) "
               "installato sul RaspberryPi 5. Comunica con il server INDI, PHD2 e "
               "Ekos via DBus, esponendo una REST API + due stream WebSocket all'app.")),
    ListItem(P("<b>App Android</b>: scritta in Flutter, fornisce 14 schermate dedicate "
               "ai vari moduli Ekos clonati per uso mobile.")),
], bulletType="bullet", leftIndent=20))

story.append(H2("1.1 Cosa puoi fare con l'app"))
story.append(ListFlowable([
    ListItem(P("Visualizzare in tempo reale lo stato di mount, camera, focuser, "
               "filter wheel, dome, weather (telemetria live via WebSocket)")),
    ListItem(P("Pianificare ed eseguire sequenze multi-job di scatti come in Ekos")),
    ListItem(P("Eseguire una pipeline pre-flight completa: slew → plate solve → sync → "
               "guide → autofocus → cattura, in un click")),
    ListItem(P("Cercare oggetti per nome (SIMBAD) e fare GoTo con un tap")),
    ListItem(P("Controllare PHD2 (calibrazione, guiding, dither) con grafico RMS live")),
    ListItem(P("Controllare il focheggiatore manualmente o avviare autofocus iterativo "
               "con plot V-curve in tempo reale")),
    ListItem(P("Effettuare plate solving via solve-field astrometry.net e sincronizzare "
               "la mount sul risultato")),
    ListItem(P("Vedere live le immagini scattate (FITS auto-stretchato in JPEG via WebSocket)")),
    ListItem(P("Modificare qualsiasi proprietà INDI dal pannello clone della Ekos INDI Control Panel")),
    ListItem(P("Pianificare jobs scheduler con condizioni twilight, altitudine target, weather")),
], bulletType="bullet", leftIndent=20))

story.append(H2("1.2 Architettura"))
story.append(P("Schema di alto livello del flusso dati:"))
story.append(CODE(
    "App Android  ──Tailscale (WireGuard)──▶  Raspberry Pi 5\n"
    "                                          ├─ astroarch-bridge :8765\n"
    "                                          │   ├─ REST  /api/*\n"
    "                                          │   ├─ WS    /ws/state  (clone live)\n"
    "                                          │   └─ WS    /ws/frames (JPEG live)\n"
    "                                          ├─ INDI server :7624\n"
    "                                          ├─ PHD2 :4400 (JSON-RPC)\n"
    "                                          ├─ KStars/Ekos (DBus)\n"
    "                                          └─ ~/Pictures/Ekos (FITS storage)"))

story.append(NOTE("Tailscale fornisce cifratura WireGuard end-to-end. Non serve "
                  "configurare HTTPS sopra: la porta 8765 è esposta in chiaro ma il "
                  "tunnel Tailscale rende il traffico inaccessibile a chiunque non "
                  "sia nella tua tailnet."))

story.append(PageBreak())

# ============================================================================
# 2. INSTALLAZIONE
# ============================================================================
story.append(H1("2. Installazione"))

story.append(H2("2.1 Prerequisiti"))
story.append(P("Sul Raspberry Pi (lato server):"))
story.append(ListFlowable([
    ListItem(P("Distribuzione AstroArch (Arch Linux for RaspberryPi)")),
    ListItem(P("Python 3.11+ con pip")),
    ListItem(P("Tailscale installato e attivo")),
    ListItem(P("KStars/Ekos installati con un profilo INDI configurato")),
    ListItem(P("PHD2 installato (opzionale, per guiding)")),
    ListItem(P("astrometry.net + index files in <font face='Courier'>"
               "~/.local/share/kstars/astrometry/</font> (opzionale, per plate solving)")),
], bulletType="bullet", leftIndent=20))
story.append(P("Sul cellulare Android (lato client):"))
story.append(ListFlowable([
    ListItem(P("Android 8.0 (API 26) o superiore")),
    ListItem(P("App Tailscale installata e collegata alla stessa tailnet del RaspberryPi")),
    ListItem(P("~50 MB di spazio libero")),
], bulletType="bullet", leftIndent=20))

story.append(H2("2.2 Installazione backend sul RaspberryPi"))
story.append(H3("Step 1 - Trasferire il backend"))
story.append(P("Dal computer dove hai il file <i>backend/</i> della distribuzione "
               "Astroarch Interface:"))
story.append(CODE("scp -r backend/ astronaut@100.74.22.40:/tmp/"))
story.append(P("(Sostituisci <font face='Courier'>100.74.22.40</font> con l'IP "
               "Tailscale del tuo RaspberryPi)"))

story.append(H3("Step 2 - Installare il servizio"))
story.append(P("SSH sul RaspberryPi ed esegui:"))
story.append(CODE("ssh astronaut@100.74.22.40\n"
                  "cd /tmp/backend\n"
                  "sudo bash deploy/install.sh --user astronaut"))
story.append(P("Lo script:"))
story.append(ListFlowable([
    ListItem(P("Crea/usa l'utente specificato (default: <i>astroarch</i>; passare "
               "<font face='Courier'>--user astronaut</font> per usare il proprio)")),
    ListItem(P("Installa le dipendenze Python (FastAPI, uvicorn, astropy, pillow, "
               "watchdog, pydantic, websockets, numpy)")),
    ListItem(P("Installa il package <font face='Courier'>astroarch_bridge</font>")),
    ListItem(P("Crea il servizio systemd <font face='Courier'>astroarch-bridge.service</font>")),
    ListItem(P("Abilita l'avvio automatico al boot")),
    ListItem(P("Avvia il daemon")),
], bulletType="bullet", leftIndent=20))
story.append(P("Al termine, lo script stampa l'URL e il <b>token Bearer</b> "
               "auto-generato. Annotalo: ti servirà per connettere l'app."))
story.append(CODE("==> astroarch-bridge installed and running\n"
                  "    URL:   http://100.74.22.40:8765\n"
                  "    Token: kJ3xSn9mZ7TqW...   (es)"))

story.append(H3("Step 3 - Verificare il servizio"))
story.append(CODE("systemctl --user status astroarch-bridge\n"
                  "journalctl --user -u astroarch-bridge -f\n"
                  "curl http://localhost:8765/healthz"))
story.append(P("L'output di healthz deve mostrare:"))
story.append(CODE('{"ok":true,"version":"0.1.0","indi":"...","phd2":"..."}'))

story.append(H2("2.3 Installazione dashboard desktop"))
story.append(P("Sul desktop di AstroArch viene installata una mini-dashboard Tk per "
               "monitorare lo stato del bridge e generare il QR code per l'app:"))
story.append(CODE("scp -r desktop_dashboard/ astronaut@100.74.22.40:/home/astronaut/astroarch-bridge-dashboard\n"
                  "scp desktop_dashboard/AstroarchBridge.desktop \\\n"
                  "    astronaut@100.74.22.40:/home/astronaut/Desktop/\n"
                  "ssh astronaut@100.74.22.40 'chmod +x ~/Desktop/AstroarchBridge.desktop'"))
story.append(P("Sul desktop AstroArch vedrai l'icona <b>Astroarch Bridge</b> che apre "
               "una finestra con stato servizio, info Ekos, URL/Token, QR code per "
               "configurazione automatica dell'app, e bottoni Connetti/Disconnetti."))

story.append(H2("2.4 Installazione APK su Android"))
story.append(P("Sul cellulare:"))
story.append(ListFlowable([
    ListItem(P("Trasferisci il file <font face='Courier'>"
               "AstroarchInterface-v0.2.4.apk</font> al telefono "
               "(USB / Drive / Tailscale Drop)")),
    ListItem(P("Apri il file dal file manager. Android chiederà di abilitare "
               '"Installa app da fonti sconosciute" per il file manager: confermalo.')),
    ListItem(P("Tap <b>Installa</b> → l'app appare nel launcher come "
               '<b>"Astroarch Interface"</b>')),
], bulletType="bullet", leftIndent=20))

story.append(H2("2.5 Primo accesso"))
story.append(P("Apri l'app:"))
story.append(ListFlowable([
    ListItem(P("Tappa <b>SCAN QR DALLA DASHBOARD</b> e inquadra il QR code "
               "mostrato sulla dashboard desktop del RaspberryPi: "
               "host, porta e token vengono compilati automaticamente.")),
    ListItem(P("In alternativa, inserisci manualmente:")),
], bulletType="bullet", leftIndent=20))
story.append(kv_table([
    ["HOST", "IP Tailscale del RaspberryPi (es. 100.74.22.40)"],
    ["PORTA", "8765"],
    ["TOKEN", "Quello mostrato dall'installer o letto via cat ~/.config/astroarch-bridge/token"],
]))
story.append(P("Tap <b>CONNETTI</b>. Se la connessione è ok, l'app passa direttamente "
               "alla Dashboard. Se fallisce, tap <b>TEST</b> per la diagnostica step-by-step."))

story.append(WARN("Se la connessione fallisce con timeout, verifica che Tailscale sia "
                  "attivo sul cellulare. Su alcuni dispositivi Android (Xiaomi/MIUI, "
                  "OnePlus, Samsung) bisogna disabilitare il battery optimization "
                  "per Tailscale, altrimenti la VPN viene uccisa in background."))

story.append(PageBreak())

# ============================================================================
# 3. INTERFACCIA - SCHERMATE PRINCIPALI
# ============================================================================
story.append(H1("3. Schermate principali"))
story.append(P("L'app ha una <b>bottom navigation</b> a 5 voci sempre visibili "
               "(Dashboard, Mount, Capture, Guide, Menu) e un <b>drawer laterale</b> "
               "con le schermate avanzate raggiungibile dal pulsante Menu."))

story.append(H2("3.1 Dashboard"))
story.append(P("Schermata di partenza dopo il login. Mostra in tempo reale:"))
story.append(ListFlowable([
    ListItem(P("<b>Banner connessione</b> in cima con stato INDI / PHD2 / WS state / "
               "WS frames a colpo d'occhio (verde=ok, giallo=connecting, rosso=fail)")),
    ListItem(P("<b>Target attivo</b> con coordinate RA/Dec e stato mount")),
    ListItem(P("<b>Preview ultima immagine catturata</b> auto-stretchata, tap per "
               "Live View a schermo intero")),
    ListItem(P("4 card stato: Mount (tracking), Camera (temperatura), Guide (RMS PHD2), "
               "Focuser (posizione)")),
    ListItem(P("Telemetria osservatorio: meteo, dome, weather safe")),
], bulletType="bullet", leftIndent=20))

story.append(H2("3.2 Mount"))
story.append(P("Controllo telescopio completo:"))
story.append(ListFlowable([
    ListItem(P("<b>Coordinate live</b> RA/Dec aggiornate in tempo reale, pier side, "
               "stato corrente del mount")),
    ListItem(P("<b>Search SIMBAD</b>: digita un nome (M 31, NGC 7000, Vega) e tappa "
               "CERCA. Ottieni RA/Dec via astropy. Bottoni: GOTO+TRACK / SLEW / SYNC")),
    ListItem(P("<b>GoTo manuale</b> con campi RA (ore) e Dec (gradi)")),
    ListItem(P("<b>Joypad slew</b> manuale N/S/E/W con selezione rate "
               "(GUIDE / CENTERING / FIND / MAX a seconda del driver)")),
    ListItem(P("<b>Park/Unpark/Sync/Stop</b> rapidi")),
    ListItem(P("<b>Tracking mode</b> chip selezionabili: Sidereal / Lunar / Solar / Off")),
], bulletType="bullet", leftIndent=20))

story.append(H2("3.3 Capture"))
story.append(P("Sequencer multi-job stile Ekos:"))
story.append(ListFlowable([
    ListItem(P("<b>Pannello Cooler</b> con temperatura sensore live, target editabile, "
               "barra Power %, toggle ON/OFF visivo (verde quando ON), bottone "
               "RICONNETTI DRIVER per recuperare i casi di driver bloccato (es ToupTek)")),
    ListItem(P("<b>Lista jobs</b> trascinabili per riordinare, con menu contestuale "
               "(Modifica / Duplica / Rimuovi)")),
    ListItem(P("Ogni job ha: filter, count, exposure, gain, offset, binning, "
               "frame type (Light/Dark/Flat/Bias), transfer format (FITS/NATIVE/XISF), "
               "capture format (RAW/RGB), delay, dither flag, target name")),
    ListItem(P("<b>+ NUOVO JOB</b>: form completo con tutti i parametri")),
    ListItem(P("<b>Preset</b>: salva/carica sequenze JSON (es. 'M31 LRGB notte 1')")),
    ListItem(P("<b>AVVIA SEQUENZA</b>: dialog con 3 opzioni — vedi capitolo 4")),
], bulletType="bullet", leftIndent=20))

story.append(H2("3.4 Guide"))
story.append(P("Controllo PHD2 completo:"))
story.append(ListFlowable([
    ListItem(P("Card: RMS Total, SNR, RMS RA, RMS Dec")),
    ListItem(P("Grafico errore inseguimento RA/Dec live (storico ultime ~120 letture)")),
    ListItem(P("Bottoni: START / STOP / DITHER / FIND STAR / CALIBRATE / CLEAR CAL / PAUSE")),
    ListItem(P("Equipaggiamento PHD2: versione, scale ″/px, calibrato, settling")),
], bulletType="bullet", leftIndent=20))

story.append(PageBreak())

# ============================================================================
# 4. PIPELINE OSSERVAZIONE COMPLETA
# ============================================================================
story.append(H1("4. Pipeline pre-flight"))
story.append(P("Quando tappi <b>AVVIA SEQUENZA</b> nella Capture compare un dialog "
               "con <b>tre modalità</b> di esecuzione:"))

story.append(H2("4.1 OSSERVAZIONE COMPLETA (consigliata)"))
story.append(P("Esegue una pipeline orchestrata di 10 fasi che replica esattamente "
               "il comportamento di Ekos Scheduler:"))
story.append(grid_table(
    ["#", "Fase", "Descrizione", "Skip"],
    [
        ["1", "resolve_target", "Risolve nome via SIMBAD/astropy → RA/Dec", "—"],
        ["2", "slew", "Mount goto+track verso il target", "—"],
        ["3", "tracking", "Aspetta state Ok del mount (max 5 min)", "—"],
        ["4", "plate_solve", "solve-field sull'ultimo frame con hint ±5°", "opt"],
        ["5", "sync_mount", "Sincronizza mount sul solve, riattiva tracking", "auto"],
        ["6", "autofocus", "Loop iterativo HFR con V-curve", "opt"],
        ["7", "guide_calibrate", "PHD2 clear+recalibrate, attesa Guiding (4 min)", "opt"],
        ["8", "guide_start", "PHD2 start guiding, attesa settle (3 min)", "opt"],
        ["9", "capture_load", "Carica .esq in Ekos via DBus", "—"],
        ["10", "capture_started", "Avvia coda Ekos Capture", "—"],
    ],
    col_widths=[1 * cm, 3 * cm, 9 * cm, 1.5 * cm]))
story.append(P("Solo dopo che ogni fase passa con successo, parte la cattura. "
               "L'app mostra una <b>timeline live</b> con stato colorato per ogni fase "
               "(grigio=pending, ambra=running, verde=done, rosso=failed)."))

story.append(NOTE("Le fasi opzionali si abilitano nella schermata Observation. "
                  "Per la prima sera consiglio di attivare tutto. Nei cicli successivi "
                  "puoi disabilitare plate solve e calibrate (sono i più lenti) per uno "
                  "start più rapido."))

story.append(H2("4.2 VIA EKOS (loadSequenceQueue)"))
story.append(P("Genera un file <font face='Courier'>.esq</font> dai jobs Flutter e lo "
               "carica nella Ekos Capture queue via DBus, poi avvia. La sequenza "
               "appare <b>dentro</b> la finestra Capture di Ekos sul desktop. "
               "Ekos gestisce dither, autofocus on filter change, naming FITS, "
               "meridian flip — tutto il suo workflow standard."))

story.append(H2("4.3 DIRETTO (via INDI)"))
story.append(P("L'app comanda direttamente i driver INDI senza passare da Ekos. "
               "Più veloce ma Ekos non vede la sequenza nella sua UI."))

story.append(WARN("In modalità DIRETTO l'app forza automaticamente "
                  "<font face='Courier'>UPLOAD_MODE=BOTH</font> e "
                  "<font face='Courier'>UPLOAD_DIR=~/Pictures/Ekos/AstroarchInterface/</font> "
                  "così i FITS arrivano sia a Ekos sia al watcher dell'app."))

story.append(PageBreak())

# ============================================================================
# 5. SCHERMATE AVANZATE
# ============================================================================
story.append(H1("5. Schermate avanzate"))
story.append(P("Tutte raggiungibili dal drawer laterale (tap Menu nella bottom nav)."))

story.append(H2("5.1 Live View"))
story.append(P("Visualizzatore a schermo intero dell'ultimo frame catturato, con "
               "zoom pinch e metadata (HFR, stelle, esposizione, filter)."))

story.append(H2("5.2 Focus"))
story.append(P("Controllo focheggiatore con autofocus iterativo:"))
story.append(ListFlowable([
    ListItem(P("Movimento manuale ±10/100/1000 step in/out")),
    ListItem(P("Posizione assoluta con campo numerico")),
    ListItem(P("<b>Autofocus iterativo</b>: imposta step size, n step (dispari), "
               "esposizione → AVVIA. Il bridge fa N scatti a posizioni diverse, "
               "calcola HFR per ciascuna, trova il minimo, sposta sul best position.")),
    ListItem(P("<b>Plot V-curve live</b> con punti colorati e linea verticale "
               "tratteggiata sul best position trovato")),
], bulletType="bullet", leftIndent=20))

story.append(H2("5.3 Align (Plate Solve)"))
story.append(P("Plate solving via solve-field astrometry.net:"))
story.append(ListFlowable([
    ListItem(P("Mostra l'ultimo frame catturato e i suoi metadata")),
    ListItem(P("Tap <b>PLATE SOLVE</b> → backend lancia "
               "<font face='Courier'>solve-field</font> con hint dal mount corrente "
               "(raggio 5°), poll status ogni 2s")),
    ListItem(P("Quando finisce, mostra RA/Dec/scale ″/px estratti via "
               "<font face='Courier'>astropy.wcs.WCS</font> dal file .wcs")),
    ListItem(P("Bottone <b>SYNC MOUNT</b>: sincronizza la mount sul risultato del solve")),
    ListItem(P("Output completo di solve-field espandibile per debug")),
], bulletType="bullet", leftIndent=20))

story.append(H2("5.4 Observatory"))
story.append(P("Controllo dome, dust cap, flat panel, weather:"))
story.append(ListFlowable([
    ListItem(P("Card weather con tutti i parametri (temp, umidità, vento, cielo)")),
    ListItem(P("Dome shutter Open/Close")),
    ListItem(P("Dust cap Park/Unpark")),
    ListItem(P("Flat panel toggle + slider intensità 0-255")),
], bulletType="bullet", leftIndent=20))

story.append(H2("5.5 Scheduler"))
story.append(P("Pianificatore notturno multi-target:"))
story.append(ListFlowable([
    ListItem(P("Card sky-state: fase twilight (day/civil/nautical/astronomical/night), "
               "altitudine sole/luna, lat/lon (auto-rilevate dal mount)")),
    ListItem(P("Lista jobs persistenti con RA/Dec, altitudine minima, time window")),
    ListItem(P("+NUOVO JOB: form con risoluzione SIMBAD automatica del target")),
    ListItem(P("Per ogni job: tap ✓ per verificare condizioni live (twilight required, "
               "altitudine attuale, weather safe) → dialog con elenco issue")),
], bulletType="bullet", leftIndent=20))

story.append(H2("5.6 Setup / Profili"))
story.append(P("Lista driver INDI attualmente caricati con toggle "
               "<b>CONNECT/DISCONNECT</b> (utile per attivare driver come XAGYL Wheel "
               "o Weather Watcher quando Ekos li carica ma non li connette)."))

story.append(H2("5.7 INDI Panel"))
story.append(P("Clone esatto della INDI Control Panel di KStars/Ekos:"))
story.append(ListFlowable([
    ListItem(P("Lista di tutti i device connessi")),
    ListItem(P("Tap su un device → tutte le sue properties raggruppate per Group "
               "(Main Control, Options, ecc.)")),
    ListItem(P("Switch interattivi (ChipToggle), Number editabili, Text editabili, "
               "Light read-only con stato colorato")),
    ListItem(P("Cambiamenti propagati live in entrambe le direzioni: modifichi "
               "qui → Ekos lo vede, modifichi in Ekos → qui appare")),
    ListItem(P("Bottone CONNECT/DISCONNECT in alto per ogni device")),
], bulletType="bullet", leftIndent=20))

story.append(H2("5.8 Files"))
story.append(P("Browser dei FITS in <font face='Courier'>~/Pictures/Ekos/</font>:"))
story.append(ListFlowable([
    ListItem(P("Lista file recenti con thumbnail auto-stretchata")),
    ListItem(P("Tap → preview a schermo intero con zoom")),
    ListItem(P("Filtri Light/Dark/Flat/Bias/All")),
], bulletType="bullet", leftIndent=20))

story.append(H2("5.9 Logs / Activity Log"))
story.append(P("Due schermate distinte:"))
story.append(ListFlowable([
    ListItem(P("<b>INDI Logs</b>: stream messaggi INDI/Ekos in tempo reale "
               "con filtri per modulo")),
    ListItem(P("<b>Activity Log</b>: tutte le richieste HTTP fatte dall'app al bridge, "
               "con timestamp ms, status code colorato, durata, body. Tap per "
               "dettaglio + copia. Indispensabile per debug.")),
], bulletType="bullet", leftIndent=20))

story.append(H2("5.10 Analyze"))
story.append(P("Timeline sessione corrente:"))
story.append(ListFlowable([
    ListItem(P("Counters: WS events, properties totali, devices")),
    ListItem(P("Last frame info (object, filter, exposure, HFR, stars, size)")),
    ListItem(P("Grafico storico RMS PHD2 (RA in ambra, Dec in azzurro)")),
    ListItem(P("Stream messaggi INDI ultime 20 righe")),
], bulletType="bullet", leftIndent=20))

story.append(PageBreak())

# ============================================================================
# 6. TROUBLESHOOTING
# ============================================================================
story.append(H1("6. Troubleshooting"))
story.append(grid_table(
    ["Sintomo", "Causa probabile", "Fix"],
    [
        ["App: 'unreachable' al login",
         "Tailscale non attivo sul cellulare oppure RPi offline",
         "Verifica app Tailscale Connected; ping 100.74.22.40 dal browser cellulare"],
        ["App: 'auth_failed'",
         "Token sbagliato",
         "cat ~/.config/astroarch-bridge/token sul RPi"],
        ["App vede 0 device",
         "Profilo Ekos non avviato",
         "Apri Ekos sul desktop e avvia il profilo INDI"],
        ["Cooler non funziona (POWER 0%)",
         "Driver toupbase bloccato dopo on/off rapidi",
         "Tap RICONNETTI DRIVER nella Capture"],
        ["Sequenza non parte in Ekos",
         "UPLOAD_MODE in CLIENT (default driver)",
         "Forzato auto a BOTH dall'app v0.2.2+"],
        ["Plate solve fail",
         "Index files astrometry mancanti o scope sbagliato",
         "Verifica ~/.local/share/kstars/astrometry/, hint scale"],
        ["WS frames non si aggiorna",
         "WS state disconnesso (banner rosso)",
         "Refresh manuale (icona in Dashboard) o ri-connetti"],
        ["FITS non vengono salvati",
         "UPLOAD_DIR scritto male o dir non esiste",
         "L'app crea la dir auto a /Pictures/Ekos/AstroarchInterface/"],
        ["Multi-camera errore 409",
         "Bridge non sa quale camera usare",
         "Usa il dropdown Camera nella Capture (auto = primary)"],
    ],
    col_widths=[5 * cm, 4.5 * cm, 6 * cm]))

story.append(H2("6.1 Comandi diagnostici sul RaspberryPi"))
story.append(CODE("# Stato servizio bridge\n"
                  "systemctl --user status astroarch-bridge\n\n"
                  "# Log live\n"
                  "journalctl --user -u astroarch-bridge -f\n\n"
                  "# Test endpoint\n"
                  "curl http://localhost:8765/healthz\n\n"
                  "# Sblocca driver INDI bloccato\n"
                  "indi_setprop 'NOMECAMERA.CONNECTION.DISCONNECT=On'\n"
                  "sleep 2\n"
                  "indi_setprop 'NOMECAMERA.CONNECTION.CONNECT=On'\n\n"
                  "# Verifica stato cooler\n"
                  "indi_getprop 'NOMECAMERA.CCD_TEMPERATURE.CCD_TEMPERATURE_VALUE'\n"
                  "indi_getprop 'NOMECAMERA.CCD_COOLER_POWER.COOLER_POWER'"))

story.append(H2("6.2 Diagnostica nell'app"))
story.append(P("Sulla schermata Login c'è il bottone <b>TEST</b> che apre la "
               "schermata Diagnostica con 7 step in sequenza:"))
story.append(ListFlowable([
    ListItem(P("Risoluzione host (DNS / Tailscale)")),
    ListItem(P("HTTP GET /healthz")),
    ListItem(P("HTTP GET /api/system/info (auth Bearer)")),
    ListItem(P("HTTP GET /api/system/snapshot (verifica payload)")),
    ListItem(P("WebSocket /ws/state (apertura)")),
    ListItem(P("WebSocket - primo messaggio entro 5s")),
    ListItem(P("WebSocket - ricezione property_def chunked")),
], bulletType="bullet", leftIndent=20))
story.append(P("Ogni step mostra durata in ms e dettaglio errore in caso di fail. "
               "Risolve il 95% dei problemi al primo colpo."))

story.append(PageBreak())

# ============================================================================
# 7. APPENDICE - API REST
# ============================================================================
story.append(H1("7. Appendice - API REST"))
story.append(P("Tutte le richieste richiedono header "
               "<font face='Courier'>Authorization: Bearer &lt;token&gt;</font> "
               "(eccetto /healthz). Risposte sempre JSON."))

story.append(H2("7.1 System"))
story.append(grid_table(
    ["Endpoint", "Metodo", "Descrizione"],
    [
        ["/healthz", "GET", "Health (no auth)"],
        ["/api/system/info", "GET", "Info bridge (versione, autore)"],
        ["/api/system/snapshot", "GET", "Stato globale (devices, properties, phd2, last_frame)"],
        ["/api/system/connections", "GET", "Stato connessioni INDI/PHD2"],
        ["/api/system/devices", "GET", "Lista device INDI"],
        ["/api/system/camera_roles", "GET", "Identifica camera primary vs guide via PHD2"],
        ["/api/system/simbad", "GET", "?name=M31 → RA/Dec via SIMBAD"],
    ],
    col_widths=[6.5 * cm, 1.5 * cm, 7.5 * cm]))

story.append(H2("7.2 Mount, Camera, Focuser, Filter, Guide"))
story.append(grid_table(
    ["Endpoint", "Metodo", "Descrizione"],
    [
        ["/api/mount/status, /goto, /park, /track, /slew, /slew_rate, /abort", "GET/POST", "Controllo telescopio"],
        ["/api/camera/status, /expose, /abort, /cooler, /gain, /offset, /binning, /frame_type, /transfer_format, /capture_format, /upload_setup", "GET/POST", "Controllo camera"],
        ["/api/focuser/status, /abs, /rel, /abort, /autofocus, /autofocus/{id}", "GET/POST", "Focheggiatore + autofocus iterativo"],
        ["/api/filter_wheel/status, /select", "GET/POST", "Ruota filtri"],
        ["/api/guide/status, /start, /stop, /dither, /loop, /clear_calibration, /pause, /find_star, /calibrate, /profile", "GET/POST", "Guida PHD2"],
    ],
    col_widths=[8 * cm, 1.5 * cm, 6 * cm]))

story.append(H2("7.3 Align, Capture/Ekos, Observation, Scheduler, Setup"))
story.append(grid_table(
    ["Endpoint", "Descrizione"],
    [
        ["/api/align/status, /solve, /solve/{id}/sync_mount", "Plate solving completo"],
        ["/api/capture/ekos_alive, /ekos_run, /ekos_status, /ekos_abort, /ekos_clear", "Capture via Ekos DBus"],
        ["/api/observation/run, /{id}, /{id}/abort", "Pipeline pre-flight 10 fasi"],
        ["/api/scheduler/sky_state, /jobs, /jobs/{id}/check_conditions, /weather_safe", "Scheduler temporale"],
        ["/api/setup/profiles, /active_drivers", "Profili Ekos + driver attivi"],
        ["/api/observatory/status, /dome/shutter, /dust_cap, /flat_panel", "Dome + flat panel"],
        ["/api/files/recent, /preview, /download", "Browser FITS"],
    ],
    col_widths=[9.5 * cm, 6 * cm]))

story.append(H2("7.4 INDI panel (clone control panel)"))
story.append(grid_table(
    ["Endpoint", "Descrizione"],
    [
        ["GET /api/indi/devices", "Lista device"],
        ["GET /api/indi/devices/{dev}/properties", "Tutte le property del device"],
        ["GET /api/indi/devices/{dev}/properties/{name}", "Singola property"],
        ["POST /api/indi/devices/{dev}/properties/{name}", "Set valori (Switch/Number/Text)"],
        ["POST /api/indi/devices/{dev}/connect, /disconnect", "Connect/disconnect driver"],
        ["POST /api/indi/refresh", "Force getProperties"],
    ],
    col_widths=[9.5 * cm, 6 * cm]))

story.append(H2("7.5 WebSocket"))
story.append(grid_table(
    ["URL", "Cosa pusha"],
    [
        ["GET /ws/state?token=...",
         "snapshot_begin → N property_def → snapshot_end (init), poi property_def, "
         "property_set, property_del, indi_message, phd2_event, phd2_live, frame_meta, connection"],
        ["GET /ws/frames?token=...",
         "Per ogni frame: header JSON {type:frame_meta, size, hfr, ...} seguito dai bytes JPEG"],
    ],
    col_widths=[5.5 * cm, 10 * cm]))

story.append(PageBreak())

# ============================================================================
# 8. CHANGELOG / VERSIONI
# ============================================================================
story.append(H1("8. Changelog"))
story.append(grid_table(
    ["Versione", "Data", "Cambiamenti principali"],
    [
        ["0.1.0", "2026-05-03", "Prima release: 13 schermate base, WebSocket clone live, Tailscale auth"],
        ["0.1.2-3", "2026-05-04", "Fix drawer + banner stato connessione + scanner QR"],
        ["0.1.4", "2026-05-04", "WebSocket chunked snapshot (fix 200KB payload Android)"],
        ["0.1.5-6", "2026-05-04", "Fix cleartext HTTP/WS + diagnostica step-by-step"],
        ["0.1.7", "2026-05-04", "Camera primary/guide auto-detection via PHD2"],
        ["0.1.8-10", "2026-05-04", "Cooler toggle robusto + sequenza scatti + Activity Log"],
        ["0.1.11", "2026-05-04", "Planner Capture con preview + AVVIA esplicito"],
        ["0.2.0", "2026-05-04", "Clone Ekos completo: 8 moduli (A-H) + multi-job + SIMBAD + autofocus V-curve"],
        ["0.2.1", "2026-05-04", "Plate solving via solve-field + Scheduler temporale + sky_state"],
        ["0.2.2", "2026-05-04", "UPLOAD_MODE auto BOTH + format selector (FITS/NATIVE/XISF, RAW/RGB)"],
        ["0.2.3", "2026-05-04", "Capture via Ekos DBus (loadSequenceQueue + start)"],
        ["0.2.4", "2026-05-04", "Pipeline OSSERVAZIONE COMPLETA con 10 fasi pre-flight"],
    ],
    col_widths=[2 * cm, 2.5 * cm, 11 * cm]))

story.append(Spacer(1, 1 * cm))
story.append(H2("Roadmap futura"))
story.append(ListFlowable([
    ListItem(P("Polar alignment routine guidata (3-step drift)")),
    ListItem(P("Mosaic planner")),
    ListItem(P("Notifiche push (frame finito, sequenza completata, weather alert)")),
    ListItem(P("Donazione codice come integrazione ufficiale a "
               "<font face='Courier'>devDucks/astroarch</font>")),
], bulletType="bullet", leftIndent=20))

story.append(Spacer(1, 1.5 * cm))
story.append(P('<para alignment="center"><font color="#8a93a6">'
               "— Buone osservazioni —<br/>"
               "Astroarch Interface · Zarletti-Osservatorio Jupiter"
               "</font></para>"))


# ----------------------------------------------------------------------------
# BUILD
# ----------------------------------------------------------------------------
def _on_first_page(canvas, doc):
    cover_layout(canvas, doc)


def _on_later_pages(canvas, doc):
    page_layout(canvas, doc)


doc = SimpleDocTemplate(
    OUTPUT, pagesize=A4,
    leftMargin=2 * cm, rightMargin=2 * cm,
    topMargin=2 * cm, bottomMargin=1.6 * cm,
    title="Astroarch Interface - Manuale utente",
    author="Zarletti-Osservatorio Jupiter",
    subject="Manuale utente e installazione",
    creator="Astroarch Interface v0.2.4",
)
doc.build(story, onFirstPage=_on_first_page, onLaterPages=_on_later_pages)

import os
size_kb = os.path.getsize(OUTPUT) / 1024
print(f"OK: {OUTPUT} ({size_kb:.0f} KB)")
