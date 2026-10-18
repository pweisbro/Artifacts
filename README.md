# Stim Lab

A home for small interactive web apps. The homepage (`index.html`) shows every app with a live preview; tap one to open it, and the grid button inside each app brings you back.

Open https://pweisbro.github.io/Stim-Lab/ in Safari, then use **Share → Add to Home Screen** with **Open as Web App** on. After the first visit everything works offline.

## Apps

### Spectrum Bench

`spectrum-bench.html` is a playable optics bench: light sources, prisms, lenses, a flowing clear liquid, flat and curved mirrors, diffraction gratings, color filters, beam splitters, slits and screens.

**Sound** makes the bench react to the microphone or a song file. The Sound panel only picks the source and starts or stops listening; every audio setting lives on its piece. Each light's **Audio reactive** tab sets what it listens to (sensitivity and a frequency range, with a live input spectrum) and what it does: carry the sound on its beam (the live waveform like an oscilloscope trace, or spectrum bars, a running histogram of its range whose bars ride outward from the light), sway with loudness and beats, follow the volume, and take its laser color from pitch. Both styles follow every bounce and split. Any prism, liquid or lens can be tuned the same way in its **Sound** section: its own sensitivity and frequency range drive its refraction, color spread, reflection, and tilt or ripple. All of these settings are saved with setups.

**Light speed** is set on each light source (tap a light), from Instant down through 100 m/s to about 30 mm/s, and is saved with setups. Beams then take time to travel, a swaying source bends its beam like a hose, and a change starts where it happens and ripples outward: turn a mirror and only light that reaches it afterward goes the new way.

### Resonant Ink

`resonant-ink.html` is a multi-touch fluid simulation. Stir the dye with as many fingers as you like, and tune vorticity, viscosity, dye density, fade and diffusion. Colors, bloom and a kaleidoscope mirror are adjustable. Audio-reactive spots fire from a frequency band you pick on the live spectrum, with an adjustable sensitivity. The sound can come from the built-in demo beat, a song file, or the microphone.

Beyond the basic sliders there are forces (buoyancy, a whirlpool, animated turbulence, and an auto stir that keeps it moving on its own), a time-speed control for slow motion, color maps (heat, spectral contours, flow direction), speed glow, chromatic split, vignette and color jitter, and a brush that can stir, paint, or both.

The **Effects** tab holds bloom (toned down by default, with intensity and threshold sliders) and ten GLSL shader styles that run over the finished image: Cel (toon shading with ink outlines), Oil paint (Kuwahara filter), Watercolor, Halftone, Pixel, Dither, CRT, Emboss, Neon edges and Chrome (liquid metal). Each has a strength and size slider plus its own settings.

Sixteen built-in presets cover the range, including Comic, Mercury, Arcade and Gallery for the shader styles. **Presets** in the controls lets you save your own looks by name and send them as preset codes: one line of text starting with `RI1:` that holds every setting, audio included, the same way Spectrum Bench shares setups. Paste a code into the same tab to load it. On iPhone, **Share…** sends the code through the share sheet.

Resonant Ink can also go on the Home Screen as its own app, with its own icon: open https://pweisbro.github.io/Stim-Lab/resonant-ink.html in Safari, tap **Share → Add to Home Screen** and keep **Open as Web App** on. It opens straight into the tank, full screen, and works offline after the first visit (songs you load still play from the device).

The microphone needs a secure (https) host such as GitHub Pages and your permission. Songs play locally and are never uploaded. Settings and saved presets are kept in the browser on each device.

### Drift Pad

`drift-pad.html` is an ambient sound pad: twenty glowing pads tuned to a scale, low notes at the bottom left rising to the top right. Tap a pad to play it, hold to let a note swell, or drag across to strum. Pick a voice (Glass, Pad or Kalimba), a scale (pentatonic, minor pentatonic, Dorian, Lydian or Hirajoshi) and a key, and set reverb, echo and volume.

Two things make it play itself. **Loop** sets pads repeating: each looping pad gets its own length, from about 5 to 20 seconds, so they drift in and out of step like tape loops, and a small ring on the pad sweeps once per loop. **Drift** wanders over the pads on its own, at the pace and density you set. Both can run together, and the sound pauses while the app is in the background.

Everything is synthesized in the browser, so it works offline. Settings are kept in the browser on each device.

### Gravity Wells

`gravity-wells.html` is a multi-touch particle toy. Every finger (or the mouse) becomes a gravity well, and thousands of sparks fall toward it, orbit and slingshot, colored by how fast they move. The longer you hold a well the heavier it gets; let go of a heavy one and it collapses into a shockwave. The dock switches what your fingers do (**Pull**, **Push** or **Swirl**), **Tilt** lets the phone's own tilt pour the particles around (iPhone asks for motion access the first time), and **Big bang** gathers everything into one point and blows it apart.

## Updating

To update an app, replace its page with the new version. Pages refresh themselves the next time you open them online.

To add an app, put its page next to the others and follow the checklist in `CLAUDE.md`: an entry in the homepage's `APPS` list, a button back home, and a line in `sw.js` for offline use.
