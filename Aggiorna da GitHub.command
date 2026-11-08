#!/bin/bash
# Aggiorna la cartella 02_Robotica del Mac con l'ultima versione su GitHub (ramo main).
# Doppio clic su questo file. Non cancella niente e non tocca le cartelle che non sono su GitHub
# (versioni vecchie, Prove di Shuri, Replay...). Se un file è stato cambiato sia qui sul Mac sia su
# GitHub, si ferma e non sovrascrive niente.
cd "$(dirname "$0")" || exit 1
echo "=== Aggiorno 02_Robotica da GitHub ==="
if ! git fetch origin main; then
    echo
    echo "NON RIESCO A COLLEGARMI A GITHUB (rete?). Non ho cambiato niente."
    read -r -p "Premi Invio per chiudere" _
    exit 1
fi
# File nuovi su GitHub che sul Mac ci sono già (per esempio una scatola nera mandata a Claude):
# se sono IDENTICI li tolgo, così git li rimette uguali; se sono diversi non li tocco e lo dico.
git diff -z --name-only --diff-filter=A HEAD origin/main | while IFS= read -r -d '' f; do
    if [ -e "$f" ] && ! git ls-files --error-unmatch -- "$f" >/dev/null 2>&1; then
        if git show "origin/main:$f" | cmp -s - "$f"; then
            rm -- "$f"
        else
            echo "ATTENZIONE: $f c'è già sul Mac ma è DIVERSO da quello su GitHub: non lo tocco."
        fi
    fi
done
if [ "$(git rev-parse HEAD)" = "$(git rev-parse origin/main)" ]; then
    echo
    echo "Già aggiornata: niente di nuovo su GitHub."
elif git merge --ff-only origin/main; then
    echo
    echo "FATTO: cartella aggiornata. Ultime modifiche:"
    git log --oneline -5
else
    echo
    echo "ATTENZIONE: non ho aggiornato niente."
    echo "Alcuni file sono stati cambiati sia qui sul Mac sia su GitHub (vedi l'elenco sopra)."
    echo "Copia questo messaggio e mandalo a Claude."
fi
echo
read -r -p "Premi Invio per chiudere" _
