# ClaudeRob_Simulatore_V31

Fa girare il vostro `RwdFoto.py` **senza modificarlo** su un robot virtuale con gli stessi componenti
(2 PCA9685, 4 servo 360°, braccio e pinza, 3 VL53L0X, giroscopio, 2 camere, LED).
Funziona su qualsiasi PC (Windows, Linux, Mac): il Raspberry non serve.

## Installazione (una volta sola)

```
pip install numpy opencv-python
```

## Su un PC Windows

1. Installate Python 3 da python.org (non dal Microsoft Store). Durante l'installazione spuntate
   **"Add python.exe to PATH"**.
2. Mettete nella stessa cartella le due cartelle estratte dagli zip: `ClaudeRob_Simulatore_V31` e
   `ClaudeRob_V34` (una accanto all'altra). I modelli YOLO non servono: nel simulatore YOLO è finto.
3. Doppio clic su **`SIMULA.bat`**. La prima volta installa da solo `numpy` e `opencv-python` (serve internet),
   poi fa una gara sul campo 2026 (circa 30 secondi) e apre la pagina del replay nel browser.
4. Per un altro campo, dal Prompt dei comandi nella cartella del simulatore:
   `SIMULA.bat lunga` (oppure `contorto`, `gara`, `arena`, `arena_parete`). Per provare un'altra versione del codice:
   `SIMULA.bat rcj2026 "..\ClaudeRob_V23"`.

Se non volete usare il file .bat, gli stessi comandi a mano sono:
```
py -m pip install numpy opencv-python
py esegui.py "..\ClaudeRob_V34" mia_prova 480 rcj2026
py crea_replay.py mia_prova.html replay_mia_prova.json:"La mia prova"
```

## Su un Mac (anche con processore M1, M2, M3)

1. Installate Python 3 da python.org (il pacchetto per macOS, va bene per i processori Apple).
2. Mettete nella stessa cartella le due cartelle estratte dagli zip: `ClaudeRob_Simulatore_V31` e `ClaudeRob_V34`.
3. Doppio clic su **`SIMULA.command`**. La prima volta macOS può dire che viene da uno "sviluppatore non
   identificato": tasto destro sul file → **Apri** → **Apri** (oppure Impostazioni di Sistema → Privacy e
   sicurezza → "Apri comunque"). Si apre il Terminale: la prima volta prepara una cartella `.venv` con
   `numpy` e `opencv-python` (serve internet), poi fa la gara e apre il replay nel browser.
4. Altri campi, dal Terminale nella cartella del simulatore: `./SIMULA.command contorto`
   (oppure `gara`, `arena`, `arena_parete`). Se il doppio clic non parte: `bash SIMULA.command`.

## Come si usa

1. Mettete la cartella `ClaudeRob_Simulatore_V31` accanto alla cartella `ClaudeRob_V34` con i vostri file `.py`
   (devono esserci almeno `RwdFoto.py`, `ViennaClsRobot.py`, `ViennaClsWebCam.py`, `ViennaDataConf.py`).
2. Lanciate una prova:
   ```
   python esegui.py "../ClaudeRob_V34" mia_prova 420 gara
   ```
   - `mia_prova` = nome della prova (crea `replay_mia_prova.json`)
   - `420` = secondi massimi di gara simulata
   - `gara` = percorso completo, oppure `arena` = parte davanti all'ingresso dell'arena
   Una gara di 7 minuti si simula in circa 10–15 secondi.
3. Create la pagina da aprire nel browser:
   ```
   python crea_replay.py confronto.html replay_mia_prova.json:"La mia prova" replay_v2_gara.json:"v2"
   ```
   Aprite `confronto.html` con doppio clic.

## Novità della V31: l'arena VERA della scuola (foto dall'alto del 5/11)

- Arena **120 x 90 cm**: il lato lungo (120) è il muro in comune con la pista, profonda 90 cm.
- **INGRESSO** (argento) sul lato lungo, 3a colonna: come prima, la foto lo conferma.
- **USCITA** (striscia nera) spostata sul **lato corto** verso la colonna accanto all'arena, da 29 a 56 cm dal muro
  in comune, accanto al triangolo **ROSSO**. Il triangolo **VERDE** è nell'angolo opposto. La vecchia uscita
  della 1a colonna ora è muro.
- Dall'uscita la linea scende nella colonna accanto all'arena; la **linea rossa d'arrivo** l'ho messa lì, circa
  30 cm dopo l'uscita: **nella foto non si vede, da verificare** (si cambia `ROSSO_FOTO` in `pista_scuola.py`).
- Palline in posizioni di prova (nella foto erano già negli angoli). I triangoli si spostano cambiando
  `C["triangoli"]` in `pista_scuola.py`.

```
SIMULA.bat scuola                (Windows)      ./SIMULA.command scuola       (Mac)
```

## Novità della V30: parete lungo il bordo destro della pista della scuola

- Dalla terza foto del 3/11: lungo il bordo DESTRO della pista (sotto la colonna accanto all'arena) c'è una parete,
  e il robot vero la tocca sul semicerchio (scatola nera V30, secondo 81). Ora c'è anche nel simulatore.
- Nell'arena: triangolo VERDE in fondo a sinistra, triangolo ROSSO nell'angolo vicino a destra (dietro il muro dopo
  l'ingresso), palline in fondo, come nella foto.
- Nuova partenza `scuola_parete`: dopo l'interruzione della 4a colonna, verso il semicerchio accanto alla parete.

## Novità della V29: la PISTA DELLA SCUOLA e i guasti del robot vero

**La pista della scuola** (ricostruita dalle due foto del 3/11, file `pista_scuola.py`):
4 x 7 piastrelle più la colonna accanto all'arena, con l'arena dietro il bordo alto delle foto. Sul muro in comune
ci sono l'**INGRESSO** (striscia argento, 3a colonna) e l'**USCITA** (striscia nera, 1a colonna, all'angolo); dall'uscita
la linea scende fino alla **linea rossa** d'arrivo. Nel simulatore la pista è girata di 90 gradi (l'arena è a destra,
il robot entra andando verso est), ma è la stessa. Tre partenze:
- `scuola`: sulla linea lunga in alto a sinistra, verso destra (falso verde, tubo, zig-zag, quadrato, ingresso, arena,
  uscita, arrivo);
- `scuola_rampa`: in fondo alla rampa con i tubi (piattaforma, cerchio, curve a S...);
- `scuola_basso`: verticale di sinistra in basso (angolo, zig-zag, T con doppio verde).

```
SIMULA.bat scuola                (Windows)      ./SIMULA.command scuola       (Mac)
python esegui.py "../ClaudeRob_V30" prova 420 scuola
```

**Da verificare sulla pista vera** (nelle foto non si vede): misure dell'arena (messa 120 x 120 cm), posizione dei
triangoli e delle palline, altezza della piattaforma e pendenza della rampa (messa 12 gradi sulle 2 piastrelle con i
tubi; la piattaforma è in piano), cosa c'è a destra e sopra la colonna accanto all'arena. Si cambiano in cima a
`pista_scuola.py`.

**I guasti visti sul robot vero** (scatola nera del 3/11), da aggiungere a una prova con `cfg`:
- `imu_bloccato: True` (e `imu_blocca_da` in secondi): il giroscopio manda sempre (-2, -2, 0);
- `tof_fr_spurie: 0.15` / `tof_lat_spurie: 0.1`: probabilità che una lettura del laser frontale / laterale sia un
  valore a caso tra 3 e 480 cm (il 3/11: 15% e 10%);
- `arduino_muto_da: 120` (e `arduino_muto_per`): da quel secondo l'Arduino non manda più niente.

Esempio: `esegui.esegui("../ClaudeRob_V30", "guasti", 480, {"imu_bloccato": True, "tof_fr_spurie": 0.15}, "rcj2026")`.
Con questi guasti la V30 fa 1103 punti su rcj2026 (tutte le palline salvate); la V29 non arriva in fondo.

## Novità della V28: verdi in diagonale e falso argento sulle rampe

- Piastrella incrocio con **verdi in diagonale** (foto del 29/10): `verdi="diagonale_dx"` (valido a destra, falso a
  sinistra dopo l'incrocio) e `verdi="diagonale_sx"`. Sulla pista `lunga` ci sono tutte e due: la T prima dell'arena
  e l'incrocio dopo il GAP 20.
- `"yolo_argento_rampa": True` nella configurazione: nel primo secondo di ogni rampa YOLO vede un falso ARGENTO grande
  quanto l'immagine, come nella scatola nera del 29/10 (secondo 93,6). Con la V26 il robot "entra nell'arena" sulla
  rampa e prende 8 LoP; con la V27 l'ingresso si annulla e il robot arriva in fondo:
  `esegui.esegui("../ClaudeRob_V27", "rampa", 480, {"yolo_argento_rampa": True}, "lunga")`
- La scatola nera simulata ha il campo `pend` (pendenza capita dal giroscopio, FIX 82): apritela col cruscotto.

## Novità della V27: giroscopio in ritardo e incrocio prima dell'arena

- Dalle scatole nere del 23 e del 26 ottobre: il robot vero **vede la rotazione sul giroscopio 0,2 s dopo il
  comando** e dopo lo stop scivola ancora di 5–7°. Ora il simulatore fa lo stesso (`imu_ritardo = 0.10` s in
  `mondo.py`, più `tau_servo_reale = 0.10` per i servo). Con la V25 si rivedono gli stessi errori della gara:
  correzioni che vanno oltre e palline prese di lato.
- Pista **`lunga`**: subito prima dell'ingresso dell'arena c'è un **incrocio a T con il verde a sinistra**, come sul
  campo della scuola. La V25 vede l'argento a metà svolta ed entra storta di 30–40°; la V26 entra a 90° e centrata.
- Nel replay: "Pista lunga · V26" e "Pista lunga · V25" mostrano la stessa pista con le due versioni.
- Il punteggio massimo della pista lunga ora è 1.893.

## Novità della V26: pista lunga con l'arena della scuola

- Scenario **`lunga`**: 26 × 14 piastrelle (7,8 × 4,2 m), 84 piastrelle di percorso con tutto quello del campo
  2026 (rampe, altopiano, interruzioni fino a 20 cm, dossi, detriti, incroci, vicolo cieco, falsi verdi,
  tratteggiata, ostacolo, altalena) e una **zona di evacuazione 4 × 4 con ingresso e uscita sullo stesso muro**,
  come l'arena della scuola. Punteggio massimo 1.893 (V27).
- Il regolamento dà 8 minuti: su questa pista il robot (11 cm/s) di solito non arriva in fondo. Per vedere tutta la
  gara: `esegui.esegui(cartella, nome, 900, {"tempo_gara": 900}, "lunga")`.
- Nel costruttore delle piastrelle `K.arena(...)` accetta `righe=4`, `uscita_lato="sinistro"` e `uscita_riga`.

## Novità della V26: servo come quelli veri

La scatola nera del 23/10 ha mostrato che i servo a rotazione continua del robot arrivano quasi subito al
massimo: il robot va a circa 11 cm/s (quasi uguale a velocità 34, 47 o 68), ruota sul posto a circa 35 gradi
al secondo e, a velocità 47, con uno sterzo tra -50 e +50 **non gira**. Prima il simulatore faceva crescere la
velocità in modo lineare fino a 30 cm/s, quindi le sterzate piccole funzionavano e i problemi del robot vero
(muro a 10-30 cm nel giro dei muri) non si vedevano.

- `servo_modello`: `"reale"` (nuovo, normale) oppure `"lineare"` (come fino alla V25).
- `servo_k`, `vmax_reale`, `slittamento_reale`: forma della curva, velocità massima e slittamento, tarati sulla
  scatola nera.
- `bussola_distorsione`: gradi di errore del giroscopio che cambia con la direzione (come un BNO055 disturbato
  dai motori). Normale 0; provate 15 per vedere quanto il codice resiste.

Si cambiano con `esegui.esegui(cartella, nome, 420, {"servo_modello": "lineare"}, "gara")`.
Con i servo "reali" anche le sterzate del seguilinea sono più deboli: sul campo contorto ricompare il "BOOSTER"
sinistra/destra che si vede nella scatola nera (secondi 33-46).

## Novità della V22: campo RCJ 2026 a piastrelle

```
python esegui.py "../ClaudeRob_V27" mia_gara 480 rcj2026
```

- **Campo grande (20 × 12 piastrelle)** costruito con le piastrelle del regolamento 2026 (`piastrelle.py`):
  zig-zag, curve strette, angolo retto e acuto, interruzioni da 14 e 18 cm, rampa di 20° fino a un altopiano alto 22 cm,
  tratto inclinato di lato, discesa con onde, dossi, detriti, falso verde, vicolo cieco, incrocio attraversato due volte,
  ostacolo, altalena, zona di evacuazione 4 × 3 e arrivo con la striscia rossa.
- **Fisica 3D**: in salita il robot rallenta, in discesa accelera, sui tratti inclinati scivola verso valle, da fermo in
  pendenza scivola un po'. Le ruote davanti salgono sulla rampa prima di quelle dietro. I laser sono a 6 cm d'altezza
  e possono colpire la rampa. La camera della linea guarda il pavimento inclinato. Dai bordi rialzati si cade.
  I numeri sono in `CONFIG` (`scivolo_laterale`, `scivolo_fermo`, `scivolo_pendenza`, `tof_altezza`, `caduta_min`...).
- **Arbitro e punteggio ufficiale 2026** (e bozza 2027): piastrelle e checkpoint 5/3/1, ostacoli, vittime ×1,4,
  bonus d'uscita, 8 minuti. Mancanza di progresso (LoP) automatica: il simulatore spegne lo switch, rimette il robot
  all'ultimo checkpoint e lo riaccende. Dopo 3 tentativi passa al checkpoint successivo.
- **Capitano**: se il robot non raggiunge nessuna piastrella nuova per `lop_fermo_s` secondi (45) il simulatore chiama la LoP.
- **Seme**: `"seme": 3` nella configurazione cambia il rumore dei sensori. Fate più gare con semi diversi e guardate
  la media dei punti, non una gara sola.
- **Campo contorto** (`contorto`): serpentone di file a 30 cm l'una dall'altra, 15 interruzioni (anche dopo una
  curva a U e tratteggiate), altopiano stretto tra due file, ramo senza verde, vicolo cieco, due ostacoli.
  `python esegui.py "../ClaudeRob_V27" prova 480 contorto`
- Per costruire un campo vostro copiate `crea_campo_rcj2026()` in `campo.py`: ogni riga `m("tipo", ...)` è una piastrella.
  Opzioni: `pendenza=20` (rampa, negativa = discesa), `banca=10` (inclinata di lato), `cp=True` (checkpoint),
  `etichetta="..."`. Per gli incroci: `forma="T"|"+"|"Tdx"|"Tsx"`, `verdi="dx"|"sx"|"doppio"|""|"falso_dx"|"falso_sx"`.

## I file

| File | Cosa contiene |
|---|---|
| `campo.py` | I campi: quello vecchio (gara, arena, arena_parete) e quello nuovo a piastrelle (rcj2026). |
| `piastrelle.py` | Tutte le piastrelle del regolamento 2026 e il costruttore del campo a piastrelle. |
| `mondo.py` | Fisica, sensori, camere e il "YOLO oracolo". In cima c'è `CONFIG` con tutte le misure del robot. |
| `finto_hw.py` | Sostituisce smbus2, serial, gpiozero, picamera2, ultralytics e il tempo con versioni simulate. |
| `esegui.py` | Lancia il vostro programma nel mondo simulato. |
| `crea_replay.py` + `visualizzatore.html` | Creano la pagina di replay. |

## Da sapere

- **Le camere sono misurate** (foto di calibrazione dell'8 ottobre 2026): camera linea a 8,3 cm, 15° dalla
  verticale, campo 80°, sul muso; camera arena a 9,8 cm, 26° verso il basso, campo 68°.
- **Le altre misure in `CONFIG` sono ancora stime**: posizione dei laser, velocità massima dei servo,
  lunghezza del braccio. Se le misurate correggetele: il risultato su ostacolo e triangoli dipende da questi numeri.
- **YOLO è un oracolo**: risponde con quello che c'è davvero davanti alla camera. Il modello vero
  può sbagliare; il simulatore prova la *logica* del programma, non la qualità del modello.
- `time.sleep` nel vostro codice fa avanzare il tempo simulato: la simulazione è sempre uguale
  a se stessa (stessi risultati ogni volta), utile per confrontare due versioni del codice.
- Le `print` del programma finiscono nel riquadro "Cosa stampa il programma" della pagina.
- **Scatola nera anche nel simulatore**: ogni prova scrive in `scatole_simulate/` lo stesso file che scrive il robot.
  Apritelo con `ClaudeRob_V27/cruscotto/cruscotto.html` (c'è già `esempio_gara_simulata.jsonl`).
- **Arena della scuola**: lo scenario `arena_parete` ha ingresso e uscita sullo stesso muro, come nel video dell'8/10.
  Con `{"yolo_porta_solo_ingresso": true}` il modello dei triangoli vede come porta solo l'ingresso (il caso peggiore).
  I laser fuori portata (oltre 120 cm) mandano 0 come sul robot vero. Con `{"tof_fuori_portata": 200, "tof_max": 200}` si torna al vecchio comportamento (200).
  Con `{"yolo_argento_falso": true}` YOLO vede un falso ARGENTO in mezzo alla linea all'inizio della gara (prova del FIX 46).
  Esempio: `python esegui.py "../ClaudeRob_V27" prova 300 arena_parete`.
