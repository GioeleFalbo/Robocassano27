# RoboCassano – ClaudeRob

Robot della squadra **RoboCassano** (IISS "Erodoto di Thurii", Cassano allo Ionio) per la RoboCup Junior **Rescue Line**.

| Cartella | Cosa c'è |
|---|---|
| `ClaudeRob_V40/` | il codice del robot (ultima versione). Sul Raspberry: `cd ~/ClaudeRob_V40 && python3 RwdFoto.py` |
| `ClaudeRob_V39/` | la versione precedente, tenuta per i confronti nel simulatore |
| `ClaudeRob_Simulatore_V31/` | il simulatore (Python 3 + `numpy` + `opencv-python`), con la pista della scuola |
| `Strumenti_prove_Claude/` | prove automatiche di porte e altalena nel simulatore |
| `Laboratorio Shuri/` | gli strumenti di **Shuri**, l'agente collaudatore sul Mac del prof: batteria di prove nel simulatore, analisi delle scatole nere, ultimo rapporto. Chi è: `CHI_E_SHURI.md` |
| `Meccanica_STL/` | i pezzi stampati in 3D del robot (millimetri) |
| `ScatoleNere/` | alcune scatole nere vere (gare del 5 e 6 novembre 2026) e la foto dell'arena dall'alto |
| `CLAUDE.md` | regole del progetto, storia delle versioni e cose da fare (lo legge Claude Code) |
| `COME_LAVORARE.md` | **per chi entra nella squadra**: come si lavora con GitHub, le regole delle versioni, le prove nel simulatore |
| `Aggiorna da GitHub.command` | doppio clic sul Mac: aggiorna la cartella `02_Robotica` con l'ultima versione di `main` |

Provare una versione nel simulatore:
```
cd ClaudeRob_Simulatore_V31
python esegui.py "../ClaudeRob_V40" prova 480 scuola
python crea_replay.py prova.html replay_prova.json:"Prova V40"
```
La storia completa delle modifiche (FIX 1-105) è in `ClaudeRob_V40/CHANGELOG.md`.
