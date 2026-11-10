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
     "codice": "Braccio: PCA9685 0x40 canale 4; pinza: canale 11. Camera linea: Picamera2(0), 440x260, YOLO Cross3."},
    {"file": "CupolaWebArenaLED.stl", "nome": "Cupola della camera arena e delle luci", "colore": "#d64f6a",
     "via": [-150, 45, 0], "dove": "Sul muso, in alto: un pannello sottile.",
     "porta": "La camera che guarda l'arena e le luci LED.",
     "codice": "Camera arena: Picamera2(1), 440x260, YOLO PalCol3 / TrianFull3 / Exit3. Luci: GPIO 22 e 23."},
]


# Componenti veri del robot che non hanno ancora un file 3D: nella pagina compaiono nell'elenco, in grigio.
# Quando arriva il loro STL, spostarli in PEZZI (con colore e "via").
SENZA_MODELLO = [
    {"nome": "4 servo a rotazione continua (uno per ruota)", "nota": "PCA9685 0x41, canali 15, 4, 0, 11 · Sterzo() in ViennaClsRobot.py"},
    {"nome": "Batteria LiPo 3S 11,1 V", "nota": "nominale 11,1 V, carica 12,6 V · posizione e capacità da confermare"},
    {"nome": "Schede buck DC-DC", "nota": "abbassano la tensione della batteria per Raspberry e servo · quante e quali tensioni: da confermare"},
    {"nome": "Arduino Nano", "nota": "3 laser, giroscopio, switch · USB 230400 baud · posizione da confermare"},
    {"nome": "Braccio", "nota": "PCA9685 0x40 canale 4 · STL in arrivo"},
    {"nome": "Pinza", "nota": "PCA9685 0x40 canale 11 · STL in arrivo"},
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
  </div>
</div>
<aside>
  <h1>RoboCassano</h1>
  <p class="sotto">L'esploso del robot: 5 pezzi stampati in 3D (millimetri). Trascina per girare, rotella per lo zoom,
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
const box = new THREE.Box3();
PEZZI.forEach((p, i) => {
  const bin = Uint8Array.from(atob(p.stl), (c) => c.charCodeAt(0)).buffer;
  const geo = loader.parse(bin); geo.computeVertexNormals();
  const mat = new THREE.MeshStandardMaterial({ color: p.colore, roughness: 0.6, metalness: 0.05 });
  const mesh = new THREE.Mesh(geo, mat); mesh.userData.i = i;
  gruppo.add(mesh); oggetti.push(mesh);
  geo.computeBoundingBox(); box.union(geo.boundingBox);
});
const centro = box.getCenter(new THREE.Vector3());
gruppo.position.copy(centro).multiplyScalar(-1);
// la telecamera inquadra anche il robot smontato del tutto
const tutto = box.clone();
PEZZI.forEach((p) => { tutto.expandByVector(new THREE.Vector3(Math.abs(p.via[0]), Math.abs(p.via[1]), Math.abs(p.via[2]))); });
const raggio = tutto.getSize(new THREE.Vector3()).length() / 2;
const dist = raggio / Math.sin(THREE.MathUtils.degToRad(cam.fov / 2)) * 0.55;
const mira = tutto.getCenter(new THREE.Vector3()).sub(centro).multiplyScalar(0.5);
const dir = new THREE.Vector3(-0.75, 0.5, 0.75).normalize();
cam.position.copy(mira.clone().add(dir.multiplyScalar(dist)));
ctrl.target.copy(mira); ctrl.update();

let t = 0, meta = 0;
const cursore = document.getElementById("smonta");
cursore.oninput = () => { meta = +cursore.value; };
document.getElementById("tutto").onclick = () => { meta = 1; cursore.value = 1; };
document.getElementById("rimonta").onclick = () => { meta = 0; cursore.value = 0; };

const elenco = document.getElementById("elenco");
PEZZI.forEach((p, i) => {
  const li = document.createElement("li");
  li.innerHTML = `<input type="checkbox" checked title="mostra o nascondi"><span class="pallino" style="background:${p.colore}"></span><span>${p.nome}</span>`;
  li.querySelector("input").onclick = (e) => { e.stopPropagation(); oggetti[i].visible = e.target.checked; };
  li.onclick = () => scegli(i);
  elenco.appendChild(li);
});

let scelto = -1;
function scegli(i) {
  scelto = i;
  [...elenco.children].forEach((li, k) => li.classList.toggle("scelto", k === i));
  oggetti.forEach((m, k) => { m.material.emissive.setHex(k === i ? 0x333333 : 0x000000); m.material.opacity = 1; });
  const p = PEZZI[i];
  document.getElementById("scheda").innerHTML = `<h2>${p.nome}</h2><dl>
    <dt>File</dt><dd><code>Meccanica_STL/${p.file}</code></dd>
    <dt>Ingombro</dt><dd>${p.ingombro.join(" × ")} mm · ${p.triangoli} triangoli</dd>
    <dt>Dove sta</dt><dd>${p.dove}</dd>
    <dt>Cosa porta (da confermare)</dt><dd>${p.porta}</dd>
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
  oggetti.forEach((m, i) => { const v = PEZZI[i].via; m.position.set(v[0] * e, v[1] * e, v[2] * e); });
  ctrl.update(); rend.render(scene, cam); requestAnimationFrame(giro);
})();
</script>
</body>
</html>
"""

if __name__ == "__main__":
    main()
