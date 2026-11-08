# Come lavorare su RoboCassano (per Battista, Gioele e chi entra nella squadra)

Questa repository contiene il software del robot **RoboCassano** (RoboCup Junior Rescue Line). Ci lavorano il prof
(Giovanni Vaccaro), gli studenti **Battista** e **Gioele**, e Claude (un'intelligenza artificiale che propone correzioni e
le prova nel simulatore).
**Nessuna modifica entra nella versione ufficiale senza che il prof la approvi.**

Prima di cominciare leggi anche `CLAUDE.md`: ci sono le regole fisse, la storia delle versioni e cosa resta da fare.

---

## 0. Prima il robot, poi il codice

La cosa più preziosa in questo progetto **non è saper scrivere Python**: è **capire il robot**. Perché un servo a
rotazione continua non gira sotto una certa soglia, cosa vede un laser contro uno stipite, cosa succede quando lo switch
si spegne in gara. Le correzioni migliori sono sempre nate dalla scatola nera e dalla fisica, non dal codice. Il Python
viene dopo, e lì vi aiuta Claude.

Per questo **ogni pull request deve saper rispondere a tre domande**, a voce, senza leggere il codice:

1. **Che problema risolve?** Quale scatola nera, quale secondo, cosa faceva il robot.
2. **Cosa farà di diverso il robot adesso?** Spiegato a parole, come lo spieghereste a un compagno.
3. **Come sappiamo che funziona e che non rompe il resto?** Le prove nel simulatore, prima e dopo.

Se non sapete rispondere, la pull request non è pronta, anche se il codice "funziona". Alla RoboCup i giudici fanno
proprio queste domande.

Il Python si impara **un pezzo alla volta, sul nostro robot**: si comincia da `ViennaDataConf.py` (solo parametri:
velocità, distanze, soglie; cambiare un numero si vede subito sul robot), poi una funzione alla volta tra quelle che
conoscete già dal comportamento del robot. Quando non capite qualcosa chiedete a Claude: *"spiegami questa funzione in
italiano semplice"*, *"cosa fa questa riga?"*. E spiegatevelo a vicenda: insegnare è il modo più veloce per imparare.

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
3. **Le versioni si prenotano con le issue.** Prima di cominciare guarda la scheda **Issues** e le **Pull requests**
   aperte, poi apri una issue tipo "V41 – Battista – altalena" e assegnala a te. **Chi apre per primo l'issue prende quel
   numero** (e i FIX successivi): se la V41 è già presa, tu prendi la V42. Così nessuno fa due versioni con lo stesso numero.
4. **Ognuno il suo pezzo di robot.** Per esempio Battista l'altalena e il seguilinea, Gioele l'arena (ingresso, palline,
   uscita). Se due persone cambiano la stessa funzione nello stesso momento nascono conflitti difficili da sistemare:
   se ti serve toccare il pezzo di un altro, parlatene prima (anche con un commento nella sua issue).
5. I **nomi dei file** non cambiano mai (`RwdFoto.py`, `ViennaClsRobot.py`, `ViennaDataConf.py`, …).
6. Ogni modifica nel codice ha un commento **`# [FIX n]`** con il motivo (quale scatola nera, quale secondo, cosa si
   vede). Prendi il numero dopo l'ultimo (l'ultimo è scritto in `CLAUDE.md`).
7. In `ViennaDataConf.py` aggiorna `VERSIONE = "ClaudeRob V41"`. I parametri nuovi si mettono **solo** lì e si leggono
   con `getattr(RwdConf, "NOME", valore_di_riserva)`.
8. Aggiorna `CHANGELOG.md` (sezione nuova in cima + una riga nella tabella "In breve") e `LEGGIMI_MODIFICHE.md`
   (una riga per FIX). Questi due file hanno la **fine riga CRLF** (Windows): in Visual Studio Code lo vedi in basso a
   destra; se c'è scritto `LF`, cliccaci e scegli `CRLF`.
9. **Prima della pull request, prova nel simulatore** e confronta con la versione precedente (vedi sotto).

## 4. Il lavoro, passo per passo

1. In GitHub Desktop: **Fetch origin** (scarichi le novità), poi controlla di essere su `main`.
2. **Branch → New branch**, con un nome chiaro: `battista/altalena`, `gioele/uscita`, …
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
8. Se nel frattempo è stata unita la pull request di un altro, nella tua compare il pulsante **Update branch**: premilo
   (o in GitHub Desktop: **Branch → Update from main**), riprova nel simulatore e controlla che vada ancora tutto bene.
9. Dopo il Merge: in GitHub Desktop torna su `main` e fai **Fetch origin** / **Pull origin**. Chiudi l'issue.

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

## 7. Lavorare con Claude Code

1. Ognuno ha il **suo account Claude** (piano Pro, che comprende Claude Code): mai l'account di un altro.
2. Su claude.ai **collega il tuo account GitHub** (lo stesso con cui sei collaboratore).
3. Apri **Claude Code**, scegli la repository `Giooooonni93/Robocassano27`. Claude legge da solo `CLAUDE.md` e conosce
   le regole. Il ramo lo crea Claude; se vuoi un nome chiaro, chiediglielo: *"lavora sul ramo `battista/altalena`"*.
4. Prima richiesta di ogni lavoro: *"guarda le issue e le pull request aperte e dimmi che versione posso usare"*.
5. Un compito = una sessione nuova = un ramo = una pull request.
6. Prima di aprire la pull request, chiedi a Claude di spiegarti la modifica finché sai rispondere da solo alle tre
   domande della sezione 0. **La pull request la firmi tu**: il prof la approva solo se sai spiegarla.

## 8. Cosa NON fare

- Non lavorare direttamente su `main` (è protetto: GitHub non te lo lascia fare).
- Non modificare le cartelle delle versioni già consegnate né il simulatore `ClaudeRob_Simulatore_V31`
  (il simulatore ha la sua numerazione: se serve cambiarlo, si fa `ClaudeRob_Simulatore_V32`).
- Non caricare foto o video con persone riconoscibili, password o dati personali.
- Non caricare file enormi (sopra 50 MB): zip, video, cartelle dei modelli YOLO restano fuori.

## 9. Sul robot

Sul Raspberry si lancia sempre la cartella pulita della versione:

```
cd ~/ClaudeRob_V41 && ./avvia.sh
```

(dentro vanno copiate le 4 cartelle dei modelli YOLO `best_ncnn_model_...`, che non sono su GitHub).
