// Shared geography: projection, a synthetic heightfield and lake mask, all pure functions of trip.json.
// The map (film.html) and the 3D dive (dive/dive.js) both read this, so a dive starts exactly where the map is.
// Nothing is downloaded: the terrain is seeded noise shaped by the places (peaks raise it, lakes carve it).
(function () {
  const F = window.FILM, PL = F.places, D2R = Math.PI / 180;
  let N = -1e9, S = 1e9, Wl = 1e9, E = -1e9;
  for (const k in PL) { const p = PL[k]; N = Math.max(N, p.lat); S = Math.min(S, p.lat); E = Math.max(E, p.lng); Wl = Math.min(Wl, p.lng); }
  const pl = (N - S) * .45, pg = (E - Wl) * .45; N += pl; S -= pl; E += pg; Wl -= pg;
  const lat0 = (N + S) / 2, C0 = Math.cos(lat0 * D2R), WW = 2400, K = WW / ((E - Wl) * C0), WH = (N - S) * K;
  const KM = 111.32 / K;                         // km per world unit
  const HZ = 1.1 / KM;                           // world units per unit of height (h = 1 is about 1.1 km of relief)
  const proj = (lat, lng) => [(lng - Wl) * C0 * K, (N - lat) * K];
  const P = {}; for (const k in PL) { const [x, y] = proj(PL[k].lat, PL[k].lng); P[k] = Object.assign({ id: k, x, y }, PL[k]); }
  let SEED = 0; for (const ch of (F.brand.name || 'trip')) SEED = (SEED * 31 + ch.charCodeAt(0)) | 0;
  function hash(i, j) { let h = (Math.imul(i, 374761393) + Math.imul(j, 668265263) + Math.imul(SEED, 1442695041)) | 0;
    h = Math.imul(h ^ (h >>> 13), 1274126177); return ((h ^ (h >>> 16)) >>> 0) / 4294967296; }
  function vn(x, y) { const i = Math.floor(x), j = Math.floor(y), fx = x - i, fy = y - j, u = fx * fx * (3 - 2 * fx), v = fy * fy * (3 - 2 * fy);
    const a = hash(i, j), b = hash(i + 1, j), c = hash(i, j + 1), d = hash(i + 1, j + 1); return a + (b - a) * u + (c - a) * v + (a - b - c + d) * u * v; }
  function fbm(x, y) { let s = 0, a = .5, f = 1; for (let o = 0; o < 5; o++) { s += a * vn(x * f + o * 17.3, y * f); f *= 2.03; a *= .5; } return s; }
  const peaks = Object.values(P).filter(p => p.kind === 'peak'), lakes = Object.values(P).filter(p => p.kind === 'lake'), hub = P[F.hub];
  lakes.forEach(l => { l.rx = (l.rx_km || 1) / KM; l.ry = (l.ry_km || .7) / KM; });
  function lake(x, y) { let m = 0; for (const l of lakes) { const dx = (x - l.x) / l.rx, dy = (y - l.y) / l.ry;
      const q = (dx * dx + dy * dy) * (1 + .35 * (vn(x / 90, y / 90) - .5)); m = Math.max(m, Math.exp(-q * q)); } return m; }   // > .5 is water
  function ridged(x, y) { let s = 0, a = .5, f = 1; for (let o = 0; o < 4; o++) { const v = 1 - Math.abs(2 * vn(x * f + 40, y * f) - 1); s += a * v * v; f *= 2.1; a *= .5; } return s; }
  function H(x, y) {
    const r = fbm(x / 380, y / 380), rg = ridged(x / 170, y / 170);
    let h = (r - .48) * .7 + rg * .32 - .12;
    for (const p of peaks) { const d = Math.hypot(x - p.x, y - p.y); h += (p.amp || .8) * Math.exp(-d / 210) * (.7 + .6 * rg); }
    if (hub) { const d2 = (x - hub.x) ** 2 + (y - hub.y) ** 2; h -= .28 * Math.exp(-d2 / (2 * 520 * 520)); }
    const m = lake(x, y); if (m > 0) h = h * (1 - m) + (-.32) * m;
    return h;
  }
  const dist = (a, b) => Math.hypot(P[a].x - P[b].x, P[a].y - P[b].y);
  window.GEO = { P, proj, H, lake, fbm, vn, SNOW: .82, KM, HZ, WW, WH, dist, WATER: -.25 };
})();
