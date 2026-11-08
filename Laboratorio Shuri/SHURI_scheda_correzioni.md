# Scheda per Claude — ClaudeRob_V37 (batteria del 2026-11-05 21:13)

Questo file è scritto per essere letto da Claude (e dai ragazzi) per **migliorare il codice del robot**.
Regole per chi lo usa:
- Il codice da cui partire è `02_Robotica/ClaudeRob_V37`: **non modificarlo**. Copialo in una nuova cartella
  `ClaudeRob_V<n+1>`, applica lì le correzioni, segna ogni modifica nel codice con `# [FIX n]` (numerazione
  di `LEGGIMI_MODIFICHE.md`) e aggiorna `CHANGELOG.md` e `LEGGIMI_MODIFICHE.md`.
- Correggi un problema alla volta, partendo da quelli a gravità **alta**.
- Per verificare: ogni problema ha **come riprodurlo** (comando da lanciare nella cartella `Laboratorio Shuri`)
  e un **criterio di successo**. Poi Shuri rifà tutta la batteria e il confronto con questa versione.
- Il simulatore prova la logica del programma: YOLO è un oracolo e alcune misure in CONFIG sono stime.

## Medie per pista

| Pista | Prove | Punti medi | % media | LoP totali | Urti medi |
|---|---|---|---|---|---|
| arena_parete | 2 | — | — | 0.0 | 0.5 |
| contorto | 2 | 1865.9 | 93.8 | 0.0 | 4.0 |
| lunga | 4 | 1691.7 | 89.4 | 2.0 | 3.2 |
| rcj2026 | 5 | 1347.0 | 91.8 | 1.0 | 5.5 |
| scuola | 1 | — | — | 0.0 | 2.0 |
| scuola_parete | 1 | — | — | 0.0 | 0.0 |
| scuola_rampa | 1 | — | — | 0.0 | 0.0 |

## Problemi (10)

### P1 · [ALTA] robot fermo — Pista della SCUOLA: dalla rampa con i tubi, secondo 218.03

- **Cosa succede:** Robot fermo da 60 secondi: gara interrotta
- **Ultime stampe del programma prima dell'evento:**
  ```
  ARRESTO SICURO DEL ROBOT
  Chiusura Robot...
  Robot fermato correttamente.
  ```
- **Dove guardare nel codice:**
  - `ViennaClsRobot.py` riga 1172 in `def StopLetture(self):` → `print("Robot fermato correttamente.")` (FIX vicini: 6, 70)
  - `ViennaClsRobot.py` riga 1162 in `def StopLetture(self):` → `print("Chiusura Robot...")` (FIX vicini: 6, 70, 72)
  - `RwdFoto.py` riga 4387 in `def ArenaAI():` → `print("ARRESTO SICURO DEL ROBOT")` (FIX vicini: 6, 37, 46, 100)
- **Come riprodurlo:** `cd ../ClaudeRob_Simulatore_*/ && python3 -c "import esegui; esegui.esegui('../ClaudeRob_V37', 'riprova_scuola_rampa', 300, {'seme': 1}, 'scuola_rampa')"`
- **Criterio di successo:** L'evento non si ripete nella stessa prova.
- **Ipotesi:** VERIFICATO (posizioni del replay): a ~102 s, a (34-48, 105) cm il robot va verso la parete della pista (muro a y=123,5) e il laser frontale la legge a 8-16 cm: 'POSSIBILE OSTACOLO' (RwdFoto.py riga 3042) -> 'Ostacolo confermato' (riga 2914). ScegliLatoOstacolo [FIX 90] riconosce la parete solo se è DI LATO (laser laterale < OST_PARETE_CM): qui è DAVANTI, quindi aggira a destra (default -1), passa oltre il bordo del muro (x=-11) e dietro la parete (y 133-146), 'Trovata Linea' su un pezzo sbagliato, poi gira sul posto 60 s ('Linea NON ritrovata') -> fermo. IPOTESI: la ricostruzione della pista (pista_scuola.py, parete a 123,5 cm e semicerchio) potrebbe mettere la linea più vicina al muro del vero: sul robot vero (16:12, V36) a 72 s c'è un 'OSTACOLO: lo aggiro' che va controllato con le note dei ragazzi.
- **Proposta:** In ScegliLatoOstacolo / OstAutDet: se durante il 'LATO LUNGO' il laser laterale vede l'ostacolo per più di ~30 cm (un mattone è 15-20 cm), è una parete: tornare indietro sulla linea e cercarla con RecuperaLinea invece di continuare il giro. In più, prima di aggirare, guardare la camera linea: se la linea curva a destra o sinistra entro pochi cm, seguirla invece di aggirare. Controllare con Giovanni la distanza vera linea-parete in quel punto.

### P2 · [ALTA] LoP nella zona di evacuazione — STRESS: giroscopio disturbato di 15°, secondo 442.1

- **Cosa succede:** LoP n. 1 nella zona: 150 s nella zona senza salvare vittime né uscire. Si riparte dalla piastrella 44
- **Punti persi nella gara:** 483.9
- **Come riprodurlo:** `cd ../ClaudeRob_Simulatore_*/ && python3 -c "import esegui; esegui.esegui('../ClaudeRob_V37', 'riprova_stress_bussola', 480, {'seme': 1, 'bussola_distorsione': 15}, 'rcj2026')"`
- **Criterio di successo:** Nella stessa prova (stress_bussola) l'evento non si ripete e i punti salgono oltre 984.
- **Ipotesi:** VERIFICATO (replay stress_bussola, campioni 397-442 s): dopo 3 palline il giro dei muri trova 'una porta proprio qui' subito dopo l'angolo (RwdFoto.py riga 2151, [FIX 63]/[FIX 94]); ControllaAperturaMuro: 'camera arena dice uscita, pavimento None' -> EsciControllando senza aver visto la striscia nera; esce storto (rotta 154 invece di ~180, bussola distorta di 15°) e resta incastrato nella porta a (531, 141) per 45 s: 'Uscito senza vedere la striscia nera', poi 'Uscita confermata: ritrovata la linea nera' (era la striscia d'uscita), 2 × '[Gira] TIMEOUT', 7 urti, LoP zona a 442 s. IPOTESI sulla causa: EsciControllando restituisce 'incerto' e ControllaAperturaMuro (riga ~1912) lo accetta come 'uscita'; StrisciaFerma [FIX 84/99] controlla l'incastro solo se la striscia nera si vede, quindi l'incastro storto non viene visto. La V30 nella stessa prova usciva (1468 punti).
- **Proposta:** 1) Con esito 'incerto' non dichiarare l'uscita fatta: controllare che il robot si sia mosso (laser frontale che cambia, o LineaFuori che trova una linea che NON sia la striscia d'uscita) e altrimenti arretrare e rifare SquadraSullUscita. 2) Usare RobotFermo/laser come controllo di incastro anche quando la striscia non si vede. 3) Prima di uscire raddrizzarsi sulla parete appena seguita (AsseParete) invece che sulla rotta della bussola.

### P3 · [ALTA] LoP sul percorso — STRESS: gli stessi guasti sulla pista lunga, secondo 68.71

- **Cosa succede:** LoP n. 1: caduto da un bordo rialzato. Si riparte dalla piastrella 12
- **Punti persi nella gara:** 806.8
- **Stampa ripetuta prima dell'evento:** "Sinistro" × 7
- **Ultime stampe del programma prima dell'evento:**
  ```
  Linea ritrovata girando di 30 gradi
  Sinistro
  Sinistro
  Sinistro
  Sinistro
  Sinistro
  Sinistro
  Sinistro
  IA         BIANCO               Bi Bi Bi Bi Bi: 
  ```
- **Dove guardare nel codice:**
  - `ViennaClsWebCam.py` riga 1144 in `def CalcolaErrore(frame):` → `print(TrovSinistro,"      ", TrovDestro)` (FIX vicini: 10, 29)
  - `ViennaClsWebCam.py` riga 1153 in `def CalcolaErrore(frame):` → `print("Alto Destro Sinistro", (CentroX-cBkAlX) )` (FIX vicini: 10, 29)
  - `ViennaClsWebCam.py` riga 1158 in `def CalcolaErrore(frame):` → `print("Sinistro-Destro")` (FIX vicini: 10, 29)
  - `RwdFoto.py` riga 3287 in `def InseguitoreIA():` → `print ('IA         BIANCO               Bi Bi Bi Bi Bi: ')` (FIX vicini: 9, 32, 44, 58, 75, 95)
  - `RwdFoto.py` riga 3305 in `def InseguitoreIA():` → `print ('IA         BIANCO               Bi Bi Bi Bi Bi: ')` (FIX vicini: 9, 44, 58, 75, 95)
- **Come riprodurlo:** `cd ../ClaudeRob_Simulatore_*/ && python3 -c "import esegui; esegui.esegui('../ClaudeRob_V37', 'riprova_stress_guasti_lunga', 480, {'seme': 1, 'imu_bloccato': True, 'tof_fr_spurie': 0.15, 'tof_lat_spurie': 0.1}, 'lunga')"`
- **Criterio di successo:** Nella stessa prova (stress_guasti_lunga) l'evento non si ripete e i punti salgono oltre 1087.
- **Ipotesi:** GIÀ NOTO (rapporto V30, problema 3): giroscopio bloccato, caduta dall'altopiano a 68,7 s, uguale alla V30 (stesso punteggio 1087). VERIFICATO nel replay; causa IPOTESI: AttraversaVuoto/RecuperaLinea [FIX 58] con la rotta stimata girano verso il bordo.
- **Proposta:** Come nella scheda V30: con 'bus' = stimata, in RecuperaLinea limitare la rotazione e non avanzare oltre 0,3 s senza linea vicino a un bordo; caso raro sul robot vero (giroscopio riparato: nelle gare del 5/11 il ritardo è 0,3 s e la rotazione 33-44 °/s).

### P4 · [ALTA] LoP sul percorso — STRESS: gli stessi guasti sulla pista lunga, secondo 262.21

- **Cosa succede:** LoP n. 2: ha preso una linea fuori sequenza. Si riparte dalla piastrella 48
- **Punti persi nella gara:** 806.8
- **Stampa ripetuta prima dell'evento:** "Alto" × 38
- **Ultime stampe del programma prima dell'evento:**
  ```
  Alto
  Alto
  Alto
  Alto
  Alto
  Alto
  Alto
  Alto
  Alto
  Alto
  Alto
  Alto
  ```
- **Dove guardare nel codice:**
  - `ViennaClsWebCam.py` riga 1142 in `def CalcolaErrore(frame):` → `print("      ", TrovAlto, "      ")` (FIX vicini: 5, 10, 29)
  - `ViennaClsWebCam.py` riga 1153 in `def CalcolaErrore(frame):` → `print("Alto Destro Sinistro", (CentroX-cBkAlX) )` (FIX vicini: 10, 29)
  - `ViennaClsWebCam.py` riga 1168 in `def CalcolaErrore(frame):` → `print("Alto -Sinistro-Destro Basso")` (FIX vicini: 10, 29)
- **Come riprodurlo:** `cd ../ClaudeRob_Simulatore_*/ && python3 -c "import esegui; esegui.esegui('../ClaudeRob_V37', 'riprova_stress_guasti_lunga', 480, {'seme': 1, 'imu_bloccato': True, 'tof_fr_spurie': 0.15, 'tof_lat_spurie': 0.1}, 'lunga')"`
- **Criterio di successo:** Nella stessa prova (stress_guasti_lunga) l'evento non si ripete e i punti salgono oltre 1087.
- **Ipotesi:** VERIFICATO (log e campioni 224-262 s): all'ingresso dell'arena, giroscopio bloccato: 'Ingresso subito dopo una svolta a SINISTRA: entro verso 308 (robot a 39)' (RwdFoto.py riga 1671, DirezioneIngresso, [FIX 96]/[FIX 101]): la direzione attesa e la rotta stimata differiscono di ~91 gradi. Il robot si gira verso il muro, 'Centratura sull'ingresso: striscia non vista' (riga 1603), gira sul posto 30 s a (649, 249) con 3 urti, poi 'Linea ritrovata tornando indietro' e riparte nel verso sbagliato -> LoP 'linea fuori sequenza'. Nella V30 questo non succedeva (1 LoP). IPOTESI: con la bussola stimata (FIX 88) dopo una svolta l'errore è grande e 'attesa' (SvoltaAttesa) non è affidabile.
- **Proposta:** In DirezioneIngresso: se |attesa - rotta attuale| > 45 gradi, non fidarsi di 'attesa' (e meno ancora se Rwd 'bus' è 'stimata'): usare la retta della striscia vista dalla camera (ramo 'linea' sotto) o la rotta attuale. Riprodurre con il comando della scheda e controllare che la frase 'entro verso X (robot a Y)' abbia X e Y vicini.

### P5 · [ALTA] programma bloccato — STRESS: giroscopio bloccato + laser che saltano (come il robot vero il 3/11)

- **Cosa succede:** BLOCCATO: dopo 110 s reali la gara non era finita (il tempo simulato non avanza: probabile ciclo senza sleep nel codice). Nessun replay: per capire DOVE si blocca, rilanciare con 120, 240, 360 s e leggere le ultime righe del log.
- **Come riprodurlo:** `cd ../ClaudeRob_Simulatore_*/ && python3 -c "import esegui; esegui.esegui('../ClaudeRob_V37', 'riprova_stress_guasti_reali', 480, {'seme': 1, 'imu_bloccato': True, 'tof_fr_spurie': 0.15, 'tof_lat_spurie': 0.1}, 'rcj2026')"`
- **Criterio di successo:** La gara finisce da sola entro 480 s simulati (arrivo o tempo scaduto) in meno di 60 s reali.
- **Ipotesi:** VERIFICATO (rifatta da sola: >172 s reali, e con faulthandler): il robot arriva a 414 s simulati in 18 s reali, poi si blocca in ControllaAperturaMuro, RwdFoto.py righe 1838-1845 (ciclo 'while time.time() - t0 < 3.0: Rwd.Dritto(...); LaserVeri()'). A ~414 s scatta la LoP della zona (150 s senza salvare né uscire, false aperture da 13 cm per i laser che saltano): il simulatore spegne lo switch. Rwd.Dritto esce subito con lo switch spento ([FIX 88], ViennaClsRobot.py riga ~1034) SENZA dormire, quindi il ciclo gira senza sleep e il tempo simulato non avanza più. Sul robot vero sono 3 s di CPU al 100%, ma lo stesso ciclo, a switch spento, continua la manovra della porta invece di tornare in attesa.
- **Proposta:** Nei cicli 'while time.time() - t0 < ...' che chiamano solo Dritto/LaserVeri (ControllaAperturaMuro righe 1838 e 1857, ricerca lenta della porta riga ~1899, ecc.) aggiungere 'if not Rwd.GetSwitch()["sw_sof"]: return None' oppure fare in modo che Dritto, quando esce per lo switch, faccia comunque time.sleep(0.02). Meglio la seconda: copre tutti i cicli. Criterio: stress_guasti_reali finisce in meno di 60 s reali.

### P6 · [MEDIA] punteggio basso senza errori evidenti — Campo contorto, seme 2

- **Cosa succede:** 1742/1989 punti (87.6%), esito tempo scaduto
- **Punti persi nella gara:** 247.0
- **Come riprodurlo:** `cd ../ClaudeRob_Simulatore_*/ && python3 -c "import esegui; esegui.esegui('../ClaudeRob_V37', 'riprova_contorto_s2', 480, {'seme': 2}, 'contorto')"`
- **Criterio di successo:** Punteggio almeno al 90% del massimo.
- **Ipotesi:** VERIFICATO (replay): nessun errore. Il robot fa tutto il percorso e le 3 palline, ma resta 196 s nella zona (238 -> 434 s) e scrive 'FESTA! Percorso completato' a 479,7 s: il simulatore chiude a 480 s senza contare l'arrivo (mancano 0,3 s). La V30 qui faceva 1825 (anche lei tempo scaduto). Sono il giro dei muri e l'uscita a essere lenti (3 urti in arena a 280-312 s, 'Non avanzo e davanti è vicino: è un angolo' a 408 s).
- **Proposta:** Nessuna correzione urgente. Per guadagnare tempo: misurare quanto dura il giro dei muri [FIX 94] in contorto_s2 e ridurre le soste dopo gli angoli; obiettivo arrivo entro 470 s.

### P7 · [MEDIA] errore segnalato dal simulatore — Pista della SCUOLA: semicerchio accanto alla parete destra (Simulatore V30), secondo 115.4

- **Cosa succede:** Il robot è uscito dal campo
- **Ultime stampe del programma prima dell'evento:**
  ```
  Inizio Ostacolo Dritto
  ARRESTO SICURO DEL ROBOT
  Chiusura Robot...
  Robot fermato correttamente.
  ```
- **Dove guardare nel codice:**
  - `ViennaClsRobot.py` riga 1172 in `def StopLetture(self):` → `print("Robot fermato correttamente.")` (FIX vicini: 6, 70)
  - `ViennaClsRobot.py` riga 1162 in `def StopLetture(self):` → `print("Chiusura Robot...")` (FIX vicini: 6, 70, 72)
  - `RwdFoto.py` riga 4387 in `def ArenaAI():` → `print("ARRESTO SICURO DEL ROBOT")` (FIX vicini: 6, 37, 46, 100)
  - `RwdFoto.py` riga 1158 in `def OstAutDet(Verso=1): # Verso assume valori -1 e 1 e definisce il lato di agir` → `print("Inizio Ostacolo Dritto")` (FIX vicini: 27, 54, 73, 90)
  - `RwdFoto.py` riga 1221 in `def OstAutDet(Verso=1): # Verso assume valori -1 e 1 e definisce il lato di agir` → `print("Inizio Ostacolo Dritto")` (FIX vicini: 27, 28, 54, 73, 90)
- **Come riprodurlo:** `cd ../ClaudeRob_Simulatore_*/ && python3 -c "import esegui; esegui.esegui('../ClaudeRob_V37', 'riprova_scuola_parete', 300, {'seme': 1}, 'scuola_parete')"`
- **Criterio di successo:** L'evento non si ripete nella stessa prova.
- **Ipotesi:** VERIFICATO (posizioni): stessa causa di P1. A 97 s (robot a ~(50, 98) diretto verso la parete a y=123,5) 'POSSIBILE OSTACOLO' -> 'Ostacolo confermato a 8 cm' -> aggira a destra, 'Inizio Ostacolo Dritto' verso ovest, esce dal campo a x=-15 (115 s). Prima, a 95,6 s, 12 × 'Controllo verde: YOLO dice Sx, ma ho appena girato a questo incrocio: seguo la linea' (ViennaClsWebCam.py riga 1056, [FIX 80]/[FIX 91]): da controllare se quel verde andava preso. IPOTESI anche qui: ricostruzione della pista (pista_scuola.py) da verificare.
- **Proposta:** La stessa di P1 (parete davanti riconosciuta come parete). In più: nell'aggiramento fermarsi se il laser laterale non rivede l'ostacolo entro ~40 cm di 'Ostacolo Dritto' (non c'è un ostacolo così lungo).

### P8 · [MEDIA] errore segnalato dal simulatore — STRESS: gli stessi guasti sulla pista lunga, secondo 68.71

- **Cosa succede:** CADUTO da un bordo rialzato (22 cm)
- **Punti persi nella gara:** 806.8
- **Stampa ripetuta prima dell'evento:** "Sinistro" × 7
- **Ultime stampe del programma prima dell'evento:**
  ```
  Linea ritrovata girando di 30 gradi
  Sinistro
  Sinistro
  Sinistro
  Sinistro
  Sinistro
  Sinistro
  Sinistro
  IA         BIANCO               Bi Bi Bi Bi Bi: 
  ```
- **Dove guardare nel codice:**
  - `ViennaClsWebCam.py` riga 1144 in `def CalcolaErrore(frame):` → `print(TrovSinistro,"      ", TrovDestro)` (FIX vicini: 10, 29)
  - `ViennaClsWebCam.py` riga 1153 in `def CalcolaErrore(frame):` → `print("Alto Destro Sinistro", (CentroX-cBkAlX) )` (FIX vicini: 10, 29)
  - `ViennaClsWebCam.py` riga 1158 in `def CalcolaErrore(frame):` → `print("Sinistro-Destro")` (FIX vicini: 10, 29)
  - `RwdFoto.py` riga 3287 in `def InseguitoreIA():` → `print ('IA         BIANCO               Bi Bi Bi Bi Bi: ')` (FIX vicini: 9, 32, 44, 58, 75, 95)
  - `RwdFoto.py` riga 3305 in `def InseguitoreIA():` → `print ('IA         BIANCO               Bi Bi Bi Bi Bi: ')` (FIX vicini: 9, 44, 58, 75, 95)
- **Come riprodurlo:** `cd ../ClaudeRob_Simulatore_*/ && python3 -c "import esegui; esegui.esegui('../ClaudeRob_V37', 'riprova_stress_guasti_lunga', 480, {'seme': 1, 'imu_bloccato': True, 'tof_fr_spurie': 0.15, 'tof_lat_spurie': 0.1}, 'lunga')"`
- **Criterio di successo:** Nella stessa prova (stress_guasti_lunga) l'evento non si ripete e i punti salgono oltre 1087.
- **Ipotesi:** È lo stesso evento di P3 (caduta dal bordo rialzato a 68,7 s): GIÀ NOTO dalla V30.
- **Proposta:** Vedi P3.

### P9 · [BASSA] molti urti — STRESS: giroscopio disturbato di 15°

- **Cosa succede:** 8.0 urti in una gara
- **Come riprodurlo:** `cd ../ClaudeRob_Simulatore_*/ && python3 -c "import esegui; esegui.esegui('../ClaudeRob_V37', 'riprova_stress_bussola', 480, {'seme': 1, 'bussola_distorsione': 15}, 'rcj2026')"`
- **Criterio di successo:** Meno di 4 urti nella stessa prova.
- **Ipotesi:** VERIFICATO: 8 urti, 7 dei quali dopo le palline (319-441 s) mentre il robot cerca l'uscita ed è incastrato nella porta (vedi P2).
- **Proposta:** Si risolve con P2.

### P10 · [BASSA] molti urti — STRESS: gli stessi guasti sulla pista lunga

- **Cosa succede:** 7.0 urti in una gara
- **Come riprodurlo:** `cd ../ClaudeRob_Simulatore_*/ && python3 -c "import esegui; esegui.esegui('../ClaudeRob_V37', 'riprova_stress_guasti_lunga', 480, {'seme': 1, 'imu_bloccato': True, 'tof_fr_spurie': 0.15, 'tof_lat_spurie': 0.1}, 'lunga')"`
- **Criterio di successo:** Meno di 4 urti nella stessa prova.
- **Ipotesi:** VERIFICATO: 7 urti, 3 all'ingresso dell'arena (229-245 s, vedi P4) e 4 tra 311 e 464 s nella zona e in uscita con giroscopio bloccato.
- **Proposta:** Si risolve in buona parte con P4; il resto è il caso estremo giroscopio bloccato (hardware riparato sul robot vero).
