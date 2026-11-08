# Shuri · Rapporto ClaudeRob_V37 — 5 novembre 2026 (sera)

## In breve
- Provata **ClaudeRob_V37** nel **Simulatore V31** (16 prove) e analizzate le **6 scatole nere vere** nuove (3/11 V30, 5/11 V30-V33-V34-V35-V36).
- Sulle 9 prove confrontabili con la V30: **95,0%** medio (V30: 94,3%); pista lunga, contorto 1 e argento-rampa ora **arrivano alla linea rossa**, e la **pista della scuola va dall'inizio all'arrivo** (255 s, 3 palline). La gara vera delle 16:12 (V36) è stata completa fino alla linea rossa.
- **La cosa più importante:** nella prova "giroscopio bloccato" il programma **si pianta** (ciclo senza attesa in `ControllaAperturaMuro` quando lo switch è spento dopo una LoP) e con la bussola disturbata l'**uscita "incerta"** lascia il robot incastrato nella porta. Sul robot vero: **Arduino muto** in 5 gare su 6 (hardware).

**Codice:** ClaudeRob_V37 (impronta 6bd7433259d5c305) · **Simulatore:** ClaudeRob_Simulatore_V31 · **Piste:** rcj2026 (semi 1-3), lunga (1-2), contorto (1-2), arena_parete (1), stress_argento_rampa, stress_bussola, stress_porta, stress_guasti_reali, stress_guasti_lunga, scuola, scuola_rampa, scuola_parete (seme 1).
> ⚠ **Impronta DIVERSA in tutte le 6 scatole nere**: non sono file modificati di nascosto. L'intestazione elenca **82 file .py** nella cartella da cui gira il robot (Bovalino26.py, CT26*, RwdFotoOK.py, …): il robot gira da una cartella di lavoro piena di programmi vecchi, e l'impronta [FIX 86] li conta tutti. Proposta: copiare sul Raspberry la cartella `ClaudeRob_V37` pulita e lanciare da lì (`./avvia.sh`); così l'impronta torna a dire se i 5 file di gara sono quelli giusti.
> ⚠ Le gare vere sono state fatte con V30-V36: la **V37 non è ancora stata provata sul robot vero**.
> ⚠ `stress_guasti_reali` **non eseguita** (programma bloccato, vedi problema 1): la media non la comprende.

## Robot vero (scatole nere)

| Gara | Versione | Durata | Problemi | Arrivo | Note |
|---|---|---|---|---|---|
| 03/11 10:50 | V30 | 542 s | 3 | no | Gira TIMEOUT a 165 s; Arduino muto da 292 s (243 s in tutto) |
| 05/11 11:47 | V30 | 190 s | 2 | no | Gira TIMEOUT alla rotonda (73 s), Arduino muto da 85 s |
| 05/11 12:20 | V33 | 335 s | 6 | **sì** | uscita lenta, dietrofront dopo la festa (rivede l'argento) |
| 05/11 15:12 | V34 | 544 s | 13 | no | dopo l'altalena 8 dietrofront di fila sull'argento (Gira 180 non girava) |
| 05/11 15:52 | V35 | 284 s | 3 | no | uscendo `TypeError` in `StrisciaFerma`: programma chiuso a 284 s |
| 05/11 16:12 | V36 | 538 s | 4 | **sì** | percorso completo (arrivo 429 s), 3 palline; ingresso al 3° tentativo |

Quasi tutti i problemi del 5/11 sono **già stati corretti** nelle versioni successive (V31-V37, FIX 90-102: le scatole nere sono state usate per scriverli). Restano da guardare:
- **DOVE** tutte le gare tranne 15:52 · **COSA** "ARDUINO NON RISPONDE": laser e giroscopio a 0 (da 31 a 243 s a switch acceso; alle 16:12 a 257 s, in arena) · **STATO** VERIFICATO il fatto, causa IPOTESI (hardware) · vedi sotto.
- **DOVE** 16:12, s 36,8 · **COSA** YOLO vede "argento" (0,84) su una rampa (foto camera arena: si vede la pista con il ponte bianco, non l'arena); salita 13° e rollio 14°: il controllo della pendenza (V27) **annulla l'ingresso, giusto** · **STATO** VERIFICATO (foto + giroscopio) · [analisi](../ScatoleNere/analisi/run_2026-11-05_16-12-52_V36/analisi.md)
- **DOVE** 16:12, s 391 · **COSA** "Non avanzo: forse uno spigolo contro uno stipite" nel giro dei muri per l'uscita, dopo "anticipo la svolta" [FIX 94]; poi esce · **STATO** IPOTESI
- **DOVE** 15:12, s 470-493 · **COSA** dietrofront ogni 3 s; nella foto della camera linea c'è pavimento bianco e il piede di una persona: il robot era ormai fuori pista · **STATO** VERIFICATO, già corretto da FIX 97-98 (V35) · [analisi](../ScatoleNere/analisi/run_2026-11-05_15-12-32_V34/analisi.md)
- **DOVE** 03/11 10:50 s 165, 05/11 11:47 s 73 · **COSA** `[Gira] TIMEOUT` con errore residuo -129 / 149 gradi a giroscopio funzionante · **STATO** IPOTESI: stessa causa del FIX 97 (rotazioni vicino a 180°), da riverificare con la V37.

**Misure robot vero vs simulatore:** il **giroscopio è tornato a funzionare** (riparato dopo il 3/11). Ritardo comando → rotta **0,3 s** (0,21 alle 11:47) contro circa **0,2 s** del simulatore (`imu_ritardo` 0,10 + `tau_servo_reale` 0,10): il robot vero risponde ~0,1 s più tardi, da allineare in `mondo.py`. Rotazione sul posto **33-44 °/s**; dopo lo stop 0-5 gradi. Camera linea 10 fps, CPU fino a 62 °C, nessuna sottotensione.
Scheda completa con ipotesi e proposte per ogni problema: [`ScatoleNere/SHURI_scheda_reale.md`](../ScatoleNere/SHURI_scheda_reale.md)

## Hardware da controllare
- **Arduino muto** in 5 gare su 6 (31-243 s a switch acceso; 16:12 per 95 s, già in arena): cavo USB (fissarlo), alimentazione dell'Arduino separata dai motori, tensione della batteria a fine gara. Il codice se ne accorge e usa la bussola stimata [FIX 88], ma senza laser l'arena è alla cieca.
- **Cartella sul Raspberry**: 82 file .py misti (vedi avviso sopra).

## Simulatore

![](Prove/2026-11-05_2113_ClaudeRob_V37/risultati.png)

| Prova | Esito | Punti | % | LoP | Urti | Vittime |
|---|---|---|---|---|---|---|
| rcj2026_s1 / s2 / s3 | arrivo | 1468/1468 | 100 | 0 | 4 / 5 / 5 | 3 |
| lunga_s1 / s2 | arrivo | 1893/1893 | 100 | 0 | 0 / 3 | 3 |
| contorto_s1 | arrivo | 1989/1989 | 100 | 0 | 4 | 3 |
| contorto_s2 | tempo scaduto | 1742/1989 | 87,6 | 0 | 4 | 3 |
| arena_parete_s1 | arrivo (227 s) | — | — | — | 1 | 3 |
| stress_argento_rampa | arrivo | 1893/1893 | 100 | 0 | 3 | 3 |
| stress_bussola | tempo scaduto | 984/1468 | 67,0 | 1 (zona) | 8 | 3 |
| stress_porta | arrivo (231 s) | — | — | — | 0 | 3 |
| stress_guasti_reali | **NON ESEGUITA** (bloccato) | — | — | — | — | — |
| stress_guasti_lunga | tempo scaduto | 1087/1893 | 57,4 | 2 | 7 | 3 |
| scuola | **arrivo (255 s)** | — | — | — | 2 | 3 |
| scuola_rampa | bloccato (218 s) | — | — | — | 0 | 0 |
| scuola_parete (nuova) | fuori campo (115 s) | — | — | — | 0 | 0 |

## Confronto con la batteria precedente (V30)
Dettagli: [`Confronti/ClaudeRob_V30_vs_ClaudeRob_V37/SHURI_confronto.md`](Confronti/ClaudeRob_V30_vs_ClaudeRob_V37/SHURI_confronto.md) (⚠ simulatori diversi: V29 → V31).
- **Migliorate:** lunga_s1 e s2 (+206), contorto_s1 (+247), stress_argento_rampa (+165): con la V30 finivano per tempo, ora arrivano (FIX 94 giro dei muri, FIX 95 arrivo, FIX 96/101 ingresso). **Pista della scuola**: con la V30 l'arena non era mai raggiunta, ora arrivo in 255 s (FIX 91/92).
- **Peggiorate:** stress_bussola (-484, LoP zona), contorto_s2 (-82, per 0,3 s), stress_guasti_reali (bloccata).
- **Uguali:** rcj2026 (100%), stress_guasti_lunga (1087, ma 1 LoP in più).

## Problemi trovati nel simulatore

**1. Programma bloccato dopo una LoP (ciclo senza attesa)** — **DOVE** `stress_guasti_reali` seme 1, 414 s simulati (rifatta da sola: 414 s in 18 s reali, poi fermo per oltre 150 s) · **CODICE** `RwdFoto.py` righe 1838-1845, `ControllaAperturaMuro()`: `while time.time() - t0 < 3.0: Rwd.Dritto(VelP, 0.1, …); LaserVeri()`; `ViennaClsRobot.py` `Dritto()` riga ~1034 esce subito a switch spento [FIX 88] · **STATO** VERIFICATO (faulthandler: il programma è in quel ciclo; ultime stampe "Apertura nel muro: la misuro").
A 414 s scatta la LoP della zona (150 s senza salvare né uscire: con i laser che saltano il robot misura "aperture da 13 cm" che non sono porte); il simulatore spegne lo switch. `Dritto` esce subito senza `sleep`, il ciclo gira all'infinito e il tempo simulato non avanza. Sul robot vero sarebbero 3 s di CPU al 100%, ma soprattutto il robot **continua la manovra della porta a switch spento** invece di tornare in attesa. Proposta: in `Dritto`, quando esce per lo switch, fare comunque `time.sleep(0.02)`; oppure controllare lo switch nei cicli di `ControllaAperturaMuro`. Prova: il comando della scheda P5 deve finire in meno di 60 s reali.

**2. Uscita "incerta" con bussola disturbata: incastrato nella porta** — **DOVE** `stress_bussola`, 386-442 s · **CODICE** `RwdFoto.py` riga 2151 (porta "subito dopo l'angolo", [FIX 63]/[FIX 94]) → `ControllaAperturaMuro` riga ~1912 (`esito_u in ("uscita", "incerto")` = uscita) → `EsciControllando` riga 2499, `StrisciaFerma` [FIX 84/99] · **STATO** VERIFICATO il moto (robot fermo a x 531, y 141 nella porta, rotta 154 invece di ~180, per 45 s; 2 × `[Gira] TIMEOUT`, 7 urti, LoP zona a 442 s), IPOTESI la causa.
Stampe: "camera arena dice uscita, pavimento None" → "Uscito senza vedere la striscia nera" → "Uscita confermata: ritrovata la linea nera" (era la striscia d'uscita). Con la V30 la stessa prova arrivava (1468). Ipotesi: un'uscita senza striscia nera vista viene presa per buona e, dopo FIX 99, `StrisciaFerma` non vede l'incastro se la striscia non è inquadrata. Proposta: con esito "incerto" controllare che il robot avanzi davvero (laser frontale che cambia) e altrimenti arretrare e ripetere `SquadraSullUscita`; uscire lungo l'asse della parete appena seguita.

**3. La parete della pista della scuola presa per un ostacolo** — **DOVE** `scuola_parete` 97-115 s (fuori campo) e `scuola_rampa` 102-218 s (fermo 60 s) · **CODICE** `RwdFoto.py` riga 3042 "POSSIBILE OSTACOLO", riga 2914 "Ostacolo confermato", `ScegliLatoOstacolo()` riga 1016 [FIX 90] · **STATO** VERIFICATO nei dati (in entrambe le prove il robot, a circa 50 cm dal bordo sinistro, va verso la parete a 123,5 cm e la legge a 8-16 cm; poi aggira passando oltre la fine del muro). IPOTESI: la **ricostruzione** della pista (`pista_scuola.py`) potrebbe avvicinare troppo la linea alla parete.
FIX 90 riconosce la parete solo quando è **di lato**; qui è davanti. Proposta: se durante il lato lungo dell'aggiramento il laser laterale vede "ostacolo" per più di ~30-40 cm è una parete: tornare sulla linea. Prima, chiedere ai ragazzi quanto è vicina la linea alla parete in quel punto. Prima dell'ostacolo, a 95,6 s, 12 × "YOLO dice Sx, ma ho appena girato a questo incrocio: seguo la linea" (`ViennaClsWebCam.py` riga 1056, [FIX 80]/[FIX 91]): controllare se quel verde andava preso.

**4. Ingresso con direzione sbagliata di 91° (giroscopio bloccato)** — **DOVE** `stress_guasti_lunga`, 224-262 s · **CODICE** `RwdFoto.py` riga 1671 `DirezioneIngresso()` [FIX 96]/[FIX 101], riga 1557 `IngressoDopoArgento()` [FIX 75] · **STATO** VERIFICATO (stampa "entro verso 308 (robot a 39)"; robot fermo a girare 30 s a x 649, y 249; poi torna indietro → LoP "linea fuori sequenza"), IPOTESI la causa (bussola stimata dopo la svolta).
Proposta: se la direzione attesa e la rotta attuale differiscono di più di 45° non fidarsi di `SvoltaAttesa`, usare la retta della striscia vista dalla camera.

**5. Contorto seme 2: festa a 479,7 s** — **DOVE** `contorto_s2`, 238-434 s in arena · **STATO** VERIFICATO: nessun errore, 196 s nella zona; il simulatore chiude a 480 s senza contare l'arrivo. Da accorciare il giro dei muri.

Scheda per Claude con comandi per riprodurre e criteri di successo: [`SHURI_scheda_correzioni.md`](SHURI_scheda_correzioni.md)

## Già noti
- Caduta dall'altopiano con giroscopio bloccato (`stress_guasti_lunga` 68,7 s) — come nella V30 (problema 3 del rapporto V30), non peggiorato.
- Palline 3-7 cm fuori dai triangoli, conteggio delle prese, batteria non misurata, YOLO da riaddestrare (CHANGELOG "Ancora aperto").
- Ostacolo che a volte riprende la linea nel verso sbagliato (CHANGELOG "Ancora aperto").

## Cose che funzionano bene
- **Campo 2026, pista lunga e contorto 1: 100%**, sempre fino alla linea rossa.
- **Pista della scuola dall'inizio: arrivo in 255 s con 3 palline** (con la V30 l'arena non veniva mai raggiunta).
- Gara vera delle 16:12: **percorso completo e 3 palline su 3**; il falso argento sulla rampa è stato **scartato giustamente** dal controllo della pendenza.
- I ragazzi stanno usando bene le scatole nere: ogni gara del 5/11 ha portato a una correzione (FIX 90-102).
- Nessun falso ostacolo con il laser frontale disturbato ("lettura isolata ignorata", FIX 87) in tutte le prove.

## Da provare con i ragazzi
1. **Copiare la V37 pulita sul Raspberry** e lanciare da quella cartella: nella prossima scatola nera l'impronta deve risultare "uguale".
2. **Prova della porta** (FIX 101): robot fermo davanti all'ingresso spostato di 10-20 cm a destra e a sinistra, dopo una svolta a destra e una a sinistra; contare quante volte entra al primo colpo.
3. **Prova dell'altalena** (FIX 102): far passare il robot sull'altalena 5 volte e guardare se scrive "PROBABILE ALTALENA SUPERATA" e ritrova la linea.
4. **Esercizio sul codice** (problema 1): trovare insieme un ciclo `while time.time() - t0 < …` che non contiene `sleep` e spiegare perché nel simulatore blocca il tempo; proporre la correzione su una copia `ClaudeRob_V38`.

## Cosa il simulatore NON può dire
- YOLO qui è un oracolo: il falso argento sulla rampa delle 16:12 e i verdi visti a metà svolta si vedono solo nelle scatole nere.
- La **pista della scuola è una ricostruzione** (misure, parete, rampa sono stime): i problemi 3 (parete) vanno controllati sul campo vero prima di cambiare il codice.
- Il giroscopio del simulatore risponde in ~0,2 s, quello vero in ~0,3 s: le manovre in arena (porta, stipiti) sul robot vero possono essere un po' peggiori.
- Arduino muto, cavi e batteria non si simulano: per questi valgono solo le scatole nere.
- Da controllare sul robot vero con la V37: ingresso al primo tentativo (FIX 101), altalena (FIX 102), nessun `[Gira] TIMEOUT`.

**Come vedere il robot:** apri `Prove/2026-11-05_2113_ClaudeRob_V37/replay.html` con doppio clic sul Mac.
