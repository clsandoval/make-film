// Seek-driven composition contract shared by every clip: window.__seek / __duration / __ready.
// opts.step quantizes film time (1/12 = animation "on twos") for styles whose motion should snap.
window.mk = (build, dur, opts = {}) => {
  gsap.ticker.remove(gsap.updateRoot);
  const tl = gsap.timeline({ paused: true });
  build(tl);
  tl.set({}, {}, dur);
  const step = opts.step;
  window.__seek = (t) => { if (step) t = Math.floor(t / step + 1e-6) * step; tl.seek(t, false); };
  window.__duration = dur;
  Promise.all([...document.images].map((i) => i.decode().catch(() => {})))
    .then(() => { window.__seek(0); window.__ready = true; });
};
