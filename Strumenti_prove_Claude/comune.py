# Strumenti di prova usati da Claude per ClaudeRob (V35-V39). Trovano il simulatore accanto a questa cartella
# (../ClaudeRob_Simulatore_V31) oppure nella variabile d'ambiente SIMULATORE.
import os, sys, shutil
QUI = os.path.dirname(os.path.abspath(__file__))
SIM = os.path.abspath(os.environ.get("SIMULATORE") or os.path.join(QUI, "..", "ClaudeRob_Simulatore_V31"))
sys.path.insert(0, SIM)
PROVE = os.path.join(QUI, "copie_di_prova")       # copie delle versioni con un "main" di prova (si possono cancellare)


def copia_con_main(src, nome, main):
    """Copia la cartella della versione e sostituisce il programma principale di RwdFoto.py con 'main'."""
    dst = os.path.join(PROVE, nome)
    if os.path.exists(dst):
        shutil.rmtree(dst)
    shutil.copytree(src, dst, ignore=shutil.ignore_patterns("__pycache__"))
    p = os.path.join(dst, "RwdFoto.py")
    s = open(p, encoding="utf-8").read()
    i = s.index("SwPrec = False      # [FIX 7]")
    open(p, "w", encoding="utf-8").write(s[:i] + main)
    return dst


def replay(nome):
    import json
    return json.load(open(os.path.join(SIM, f"replay_{nome}.json"), encoding="utf-8"))
