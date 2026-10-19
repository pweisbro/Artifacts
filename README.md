# Stim Lab

A home for small interactive web apps. The homepage (`index.html`) shows every app with a live preview; tap one to open it, and the grid button inside each app brings you back.

Open https://pweisbro.github.io/Stim-Lab/ in Safari, then use **Share → Add to Home Screen** with **Open as Web App** on. After the first visit everything works offline.

## Apps

### Spectrum Bench

`spectrum-bench.html` is a playable optics bench: light sources, prisms, lenses, a flowing clear liquid, flat and curved mirrors, diffraction gratings, color filters, beam splitters, slits and screens.

The **black hole** bends light passing near it the way gravity does, more the closer it passes, so it casts a dark shadow about ten times wider than its horizon, and light skimming its photon ring can loop around before escaping. Gravity really bends every color alike, but here **Colors bend like** borrows the color spread of one of the bench's materials (with the same **Rainbow boost** as prisms), so violet swings in tighter than red; pick **Real gravity** to turn that off. **Pull reaches** sets how far out the pull is felt. The **Black hole** starter setup shows it.

**Sound** makes the bench react to the microphone or a song file. The Sound panel picks the source, starts or stops listening, and sets an overall **Sensitivity** for the whole bench. Listening is a setting rather than a mode: it keeps going after you close the panel, recovers if the microphone drops out, and starts again the next time you open the bench, until you tap **Stop listening**; everything else lives on its piece. Each light's **Audio reactive** tab sets what it listens to (its own sensitivity on top of the overall one, and a frequency range, with a live input spectrum) and what it does: carry the sound on its beam (the live waveform like an oscilloscope trace, or spectrum bars, a running histogram of its range whose bars ride outward from the light), sway with loudness and beats, follow the volume, and take its laser color from pitch. Both styles follow every bounce and split. Any prism, liquid or lens can be tuned the same way in its **Sound** section: its own sensitivity and frequency range drive its refraction, color spread, reflection, and tilt or ripple. All of these settings are saved with setups.

Each of those pieces also has its own **Leveling**, because highs in music are often 15 to 30 dB quieter than bass. **Auto** (the default) learns the range's quiet and loud levels as the music plays, so a treble range swings as fully as a bass range. **Calibrated** uses levels measured with **Calibrate**, which listens to that range for 5 seconds. **Off** uses one fixed scale for every range. The meter shows the quiet and loud levels as two dashed lines across the range.

**Light speed** is set on each light source (tap a light), from Instant down through 100 m/s to about 30 mm/s, and is saved with setups. Beams then take time to travel, a swaying source bends its beam like a hose, and a change starts where it happens and ripples outward: turn a mirror and only light that reaches it afterward goes the new way. Slowed light travels as a train of short pulses, and each light's **Beam resolution** sets how far apart they are (2 to 60 mm). The same setting sets how finely a sound waveform is drawn along the beam. Finer is smoother; coarser is faster. If a beam is too heavy for the device (a wide white beam carries thousands of rays), the bench spaces its pulses out until it keeps up and says so under the slider.

### Resonant Ink

`resonant-ink.html` is a multi-touch fluid simulation. Stir the dye with as many fingers as you like, and tune vorticity, viscosity, dye density, fade and diffusion. Colors, bloom and a kaleidoscope mirror are adjustable. Audio-reactive spots fire from a frequency band you pick on the live spectrum, with an adjustable sensitivity. The sound can come from the built-in demo beat, a song file, or the microphone.

Beyond the basic sliders there are forces (buoyancy, a whirlpool, animated turbulence, and an auto stir that keeps it moving on its own), a time-speed control for slow motion, color maps (heat, spectral contours, flow direction), speed glow, chromatic split, vignette and color jitter, and a brush that can stir, paint, or both.

The **Effects** tab holds bloom (toned down by default, with intensity and threshold sliders) and ten GLSL shader styles that run over the finished image: Cel (toon shading with ink outlines), Oil paint (Kuwahara filter), Watercolor, Halftone, Pixel, Dither, CRT, Emboss, Neon edges and Chrome (liquid metal). Each has a strength and size slider plus its own settings.

Sixteen built-in presets cover the range, including Comic, Mercury, Arcade and Gallery for the shader styles. **Presets** in the controls lets you save your own looks by name and send them as preset codes: one line of text starting with `RI1:` that holds every setting, audio included, the same way Spectrum Bench shares setups. Paste a code into the same tab to load it. On iPhone, **Share…** sends the code through the share sheet.

Resonant Ink can also go on the Home Screen as its own app, with its own icon: open https://pweisbro.github.io/Stim-Lab/resonant-ink.html in Safari, tap **Share → Add to Home Screen** and keep **Open as Web App** on. It opens straight into the tank, full screen, and works offline after the first visit (songs you load still play from the device).

The microphone needs a secure (https) host such as GitHub Pages and your permission. Songs play locally and are never uploaded. Settings and saved presets are kept in the browser on each device.

### Drift Pad

`drift-pad.html` is an ambient sound pad: twenty glowing pads tuned to a scale, low notes at the bottom left rising to the top right. Tap a pad to play it, hold to let a note swell, or drag across to strum. Pick an instrument (Glass, Pad, Kalimba, Wood blocks, Steel drum, Gong, Singing bowl, Marimba, Music box, Harp or Choir), a scale (pentatonic, minor pentatonic, Dorian, Lydian or Hirajoshi) and a key, and set reverb, echo and volume.

**Custom** is an instrument you build yourself. Start from any of the others, or tap **Customize this sound** on one, then tune its waveform, overtones (pure, harmonic, hollow, bell or metal), octave, attack, ring, sustain and release, brightness, resonance and filter sweep, a mallet-like strike of noise, pitch drop, shimmer and vibrato. Your custom instrument is saved with the other settings.

Two things make it play itself. **Loop** sets pads repeating: each looping pad gets its own length, from about 5 to 20 seconds, so they drift in and out of step like tape loops, and a small ring on the pad sweeps once per loop. **Drift** wanders over the pads on its own, at the pace and density you set. Both can run together, and the sound pauses while the app is in the background.

Everything is synthesized in the browser, so it works offline. Settings are kept in the browser on each device.

### Gravity Wells

`gravity-wells.html` is a multi-touch particle toy. Every finger (or the mouse) becomes a gravity well, and thousands of sparks fall toward it, orbit and slingshot, colored by how fast they move. The longer you hold a well the heavier it gets; let go of a heavy one and it collapses into a shockwave. The dock switches what your fingers do (**Pull**, **Push** or **Swirl**), **Tilt** lets the device's own tilt pour the particles around (iPhone and iPad ask for motion access the first time). Tilt is measured from however you hold the device when you turn it on, and the target button next to it sets a new level from the current position, and **Big bang** gathers everything into one point and blows it apart.

### Grainfall

`grainfall.html` is a falling-sand sandbox played on a mint clay CRT TV in a pastel 3D bedroom at night, with lamplight, moonlight through the blinds and dust drifting in the beam. Draw on the TV screen with 18 materials: sand, stone, gunpowder, water, oil, acid, lava, fire, spark, steam, wall, wood, plant, ice, copper wire, spout, wind and erase. They react: water and lava make steam and stone, fire spreads through wood, plants and oil, gunpowder explodes with a pressure blast, acid eats solids, plants grow into water, ice freezes it, sparks run along wire, and a spout copies whatever touches it. **Air view** shows the pressure field that Wind and explosions push around.

Drag anywhere off the screen to look around the room, or turn on **Tilt** (iPhone and iPad ask for motion access the first time) and lean the device instead; however you hold it when you turn Tilt on counts as level. **Zoom in** swings the camera square onto the screen. If the device struggles, the room lowers its own resolution and effects step by step; add `?fps` to the address to see the frame rate and which step it is on. Without WebGL it falls back to the flat screen in a mint bezel.

The 3D room uses three.js from jsDelivr, which is cached after the first visit so it works offline too.

### Little Orrery

`little-orrery.html` is a miniature clay model of the solar system floating in a starfield: the Sun as a warm glowing lamp, the planets circling it on thin glowing orbit hoops, the asteroid belt and the Kuiper belt as tiny clay pebbles, the odd meteor streaking past, and pastel nebula haze kept out in the background under a dome of stars at three depths, with a tilt-shift blur that keeps the model sharp and the sky soft. Each planet is shaped like itself: the gas giants are a little squashed, Saturn's rings have the real bands and gap, Uranus rolls on its side with its thin rings, Haumea is an egg, and the Moon is at its true size. Orbit times, spin directions and axis tilts follow the real values.

Besides the eight planets there are the dwarf planets Ceres, Pluto, Haumea, Makemake and Eris; the Moon, Phobos and Deimos; Hubble and Webb beside Earth; and Voyager 1, Voyager 2 and New Horizons heading out. Twenty-one landing sites are pinned on Mars, Venus, the Moon and Jupiter (Viking to Perseverance, Venera, Apollo, Chang'e, Chandrayaan-3, the Galileo probe), and their names appear when you follow that world. Tap anything to follow it and read a line about it.

**To scale** switches between the cute squeeze (sizes by square root, distances by a log, tidy round orbits) and real proportions: Jupiter is 11 Earths wide, Neptune sits 77 times farther out than Mercury, and every orbit takes its real elliptical shape, tilt and direction, so Pluto's stretched loop dips inside Neptune's and Eris swings far out at 44 degrees. Only the Sun stays shrunk, since at true proportion it would swallow Mercury's orbit on any screen. Drag to spin the model, pinch or scroll to zoom. The **Speed** slider sets how long an Earth year takes (2 seconds to 2 minutes), **Names** and **Orbits** toggle the labels and the hoops, and **Reset view** goes back to the overview. The 3D model uses three.js from jsDelivr, cached after the first visit; add `?fps` to the address to see the frame rate.

### Earworm

`earworm.html` is for getting a song that's stuck in your head down before it's gone. Pick a track and tap **Hum**: after a one-bar count-in, hum the part along to the click, and when the section ends your hum is turned into notes on a grid (pitch detection on the microphone, snapped to the beat and to the key it guesses from your humming). Hum each part on its own track, a melody, a bass line, a harmony, while the others play back. A **Beat** track listens for beatboxing instead: *boom* is a kick, *kah* a snare, *tss* a hat.

Each track has its own instrument (piano, electric piano, bass, sub bass, synth lead, flute, brass, strings, pads, choir, harp, marimba, kalimba and more, or three drum kits), an octave shift, volume, mute and solo, and can play its notes, your original hum, or both. Tap the grid to add a note, tap a note to remove it, drag it to move it, drag its right end to stretch it. Your hum stays on the grid as a faint pencil line to check against.

Sections (A, B, C…) each hold their own notes; tap the current one to rename, resize (1 to 16 bars), duplicate or delete it. **Play song** strings sections together in any order. Settings hold tempo, how finely hums snap (16ths, 8ths or beats), the key and scale, the click and count-in, and a timing nudge if notes land early or late. **Export MIDI** shares a .mid file with one track per part for GarageBand, Logic or any DAW. The sketch is saved in the browser, hums included, and there's undo for every change.

### X-Y Scope

`xy-scope.html` is a browser oscilloscope in X-Y mode, for oscilloscope music: the left channel moves the beam sideways and the right channel moves it up and down. **Lissajous** is a two-channel generator (frequency, wave shape, phase and a small detune that makes the figure rotate, with ratio presets from 1:1 to 1:3). **Shapes** traces a spinning wireframe cube, a square, star, heart or mushroom; the pitch slider sets how many times a second the shape is drawn, which is the note you hear. **Song** loads any audio file to see what it draws, and **Shape on top** mixes the current shape over it. Songs stream from the device as they play rather than loading into memory, so files of several hundred MB work, and a **Position** slider shows and jumps around the track. WAVs are read by the app itself, so any WAV opens, including the 24-bit, 32-bit float and high-sample-rate ones oscilloscope-music tracks often come as; other formats play through the browser. Gain, afterglow and intensity set the look of the phosphor.

**Start sound** plays exactly what's on screen out of the headphone jack, so it can drive a real scope: left into CH1, right into CH2, X-Y mode, volume low, and sound enhancements off. Keep a real CRT's brightness low and turn it down before stopping the sound, since a still dot burns the phosphor. Everything is generated in the browser, so it works offline; songs play locally and are never uploaded.

## Updating

To update an app, replace its page with the new version. Pages refresh themselves the next time you open them online.

To add an app, put its page next to the others and follow the checklist in `CLAUDE.md`: an entry in the homepage's `APPS` list, a button back home, and a line in `sw.js` for offline use.
