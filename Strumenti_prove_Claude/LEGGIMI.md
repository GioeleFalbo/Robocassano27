# Strumenti di prova di Claude (V35-V39)

Script usati per provare le porte e l'altalena nel simulatore (dal 10/11 il Simulatore V32). Stanno in `02_Robotica/Strumenti_prove_Claude/` e trovano
da soli il simulatore in `../ClaudeRob_Simulatore_V32` (oppure nella variabile d'ambiente `SIMULATORE`). Si lanciano da questa
cartella. Le copie di prova delle versioni finiscono in `copie_di_prova/` (si possono cancellare); i replay nel simulatore.

| Script | Cosa prova | Risultato V39 |
|---|---|---|
| `gira.py` | una gara intera con riassunto | scuola semi 1-6 arrivo; rcj2026 1468, lunga 1893, contorto 1989 |
| `prova_ingresso.py` | porta d'ingresso con il robot spostato (y 55-95) e lato previsto | 8/8 col lato giusto, 6/8 col lato sbagliato |
| `prova_uscita.py` | porta d'uscita con il robot spostato (-12..+12 cm) | 9/9 |
| `prova_uscita_angolo.py` | uscita vista seguendo il muro, davanti al muro accanto alla porta (x 222-234) | 4/4 |
| `prova_altalena.py` | riconoscimento dell'altalena con uno stoppie finto | "PROBABILE ALTALENA SUPERATA", riparte |
| `analizza_scatola_nera.py` | eventi di una scatola nera vera, o i campioni tra due istanti | – |
| `terminale_nuovo.py` | **moviola**: rivede una scatola nera vera nel terminale con la cabina di pilotaggio della V42 (camere, cronometro, fasi). Finestra di almeno 100 x 38 | – |

Esempi:
```
python gira.py ../ClaudeRob_V39 prova scuola 480 seme=3
python prova_ingresso.py ../ClaudeRob_V39 ing_95 95 -1
python prova_uscita.py ../ClaudeRob_V39 usc_10 10
python prova_uscita_angolo.py ../ClaudeRob_V39 ang_230 230
python prova_altalena.py ../ClaudeRob_V39 alt
python -I analizza_scatola_nera.py ../ScatoleNere/run_2026-11-06_10-48-52_V38.jsonl
python3 -I terminale_nuovo.py ../ScatoleNere/run_2026-11-09_10-46-10_V40.jsonl --da 120 --velocita 2
python ../ClaudeRob_Simulatore_V32/crea_replay.py confronto.html <replay_A.json>:"A" <replay_B.json>:"B"
```
