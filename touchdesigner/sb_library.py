"""Saved setups for Spectrum Bench in TouchDesigner.

Two files next to your .toe, both plain text you can open in Notepad:

    setup_code.txt   the inbox. Save a setup code here and it loads straight away, and is added to the library.
    setups/          the library: one .txt per saved setup, named after the bench, each holding its code.

On spectrum_bench, the Setup menu switches between saved setups, Previous and Next step through them, Save adds
the code that's showing now, and Delete removes the selected one from the library (the file goes to setups/deleted).
"""
import os
import re
import shutil
import time

INBOX = 'setup_code.txt'
FOLDER = 'setups'
_seen = {}  # inbox path -> modified time last read


def _bench():
    return op('/project1/spectrum_bench')


def folder():
    f = os.path.join(project.folder, FOLDER)
    os.makedirs(f, exist_ok=True)
    return f


def inbox():
    return os.path.join(project.folder, INBOX)


def _code_in(text):
    """The setup code in some text, or None. Other lines around it are fine, and so is a code wrapped over lines."""
    lines = (text or '').splitlines()
    for i, line in enumerate(lines):
        m = re.search(r'SB1:[A-Za-z0-9+/=]*', line)
        if not m:
            continue
        code = m.group(0)
        for more in lines[i + 1:]:
            more = more.strip()
            if code.endswith('=') or not re.fullmatch(r'[A-Za-z0-9+/=]+', more):
                break
            code += more
        return code
    return None


def _name_of(code):
    try:
        return op('/project1/spectrum_bench/sb_scene').module.decode_code(code)['name']
    except Exception:
        return None


def _filename(name):
    s = re.sub(r'[<>:"/\\|?*\x00-\x1f]', '', name).strip().rstrip('.') or 'Setup'
    return s[:60] + '.txt'


def names():
    return sorted((f[:-4] for f in os.listdir(folder()) if f.lower().endswith('.txt')), key=str.lower)


def refresh(select=None):
    """Fills the Setup menu from the library folder."""
    B = _bench()
    n = names()
    B.par.Setup.menuNames = n or ['']
    B.par.Setup.menuLabels = n or ['(nothing saved yet)']
    if select is not None and select in n:
        B.store('sb_quiet', True)  # setting the menu shouldn't load the file again
        B.par.Setup = select
        B.store('sb_quiet', False)


def save(code, select=True):
    """Adds a code to the library under its bench's name. Returns the saved name, or None if it isn't a code."""
    code = _code_in(code)
    name = code and _name_of(code)
    if not name:
        return None
    fn = _filename(name)
    with open(os.path.join(folder(), fn), 'w', encoding='utf-8') as f:
        f.write(code + '\n')
    refresh(fn[:-4] if select else None)
    return fn[:-4]


def load(name):
    """Shows a saved setup."""
    p = os.path.join(folder(), name + '.txt')
    if not os.path.isfile(p):
        return
    with open(p, encoding='utf-8') as f:
        code = _code_in(f.read())
    if code:
        _bench().par.Setupcode = code


def step(d):
    n = names()
    if not n:
        return
    cur = _bench().par.Setup.eval()
    i = n.index(cur) if cur in n else (-1 if d > 0 else 0)
    pick = n[(i + d) % len(n)]
    refresh(pick)
    load(pick)


def delete():
    name = _bench().par.Setup.eval()
    p = os.path.join(folder(), name + '.txt')
    if name and os.path.isfile(p):
        trash = os.path.join(folder(), 'deleted')
        os.makedirs(trash, exist_ok=True)
        shutil.move(p, os.path.join(trash, name + '.txt'))
    refresh()


def on_par(par):
    """Called by the bench's Parameter Execute DAT."""
    B = _bench()
    if par.name == 'Setup' and not B.fetch('sb_quiet', False):
        load(par.eval())
    elif par.name == 'Savesetup':
        save(B.par.Setupcode.eval())
    elif par.name == 'Prevsetup':
        step(-1)
    elif par.name == 'Nextsetup':
        step(1)
    elif par.name == 'Deletesetup':
        delete()


def poll():
    """Called every frame; twice a second, loads setup_code.txt if it has changed."""
    now = time.monotonic()
    if now - _seen.get('at', 0) < 0.5:
        return
    _seen['at'] = now
    p = inbox()
    try:
        t = os.path.getmtime(p)
    except OSError:
        return
    if _seen.get(p) == t:
        return
    first = p not in _seen
    _seen[p] = t
    if first:
        return  # don't reload an old inbox every time the project opens
    with open(p, encoding='utf-8', errors='replace') as f:
        code = _code_in(f.read())
    if not code:
        return
    name = save(code)
    _bench().par.Setupcode = code
    print('Spectrum Bench: loaded "%s" from %s' % (name or 'setup', INBOX))


def start():
    """Makes the inbox and library on first run and saves the setup that's showing."""
    if not os.path.exists(inbox()):
        with open(inbox(), 'w', encoding='utf-8') as f:
            f.write('Paste a Spectrum Bench setup code here and save. It loads straight away.\n')
    _seen[inbox()] = os.path.getmtime(inbox())
    if not names():
        save(_bench().par.Setupcode.eval())
    refresh(_name_of(_bench().par.Setupcode.eval()))
