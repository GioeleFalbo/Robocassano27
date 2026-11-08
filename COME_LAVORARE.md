# Come lavorare su RoboCassano (per Battista e per chi entra nella squadra)

Questa repository contiene il software del robot **RoboCassano** (RoboCup Junior Rescue Line). Ci lavoriamo in tre:
il prof (Giovanni Vaccaro), tu, e Claude (un'intelligenza artificiale che propone correzioni e le prova nel simulatore).
**Nessuna modifica entra nella versione ufficiale senza che il prof la approvi.**

Prima di cominciare leggi anche `CLAUDE.md`: ci sono le regole fisse, la storia delle versioni e cosa resta da fare.

---

## 1. Le parole da sapere

| Parola | Cosa vuol dire |
|---|---|
| **repository** | la cartella del progetto su GitHub, con tutta la sua storia |
| **`main`** | il ramo **ufficiale**: quello che va sul robot. È protetto, non si modifica direttamente |
| **ramo** (*branch*) | la tua copia di lavoro: ci fai tutte le prove che vuoi senza toccare `main` |
| **commit** | un salvataggio con una frase che dice cosa hai cambiato |
| **push** | mandi i tuoi commit su GitHub |
| **pull request** (PR) | la proposta "porta le mie modifiche in `main`": il prof la legge e decide |
| **issue** | un problema o un compito scritto su GitHub (scheda *Issues*), con chi se ne occupa |

## 2. Preparare il computer (una volta sola)

1. Crea un account su **github.com** e manda il nome utente al prof. Ti arriva un invito per email: **accettalo**.
2. Installa **GitHub Desktop** (desktop.github.com) e fai l'accesso con il tuo account.
3. In GitHub Desktop: **File → Clone repository** → `Giooooonni93/Robocassano27` → scegli dove metterla.
4. Per il simulatore serve Python 3 con due librerie. Nel Terminale (Mac) o nel Prompt dei comandi (Windows):
   ```
   pip3 install numpy opencv-python
   ```
5. Un editor per il codice: va bene **Visual Studio Code** (code.visualstudio.com) oppure Notepad++.

## 3. Le regole del progetto (sempre)

1. **Ogni modifica al codice del robot è una versione nuova**, in una cartella nuova: si copia l'ultima
   (`ClaudeRob_V40`) in `ClaudeRob_V41` e si lavora **solo** sulla copia.
2. **Non si modifica mai** una cartella già consegnata (V39, V40, …): serve per i confronti.
3. **Una versione nuova alla volta.** Prima di cominciare apri una **issue** tipo "V41 – Battista – altalena" e
   assegnala a te: così il prof e Claude sanno che la V41 è tua e nessuno ne fa un'altra nello stesso momento.
4. I **nomi dei file** non cambiano mai (`RwdFoto.py`, `ViennaClsRobot.py`, `ViennaDataConf.py`, …).
5. Ogni modifica nel codice ha un commento **`# [FIX n]`** con il motivo (quale scatola nera, quale secondo, cosa si
   vede). Prendi il numero dopo l'ultimo (l'ultimo è scritto in `CLAUDE.md`).
6. In `ViennaDataConf.py` aggiorna `VERSIONE = "ClaudeRob V41"`. I parametri nuovi si mettono **solo** lì e si leggono
   con `getattr(RwdConf, "NOME", valore_di_riserva)`.
7. Aggiorna `CHANGELOG.md` (sezione nuova in cima + una riga nella tabella "In breve") e `LEGGIMI_MODIFICHE.md`
   (una riga per FIX). Questi due file hanno la **fine riga CRLF** (Windows): in Visual Studio Code lo vedi in basso a
   destra; se c'è scritto `LF`, cliccaci e scegli `CRLF`.
8. **Prima della pull request, prova nel simulatore** e confronta con la versione precedente (vedi sotto).

## 4. Il lavoro, passo per passo

1. In GitHub Desktop: **Fetch origin** (scarichi le novità), poi controlla di essere su `main`.
2. **Branch → New branch**, con un nome chiaro: `battista/altalena`, `battista/ostacolo`, …
3. Copia la cartella dell'ultima versione (es. `ClaudeRob_V40` → `ClaudeRob_V41`) e lavora lì.
4. Prova nel simulatore (sezione 5).
5. In GitHub Desktop scrivi una frase nel riquadro in basso a sinistra (es. "V41: FIX 106 altalena, ritrova la
   linea") e premi **Commit**.
6. **Push origin**, poi **Create Pull Request**. Nella pull request scrivi:
   - **da dove viene** il problema (scatola nera, secondo, cosa si vede);
   - **cosa hai cambiato**;
   - **le prove**: una tabella "prima / dopo" con i risultati del simulatore.
7. Il prof legge, commenta, e se va bene fa **Merge**. Se chiede modifiche: correggi sullo stesso ramo, Commit,
   Push. La pull request si aggiorna da sola.

## 5. Provare nel simulatore

Dalla cartella `Strumenti_prove_Claude`:

```
python3 gira.py ../ClaudeRob_V41 prova scuola 480 seme=1
```

Risultato atteso (V39 e V40): **arrivo** in 255-259 s con i semi da 1 a 6. Prova anche le altre piste
(`rcj2026`, `lunga`, `contorto`, `arena_parete`, `gara`) e confronta con la versione precedente:

```
python3 gira.py ../ClaudeRob_V40 prima rcj2026 480 seme=1
python3 gira.py ../ClaudeRob_V41 dopo  rcj2026 480 seme=1
```

I risultati di riferimento sono in `CLAUDE.md` (sezione "Il simulatore"). Altre prove (porte, altalena) sono descritte
in `Strumenti_prove_Claude/LEGGIMI.md`. Per vedere la gara nel browser:

```
cd ../ClaudeRob_Simulatore_V31
python3 crea_replay.py confronto.html replay_prima.json:"V40" replay_dopo.json:"V41"
```

La batteria completa di Shuri (circa 16 gare): da `Laboratorio Shuri`, `python3 batteria.py ../ClaudeRob_V41`.

## 6. Le scatole nere

Dopo ogni prova sul robot vero, la scatola nera (`run_AAAA-MM-GG_hh-mm-ss_V<n>.jsonl`) va in `ScatoleNere/`.
Per guardarla velocemente:

```
python3 -I Strumenti_prove_Claude/analizza_scatola_nera.py ScatoleNere/<nome del file>.jsonl
```

Il metodo che funziona: trovare il momento in cui succede il problema, guardare i dati secondo per secondo (laser,
rotta, motori, YOLO), capire la causa fisica, riprodurla nel simulatore, correggere, dimostrare la correzione con una
prova prima/dopo.

## 7. Cosa NON fare

- Non lavorare direttamente su `main` (è protetto: GitHub non te lo lascia fare).
- Non modificare le cartelle delle versioni già consegnate né il simulatore `ClaudeRob_Simulatore_V31`
  (il simulatore ha la sua numerazione: se serve cambiarlo, si fa `ClaudeRob_Simulatore_V32`).
- Non caricare foto o video con persone riconoscibili, password o dati personali.
- Non caricare file enormi (sopra 50 MB): zip, video, cartelle dei modelli YOLO restano fuori.

## 8. Sul robot

Sul Raspberry si lancia sempre la cartella pulita della versione:

```
cd ~/ClaudeRob_V41 && ./avvia.sh
```

(dentro vanno copiate le 4 cartelle dei modelli YOLO `best_ncnn_model_...`, che non sono su GitHub).
