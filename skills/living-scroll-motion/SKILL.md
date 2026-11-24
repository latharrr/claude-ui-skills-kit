---
name: living-scroll-motion
description: Add immersive scroll-driven motion to any website: smooth scroll, masked text reveals, pinned scenes, colour-wipe transitions and a 3D glass-shard layer.
---

# Living Scroll Motion

A universal motion system for making any site feel "alive" on scroll (reference style: laboiteaslides.fr). It is driven by data attributes, so it drops into any stack: plain HTML, React/Next, Vue/Nuxt, Astro, Svelte or Webflow-exported code.

Stack: **Lenis** (smooth scroll) + **GSAP + ScrollTrigger + SplitText** (all free, including plugins) + **three.js** (optional 3D layer).

---

## 0. Workflow (always follow this order)

1. **Audit the target site**
   - Detect the framework, router, styling system, existing animation libraries and font loading.
   - List every section top to bottom: purpose, background (dark/light) and its main element (headline, paragraph, cards, list, media).
   - Remove or replace conflicting reveal/opacity animations (AOS, framer `whileInView`, CSS `@keyframes` fade-ins, IntersectionObserver fades).
2. **If a reference URL is given**, open it in the browser and scroll slowly, 3–4 ticks at a time with a screenshot after each. Catalogue every effect using the IDs in §2, and note the background colour sequence.
3. **Write a Motion Map** (a table) before coding: `Section | Theme/bg | Effect IDs | Tier`. Show it to the user if they are present.
4. **Choose a tier**, the user's call; default Standard:
   - **Lite:** E1–E9, E14–E16. No WebGL; CSS planet wipes.
   - **Standard:** Lite + E10 shards + E11 WebGL/CSS wipes + E12 formations.
   - **Full:** Standard + E13 thumbnail sphere + hero-moment extras.
5. **Implement in order:** core (§1) → text effects → themes/wipes → cards/lists → 3D → extras.
6. **QA** (§6): run the dev server, scroll the whole page slowly in the browser, screenshot, and fix issues.

Rules that never bend:
- Keep the site's own copy, brand and layout. Copy techniques, never another site's branding or content.
- At rest nothing may stay faded, clipped or invisible. Every reveal must reach full contrast.
- Numbers animated by counters must match every other place the same stat appears.

---

## 1. Core setup

```bash
npm i gsap lenis three
```

`motion/core.js`
```js
import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import { SplitText } from 'gsap/SplitText';
import Lenis from 'lenis';
gsap.registerPlugin(ScrollTrigger, SplitText);

export const motion = {
  velocity: 0,          // smoothed scroll velocity, shared by all effects
  reduced: matchMedia('(prefers-reduced-motion: reduce)').matches,
  mobile: matchMedia('(max-width: 768px)').matches,
  lenis: null,
};

export function initCore() {
  if (motion.reduced) return;
  const lenis = new Lenis({ lerp: 0.1, smoothWheel: true });
  lenis.on('scroll', (e) => {
    motion.velocity += (e.velocity - motion.velocity) * 0.2;
    ScrollTrigger.update();
  });
  gsap.ticker.add((t) => lenis.raf(t * 1000));
  gsap.ticker.lagSmoothing(0);
  motion.lenis = lenis;
  // decay velocity when idle + expose it to CSS
  gsap.ticker.add(() => {
    motion.velocity *= 0.92;
    document.documentElement.style.setProperty('--vel', Math.min(Math.abs(motion.velocity), 40).toFixed(2));
  });
}

export function initAll() {
  initCore();
  if (motion.reduced) return document.documentElement.classList.add('reduced');
  // call each effect initializer here (see §2)
  document.fonts.ready.then(() => ScrollTrigger.refresh());
}
```

Base CSS:
```css
html.lenis, html.lenis body { height: auto; }
.lenis.lenis-smooth { scroll-behavior: auto !important; }
:root { --bg: #fff; --fg: #111; --vel: 0; }
body { background: var(--bg); color: var(--fg); transition: background .6s, color .6s; }
.reduced * { animation: none !important; transition: none !important; }
```

---

## 2. Effect palette (data-attribute API)

Tag elements in markup; each initializer queries its attribute. In component frameworks, run initializers inside a scoped context (see §4).

### E1 Line-mask reveal: `data-reveal="lines"`
Headline lines slide up from behind a mask.
```js
export function revealLines() {
  document.querySelectorAll('[data-reveal="lines"]').forEach((el) => {
    SplitText.create(el, { type: 'lines', mask: 'lines', autoSplit: true, onSplit: (s) =>
      gsap.from(s.lines, { yPercent: 110, duration: 1.1, stagger: 0.08, ease: 'expo.out',
        scrollTrigger: { trigger: el, start: 'top 85%', once: true } }) });
  });
}
```

### E2 Pinned headline in → hold → slice out: `data-pin="headline"`
```js
export function pinHeadlines() {
  document.querySelectorAll('[data-pin="headline"]').forEach((sec) => {
    const h = sec.querySelector('h1,h2');
    SplitText.create(h, { type: 'lines', mask: 'lines', autoSplit: true, onSplit: (s) => {
      const tl = gsap.timeline({ scrollTrigger: { trigger: sec, start: 'top top', end: '+=150%', pin: true, scrub: 1 } });
      tl.from(s.lines, { yPercent: 110, stagger: 0.08 })
        .to({}, { duration: 0.6 })                       // hold
        .to(s.lines, { yPercent: -110, stagger: 0.08 });
      return tl;
    }});
  });
}
```
Accent word enters late: wrap it in `<span data-late>`, then add `tl.from('[data-late]', {yPercent:110}, '<0.15')`.

### E3 Word-fill paragraph: `data-reveal="fill"`
```js
export function wordFill() {
  document.querySelectorAll('[data-reveal="fill"]').forEach((el) => {
    const s = SplitText.create(el, { type: 'words' });
    gsap.fromTo(s.words, { opacity: 0.15 }, { opacity: 1, stagger: 0.05, ease: 'none',
      scrollTrigger: { trigger: el, start: 'top 80%', end: 'top 35%', scrub: true } });
  });
}
```
Pinned variant (`data-reveal="fill-pin"`): use `start:'top top', end:'+=120%', pin:true`.

### E4 Letter type-on giant word: `data-reveal="chars"`
Chars go from opacity 0 and x -20 to 0, with stagger 0.06 and scrub, plus a colour gradient across the chars (`gsap.utils.interpolate(colorA, colorB, i/n)`).

### E5 Section themes + adaptive header: `data-theme="dark|light" data-bg="#hex"`
```js
export function themes(onChange) {
  document.querySelectorAll('[data-theme]').forEach((sec) => ScrollTrigger.create({
    trigger: sec, start: 'top 50%', end: 'bottom 50%',
    onToggle: (s) => { if (!s.isActive) return;
      const root = document.documentElement;
      root.dataset.theme = sec.dataset.theme;
      root.style.setProperty('--bg', sec.dataset.bg);
      root.style.setProperty('--fg', sec.dataset.theme === 'dark' ? '#fff' : '#111');
      onChange?.(sec.dataset); }
  }));
}
```
The header styles itself from `[data-theme=dark] header {...}`. Over image sections use `backdrop-filter: blur(12px)` with a semi-transparent background.

### E6 Staggered card rise: `data-stagger`
Children: `y:80, rotate:2, opacity:0` → `0`, stagger 0.12, `start:'top 80%'`. Give the cards different `data-offset` values for uneven heights.

### E7 Image card clip + zoom: `data-media="clip"`
The wrapper goes `clipPath: inset(100% 0 0 0)` → `inset(0% 0 0 0)` and the inner img goes `scale 1.15` → `1`, both scrubbed.

### E8 Pinned headline + sliding card carousel: `data-carousel`
Pin the section. The card track goes `xPercent: 0 → -(trackWidth - vw)`, scrubbed, and each card gets `rotate: gsap.utils.random(-4,4)`. Cards are frosted glass: `background: rgb(255 255 255 / .08); backdrop-filter: blur(16px)`.

### E9 Active-row list (scroll spotlight): `data-active-list`
```js
rows.forEach((row, i) => ScrollTrigger.create({ trigger: row, start: 'top center', end: 'bottom center',
  toggleClass: 'is-active', onEnter: () => showPreview(i), onEnterBack: () => showPreview(i) }));
```
Rows are pale outline text by default (`-webkit-text-stroke`) and turn solid accent when active. A floating preview card follows the active row and crossfades between rows.

### E10 3D glass-shard layer (WebGL)
One fixed canvas for the whole page: `position:fixed; inset:0; z-index:-1; pointer-events:none`.
```js
import * as THREE from 'three';
import { RoomEnvironment } from 'three/examples/jsm/environments/RoomEnvironment.js';

export function createShards(canvas, { count = motion.mobile ? 20 : 50 } = {}) {
  const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true });
  renderer.setPixelRatio(Math.min(devicePixelRatio, 1.5));
  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(35, innerWidth / innerHeight, 0.1, 200);
  camera.position.z = 22;
  scene.environment = new THREE.PMREMGenerator(renderer).fromScene(new RoomEnvironment(), 0.04).texture;

  const tri = new THREE.Shape(); tri.moveTo(0, 1); tri.lineTo(-0.87, -0.5); tri.lineTo(0.87, -0.5); tri.closePath();
  const geo = new THREE.ExtrudeGeometry(tri, { depth: 0.12, bevelEnabled: true, bevelSize: 0.03, bevelThickness: 0.03, bevelSegments: 2 });
  geo.center();
  const mat = motion.mobile
    ? new THREE.MeshStandardMaterial({ color: '#8f6bff', transparent: true, opacity: 0.6, roughness: 0.2, metalness: 0.1 })
    : new THREE.MeshPhysicalMaterial({ color: '#8f6bff', transmission: 0.9, roughness: 0.12, thickness: 0.6, ior: 1.4, clearcoat: 1 });
  const mesh = new THREE.InstancedMesh(geo, mat, count);
  scene.add(mesh, new THREE.AmbientLight('#fff', 0.6));

  const seeds = Array.from({ length: count }, () => ({ phase: Math.random() * 6.28, speed: 0.3 + Math.random() * 0.7, scale: 0.6 + Math.random() * 1.4 }));
  const state = { formA: null, formB: null, mix: 0, spin: 0, mouse: { x: 0, y: 0 }, camY: 0 };
  const dummy = new THREE.Object3D();
  addEventListener('pointermove', (e) => { state.mouse.x = e.clientX / innerWidth - 0.5; state.mouse.y = e.clientY / innerHeight - 0.5; });
  addEventListener('resize', () => { camera.aspect = innerWidth / innerHeight; camera.updateProjectionMatrix(); renderer.setSize(innerWidth, innerHeight, false); });
  renderer.setSize(innerWidth, innerHeight, false);

  let visible = true; document.addEventListener('visibilitychange', () => (visible = !document.hidden));
  gsap.ticker.add((time) => {
    if (!visible || !state.formA) return;
    state.spin += motion.velocity * 0.0004;
    for (let i = 0; i < count; i++) {
      const a = state.formA[i], b = (state.formB || state.formA)[i], s = seeds[i];
      dummy.position.lerpVectors(a.p, b.p, state.mix);
      dummy.position.y += Math.sin(time * s.speed + s.phase) * 0.15;
      dummy.rotation.set(
        THREE.MathUtils.lerp(a.r.x, b.r.x, state.mix) + time * 0.1 * s.speed + state.spin,
        THREE.MathUtils.lerp(a.r.y, b.r.y, state.mix) + time * 0.15 * s.speed,
        THREE.MathUtils.lerp(a.r.z, b.r.z, state.mix));
      dummy.scale.setScalar(THREE.MathUtils.lerp(a.s ?? s.scale, b.s ?? s.scale, state.mix));
      dummy.updateMatrix(); mesh.setMatrixAt(i, dummy.matrix);
    }
    mesh.instanceMatrix.needsUpdate = true;
    camera.position.x += (state.mouse.x * 0.6 - camera.position.x) * 0.05;
    camera.position.y += (-state.mouse.y * 0.6 + state.camY - camera.position.y) * 0.05;
    camera.lookAt(0, state.camY, 0);
    renderer.render(scene, camera);
  });
  return { scene, camera, mesh, mat, state, count };
}
```

### E11 Planet wipe (colour transition with a curved horizon): `data-planet="#hex"`
- **CSS version** (Lite): add a child `<div class="planet">` to the incoming section.
```css
.planet { position:absolute; left:50%; top:0; width:300vw; aspect-ratio:1; border-radius:50%;
  background: var(--planet); transform: translate(-50%, 100vh); z-index:-1; }
```
```js
gsap.to(planet, { y: 0, ease: 'none', scrollTrigger: { trigger: sec, start: 'top bottom', end: 'top top', scrub: true } });
```
- **WebGL version:** add a `SphereGeometry(40, 64, 64)` with a `MeshBasicMaterial` under the camera. Scrub `sphere.position.y` from -60 to -38 per transition and retint it per section through E5's `onChange`. Reuse one sphere for every wipe.

### E12 Shard formations: `data-shards="cloud|row|pinwheel|ring|hidden"`
Precompute target arrays of `{p: Vector3, r: Euler, s?}`:
```js
const V = THREE.Vector3, E = THREE.Euler, R = THREE.MathUtils.randFloatSpread;
export const formations = {
  cloud: (n) => Array.from({ length: n }, () => ({ p: new V(R(26), R(16), R(14) - 4), r: new E(R(6), R(6), R(6)) })),
  row: (n) => Array.from({ length: n }, (_, i) => ({ p: new V(-14 + i * 1.1, -3 + i * 0.25, -i * 0.9), r: new E(0, 0.4, Math.PI), s: 1.6 })),
  pinwheel: (n) => Array.from({ length: n }, (_, i) => i < 4
    ? { p: new V(-6 + Math.cos(i * Math.PI / 2) * 1.4, Math.sin(i * Math.PI / 2) * 1.4, 0), r: new E(0, 0, i * Math.PI / 2), s: 2.2 }
    : { p: new V(R(30), R(20), -30), r: new E(), s: 0 }),
  hidden: (n) => Array.from({ length: n }, () => ({ p: new V(R(30), R(20), -40), r: new E(), s: 0 })),
};
export function bindFormations(sh) {
  const cache = {}; const get = (k) => (cache[k] ||= formations[k](sh.count));
  sh.state.formA = get('cloud');
  document.querySelectorAll('[data-shards]').forEach((sec) => ScrollTrigger.create({
    trigger: sec, start: 'top 60%', end: 'bottom 40%',
    onToggle: (s) => { if (!s.isActive) return;
      sh.state.formA = sh.state.formB || sh.state.formA; sh.state.formB = get(sec.dataset.shards); sh.state.mix = 0;
      gsap.to(sh.state, { mix: 1, duration: 1.6, ease: 'expo.inOut' }); }
  }));
}
```
Tint per section: `gsap.to(sh.mat.color, { ...new THREE.Color(hex), duration: .8 })`, from E5 `onChange`. A pinwheel that rotates with scroll: scrub a group's `rotation.z`, or add `state.spin`.

### E13 Thumbnail sphere → explode (Full tier)
Place N planes (project screenshots) on a Fibonacci sphere: `y = 1 - 2(i+.5)/N`, `r = sqrt(1-y²)`, `θ = i·2.39996`. Each plane calls `lookAt(origin)` then `rotateY(π)` so it faces outward. Spin the group slowly. Scroll scrubs the radius from 6 to 30, with opacity 1 → 0.35, while a paragraph fills in (E3). Lazy-load the textures, use 512px webp images and skip this on mobile.

### E14 Velocity chromatic fringe on headlines: `data-ca`
```css
[data-ca] { text-shadow: calc(-1px - var(--vel) * .15px) 0 #ff005099, calc(1px + var(--vel) * .15px) 0 #00dcff99; }
```

### E15 Count-up stats: `data-count="2311" data-suffix="+"`
Run once on enter: `gsap.to(obj, {v: target, snap: {v: 1}, duration: 1.6, onUpdate})`. Format with `toLocaleString()`.

### E16 Extras
- **`data-marquee`:** infinite x loop whose `timeScale` follows `1 + |velocity| * 0.05` and flips direction with scroll direction.
- **`data-tilt`:** mouse 3D tilt (max 6deg, `transformPerspective: 800`) with a radial-gradient glare at the cursor. Desktop only.
- **`data-scroll-badge`:** a circular SVG text badge on `textPath` that rotates constantly and speeds up with velocity. Fade it out after the hero.
- **Footer:** a frosted glass panel floating over the 3D scene.

---

## 3. Section recipe guide (how to map any site)

| Section type | Recommended effects |
|---|---|
| Hero | E10 cloud, E1 on load, E2 slice-out, E11 wipe to next, E16 badge, E14 |
| Big statement | E2 pinned, E3 fill-pin |
| Stats / numbers | E11 colour wipe, E6, E15, E12 row |
| Services / features | E6 uneven stagger, E16 tilt |
| Work / case studies | E7 clip+zoom, E1 titles, shards hidden |
| About / years / story | E4 giant chars, E3 fill |
| Certifications / awards / logos | E8 pinned carousel |
| Experience / clients / list | E9 active-row list |
| Process / how it works | E12 pinwheel + E3 sequential pinned blocks |
| Hero moment / showreel | E13 sphere |
| FAQ | E6 rows one by one |
| CTA | E11 wipe, E10 cloud returns, E1, E16 marquee |

Colour rhythm: alternate dark → light → accent → light → dark. Change the background colour only through E11 wipes or E5 tweens, never with hard cuts. Keep at most 3 accent colours, taken from the site's brand.

Don't pin everything. Use at most about 5 pinned scenes per page, and give text-heavy sections normal scroll.

---

## 4. Framework adapters

- **Vanilla / Astro / static:** call `initAll()` on `DOMContentLoaded`. In Astro, use `<script>` in the layout; for View Transitions, re-init on `astro:page-load` and `ScrollTrigger.getAll().forEach(t=>t.kill())` on `astro:before-swap`.
- **React / Next.js:**
  - `npm i @gsap/react lenis`.
  - Use `useGSAP(() => { ...initializers }, { scope: rootRef })`, which handles cleanup.
  - Use the `<ReactLenis root>` from `lenis/react`, and sync it in an effect with `lenis.on('scroll', ScrollTrigger.update)`.
  - Load the 3D canvas with `dynamic(() => import('./Shards'), { ssr: false })`. Initialise it after first paint (`requestIdleCallback`).
  - On App Router route change, kill the triggers and call `ScrollTrigger.refresh()`.
  - You may use `@react-three/fiber` instead of raw three; the same formation math applies inside `useFrame`.
- **Vue / Nuxt:** init in `onMounted` with `gsap.context(() => {...}, root)`, and call `ctx.revert()` in `onUnmounted`. Make the canvas a client-only component.
- **Svelte/Kit:** init in `onMount`, and return a cleanup that reverts the gsap context.
- **Webflow / no-build:** use the CDN builds of gsap, ScrollTrigger, SplitText, lenis and three (as ESM via `<script type="module">`).

---

## 5. Performance & accessibility (mandatory)

- **Animate only cheap properties:** transform, opacity and clip-path. Never animate width, height or top.
- **will-change:** only on elements that are actively pinned or scrubbed.
- **WebGL budget:**
  - DPR at most 1.5 on desktop and 1 on mobile.
  - At most 50 shards on desktop and 20 on mobile.
  - Pause rendering when the tab is hidden.
  - Use the standard material on mobile.
  - Lazy-init after LCP.
- **Fonts:** call `ScrollTrigger.refresh()` after `document.fonts.ready` and after images load, so split lines and pin spacing are correct.
- **prefers-reduced-motion:** no Lenis, no pin, no scrub and no WebGL. Show static sections with solid backgrounds and full-contrast text.
- **Mobile (≤768px):**
  - No tilt.
  - Pinned scenes cut to 60% duration, and simple headlines left unpinned.
  - No thumbnail sphere.
  - Consider `ScrollTrigger.normalizeScroll(true)` only if address-bar jumps cause issues.
- **Semantic text stays real text:** SplitText keeps the accessible text. Never replace headings with canvas or images.
- **Targets:** Lighthouse performance ≥ 85 on desktop; CLS 0 (no layout shift from splits, so reserve line heights).

---

## 6. QA checklist (run before declaring done)

1. Run the dev server and open it in the browser at 1440, 1024 and 390 widths.
2. Scroll the full page slowly, 3–4 ticks per step with a screenshot each, and also fast, then back up.
3. Verify:
   - [ ] No headline clipped at rest, and no faded or grey text left after its reveal.
   - [ ] No blank gaps from pin spacing, no overlapping sections, no jump at pin start or end.
   - [ ] The header is readable on every background.
   - [ ] Shard formations change at the intended sections, with smooth wipes and no colour cuts.
   - [ ] Counters end at values that match the rest of the site.
   - [ ] Reduced-motion mode shows a complete static page.
   - [ ] No console errors; triggers are cleaned up on route change (no duplicate animations after navigating).
   - [ ] Steady 60fps while scrolling (check the Performance panel); the mobile fallback works.
4. Report the Motion Map as built, the tier, any skipped effects with the reason, and known trade-offs.
