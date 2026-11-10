# Anatomia di RoboCassano

Scritta il 10/11/2026 sulla **ClaudeRob V41** (impronta `7fa6d06745b2776b`). I nomi delle funzioni e i valori dei parametri
vanno sempre ricontrollati nell'ultima cartella `ClaudeRob_V<n>`: il robot cambia a ogni versione.

Legenda: **[codice]** letto nel codice · **[STL]** letto nei file 3D · **[scatola nera]** misurato sul robot vero ·
**[simulatore]** valore del simulatore · **[da confermare]** dedotto (per esempio dal nome di un file), da verificare con la squadra.

---

## 0. La mappa: chi parla con chi

```
                       ┌──────────────────────── RASPBERRY PI 5 ("cervello") ────────────────────────┐
  camera LINEA ──CSI──▶│ ViennaClsWebCam.py  → Immagine (linea)  → YOLO Cross3                        │
  camera ARENA ──CSI──▶│                     → Arena  (arena)    → YOLO PalCol3 / TrianFull3 / Exit3 │
                       │                                                                              │
  ARDUINO NANO ──USB──▶│ ViennaClsRobot.py  (filo di lettura _arduino_reader, 230400 baud)            │
   3 laser VL53L1X     │      Distanze() GetGyro() GetSwitch() FrontaleFiltrato() Pendenza() ...      │
   giroscopio BNO055   │                                                                              │
   switch              │ RwdFoto.py  = il PROGRAMMA DI GARA: decide cosa fare                          │
                       │      seguilinea → ingresso → vittime → uscita → altalena → linea rossa       │
                       │ ViennaDataConf.py = TUTTI i parametri    ViennaMonitor.py = scatola nera      │
                       │                                                                              │
                       │ ViennaClsRobot.py → Sterzo(vel, sterzo) / Braccio() / Pinza()                │
                       └───────────────┬───────────────────────────────┬─────────────────────────────┘
                                   I2C │                               │ GPIO 22, 23
                      PCA9685 0x41 (ruote)   PCA9685 0x40 (braccio, pinza)      2 LUCI (relè)
                          4 servo a rotazione continua      2 servo di posizione
```

Un ciclo, in parole: l'Arduino manda ~30 volte al secondo le misure (laser, giroscopio, switch) su USB; un filo del programma
le tiene aggiornate; le camere scattano di continuo; `RwdFoto.py` guarda immagini e misure, decide, e chiama `Sterzo()` che
scrive gli impulsi sulla scheda PCA9685 delle ruote. La scatola nera registra tutto 10 volte al secondo.

---

## 1. Il corpo: i 5 pezzi stampati in 3D  [STL]

File in `Meccanica_STL/`, in **millimetri**, già nella **posizione di montaggio** (stesse coordinate per tutti: si possono
rimontare uno sull'altro). Asse verticale = **Y**; il muso (pinza e camere) è verso **X negativo**. Robot montato: circa
**202 mm** di lunghezza, **157 mm** di larghezza (le misure del codice dicono 15,6 cm), ~9 cm di altezza dei pezzi stampati.

| Pezzo | Ingombro (mm) | Dove sta | Cosa porta |
|---|---|---|---|
| `ServoRWDAmmortizzato.stl` | 202 x 8 x 151 | in basso, è la piastra più bassa (Y da -49 a -41) | i supporti dei servo delle ruote, con ammortizzazione ("RWD" = trazione) [da confermare] |
| `BaseLogica.stl` | 154 x 26 x 157 | al centro (Y da -22 a +4) | la "logica": Raspberry, Arduino, schede PCA9685 [da confermare] |
| `CoperturaAlta.stl` | 183 x 36 x 154 | in alto (Y da +5 a +41) | il coperchio che protegge l'elettronica [da confermare] |
| `SupportoPinzaWebcam_1.stl` | 61 x 67 x 157 | davanti (X da -36 a +25) | la pinza con il braccio e la camera della linea [da confermare] |
| `CupolaWebArenaLED.stl` | 8 x 52 x 148 | sul muso, sottile (X da -43 a -35) | la camera dell'arena e le luci LED [da confermare] |

Il modello del cruscotto (`ClaudeRob_V*/cruscotto/robot.stl`, 19092 triangoli, in cm) è questi 5 pezzi uniti.
**Esploso 3D**: `python3 .claude/skills/anatomia/costruisci_esploso.py` → `Meccanica_STL/esploso_robot.html`.

Misure che il codice usa [codice/simulatore]: larghezza **15,6 cm** (`ROBOT_LARGHEZZA_CM`), camera linea **12 cm** davanti
alle ruote, laser davanti 11,5 cm davanti all'asse delle ruote, laser laterali 1,5 cm davanti e a ±7,5 cm di lato.

---

## 2. Il cervello: Raspberry Pi 5  [codice]

- **Programma di gara**: `RwdFoto.py` (~4500 righe), dalla cartella della versione (oggi `~/ClaudeRob_V41`).
- **Avvio**: all'accensione `~/.config/labwc/autostart` (e `lxsession`) lancia `~/ClaudeRob_GARA/avvia.sh`; `ClaudeRob_GARA`
  è un collegamento alla versione di gara (`ln -sfn ~/ClaudeRob_V41 ~/ClaudeRob_GARA`).
- **File**: `ViennaClsRobot.py` (corpo: motori, sensori, movimenti), `ViennaClsWebCam.py` (occhi), `ViennaDataConf.py`
  (tutti i parametri: ~200), `ViennaMonitor.py` (scatola nera, terminale, cruscotto), `ViennaPannello.py` (pannello a schermo).
- **Ciclo principale** (fondo di `RwdFoto.py`): in PAUSA finché lo switch è spento; acceso → `Protetto(InseguitoreIA)` →
  `Protetto(ArenaAI)` → `Protetto(TrovaUscitaArena)`. `Protetto` (FIX 100): un errore Python non chiude la gara, passa alla
  fase dopo. `finally` (FIX 6): qualunque cosa succeda, ferma i motori.
- **Impronta** (FIX 86): codice sha256 dei file `.py` della cartella; nella scatola nera dice se gira la versione giusta.
- **Nel simulatore**: lo stesso `RwdFoto.py` gira davvero; `finto_hw.py` sostituisce le librerie del Raspberry e il tempo
  diventa virtuale (avanza solo con `time.sleep`).

---

## 3. Gli occhi: due camere e quattro reti YOLO  [codice]

| | Camera LINEA | Camera ARENA |
|---|---|---|
| Nel codice | `CamSL = Picamera2(0)` | `CamAr = Picamera2(1)` |
| Risoluzione | 440 x 260 | 440 x 260 |
| Guarda | il pavimento davanti al muso (12 cm davanti alle ruote) | davanti, più in alto: pareti, porte, palline, triangoli |
| Reti YOLO (NCNN) | `best_ncnn_model_Cross3`: linea e incroci | `PalCol3` palline · `TrianFull3` triangoli e porta · `Exit3` uscita (0) / ingresso (1) |

- **Classi della camera linea**: `Ln` linea, `In` argento (ingresso), `Bi` bianco, `No` niente, `Di` discontinuità
  (interruzione), `Ro` rosso (arrivo), verdi `Sx`/`Dx`… I modelli YOLO **non sono su GitHub**: stanno sul robot e si copiano
  in ogni cartella di versione.
- **Funzioni** (`ViennaClsWebCam.py`): `LeggiCross`, `VerificaVerde` / `VerdiGeometria` (i verdi), `PallinaNuova`,
  `CercaPortaTri`, `TipoPorta`, `VerificaUscita`, `StrisciaNera` / `GeometriaStrisciaNera`, `LineaAlCentro`,
  `CalcolaErrore`, `CercaBlocchiCol` (colori), `AutoregolaCam`, `SalvaFoto`.
- **Scatola nera**: campi `yolo` (classe e sicurezza), `verde`, e ogni ~0,5 s le miniature `img_l` (linea) e `img_a` (arena).
- **Simulatore**: YOLO è un "oracolo" che risponde quello che c'è davvero davanti: non sbaglia mai come la rete vera (luce,
  riflessi, plastica lucida scambiata per argento: scatola nera 09/11 13:00, secondo 381).
- **Punti deboli**: luce e riflessi; i verdi in diagonale (29/10); la plastica trasparente vicino alle porte vista come
  argento (09/11).

---

## 4. I sensi: Arduino Nano, 3 laser, giroscopio, switch  [codice]

- **Arduino Nano** (`InoSensor.ino`, non su GitHub) su USB (`/dev/ttyUSB*`), **230400 baud**. Una riga di **10 numeri** separati
  da virgole: `d1,d2,d3,hd,rl,pt,sw1,sw2,t0,t1`.
  - `d1,d2,d3` = laser **sinistro, davanti, destro** in cm; `hd,rl,pt` = rotta, rollio, beccheggio; `sw1,sw2` = switch;
    `t0,t1` = inclinazione.
  - Letta dal filo `_arduino_reader` in `ViennaClsRobot.py`. Righe senza 10 campi: scartate.
  - **Con lo switch spento l'Arduino smette di mandare dati**: non è un guasto (verificato su 4 scatole nere il 5/11).
    Dopo 0,3 s senza dati il programma mette tutto a 0 e scrive "Arduino zitto: switch spento?".
- **3 laser VL53L1X**: `Distanze()`, `LaserVeri()` in `RwdFoto.py` (0 = fuori portata → `LASER_LONTANO` 150 cm),
  `FrontaleFiltrato()` (FIX 87: mediana nel tempo, ignora le letture isolate).
  - Il laser vero ha un **cono largo** (~45 cm a 1 m, più di una porta) e a ~1 m balla di **±2 cm** [scatola nera 09/11];
    il simulatore usa un raggio sottile con rumore 0,7 cm (FIX 106 nasce da qui).
- **Giroscopio BNO055**: `GetGyro()` → (beccheggio, rollio, rotta). Le rotte crescono girando a **destra**. Risponde ~0,1 s in
  ritardo. Se è bloccato, `BussolaStato()` e la **bussola stimata dai motori** (FIX 88) prendono il suo posto;
  `StoriaBeccheggio()` e `Pendenza()` servono per rampe e altalena.
- **Switch**: `GetSwitch()` → `{'sw_pal', 'sw_sof'}`. `sw_sof` = avvio/pausa della gara (il capitano lo spegne per la LoP);
  `sw_pal` = switch della pallina nella pinza [da confermare].
- **Scatola nera**: `d` (laser), `dfr` (laser davanti filtrato), `imu`, `bus` (giroscopio o stimata), `rotta`, `pend`, `tilt`,
  `sw`, `ard` (Arduino vivo?).

---

## 5. Le gambe: 4 servo a rotazione continua  [codice]

- Scheda **PCA9685 all'indirizzo I2C 0x41**: canali **15** (avanti sinistra), **4** (dietro sinistra), **0** (avanti destra),
  **11** (dietro destra). Impulsi da 310 a 333 (fermo a 321).
- **`Sterzo(velocita, sterzo)`**: l'unico comando delle ruote. `sterzo` 0 = dritto, ±100 = ruota sul posto, in mezzo = curva.
  Correzioni fisse dei lati (1,17 / 0,83) perché i servo non sono uguali.
- **Sopra** Sterzo: `Stop()`, `Dritto(vel, durata, heading_ref, ruota)` (va dritto tenendo la rotta col PID, FIX 13/64/72),
  `Gira(gradi)`, `RuotaVerso(rotta)` (anello chiuso: anticipa, assesta, colpi brevi, FIX 64/72; capisce se la rotazione è
  bloccata, FIX 65), `GiraA()` in `RwdFoto.py`.
- **Velocità**: `VelCrs` 47 (seguilinea), `VelArena` 68 (arena); ~10 cm/s a `VelArena*0,7` (`VelocitaArenaCmS`).
- **Fisica da ricordare**: sotto circa **40 di sterzo** (a velocità 47) i servo non girano (FIX 64); fermati, il robot gira
  ancora di 5-7 gradi (FIX 72); con lo switch spento `Dritto` ferma i motori e aspetta 0,1 s (FIX 105).
- **Scatola nera**: `mot` = ultimo comando (es. `['Sterzo', 68, 3]`), `manovra`, `azione`.
- **Simulatore**: servo "reali" con ritardo `tau_servo_reale` 0,10 s.

---

## 6. Le mani: braccio e pinza  [codice]

- Scheda **PCA9685 all'indirizzo 0x40**: **canale 4 = braccio**, **canale 11 = pinza** (servo di posizione, in gradi).
- `Braccio(angolo)`, `Pinza(angolo)`; in `RwdFoto.py`: `AbbassaPinza`, `AlzaPinza`, `ApriPinza`, `ChiudiPinza`,
  `CaricaPalla`, `SvuotaPinza`, `ScaricaPalla(tipo)`, `AccostaTriangolo`.
- **Scatola nera**: `br` (braccio), `pz` (pinza), `pal` (palline).

---

## 7. Le luci  [codice]

Due luci su **GPIO 22 e 23** (`PIN_LUCI`), comandate con `lgpio` sul chip `pinctrl-rp1` del Raspberry 5 (FIX 50; se manca,
luci finte: il robot non si blocca mai per le luci). `GetOnLed1/2`, `GetOffLed1/2`. Si accendono per illuminare il pavimento e
l'arena. **Scatola nera**: `led`.

---

## 8. La memoria: scatola nera e cruscotto  [codice]

- **Scatola nera** (`ViennaMonitor.py`, FIX 37): `~/OneDrive/ScatolaNera/run_AAAA-MM-GG_hh-mm-ss_V<n>.jsonl`. Prima riga =
  intestazione (versione, impronta, cartella, file); poi un campione ~ogni 0,1 s (`tipo: "c"`) e gli eventi (`tipo: "evento"`).
  Non comunica con niente: si può usare in gara.
- **Cruscotto** (solo laboratorio, `CRUSCOTTO`): pagina web 3D su `http://<ip-del-robot>:8000` con il modello del robot.
- **Strumenti**: `Strumenti_prove_Claude/analizza_scatola_nera.py` (eventi, o campioni tra due istanti);
  `Laboratorio Shuri/analizza_scatola.py` (problemi + foto delle camere).

---

## 9. I comportamenti (gli "organi" del programma)  [codice]

Ogni comportamento: **sensori → funzioni → decisione → motori**. Le funzioni sono in `RwdFoto.py` se non è scritto altro.

| Comportamento | Sensori | Funzioni principali | Parametri chiave | FIX importanti |
|---|---|---|---|---|
| **Seguilinea** | camera linea, YOLO Cross3 | `InseguitoreIA`, `CalcolaErrore` (WebCam), `VedoLinea`, `RecuperaLinea` | `VelCrs` 47, `SOGLIA_NERO` 110 | 11 |
| **Verdi e incroci** | camera linea, YOLO, colori | `LeggiCross`/`VerificaVerde` (WebCam), `AnalizzaIncrocio`, `CrosDx`/`CrosSx`/`CrosFF`, `AvanzaSullIncrocio`, `CompletaSvolta`, `ConfermaDietrofront`, `AvviaPausaVerdi` | svolte "vecchie"/"nuove", `VERDE_PAUSA_S` | 41, 80, 91 (rotonda), 92 |
| **Interruzione** | camera linea (`Di`) | `SeguiFinoAlVuoto`, `AttraversaVuoto`, `AttraversaInterruzione` | | 85 |
| **Ostacolo** | laser davanti filtrato, laterali | `OstAutDet`, `ConfermaOstacolo`, `AggiraOstacolo`, `ScegliLatoOstacolo`, `StaccaDallaParete`, `AvantiOst`, `Spinge` | `OST_SPINTA_CM` 5 | 13, 87, 90 |
| **Rampe e tratti inclinati** | giroscopio | `Pendenza` (Robot), `InPianoPerArena` | | 82, 89 |
| **Altalena** | giroscopio (salto del beccheggio) | `ControllaAltalena`, `AltalenaNellaStoria`, `AspettaGiroscopioFermo` | `ALTALENA_SALTO_GRADI` 30 | 102, 104 |
| **Ingresso nell'arena** | camera linea (argento), laser davanti | `TrovaIngressoArena`, `IngressoDopoArgento`, `DirezioneIngresso`, `CentraSullIngresso`, `EntraDallaPorta` → `CercaAperturaDavanti`/`CercaApertura`, `PassaLaPorta`, `AttraversaPorta`, `SpostaDiLato` | `TempoEntrataArena` 2,5, `INGRESSO_LIBERO_CM` 40, `ENTRATA_OLTRE_CM` 9, `ENTRATA_LONTANO_*` | 68, 93, 96, 101, 104, 106 |
| **Vittime (palline)** | camera arena (PalCol3, TrianFull3), switch pinza | `ArenaAI`, `ScaricaPalla`, `AccostaTriangolo`, `GiraInArena`, `MemorizzaPosizione`/`GiraVersoMemoria` | | 21, 83 |
| **Uscita dall'arena** | laser laterali e davanti, camera linea (striscia nera), camera arena (Exit3) | `TrovaUscitaArena` → `ScegliLatoGiro`, `AvvicinatiAlMuro`, `GiroDeiMuri`/`SeguiParete`, `ControllaAperturaMuro`, `EsciDallaPortaDavanti`, `EsciControllando`, `EsciDallaPorta`, `StrisciaFerma`; se fallisce `TrovaUscitaIA` (camera) | `USCITA_MODO` "muri", `LATO_MURO_CM` 6,5, `APERTURA_CM` 15, `ANGOLO_CM` 8, `USCITA_LIBERO_CM` 30, `TEMPO_MAX_MURI` 150 | 53, 55, 63, 69, 70, 84, 94, 103, 104, 105 |
| **Linea rossa e arrivo** | camera linea (`Ro`) | `InseguitoreIA`, `Festeggia` | | 95 |
| **Switch spento / LoP** | switch | ciclo principale, `SwitchSpento` | | 6, 7, 105 |

**Punti deboli noti** (vedi "Aperto / da fare" in `CLAUDE.md`): l'uscita (09/11 13:00: girato verso il pannello accanto alla
porta, plastica lucida vista come argento, 70 s persi); alcuni verdi (09/11, da analizzare); la parete di destra presa per
ostacolo in `scuola_basso`/`scuola_rampa` (simulatore).

---

## 10. Come si "smonta" davvero un sistema (esercizi)

- **Sul robot**: `LetturaNano.py` (legge l'Arduino: laser, giroscopio, switch), `ProvaGPIO.py` (luci), `ProvaVerde.py`,
  `ProvaStriscia.py`, `TaraNero.py`, `ScattaCalibrazione.py`: strumenti da laboratorio della cartella della versione.
- **Nel simulatore**: `Strumenti_prove_Claude/gira.py` (gara intera), `prova_ingresso.py`, `prova_uscita.py`,
  `prova_uscita_angolo.py`, `prova_altalena.py`; guasti nel `cfg` (`imu_bloccato`, `tof_fr_spurie`, `tof_rumore`,
  `arduino_muto_da`…).
- **Nella scatola nera**: scegli un evento, guarda i campioni secondo per secondo, e prova a dire quale sensore ha fatto
  prendere quella decisione.
