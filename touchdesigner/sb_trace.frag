// Spectrum Bench tracer for a TouchDesigner GLSL TOP (pixel shader).
//
// Input 0: surfaces from sb_scene.pack (5 pixels each). Input 1: emitted rays (2 pixels each).
// Output: one column per traced ray, one row per piece of its path. Row k of column c is piece k of ray c.
//   uMode 0: (mid x, mid y, angle in degrees, length), with y flipped up for TouchDesigner, for instancing
//   uMode 1: (r, g, b, 1), the piece's light, already scaled for additive blending
// A piece the ray never reaches comes out as zeros.
//
// The bench splits every ray where it meets a surface (reflected and refracted, grating orders, a beam splitter's two
// ways). A shader can't spawn rays, so each emitted ray is traced uCopies times and every copy picks one way at each
// split, at random, in proportion to how bright the bench would draw it. Added up, the copies give the same picture.

uniform float uNPrim;   // surfaces
uniform float uNEmit;   // emitted rays
uniform float uCopies;  // copies traced per emitted ray
uniform float uBright;  // the setup's brightness
uniform float uDisp;    // rainbow spread: 1 is the setup as saved; audio can push it up
uniform float uSeed;    // change it to re-roll which way the copies go
uniform float uMode;

layout(location = 0) out vec4 fragColor;

#define FAR 5000.0
#define IMIN 0.012
#define REFL_MIN 0.048
#define MAXD 48.0
#define MAXEV 900

// surface kinds, as in sb_scene.py
#define K_BLOCK 0
#define K_MIRROR 1
#define K_SPLIT 2
#define K_FILTER 3
#define K_GLASS 4
#define K_GRATING 5
#define K_SCREEN 6
#define K_THIN 7
#define K_GRAV 8

vec4 P(int i, int j) { return texelFetch(sTD2DInputs[0], ivec2(i * 5 + j, 0), 0); }
vec4 E(int i, int j) { return texelFetch(sTD2DInputs[1], ivec2(i * 2 + j, 0), 0); }

uint rs;
float rnd() { rs ^= rs << 13; rs ^= rs >> 17; rs ^= rs << 5; return float(rs) * (1.0 / 4294967296.0); }
uint hash(uint x) { x ^= x >> 16; x *= 0x7feb352du; x ^= x >> 15; x *= 0x846ca68bu; x ^= x >> 16; return x; }

// Cauchy index with the rainbow spread scaled about the sodium D line
float nIdx(vec2 AB, float lam) {
  float lu = lam / 1000.0, ld = 0.5893;
  return AB.x + AB.y / (ld * ld) + uDisp * AB.y * (1.0 / (lu * lu) - 1.0 / (ld * ld));
}

// Wavelength to screen color (bruton and GAIN in spectrum-bench.html)
vec3 colorOf(float w) {
  w = clamp(w, 380.0, 780.0);
  vec3 c;
  if (w < 440.0) c = vec3((440.0 - w) / 60.0, 0.0, 1.0);
  else if (w < 490.0) c = vec3(0.0, (w - 440.0) / 50.0, 1.0);
  else if (w < 510.0) c = vec3(0.0, 1.0, (510.0 - w) / 20.0);
  else if (w < 580.0) c = vec3((w - 510.0) / 70.0, 1.0, 0.0);
  else if (w < 645.0) c = vec3(1.0, (645.0 - w) / 65.0, 0.0);
  else c = vec3(1.0, 0.0, 0.0);
  float f = 1.0;
  if (w < 420.0) f = 0.3 + 0.7 * (w - 380.0) / 40.0;
  else if (w > 690.0) f = 0.3 + 0.7 * (780.0 - w) / 90.0;
  return min(pow(c * f, vec3(0.8)) * vec3(0.78962, 0.82334, 1.0), 1.0);
}

float gravStep(float rho, float mass) { return clamp(0.14 * (rho - mass) + 0.6, 0.6, 32.0); }
float gravN(float rho, float reach, float mass, float D) {
  if (!(rho < reach)) return 1.0;
  float u = mass / rho;
  if (u >= 1.0) return 1e6;
  float w = 1.0 - rho * rho / (reach * reach);
  return 1.0 + (pow(1.0 + u, 3.0) / (1.0 - u) - 1.0) * w * w * D;
}

float transOf(vec4 f, float l) {  // f: pass (0 band, 1 long, 2 short), centre, width, dichroic
  if (f.x > 1.5) return 1.0 / (1.0 + exp((l - f.y) / 4.0));
  if (f.x > 0.5) return 1.0 / (1.0 + exp(-(l - f.y) / 4.0));
  float z = (l - f.y) / (f.z / 2.0), z2 = z * z;
  return exp(-0.693147 * z2 * z2 * z2);
}

// Nearest surface along o + d t. Returns its index (-1 for none); t, u (where along a line) and normal n are written out.
int nearest(vec2 o, vec2 d, int skip, int skipEl, out float best, out float hu, out vec2 hn) {
  best = FAR; hu = 0.0; hn = vec2(0.0);
  int hit = -1, n = int(uNPrim + 0.5);
  for (int i = 0; i < n; i++) {
    vec4 a = P(i, 0);
    int ty = int(a.x + 0.5);
    if (ty == 0) {
      if (i == skip) continue;
      vec4 g = P(i, 1);
      float den = d.x * g.w - d.y * g.z;
      if (abs(den) < 1e-12) continue;
      vec2 q = g.xy - o;
      float t = (q.x * g.w - q.y * g.z) / den;
      // a ray leaving a corner must not catch the next edge of the same piece (float precision)
      if (t <= (int(a.z + 0.5) == skipEl ? 0.02 : 1e-4) || t >= best) continue;
      float u = (q.x * d.y - q.y * d.x) / den;
      if (u < 0.0 || u > 1.0) continue;
      best = t; hit = i; hu = u; hn = P(i, 2).xy;
    } else if (ty == 1) {
      vec4 g = P(i, 1), g2 = P(i, 2);
      vec2 p = o - g.xy;
      float b = dot(d, p), c = dot(p, p) - g.z * g.z, disc = b * b - c;
      if (disc < 0.0) continue;
      float sq = sqrt(disc), eps = i == skip ? 0.05 : 1e-4;
      for (int k = 0; k < 2; k++) {
        float t = k == 0 ? -b - sq : -b + sq;
        if (t <= eps || t >= best) continue;
        vec2 q = p + d * t;
        if (dot(q, g2.xy) / g.z >= g.w) { best = t; hit = i; hn = q / g.z; break; }
      }
    } else if (ty == 2) {  // parabolic mirror y = q x² in its own frame
      vec4 g = P(i, 1), f = P(i, 2);
      vec2 p = o - g.xy;
      float lx = dot(p, f.xy), ly = dot(p, f.zw), ldx = dot(d, f.xy), ldy = dot(d, f.zw), q = g.z;
      float A = ldx * ldx * q, B = 2.0 * lx * ldx * q - ldy, C = lx * lx * q - ly, eps = i == skip ? 0.05 : 1e-4;
      float t1, t2;
      if (abs(A) < 1e-9) { if (abs(B) < 1e-9) continue; t1 = t2 = -C / B; }
      else {
        float disc = B * B - 4.0 * A * C;
        if (disc < 0.0) continue;
        float sq = sqrt(disc), x1 = (-B - sq) / (2.0 * A), x2 = (-B + sq) / (2.0 * A);
        t1 = min(x1, x2); t2 = max(x1, x2);
      }
      for (int k = 0; k < 2; k++) {
        float t = k == 0 ? t1 : t2;
        if (t <= eps || t >= best) continue;
        float x = lx + ldx * t;
        if (abs(x) > g.w) continue;
        vec2 nn = 2.0 * x * q * f.xy - f.zw;
        best = t; hit = i; hn = normalize(nn); break;
      }
    } else {  // a black hole's pull: inside it, one short step; outside, where the ray enters it
      vec4 g = P(i, 1);
      vec2 p = o - g.xy;
      float o2 = dot(p, p), R2 = g.z * g.z, b = dot(d, p), t;
      if (o2 < R2 - 1e-3 || (o2 < R2 + 1.0 && b < 0.0)) t = max(gravStep(sqrt(o2), g.w), 1e-3);
      else {
        float disc = b * b - o2 + R2;
        if (disc < 0.0 || b >= 0.0) continue;
        t = -b - sqrt(disc);
        if (t <= 1e-4) continue;
      }
      if (t >= best) continue;
      best = t; hit = i; hn = vec2(0.0);
    }
  }
  if (hit >= 0 && P(hit, 0).w > 0.5) {  // liquids: blend the normals at both ends of the edge
    vec4 nn = P(hit, 4);
    hn = normalize(mix(nn.xy, nn.zw, hu));
  }
  return hit;
}

// Picks one of the ways a ray can go. f[j] is each way's share of the light. The ray keeps the chosen share as its
// real intensity I, and its drawn brightness G grows by the sum of every way's share^0.6 (the bench draws a ray
// with intensity^0.6), so on average the copies add up to what the bench draws.
float wv[7];
int choose(float f[7], int n, float I, inout float G) {
  float s = 0.0;
  for (int j = 0; j < 7; j++) { wv[j] = (j < n && I * f[j] >= IMIN) ? pow(f[j], 0.6) : 0.0; s += wv[j]; }
  if (s <= 0.0) return -1;
  G *= s;
  float x = rnd() * s;
  for (int j = 0; j < 7; j++) { if (j >= n) break; x -= wv[j]; if (x < 0.0 && wv[j] > 0.0) return j; }
  for (int j = 6; j >= 0; j--) if (wv[j] > 0.0) return j;
  return -1;
}

void main() {
  ivec2 px = ivec2(gl_FragCoord.xy);
  int copies = int(uCopies + 0.5), ray = px.x / max(copies, 1), want = px.y;
  vec4 outv = vec4(0.0);
  if (ray >= int(uNEmit + 0.5)) { fragColor = TDOutputSwizzle(outv); return; }
  rs = hash(uint(px.x) * 9781u + hash(uint(uSeed * 1000.0) + 1u)) | 1u;

  vec4 e0 = E(ray, 0), e1 = E(ray, 1);
  vec2 p = e0.xy, d = normalize(e0.zw);
  float lam = e1.x, I = e1.y, G = pow(e1.y, 0.6), base = e1.z, depth = 0.0;
  int skip = -1, skipEl = -1, med = -1;
  vec2 medAB = vec2(1.0, 0.0);

  vec2 last = p, dLast = d;  // where the piece being built starts, and the direction there
  int nv = 0, sub = 0;       // pieces finished so far; black hole steps folded into this piece
  vec2 s0 = vec2(0.0), s1 = vec2(0.0);
  float sG = 0.0;
  bool got = false;

  for (int ev = 0; ev < MAXEV; ev++) {
    float t, hu; vec2 hn;
    int h = nearest(p, d, skip, skipEl, t, hu, hn);
    vec2 q = p + d * t;
    vec4 a = h >= 0 ? P(h, 0) : vec4(0.0);
    int kind = int(a.y + 0.5);
    bool grav = h >= 0 && kind == K_GRAV;
    // Steps through a black hole's pull are short and many: fold several into one piece unless the ray turns much
    sub++;
    if (!grav || sub >= 10 || dot(d, dLast) < 0.9985) {
      if (nv == want) { s0 = last; s1 = q; sG = G; got = true; break; }
      nv++; last = q; dLast = d; sub = 0;
    }
    if (h < 0) break;

    float f[7];
    for (int j = 0; j < 7; j++) f[j] = 0.0;
    vec2 refl = d - 2.0 * dot(d, hn) * hn;
    vec4 pr = P(h, 3);
    if (kind == K_MIRROR) { d = refl; I *= 0.95; G *= pow(0.95, 0.6); }
    else if (kind == K_SPLIT) {
      f[0] = 1.0 - pr.x; f[1] = pr.x;
      int c = choose(f, 2, I, G); if (c < 0) break;
      I *= f[c]; if (c == 1) d = refl;
    } else if (kind == K_FILTER) {
      float T = transOf(pr, lam);
      f[0] = T; f[1] = pr.w > 0.5 ? (1.0 - T) * 0.98 : 0.0;
      int c = choose(f, 2, I, G); if (c < 0) break;
      I *= f[c]; if (c == 1) d = refl;
    } else if (kind == K_THIN) {  // ideal thin lens: tan θout = tan θin − x/f
      vec4 g2 = P(h, 2);
      vec2 tt = g2.zw, nn = g2.xy;
      float x = dot(q - pr.yz, tt), du = dot(d, tt), dv = dot(d, nn), sg = dv >= 0.0 ? 1.0 : -1.0;
      float m = du / max(abs(dv), 1e-6) - x / pr.x;
      d = normalize(m * tt + sg * nn); I *= 0.99; G *= pow(0.99, 0.6);
    } else if (kind == K_GLASS) {
      int el = int(a.z + 0.5);
      vec2 nn = hn;
      float ci = -dot(d, nn);
      if (ci < 0.0) { nn = -nn; ci = -ci; }
      bool inside = med == el;
      float ng = nIdx(pr.xy, lam);
      float n1 = inside ? ng : (med >= 0 ? nIdx(medAB, lam) : 1.0), n2 = inside ? 1.0 : ng;
      float eta = n1 / n2, k = 1.0 - eta * eta * (1.0 - ci * ci);
      vec2 rr = d + 2.0 * ci * nn;
      if (k < 0.0) { d = rr; I *= 0.995; G *= pow(0.995, 0.6); }  // total internal reflection
      else {
        float ct = sqrt(k);
        float rs_ = (n1 * ci - n2 * ct) / (n1 * ci + n2 * ct), rp = (n1 * ct - n2 * ci) / (n1 * ct + n2 * ci);
        float R = 0.5 * (rs_ * rs_ + rp * rp);
        f[0] = 1.0 - R; f[1] = I * R > REFL_MIN ? R : 0.0;
        int c = choose(f, 2, I, G); if (c < 0) break;
        I *= f[c];
        if (c == 0) {
          d = normalize(eta * d + (eta * ci - ct) * nn);
          if (inside) { med = -1; } else { med = el; medAB = pr.xy; }
        } else d = rr;
      }
    } else if (kind == K_GRATING) {  // grating equation: sin θm = sin θi + mλ/d
      vec4 g2 = P(h, 2);
      vec2 nn = g2.xy, tt = g2.zw;
      if (dot(d, nn) < 0.0) nn = -nn;
      float si = dot(d, tt), dd = 1000.0 / pr.x, l = lam / 1000.0, sg = pr.z > 0.5 ? -1.0 : 1.0;
      int ord = int(pr.y + 0.5);
      for (int j = 0; j < 7; j++) {
        int m = j - 3;
        float s = si + float(m) * l / dd;
        f[j] = (abs(m) <= ord && s > -1.0 && s < 1.0) ? (m == 0 ? 0.32 : abs(m) == 1 ? 0.22 : abs(m) == 2 ? 0.07 : 0.035) : 0.0;
      }
      int c = choose(f, 7, I, G); if (c < 0) break;
      I *= f[c];
      float s = si + float(c - 3) * l / dd;
      d = s * tt + sg * sqrt(1.0 - s * s) * nn;
    } else if (kind == K_GRAV) {  // turn toward rising index by (∇n/n across the ray) × step
      vec4 g = P(h, 1), g2 = P(h, 2);
      vec2 qq = q - g.xy;
      float rho = length(qq), reach = g.z, mass = g.w;
      if (rho < reach && rho > mass) {
        float D = (nIdx(g2.xy, lam) - 1.0) / g2.z;
        float ee = min(0.5, (rho - mass) / 2.0);
        float gg = (gravN(rho + ee, reach, mass, D) - gravN(rho - ee, reach, mass, D)) / (2.0 * ee) / gravN(rho, reach, mass, D)
                   * min(t, gravStep(rho, mass) * 1.5);
        vec2 u = qq / rho;
        d = normalize(d + gg * (u - dot(u, d) * d));
      }
      depth -= 1.0 - 1.0 / 32.0;
    } else if (kind == K_SCREEN) {  // light landing on a screen: a short bright mark along it
      if (nv == want) { vec2 tt = P(h, 2).zw; s0 = q - tt * 2.5; s1 = q + tt * 2.5; sG = G * 1.3; got = true; }
      break;
    } else break;  // blocks and light housings absorb

    depth += 1.0;
    if (I < IMIN || depth > MAXD) break;
    p = q; skip = h; skipEl = int(a.z + 0.5);
  }

  if (got) {
    vec2 mid = (s0 + s1) * 0.5, dv = s1 - s0;
    float len = length(dv);
    if (uMode < 0.5) outv = vec4(mid.x, -mid.y, -degrees(atan(dv.y, dv.x)), len);
    else outv = vec4(colorOf(lam) * clamp(uBright * base * sG, 0.0, 1.0) / max(uCopies, 1.0), 1.0);
  }
  fragColor = TDOutputSwizzle(outv);
}
