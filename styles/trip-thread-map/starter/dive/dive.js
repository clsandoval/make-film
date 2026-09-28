// The pin dive, as an offline module: WebGL terrain built from GEO.H (the same heightfield the map is shaded from).
// The camera starts top-down at the map's own scale and heading (north up), so the crossfade from map to 3D is
// seamless, then tilts and settles behind the place looking at it. Everything is a pure function of (seg, u).
// Want real terrain? Replace buildMesh() with heights from a DEM you are licensed to use, or swap this module
// for a CesiumJS / 3D Tiles renderer (network, an API key and the provider's attribution rules apply).
(function () {
  const G = window.GEO, PAL = window.FILM.brand.palette, FOV = 50 * Math.PI / 180, SIZE = 1800, GRID = 200;
  const hex = c => { const n = parseInt(c.slice(1), 16); return [(n >> 16 & 255) / 255, (n >> 8 & 255) / 255, (n & 255) / 255]; };
  const VS = `attribute vec4 a_p;attribute vec3 a_n;uniform mat4 u_m;varying vec3 v_p;varying vec3 v_n;varying float v_w;
void main(){v_p=a_p.xyz;v_n=a_n;v_w=a_p.w;gl_Position=u_m*vec4(a_p.xyz,1.0);}`;
  const FS = `precision highp float;varying vec3 v_p;varying vec3 v_n;varying float v_w;
uniform vec3 u_eye,u_sun,u_fog,u_c0,u_c1,u_c2,u_c3,u_wat;uniform float u_hz,u_tod,u_near,u_far,u_sn;
float tx(vec2 p){return .5+.25*sin(p.x*.37)*sin(p.y*.41)+.25*sin(p.x*.093+p.y*.071);}
void main(){vec3 n=normalize(v_n);float h=v_p.y/u_hz;float sl=1.0-n.y;
 vec3 c=mix(u_c0,u_c1,smoothstep(-.1,.35,h));
 c*=.82+.3*tx(v_p.xz);
 c=mix(c,u_c2,clamp(smoothstep(.22,.45,sl)+smoothstep(.45,.62,h)*.6,0.0,1.0));
 float snow=smoothstep(u_sn,u_sn+.1,h+.06*tx(v_p.xz*.5))*(1.0-smoothstep(.5,.7,sl));
 c=mix(c,u_c3,snow);
 float dif=max(dot(n,u_sun),0.0);
 c*=.36+.8*dif;
 if(v_w>.5){c=u_wat*(.7+.3*dif);}
 c=mix(c,c*vec3(.22,.27,.45)+vec3(.02,.03,.06),u_tod);
 float d=distance(v_p,u_eye);
 c=mix(c,u_fog,smoothstep(u_near,u_far,d));
 gl_FragColor=vec4(c,1.0);}`;
  let gl = null, prog, L = {}, isGL2 = false; const meshes = {};
  function init(canvas) {
    const o = { preserveDrawingBuffer: true, antialias: true, alpha: false };
    gl = canvas.getContext('webgl2', o); isGL2 = !!gl;
    if (!gl) { gl = canvas.getContext('webgl', o); if (gl && !gl.getExtension('OES_element_index_uint')) gl = null; }
    if (!gl) return false;
    const sh = (t, s) => { const x = gl.createShader(t); gl.shaderSource(x, s); gl.compileShader(x);
      if (!gl.getShaderParameter(x, gl.COMPILE_STATUS)) throw new Error('dive shader: ' + gl.getShaderInfoLog(x)); return x; };
    prog = gl.createProgram(); gl.attachShader(prog, sh(gl.VERTEX_SHADER, VS)); gl.attachShader(prog, sh(gl.FRAGMENT_SHADER, FS)); gl.linkProgram(prog);
    gl.useProgram(prog);
    ['a_p', 'a_n'].forEach(k => L[k] = gl.getAttribLocation(prog, k));
    ['u_m', 'u_eye', 'u_sun', 'u_fog', 'u_c0', 'u_c1', 'u_c2', 'u_c3', 'u_wat', 'u_hz', 'u_tod', 'u_near', 'u_far', 'u_sn'].forEach(k => L[k] = gl.getUniformLocation(prog, k));
    gl.enable(gl.DEPTH_TEST); return true;
  }
  function buildMesh(id) {
    if (meshes[id]) return meshes[id];
    const p = G.P[id], n = GRID + 1, st = SIZE / GRID, x0 = p.x - SIZE / 2, z0 = p.y - SIZE / 2;
    const hy = new Float32Array(n * n), w = new Uint8Array(n * n);
    for (let j = 0; j < n; j++) for (let i = 0; i < n; i++) { const x = x0 + i * st, z = z0 + j * st, k = j * n + i;
      if (G.lake(x, z) > .5) { hy[k] = G.WATER * G.HZ; w[k] = 1; } else hy[k] = Math.max(G.H(x, z), G.WATER + .01) * G.HZ; }
    const pos = new Float32Array(n * n * 4), nor = new Float32Array(n * n * 3);
    for (let j = 0; j < n; j++) for (let i = 0; i < n; i++) { const k = j * n + i;
      pos.set([x0 + i * st, hy[k], z0 + j * st, w[k]], k * 4);
      const hl = hy[j * n + Math.max(0, i - 1)], hr = hy[j * n + Math.min(n - 1, i + 1)], hu = hy[Math.max(0, j - 1) * n + i], hd = hy[Math.min(n - 1, j + 1) * n + i];
      const nx = (hl - hr) / (2 * st), nz = (hu - hd) / (2 * st), l = Math.hypot(nx, 1, nz); nor.set([nx / l, 1 / l, nz / l], k * 3); }
    const idx = new Uint32Array(GRID * GRID * 6); let q = 0;
    for (let j = 0; j < GRID; j++) for (let i = 0; i < GRID; i++) { const a = j * n + i, b = a + 1, c = a + n, d = c + 1; idx.set([a, c, b, b, c, d], q); q += 6; }
    const mk = (t, d) => { const b = gl.createBuffer(); gl.bindBuffer(t, b); gl.bufferData(t, d, gl.STATIC_DRAW); return b; };
    return meshes[id] = { p: mk(gl.ARRAY_BUFFER, pos), n: mk(gl.ARRAY_BUFFER, nor), i: mk(gl.ELEMENT_ARRAY_BUFFER, idx), count: idx.length };
  }
  const lerp = (a, b, k) => a + (b - a) * k, cl = k => Math.min(1, Math.max(0, k)), eIO = k => k < .5 ? 4 * k * k * k : 1 - Math.pow(-2 * k + 2, 3) / 2;
  // u: 0 -> 1 over the dive, keeps growing (slowly drifting camera) under the landing card. s0/x0/y0: the map camera at dive start.
  function camera(seg, u, s0, x0, y0) {
    const p = G.P[seg.place], e = eIO(cl(u)), tp = cl((e - .15) / .85), pe = tp * tp * (3 - 2 * tp), ex = Math.max(0, u - 1);
    const TY = p.kind === 'lake' ? G.WATER * G.HZ : Math.max(G.H(p.x, p.y), G.WATER) * G.HZ * .75;
    const hd = (lerp(0, seg.heading || 0, pe) + 10 * ex) * Math.PI / 180;
    const D = (seg.dist || 720) * pe - 40 * ex;
    const cx = p.x + (x0 - p.x) * (1 - e) - Math.sin(hd) * D, cz = p.y + (y0 - p.y) * (1 - e) + Math.cos(hd) * D;
    const A0 = 960 / (s0 * Math.tan(FOV / 2));
    const ground = Math.max(G.H(cx, cz), G.WATER) * G.HZ;
    const A1 = Math.max(TY + (seg.alt || 300), ground + 90);
    const ey = Math.max(Math.exp(lerp(Math.log(A0), Math.log(A1), e)), ground + 60);
    const pit = -Math.atan2(ey - TY, Math.max(D, 1e-3));
    const f = [Math.sin(hd) * Math.cos(pit), Math.sin(pit), -Math.cos(hd) * Math.cos(pit)], r = [Math.cos(hd), 0, Math.sin(hd)];
    const up = [r[1] * f[2] - r[2] * f[1], r[2] * f[0] - r[0] * f[2], r[0] * f[1] - r[1] * f[0]];
    return { eye: [cx, ey, cz], f, r, up };
  }
  function draw(seg, u, s0, x0, y0, tod) {
    if (!gl) return;
    const W = gl.canvas.width, Hh = gl.canvas.height, c = camera(seg, u, s0, x0, y0), e = c.eye, near = 4, far = 8000, fy = 1 / Math.tan(FOV / 2), a = W / Hh;
    const dot = (v, w) => v[0] * w[0] + v[1] * w[1] + v[2] * w[2];
    const V = [c.r[0], c.up[0], -c.f[0], 0, c.r[1], c.up[1], -c.f[1], 0, c.r[2], c.up[2], -c.f[2], 0, -dot(c.r, e), -dot(c.up, e), dot(c.f, e), 1];
    const Pm = [fy / a, 0, 0, 0, 0, fy, 0, 0, 0, 0, (far + near) / (near - far), -1, 0, 0, 2 * far * near / (near - far), 0];
    const M = new Float32Array(16); for (let i = 0; i < 4; i++) for (let j = 0; j < 4; j++) { let s = 0; for (let k = 0; k < 4; k++) s += Pm[k * 4 + j] * V[i * 4 + k]; M[i * 4 + j] = s; }
    const sky = hex(PAL.sky || '#9FB7C4'), night = [.04, .06, .12], fog = sky.map((v, i) => lerp(v, night[i], tod));
    gl.viewport(0, 0, W, Hh); gl.clearColor(fog[0], fog[1], fog[2], 1); gl.clear(gl.COLOR_BUFFER_BIT | gl.DEPTH_BUFFER_BIT);
    const m = buildMesh(seg.place), T = PAL.terrain || ['#3F5B37', '#2C4630', '#77746A', '#EEF2F1'];
    gl.uniformMatrix4fv(L.u_m, false, M); gl.uniform3fv(L.u_eye, e); const sl = Math.hypot(-.5, .7, -.5); gl.uniform3fv(L.u_sun, [-.5 / sl, .7 / sl, -.5 / sl]);
    gl.uniform3fv(L.u_fog, fog); ['u_c0', 'u_c1', 'u_c2', 'u_c3'].forEach((k, i) => gl.uniform3fv(L[k], hex(T[i])));
    gl.uniform3fv(L.u_wat, hex(PAL.water || '#2E6A86')); gl.uniform1f(L.u_hz, G.HZ); gl.uniform1f(L.u_tod, tod);
    gl.uniform1f(L.u_sn, G.SNOW); const fn = Math.max(650, e[1] * 1.15); gl.uniform1f(L.u_near, fn); gl.uniform1f(L.u_far, fn + 1250);   // fog scales with altitude so the top-down start stays clear
    gl.bindBuffer(gl.ARRAY_BUFFER, m.p); gl.enableVertexAttribArray(L.a_p); gl.vertexAttribPointer(L.a_p, 4, gl.FLOAT, false, 0, 0);
    gl.bindBuffer(gl.ARRAY_BUFFER, m.n); gl.enableVertexAttribArray(L.a_n); gl.vertexAttribPointer(L.a_n, 3, gl.FLOAT, false, 0, 0);
    gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER, m.i); gl.drawElements(gl.TRIANGLES, m.count, gl.UNSIGNED_INT, 0);
  }
  window.DIVE = { init, draw, buildMesh, camera, get ok() { return !!gl; } };
})();
