"""Builds the Spectrum Bench network in TouchDesigner.

In TouchDesigner, save your .toe next to this touchdesigner folder (or set SB_DIR below), open the Textport
(Dialogs > Textport and DATs) and run:

    exec(open(project.folder + '/touchdesigner/build_td.py').read())

It makes /project1/spectrum_bench. Paste a setup code from the web bench ("Copy code for this bench") into its
Setup code parameter. Running it again replaces the network.
"""
import os

SB_DIR = globals().get('SB_DIR') or os.path.join(project.folder, 'touchdesigner')
PARENT = op('/project1')

# The Prism fan starter, so there's something on screen straight away
DEFAULT_CODE = ('SB1:eyJ2IjoyLCJuYW1lIjoiUHJpc20gZmFuIiwic2NlbmUiOlt7InR5cGUiOiJsaWdodCIsIngiOi0yNDQsInkiOjc5LCJhbmdsZSI6'
                'LTMzLjJ9LHsidHlwZSI6InByaXNtIiwieCI6LTIyLCJ5IjotMjB9LHsidHlwZSI6InNjcmVlbiIsIngiOjIyMCwieSI6OTUsImFu'
                'Z2xlIjoxMjMuMiwibGVuIjoyMzB9XSwiYnJpZ2h0IjoxfQ==')

STATE = "STATE = {}\n"

INFO_CB = r'''
# Decodes the setup code and packs the bench for the tracer. Its rows drive everything else.
def onCook(scriptOp):
    sb = op('sb_scene').module
    st = op('sb_state').module.STATE
    B = scriptOp.parent()
    code = B.par.Setupcode.eval()
    if code != st.get('code'):
        try:
            st['data'], st['err'] = sb.load_code(code), ''
        except Exception as e:
            st['data'], st['err'] = {'name': '', 'bright': 1.0, 'scene': []}, str(e)
        st['code'] = code
    d = st['data']
    animated = any(e['type'] == 'liquid' for e in d['scene'])
    pk = sb.pack(d, absTime.seconds if animated else 0.0, max_columns=int(B.par.Maxrays.eval()))
    st['pk'] = pk
    cx, cy, vw, vh = pk['view']
    w = max(vw, vh * 16 / 9)
    scriptOp.clear()
    for row in (('name', d['name']), ('error', st['err']), ('items', len(d['scene'])), ('nprims', pk['nprims']),
                ('nemit', pk['nemit']), ('copies', pk['copies']), ('columns', max(pk['columns'], 1)),
                ('tracew', pk['tracew']), ('traceh', pk['bands'] * sb.ROWS),
                ('bright', pk['bright']), ('cx', cx), ('cy', cy), ('width', w), ('linew', w / 1280 * 1.2),
                ('animated', int(animated)), ('frame', absTime.frame if animated else 0)):
        scriptOp.appendRow(list(row))
'''

TOP_CB = r'''
def onCook(scriptOp):
    op('info')['frame', 1]  # recook whenever the bench changes
    scriptOp.copyNumpyArray(op('sb_state').module.STATE['pk']['%s'])
'''

SOP_CB = r'''
# The pieces themselves, as thin outlines
def onCook(scriptOp):
    op('info')['frame', 1]
    scriptOp.clear()
    for line in op('sb_state').module.STATE['pk']['outlines']:
        poly = scriptOp.appendPoly(len(line), closed=False, addPoints=True)
        for i, (x, y) in enumerate(line):
            poly[i].point.P = (x, -y, 0)
'''

TICK_CB = r'''
# Liquids flow: repack every frame while there is one. Twice a second, look for a new code in setup_code.txt.
def onFrameStart(frame):
    if op('info')['animated', 1].val == '1':
        op('info').cook(force=True)
    op('sb_library').module.poll()
'''

LIBRARY_CB = r'''
# The Setup menu and the Previous, Next, Save and Delete buttons
def onValueChange(par, prev):
    op('sb_library').module.on_par(par)

def onPulse(par):
    op('sb_library').module.on_par(par)
'''

problems = []


def setp(o, name, value=None, expr=None):
    """Sets a parameter by name, noting it instead of failing if this TouchDesigner version names it differently."""
    p = getattr(o.par, name, None)
    if p is None:
        problems.append('%s has no parameter "%s"' % (o.path, name))
        return
    try:
        if expr is not None:
            p.expr = expr
            p.mode = ParMode.EXPRESSION
        else:
            p.val = value
    except Exception as e:
        problems.append('%s: could not set "%s" (%s)' % (o.path, name, e))


def setp_label(o, page, label, value):
    """Sets a parameter found by its page and label, for ones whose internal names vary between versions."""
    for p in o.pars():
        if p.page is not None and p.page.name == page and p.label == label:
            p.val = value
            return
    problems.append('%s: set "%s" on its %s page to %s by hand' % (o.path, label, page, value))


def info(name):
    return "float(op('info')['%s', 1].val)" % name


old = PARENT.op('spectrum_bench')
if old:
    old.destroy()
B = PARENT.create(baseCOMP, 'spectrum_bench')
B.nodeX, B.nodeY = 0, 0

pg = B.appendCustomPage('Bench')
pg.appendStrMenu('Setup', label='Setup')
pg.appendPulse('Prevsetup', label='Previous')
pg.appendPulse('Nextsetup', label='Next')
pg.appendPulse('Savesetup', label='Save')
pg.appendPulse('Deletesetup', label='Delete')
pg.appendStr('Setupcode', label='Setup code')
B.par.Setupcode = DEFAULT_CODE
pg.appendFloat('Brightness', label='Brightness')
B.par.Brightness.default = 1
B.par.Brightness = 1
B.par.Brightness.normMax = 4
pg.appendFloat('Audioamount', label='Audio rainbow spread')
B.par.Audioamount.normMax = 4
pg.appendInt('Maxrays', label='Max rays traced')
B.par.Maxrays.default = 8192
B.par.Maxrays = 8192
B.par.Maxrays.normMin, B.par.Maxrays.normMax = 1024, 16384
pg.appendFloat('Seed', label='Re-roll')
B.par.Seed.normMax = 10


def node(kind, name, x, y):
    o = B.create(kind, name)
    o.nodeX, o.nodeY = x, y
    return o


def text(name, x, y, content=None, path=None):
    t = node(textDAT, name, x, y)
    if path:
        t.par.file = path  # loads it; with sync on, edits to the file show up live
        setp(t, 'syncfile', True)
    else:
        t.text = content
    return t


text('sb_scene', -600, 300, path=os.path.join(SB_DIR, 'sb_scene.py'))
text('sb_trace', -600, 150, path=os.path.join(SB_DIR, 'sb_trace.frag'))
text('sb_state', -600, 0, STATE)
text('sb_library', -600, 450, path=os.path.join(SB_DIR, 'sb_library.py'))
lib_cb = node(parameterexecuteDAT, 'library_pars', -400, 600)
lib_cb.text = LIBRARY_CB
setp(lib_cb, 'op', B)
setp(lib_cb, 'pars', 'Setup Prevsetup Nextsetup Savesetup Deletesetup')
setp(lib_cb, 'valuechange', True)
setp(lib_cb, 'onpulse', True)

info_cb = text('info_callbacks', -400, 300, INFO_CB)
info_op = node(scriptDAT, 'info', -200, 300)
info_op.par.callbacks = info_cb
tick_cb = node(executeDAT, 'tick', -400, 450)
tick_cb.text = TICK_CB
setp(tick_cb, 'framestart', True)
setp(tick_cb, 'active', True)

tops = {}
for i, which in enumerate(('prims', 'emit')):
    cb = text(which + '_callbacks', -400, 100 - i * 150, TOP_CB % which)
    t = node(scriptTOP, which, -200, 100 - i * 150)
    t.par.callbacks = cb
    setp(t, 'format', 'rgba32float')
    tops[which] = t

# Audio: microphone level, smoothed, only listening while the amount is above zero
mic = node(audiodeviceinCHOP, 'mic', -400, -350)
setp(mic, 'active', expr='parent().par.Audioamount > 0')
lvl = node(analyzeCHOP, 'level', -200, -350)
lvl.inputConnectors[0].connect(mic)
setp(lvl, 'function', 'rmspower')
lag = node(lagCHOP, 'smooth', 0, -350)
lag.inputConnectors[0].connect(lvl)
setp(lag, 'lag1', 0.05)
setp(lag, 'lag2', 0.4)
audio = node(nullCHOP, 'audio', 200, -350)
audio.inputConnectors[0].connect(lag)

UNIFORMS = [('uNPrim', info('nprims')), ('uNEmit', info('nemit')), ('uCopies', info('copies')),
            ('uBright', info('bright') + ' * parent().par.Brightness'),
            ('uDisp', "1 + parent().par.Audioamount * (min(1, op('audio')[0].eval() * 8) if op('audio').numChans else 0)"),
            ('uSeed', 'parent().par.Seed')]
glsl = {}
for i, (name, mode) in enumerate((('trace_geo', 0), ('trace_col', 1))):
    g = node(glslTOP, name, 50, 100 - i * 150)
    g.inputConnectors[0].connect(tops['prims'])
    g.inputConnectors[1].connect(tops['emit'])
    setp(g, 'pixeldat', 'sb_trace')
    setp(g, 'outputresolution', 'custom')
    setp(g, 'resolutionw', expr="int(%s)" % info('tracew'))
    setp(g, 'resolutionh', expr="int(%s)" % info('traceh'))
    setp(g, 'format', 'rgba32float')
    for k, (u, e) in enumerate(UNIFORMS + [('uMode', str(mode))]):
        setp(g, 'vec%dname' % k, u)
        setp(g, 'vec%dvaluex' % k, expr=e)
    glsl[name] = g

# Each piece of path is one instance of a unit rectangle: moved to its middle, turned, stretched to its length
mat = node(constantMAT, 'ray_mat', 300, 250)
setp(mat, 'blending', True)
setp(mat, 'srcblend', 'one')
setp(mat, 'destblend', 'one')
setp(mat, 'depthtest', False)
setp(mat, 'depthwriting', False)

rays = node(geometryCOMP, 'rays', 300, 100)
for c in list(rays.children):
    c.destroy()
seg = rays.create(rectangleSOP, 'seg')
setp(seg, 'sizex', 1)
setp(seg, 'sizey', expr=info('linew').replace("op('info')", "op('../info')"))
seg.render = seg.display = True
rays.par.material = mat
setp(rays, 'instancing', True)
setp(rays, 'instanceop', glsl['trace_geo'])
setp(rays, 'instancetx', 'r')
setp(rays, 'instancety', 'g')
setp(rays, 'instancerz', 'b')
setp(rays, 'instancesx', 'a')
# Instance colors come from the second tracer output. Recent versions give each instance attribute its own OP.
col_op = [p for p in rays.pars('instance*op') if 'col' in (p.name + p.label).lower()]
if col_op:
    col_op[0].val = glsl['trace_col']
    for ch, lab in (('r', 'Color R'), ('g', 'Color G'), ('b', 'Color B')):
        p = getattr(rays.par, 'instance' + ch, None)  # 2023: instancer, instanceg, instanceb, labelled R, G, B
        if p is not None:
            p.val = ch
        else:
            setp_label(rays, col_op[0].page.name, lab, ch)
else:
    problems.append('rays: point instance colors at trace_col (r, g, b) on the Instance pages by hand')

pmat = node(constantMAT, 'piece_mat', 300, -250)
setp(pmat, 'colorr', .35)
setp(pmat, 'colorg', .38)
setp(pmat, 'colorb', .42)
pieces = node(geometryCOMP, 'pieces', 300, -100)
for c in list(pieces.children):
    c.destroy()
pcb = pieces.create(textDAT, 'outline_callbacks')
pcb.text = SOP_CB.replace("op('info')", "op('../info')").replace("op('sb_state')", "op('../sb_state')")
outline = pieces.create(scriptSOP, 'outline')
outline.par.callbacks = pcb
outline.render = outline.display = True
pieces.par.material = pmat

cam = node(cameraCOMP, 'cam', 300, 400)
setp(cam, 'projection', 'ortho')
setp(cam, 'orthowidth', expr=info('width'))
setp(cam, 'tx', expr=info('cx'))
setp(cam, 'ty', expr='-' + info('cy'))
setp(cam, 'tz', 100)
setp(cam, 'bgcolora', 1)  # an opaque black background (the camera holds it, not the Render TOP)

render = node(renderTOP, 'render', 550, 100)
render.par.camera = cam
render.par.geometry = 'rays pieces'
setp(render, 'outputresolution', 'custom')
setp(render, 'resolutionw', 1280)  # the Non-Commercial maximum; raise it with a paid key
setp(render, 'resolutionh', 720)
# 8-bit, so overlapping rays saturate at white the way the web bench's canvas does, instead of piling up past 1 and
# bleeding through the glow into a solid sheet
setp(render, 'format', 'rgba8fixed')

glow = node(blurTOP, 'glow', 750, 0)
glow.inputConnectors[0].connect(render)
setp(glow, 'size', 10)
final = node(compositeTOP, 'final', 950, 100)
final.inputConnectors[0].connect(render)
final.inputConnectors[1].connect(glow)
setp(final, 'operand', 'add')
out = node(nullTOP, 'out', 1150, 100)
out.inputConnectors[0].connect(final)
out.viewer = True

info_op.cook(force=True)
try:
    B.op('sb_library').module.start()
except Exception as e:
    problems.append('saved setups could not start (%s)' % e)
print('Spectrum Bench built at', B.path, '| bench:', info_op['name', 1].val, '|', info_op['items', 1].val, 'items')
print('Saved setups are in', os.path.join(project.folder, 'setups'), '| save a code to',
      os.path.join(project.folder, 'setup_code.txt'), 'to load it')
if info_op['error', 1].val:
    print('Setup code problem:', info_op['error', 1].val)
for p in problems:
    print('Check:', p)
