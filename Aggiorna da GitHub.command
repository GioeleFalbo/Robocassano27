#!/bin/bash
# Aggiorna la cartella 02_Robotica del Mac con l'ultima versione su GitHub (ramo main).
# Doppio clic su questo file.
#
# Come funziona (dal 9/11): 02_Robotica sta in iCloud e iCloud la sincronizza tra i Mac. git dentro iCloud si
# rovina (file spostati nel cloud, due Mac che scrivono insieme), quindi la copia di GitHub sta FUORI da iCloud,
# nella cartella nascosta ~/.robocassano27_git (una per ogni Mac). Lo script:
#   1. aggiorna quella copia da GitHub;
#   2. copia in 02_Robotica i file nuovi o cambiati. Non cancella niente.
# I file che Shuri scrive sul Mac (rapporti, schede, storico, analisi) non vengono mai sovrascritti: si copiano
# solo se mancano. iCloud poi porta tutto anche sull'altro Mac: basta lanciarlo su uno dei due.
DEST="$(cd "$(dirname "$0")" && pwd)"
COPIA="$HOME/.robocassano27_git"
URL="${ROBOCASSANO_URL:-https://github.com/Giooooonni93/Robocassano27.git}"

# tutto dentro { }: bash legge lo script intero prima di cominciare, così può aggiornare anche sé stesso
{

echo "=== Aggiorno 02_Robotica da GitHub ==="
if [ -d "$DEST/.git" ]; then
    echo
    echo "ATTENZIONE: in questa cartella c'è ancora la cartella nascosta .git (git dentro iCloud)."
    echo "Prima va spostata fuori da iCloud: vedi le istruzioni che ti ha dato Claude. Non ho cambiato niente."
    read -r -p "Premi Invio per chiudere" _
    exit 1
fi
if [ ! -d "$COPIA/.git" ]; then
    echo "Prima volta su questo Mac: scarico la copia di GitHub in $COPIA ..."
    git clone --quiet "$URL" "$COPIA" || { echo "NON RIESCO A SCARICARE DA GITHUB (rete?). Non ho cambiato niente."; read -r -p "Premi Invio per chiudere" _; exit 1; }
fi
if ! git -C "$COPIA" fetch --quiet origin main; then
    echo
    echo "NON RIESCO A COLLEGARMI A GITHUB (rete?). Non ho cambiato niente."
    read -r -p "Premi Invio per chiudere" _
    exit 1
fi
# la copia nascosta è solo uno specchio di GitHub: nessuno ci lavora, quindi si allinea sempre a main
git -C "$COPIA" checkout --quiet -B main origin/main && git -C "$COPIA" reset --quiet --hard origin/main

python3 - "$COPIA" "$DEST" <<'EOF'
import os, sys, shutil, subprocess, filecmp
copia, dest = sys.argv[1], sys.argv[2]
# file scritti da Shuri sul Mac: si copiano da GitHub solo se mancano, mai sopra la versione del Mac
def di_shuri(f):
    return (f.startswith("Laboratorio Shuri/SHURI_") or f in ("Laboratorio Shuri/storico.csv", "Laboratorio Shuri/ultimo_stato.json")
            or f.startswith("ScatoleNere/analisi/") or f.startswith("ScatoleNere/schede/")
            or f in ("ScatoleNere/SHURI_scheda_reale.md", "ScatoleNere/storico_reale.csv"))
file = subprocess.run(["git", "-C", copia, "ls-files", "-z"], capture_output=True, check=True).stdout.decode().split("\0")
nuovi, cambiati, tenuti = [], [], []
for f in filter(None, file):
    a, b = os.path.join(copia, f), os.path.join(dest, f)
    if os.path.exists(b):
        if filecmp.cmp(a, b, shallow=False):
            continue
        if di_shuri(f):
            tenuti.append(f)
            continue
        cambiati.append(f)
    else:
        nuovi.append(f)
    os.makedirs(os.path.dirname(b) or dest, exist_ok=True)
    shutil.copy2(a, b)
ultimo = subprocess.run(["git", "-C", copia, "log", "--oneline", "-1"], capture_output=True, text=True).stdout.strip()
print()
if not nuovi and not cambiati:
    print("Già aggiornata: niente di nuovo su GitHub.")
else:
    print(f"FATTO: {len(nuovi)} file nuovi, {len(cambiati)} aggiornati.")
    for f in (nuovi + cambiati)[:25]:
        print("   ", f)
    if len(nuovi) + len(cambiati) > 25:
        print("    ...")
if tenuti:
    print(f"Lasciati come sono sul Mac (scritti da Shuri): {len(tenuti)} file.")
print("Ultima modifica su GitHub:", ultimo)
EOF
echo
read -r -p "Premi Invio per chiudere" _
exit 0
}
