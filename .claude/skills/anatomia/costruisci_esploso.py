#!/usr/bin/env python3
"""Costruisce Meccanica_STL/esploso_robot.html: il robot RoboCassano in 3D che si smonta con un cursore.

Uso (dalla cartella principale della repository):
    python3 .claude/skills/anatomia/costruisci_esploso.py

La pagina è un file unico: dentro ci sono i 5 pezzi di Meccanica_STL/ (in millimetri, già nella posizione di montaggio) e
three.js preso dalla cartella cruscotto/ dell'ultima ClaudeRob_V<n>. Si apre con doppio clic, anche senza Internet.
Se cambia un pezzo stampato o se ne aggiunge uno, aggiornare la tabella PEZZI qui sotto e rilanciare.
"""
import base64, glob, json, os, re, struct, sys

QUI = os.path.dirname(os.path.abspath(__file__))
RADICE = os.path.abspath(os.path.join(QUI, "..", "..", ".."))
STL = os.path.join(RADICE, "Meccanica_STL")
USCITA = os.path.join(STL, "esploso_robot.html")

# Asse verticale = Y, muso verso X negativo (pinza e camere). "via" = spostamento in mm quando il robot è smontato del tutto.
# "porta" è dedotto dal nome del file: va confermato con la squadra (lo dice anche la pagina).
PEZZI = [
    {"file": "ServoRWDAmmortizzato.stl", "nome": "Piastra dei servo (trazione ammortizzata)", "colore": "#e8a33d",
     "via": [0, -70, 0], "dove": "In basso: è la piastra più bassa del robot.",
     "porta": "I supporti dei 4 servo a rotazione continua delle ruote, con l'ammortizzazione.",
     "codice": "Ruote: scheda PCA9685 0x41, canali 15 e 4 (sinistra), 0 e 11 (destra). Comando: Sterzo(velocita, sterzo) in ViennaClsRobot.py."},
    {"file": "BaseLogica.stl", "nome": "Base della logica", "colore": "#4f8fd6",
     "via": [0, 0, 0], "dove": "Al centro del robot.",
     "porta": "L'elettronica: Raspberry Pi 5, Arduino Nano, le due schede PCA9685.",
     "codice": "Raspberry: RwdFoto.py (programma di gara). Arduino: 3 laser VL53L1X, giroscopio BNO055, switch, su USB a 230400 baud."},
    {"file": "CoperturaAlta.stl", "nome": "Copertura alta", "colore": "#7c6bc4",
     "via": [0, 75, 0], "dove": "In alto: chiude il robot.",
     "porta": "Protegge l'elettronica.",
     "codice": "—"},
    {"file": "SupportoPinzaWebcam_1.stl", "nome": "Supporto della pinza e della camera linea", "colore": "#2f9e6f",
     "via": [-95, -10, 0], "dove": "Davanti, sul muso.",
     "porta": "Il braccio con la pinza per le vittime e la camera che guarda la linea (12 cm davanti alle ruote).",
     "codice": "Braccio: servo DM996, PCA9685 0x40 canale 4; pinza: canale 11. Camera linea (punta verso il basso): Picamera2(0), 440x260, YOLO Cross3."},
    {"file": "CupolaWebArenaLED.stl", "nome": "Cupola della camera arena e delle luci", "colore": "#d64f6a",
     "via": [-150, 45, 0], "dove": "Sul muso, in alto: un pannello sottile.",
     "porta": "La camera che guarda l'arena e le luci LED.",
     "codice": "Camera arena (quella inclinata): Picamera2(1), 440x260, YOLO PalCol3 / TrianFull3 / Exit3. Luci: GPIO 22 e 23."},
    {"file": "Braccio.stl", "nome": "Braccio (servo DM996)", "colore": "#22a6b3",
     "via": [-120, 120, 0],
     # [10/11] lo STL del prof (0Servo4WDFisso2006PinzaMonoVaccaro.stl) NON è nelle coordinate di montaggio. È disegnato con
     # il braccio ABBASSATO (base della pinza vicino al pavimento, davanti al muso). Il perno è il centro del disco per la
     # squadretta del servo (asse = larghezza del robot): lo si porta sul davanti, a sinistra, e nella pagina il cursore
     # "Braccio" lo ruota da 0 (giù) a "alzato" (gradi negativi). Posizione INDICATIVA, presa dalle foto.
     "posa": {"perno_stl": [41.7, 74.6, -372.4], "perno": [-30, 5, -160], "alzato_gradi": -140},
     "dove": "Sul davanti, a sinistra: il disco si avvita alla squadretta del servo DM996 (il perno), la base piatta porta la pinza. Usa il cursore 'Braccio' per alzarlo e abbassarlo. Posizione indicativa (lo STL non è nelle coordinate di montaggio).",
     "porta": "La pinza con il suo servo (STL della pinza in arrivo).",
     "codice": "Servo DM996 all metal, PCA9685 0x40 canale 4: Braccio(angolo) in ViennaClsRobot.py; AbbassaPinza / AlzaPinza / CaricaPalla in RwdFoto.py."},
    # --- componenti: modelli SEMPLIFICATI fatti da componenti.py (misure dei datasheet), montati ai loro LIVELLI (dal prof,
    # 10/11): livello 1 = piastra dei servo (piano a Y -41): batteria e buck; livello 2 = base della logica (Y +4): le due
    # PCA9685 e l'Arduino; livello 3 = copertura alta (Y +41): Raspberry e relè. Il livello è giusto; il punto preciso
    # dentro il livello è INDICATIVO. "via" = quella del loro livello, così si smontano insieme. I servo stanno sotto.
    {"file": "componenti/Servo_FS5106R.stl", "nome": "Servo delle ruote Feetech FS5106R (x4)", "colore": "#2b2b2b", "componente": True,
     "via": [0, -70, 0], "copie": [[-15, -90, -275], [-15, -90, -170], [110, -90, -275], [110, -90, -170]],
     "dove": "Sotto il robot, uno per ruota, nelle culle sotto la piastra dei servo (foto 'sotto'). Posizione indicativa.",
     "porta": "Servo a rotazione continua: si comanda la velocità, non l'angolo. Datasheet: 40,8 x 20,1 x 38 mm, 4,8-6 V.",
     "codice": "PCA9685 0x41, canali 15 e 4 (sinistra), 0 e 11 (destra). Sterzo(velocita, sterzo) in ViennaClsRobot.py."},
    {"file": "componenti/LiPo_Zeee_3S_2200.stl", "nome": "Batteria LiPo Zeee 3S 2200 mAh 50C", "colore": "#c9a227", "componente": True,
     "via": [0, -70, 0], "copie": [[45, -41, -222]],
     "dove": "Livello 1, sulla piastra dei servo (dal prof). Si toglie per caricarla.",
     "porta": "11,1 V nominali (12,6 V carica), 24,4 Wh. Misure indicative (circa 106 x 34 x 25 mm): da misurare.",
     "codice": "Il Raspberry registra sottotensione e 5 V nella scatola nera (campo pi, ViennaMonitor.py)."},
    {"file": "componenti/Buck_DCDC.stl", "nome": "Convertitori buck DC-DC (x3)", "colore": "#2f6fd6", "componente": True,
     "via": [0, -70, 0], "copie": [[124, -41, -272], [124, -41, -222], [124, -41, -172]],
     "dove": "Livello 1, sulla piastra dei servo, accanto alla batteria (dal prof).",
     "porta": "Abbassano gli 11,1 V della batteria. Modello disegnato come i comuni LM2596 (43 x 21 mm, scheda blu con bobina): da confermare, come le tensioni.",
     "codice": "Nessuna riga di codice: è alimentazione. Un buck che non ce la fa si vede nel campo pi della scatola nera."},
    {"file": "componenti/PCA9685_16canali.stl", "nome": "Schede PCA9685 a 16 canali (x2)", "colore": "#5b3fa0", "componente": True,
     "via": [0, 0, 0], "copie": [[30, 4, -262], [30, 4, -230]],
     "dove": "Livello 2, sulla base della logica (dal prof).",
     "porta": "Generano gli impulsi dei servo. Formato Adafruit: 62,5 x 25,4 mm, 16 connettori a 3 pin.",
     "codice": "0x41 = le 4 ruote; 0x40 = braccio (canale 4) e pinza (canale 11). _set_pwm in ViennaClsRobot.py."},
    {"file": "componenti/Arduino_Nano.stl", "nome": "Arduino Nano", "colore": "#1a8f9a", "componente": True,
     "via": [0, 0, 0], "copie": [[100, 4, -200]],
     "dove": "Livello 2, sulla base della logica, insieme alle due PCA9685 (dal prof).",
     "porta": "Legge i 3 laser VL53L1X, il giroscopio BNO055 e gli switch; 45 x 18 mm.",
     "codice": "USB a 230400 baud, 10 numeri per riga: _arduino_reader in ViennaClsRobot.py."},
    {"file": "componenti/Raspberry_Pi_5.stl", "nome": "Raspberry Pi 5", "colore": "#3f9e4d", "componente": True,
     "via": [0, 75, 0], "copie": [[70, 41, -222]],
     "dove": "Livello 3, in cima, sulla copertura alta (dal prof).",
     "porta": "Il cervello: esegue RwdFoto.py, le reti YOLO, la scatola nera. 85 x 56 mm.",
     "codice": "RwdFoto.py (programma di gara); avvio da ~/ClaudeRob_GARA/avvia.sh."},
    {"file": "componenti/Rele_2_canali.stl", "nome": "Scheda a 2 relè (luci)", "colore": "#1f5fbf", "componente": True,
     "via": [0, 75, 0], "copie": [[-5, 41, -222]],
     "dove": "Livello 3, insieme al Raspberry (dal prof).",
     "porta": "Accende e spegne le 2 strisce LED (5 V) delle camere. Circa 50 x 38 mm.",
     "codice": "GPIO 22 e 23 (PIN_LUCI, lgpio, FIX 50): GetOnLed1/2, GetOffLed1/2 in ViennaClsRobot.py."},
    {"file": "componenti/Servo_DM996.stl", "nome": "Servo del braccio DM996 all metal", "colore": "#3a3a3a", "componente": True,
     "via": [-120, 120, 0], "copie": [[-30, -25, -170]],
     "dove": "Sul davanti, a sinistra: la sua squadretta muove il disco del braccio. Posizione indicativa.",
     "porta": "Servo di posizione con ingranaggi in metallo (formato MG996R): 40,7 x 19,7 x 42,9 mm.",
     "codice": "PCA9685 0x40 canale 4: Braccio(angolo)."},
]


# Componenti veri del robot che non hanno ancora un file 3D: nella pagina compaiono nell'elenco, in grigio.
# Quando arriva il loro STL, spostarli in PEZZI (con colore e "via").
SENZA_MODELLO = [
    {"nome": "Pinza e il suo servo", "nota": "PCA9685 0x40 canale 11 · STL in arrivo"},
    {"nome": "2 camere (linea verso il basso, arena inclinata)", "nota": "Picamera2(0) e Picamera2(1)"},
    {"nome": "3 laser VL53L1X, giroscopio BNO055, switch", "nota": "collegati all'Arduino Nano"},
    {"nome": "2 strisce LED COB 5 V", "nota": "comandate dalla scheda a 2 relè (GPIO 22 e 23)"},
]


def ultima_versione():
    c = [p for p in glob.glob(os.path.join(RADICE, "ClaudeRob_V*")) if os.path.isdir(os.path.join(p, "cruscotto"))]
    return max(c, key=lambda p: int(re.findall(r"\d+", os.path.basename(p))[-1])) if c else None


def misure(dati):
    n = struct.unpack("<I", dati[80:84])[0]
    if len(dati) != 84 + n * 50:
        sys.exit("STL non binario o rovinato: questa pagina legge solo STL binari")
    xs, ys, zs = [], [], []
    for i in range(n):
        v = struct.unpack_from("<9f", dati, 84 + i * 50 + 12)
        xs += v[0::3]; ys += v[1::3]; zs += v[2::3]
    return n, [round(max(xs) - min(xs)), round(max(ys) - min(ys)), round(max(zs) - min(zs))]


def main():
    ver = ultima_versione()
    if not ver:
        sys.exit("Non trovo nessuna ClaudeRob_V<n>/cruscotto con three.js")
    libs = ""
    for nome in ("three.min.js", "OrbitControls.js", "STLLoader.js"):
        js = open(os.path.join(ver, "cruscotto", nome), encoding="utf-8").read()
        libs += "<script>\n" + js.replace("</script", "<\\/script") + "\n</script>\n"
    pezzi = []
    for p in PEZZI:
        dati = open(os.path.join(STL, p["file"]), "rb").read()
        n, ingombro = misure(dati)
        pezzi.append(dict(p, triangoli=n, ingombro=ingombro, stl=base64.b64encode(dati).decode()))
    html = PAGINA.replace("/*LIBRERIE*/", libs).replace("/*PEZZI*/", json.dumps(pezzi, ensure_ascii=False)) \
                 .replace("/*SENZA*/", json.dumps(SENZA_MODELLO, ensure_ascii=False)) \
                 .replace("/*VERSIONE*/", os.path.basename(ver))
    open(USCITA, "w", encoding="utf-8").write(html)
    print(f"FATTO: {os.path.relpath(USCITA, RADICE)} ({len(html) // 1024} KB, {len(pezzi)} pezzi, three.js da {os.path.basename(ver)})")


PAGINA = r"""<!DOCTYPE html>
<html lang="it">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>RoboCassano esploso</title>
<style>
  :root { --sfondo:#0f1720; --pannello:#17212c; --testo:#e6edf3; --tenue:#93a4b5; --bordo:#2a3846; --accento:#3fb68b; }
  @media (prefers-color-scheme: light) {
    :root { --sfondo:#eef2f6; --pannello:#ffffff; --testo:#14202b; --tenue:#566575; --bordo:#d5dde5; --accento:#1f8a70; }
  }
  * { box-sizing:border-box; }
  body { margin:0; font:15px/1.45 system-ui, -apple-system, "Segoe UI", sans-serif; background:var(--sfondo); color:var(--testo);
         display:grid; grid-template-columns:1fr 340px; height:100vh; }
  #scena { position:relative; min-height:0; }
  #scena canvas { display:block; width:100%; height:100%; }
  #barra { position:absolute; left:16px; right:16px; bottom:16px; background:var(--pannello); border:1px solid var(--bordo);
           border-radius:10px; padding:10px 14px; display:flex; gap:12px; align-items:center; flex-wrap:wrap; }
  #barra label { font-weight:600; }
  #smonta { flex:1; min-width:140px; accent-color:var(--accento); }
  button { font:inherit; padding:6px 12px; border-radius:8px; border:1px solid var(--bordo); background:var(--sfondo);
           color:var(--testo); cursor:pointer; }
  button:hover { border-color:var(--accento); }
  aside { background:var(--pannello); border-left:1px solid var(--bordo); padding:18px; overflow:auto; }
  h1 { font-size:20px; margin:0 0 2px; }
  .sotto { color:var(--tenue); font-size:13px; margin:0 0 14px; }
  ul { list-style:none; padding:0; margin:0 0 16px; }
  li { display:flex; align-items:center; gap:8px; padding:6px 8px; border-radius:8px; cursor:pointer; }
  li:hover, li.scelto { background:var(--sfondo); }
  li input { accent-color:var(--accento); }
  #mancanti li { cursor:default; color:var(--tenue); display:block; padding:4px 8px; }
  #mancanti li small { display:block; font-size:12px; }
  .pallino { width:12px; height:12px; border-radius:3px; flex:none; }
  #scheda { border-top:1px solid var(--bordo); padding-top:12px; }
  #scheda h2 { font-size:16px; margin:0 0 8px; }
  #scheda dt { color:var(--tenue); font-size:12px; text-transform:uppercase; letter-spacing:.04em; margin-top:10px; }
  #scheda dd { margin:2px 0 0; }
  .nota { color:var(--tenue); font-size:12px; margin-top:14px; }
  @media (max-width: 760px) { body { grid-template-columns:1fr; grid-template-rows:60vh auto; height:auto; }
                              aside { border-left:0; border-top:1px solid var(--bordo); } }
</style>
</head>
<body>
<div id="scena">
  <div id="barra">
    <label for="smonta">Smonta</label>
    <input id="smonta" type="range" min="0" max="1" step="0.01" value="0">
    <button id="tutto">Smonta tutto</button>
    <button id="rimonta">Rimonta</button>
    <span id="rigaBraccio" style="display:flex;gap:8px;align-items:center;flex:1;min-width:200px">
      <label for="braccio">Braccio</label><small>giù</small>
      <input id="braccio" type="range" step="1" style="flex:1;accent-color:#22a6b3"><small>su</small>
    </span>
  </div>
</div>
<aside>
  <h1>RoboCassano</h1>
  <p class="sotto">L'esploso del robot: i pezzi stampati in 3D e i componenti, ognuno al suo livello (millimetri). Trascina per girare, rotella per lo zoom,
     clic su un pezzo per la sua scheda.</p>
  <ul id="elenco"></ul>
  <p class="sotto" style="margin:0 0 6px"><b>Senza modello 3D</b> (ancora da aggiungere):</p>
  <ul id="mancanti"></ul>
  <div id="scheda"><p class="sotto">Scegli un pezzo dall'elenco o cliccalo nel modello.</p></div>
  <p class="nota">Cosa porta ogni pezzo è dedotto dal nome del file: da confermare con la squadra. Le misure vengono dai file STL.
     Pagina costruita con .claude/skills/anatomia/costruisci_esploso.py (three.js da /*VERSIONE*/).</p>
</aside>
/*LIBRERIE*/
<script>
const PEZZI = /*PEZZI*/;
const SENZA = /*SENZA*/;
SENZA.forEach((c) => {
  const li = document.createElement("li");
  li.innerHTML = `⬚ ${c.nome}<small>${c.nota}</small>`;
  document.getElementById("mancanti").appendChild(li);
});
const scena = document.getElementById("scena");
const rend = new THREE.WebGLRenderer({ antialias: true, alpha: true });
rend.setPixelRatio(window.devicePixelRatio || 1);
scena.prepend(rend.domElement);
const scene = new THREE.Scene();
const cam = new THREE.PerspectiveCamera(40, 1, 1, 5000);
const ctrl = new THREE.OrbitControls(cam, rend.domElement);
ctrl.enableDamping = true;
scene.add(new THREE.HemisphereLight(0xffffff, 0x445566, 0.9));
const sole = new THREE.DirectionalLight(0xffffff, 0.8); sole.position.set(-200, 400, 300); scene.add(sole);

const loader = new THREE.STLLoader();
const gruppo = new THREE.Group(); scene.add(gruppo);
const oggetti = [];
const portaPezzi = [];
const copie = [];
const box = new THREE.Box3();
PEZZI.forEach((p, i) => {
  const bin = Uint8Array.from(atob(p.stl), (c) => c.charCodeAt(0)).buffer;
  const geo = loader.parse(bin);
  if (p.posa) {   // pezzo non nelle coordinate di montaggio: il suo perno va nell'origine, poi lo muove un "porta-pezzo"
    const a = p.posa.perno_stl;
    geo.translate(-a[0], -a[1], -a[2]);
  }
  geo.computeVertexNormals();
  const mat = new THREE.MeshStandardMaterial({ color: p.colore, roughness: 0.6, metalness: 0.05 });
  if (p.copie) {    // componente: una o più copie, si smontano insieme al loro livello ("via")
    p.copie.forEach((c) => {
      const m = new THREE.Mesh(geo, mat); m.userData.i = i; m.userData.base = new THREE.Vector3(...c);
      m.position.copy(m.userData.base);
      gruppo.add(m); oggetti.push(m); copie.push(m); box.union(new THREE.Box3().setFromObject(m));
    });
    return;
  }
  const mesh = new THREE.Mesh(geo, mat); mesh.userData.i = i;
  oggetti.push(mesh);
  if (p.posa) {
    const porta = new THREE.Group(); porta.add(mesh); gruppo.add(porta);
    porta.userData.base = new THREE.Vector3(...p.posa.perno);
    porta.position.copy(porta.userData.base); porta.rotation.z = THREE.MathUtils.degToRad(p.posa.alzato_gradi || 0);
    porta.updateMatrixWorld(true); portaPezzi[i] = porta;
    box.union(new THREE.Box3().setFromObject(porta));
  } else {
    gruppo.add(mesh); portaPezzi[i] = mesh;
    geo.computeBoundingBox(); box.union(geo.boundingBox);
  }
});
const centro = box.getCenter(new THREE.Vector3());
gruppo.position.copy(centro).multiplyScalar(-1);
// la telecamera inquadra anche il robot smontato del tutto
const tutto = box.clone();
PEZZI.forEach((p) => { tutto.expandByVector(new THREE.Vector3(Math.abs(p.via[0]), Math.abs(p.via[1]), Math.abs(p.via[2]))); });
const raggio = tutto.getSize(new THREE.Vector3()).length() / 2;
const dist = raggio / Math.sin(THREE.MathUtils.degToRad(cam.fov / 2)) * 0.4;
const mira = tutto.getCenter(new THREE.Vector3()).sub(centro).multiplyScalar(0.5);
const dir = new THREE.Vector3(-0.75, 0.5, 0.75).normalize();
cam.position.copy(mira.clone().add(dir.multiplyScalar(dist)));
ctrl.target.copy(mira); ctrl.update();

let t = 0, meta = 0;
const iBraccio = PEZZI.findIndex((p) => p.posa);
const portaBraccio = iBraccio >= 0 ? portaPezzi[iBraccio] : null;
const alzato = iBraccio >= 0 ? (PEZZI[iBraccio].posa.alzato_gradi || 0) : 0;
let angolo = alzato, metaAngolo = alzato;
const cursBraccio = document.getElementById("braccio");
// il cursore va da 0 (giù, come è disegnato lo STL) a |alzato_gradi| (su); il verso della rotazione è il segno di alzato_gradi
if (portaBraccio) { cursBraccio.min = 0; cursBraccio.max = Math.abs(alzato); cursBraccio.value = Math.abs(alzato);
  cursBraccio.oninput = () => { metaAngolo = Math.sign(alzato) * +cursBraccio.value; }; }
else document.getElementById("rigaBraccio").style.display = "none";
const cursore = document.getElementById("smonta");
cursore.oninput = () => { meta = +cursore.value; };
document.getElementById("tutto").onclick = () => { meta = 1; cursore.value = 1; };
document.getElementById("rimonta").onclick = () => { meta = 0; cursore.value = 0; };

const elenco = document.getElementById("elenco");
PEZZI.forEach((p, i) => {
  if (p.componente && !PEZZI.slice(0, i).some((q) => q.componente)) {
    const t = document.createElement("p"); t.className = "sotto"; t.style.margin = "10px 0 4px";
    t.innerHTML = "<b>Componenti</b> (modelli semplificati, al loro livello):"; elenco.appendChild(t);
  }
  const li = document.createElement("li");
  li.innerHTML = `<input type="checkbox" checked title="mostra o nascondi"><span class="pallino" style="background:${p.colore}"></span><span>${p.nome}</span>`;
  li.querySelector("input").onclick = (e) => { e.stopPropagation(); oggetti.forEach((m) => { if (m.userData.i === i) m.visible = e.target.checked; }); };
  li.onclick = () => scegli(i);
  elenco.appendChild(li);
});

let scelto = -1;
function scegli(i) {
  scelto = i;
  [...elenco.querySelectorAll("li")].forEach((li, k) => li.classList.toggle("scelto", k === i));
  oggetti.forEach((m) => { m.material.emissive.setHex(m.userData.i === i ? 0x333333 : 0x000000); });
  const p = PEZZI[i];
  document.getElementById("scheda").innerHTML = `<h2>${p.nome}</h2><dl>
    <dt>File</dt><dd><code>Meccanica_STL/${p.file}</code></dd>
    <dt>Ingombro</dt><dd>${p.ingombro.join(" × ")} mm · ${p.triangoli} triangoli</dd>
    <dt>Dove sta</dt><dd>${p.dove}</dd>
    <dt>${p.componente ? "Cos'è (modello semplificato)" : "Cosa porta (da confermare)"}</dt><dd>${p.porta}</dd>
    <dt>Nel codice</dt><dd>${p.codice}</dd></dl>`;
}

const ray = new THREE.Raycaster(), mouse = new THREE.Vector2();
let giu = null;
rend.domElement.addEventListener("pointerdown", (e) => { giu = [e.clientX, e.clientY]; });
rend.domElement.addEventListener("pointerup", (e) => {
  if (!giu || Math.hypot(e.clientX - giu[0], e.clientY - giu[1]) > 5) return;
  const r = rend.domElement.getBoundingClientRect();
  mouse.set(((e.clientX - r.left) / r.width) * 2 - 1, -((e.clientY - r.top) / r.height) * 2 + 1);
  ray.setFromCamera(mouse, cam);
  const colpi = ray.intersectObjects(oggetti.filter((m) => m.visible));
  if (colpi.length) scegli(colpi[0].object.userData.i);
});

function misura() {
  const w = scena.clientWidth, h = scena.clientHeight;
  rend.setSize(w, h, false); cam.aspect = w / h; cam.updateProjectionMatrix();
}
window.addEventListener("resize", misura); misura();

(function giro() {
  t += (meta - t) * 0.12;
  const e = t * t * (3 - 2 * t);
  portaPezzi.forEach((m, i) => {
    if (!m) return;
    const v = PEZZI[i].via, b = m.userData.base;
    m.position.set(v[0] * e, v[1] * e, v[2] * e);
    if (b) m.position.add(b);
  });
  copie.forEach((m) => {
    const v = PEZZI[m.userData.i].via;
    m.position.set(v[0] * e, v[1] * e, v[2] * e).add(m.userData.base);
  });
  angolo += (metaAngolo - angolo) * 0.12;
  if (portaBraccio) portaBraccio.rotation.z = THREE.MathUtils.degToRad(angolo);
  ctrl.update(); rend.render(scene, cam); requestAnimationFrame(giro);
})();
</script>
</body>
</html>
"""

if __name__ == "__main__":
    main()
