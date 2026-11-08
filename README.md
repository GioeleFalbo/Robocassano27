# RoboCassano – ClaudeRob

Robot della squadra **RoboCassano** (IISS "Erodoto di Thurii", Cassano allo Ionio) per la RoboCup Junior **Rescue Line**.

| Cartella | Cosa c'è |
|---|---|
| `ClaudeRob_V39/` | il codice del robot (ultima versione). Sul Raspberry: `cd ~/ClaudeRob_V39 && python3 RwdFoto.py` |
| `ClaudeRob_Simulatore_V31/` | il simulatore (Python 3 + `numpy` + `opencv-python`), con la pista della scuola |
| `Strumenti_prove_Claude/` | prove automatiche di porte e altalena nel simulatore |
| `ScatoleNere/` | alcune scatole nere vere (gare del 5 e 6 novembre 2026) e la foto dell'arena dall'alto |
| `CLAUDE.md` | regole del progetto, storia delle versioni e cose da fare (lo legge Claude Code) |

Provare una versione nel simulatore:
```
cd ClaudeRob_Simulatore_V31
python esegui.py "../ClaudeRob_V39" prova 480 scuola
python crea_replay.py prova.html replay_prova.json:"Prova V39"
```
La storia completa delle modifiche (FIX 1-104) è in `ClaudeRob_V39/CHANGELOG.md`.
