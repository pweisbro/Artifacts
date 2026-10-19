# Spectrum Bench for TouchDesigner

A TouchDesigner version of Spectrum Bench, built from setup codes made in the web bench. You arrange a bench on the iPad, tap **Copy code for this bench**, and paste the code in here. There's no editor and no slowed light.

## Files

- `sb_scene.py` decodes a setup code (`SB1:` + base64 JSON) and packs the pieces and light rays into float textures. It's plain Python with numpy, so it also runs outside TouchDesigner (`python3 sb_scene.py < code.txt` prints a summary).
- `sb_trace.frag` is the tracer, a GLSL TOP pixel shader. Each column is one ray and each row is one piece of its path. It uses the same physics as the web bench: Cauchy dispersion, Fresnel reflection, total internal reflection, gratings, filters, beam splitters, lenses, curved mirrors, liquids and the black hole.
- `build_td.py` builds the network.

## Set up

1. Save a `.toe` in the folder that holds this `touchdesigner` folder (the repo root).
2. Open the Textport (Dialogs > Textport and DATs) and run:
   ```python
   exec(open(project.folder + '/touchdesigner/build_td.py').read())
   ```
3. Open `/project1/spectrum_bench/out`. The Prism fan starter is loaded.
4. Paste any setup code into the **Setup code** parameter of `spectrum_bench`.

The script prints a line for any parameter it couldn't set, since some names differ between TouchDesigner versions. Set those by hand. If the rays come out white, the instance color hookup on `rays` is the one to check: point the instance colors at `trace_col`, channels r, g and b.

## Parameters on spectrum_bench

- **Setup code**: the bench to show.
- **Brightness**: multiplies the setup's own brightness.
- **Audio rainbow spread**: above 0, the microphone level widens every rainbow (glass, liquids and the black hole's color split).
- **Max rays traced**: the tracer's width. Lower it if the frame rate drops.
- **Re-roll**: reshuffles which way each traced copy goes at a split (see below).

## How it works

`info` (a Script DAT) decodes the code and packs it. `prims` and `emit` (Script TOPs) hand the packed arrays to two GLSL TOPs running `sb_trace.frag`: `trace_geo` gives each piece's middle, angle and length, and `trace_col` gives its color. `rays` draws one instance of a thin rectangle per piece, with additive blending. `pieces` draws the outlines, `render` and `glow` light it, and `out` is the result.

The web bench splits rays at every surface. A shader can't spawn rays, so each emitted ray is traced several times, and each copy picks one way at every split, weighted by how bright the bench would draw it. Added up, the copies give the bench's picture.

## Checked so far

The shader was run in a browser (WebGL) against all 19 starter benches, and the ray paths match the web bench, including the liquid at the same moment in its flow. In TouchDesigner 2023.11600 with a Non-Commercial key, the build script runs with nothing left to set by hand, both shaders compile, and Prism fan, Black hole, Grating orders, Lens colors, Dichroic split, Liquid lens and Parabolic dish render like the web bench.

The Non-Commercial key caps every image at 1280 x 1280, so the tracer wraps its rays into bands of 64 rows instead of one long row, and the render is 1280 x 720. With a paid key you can raise the render's resolution.

## Not carried over

- Per-piece sound settings, the light's wave and bar decorations, and slowed light.
- The color strip under a selected screen. Screens show where colors land as short bright marks.
- Exporting a code back out. Adding it is easy if tweaks made here should go back to the web bench.
