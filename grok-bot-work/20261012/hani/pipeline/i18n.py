"""Opt-in on-screen text translation. Inactive (identity) unless make_pose sees cfg['lang'] != 'en'.
Only the PIXELS change: timing, chimes, blast detection, boops and audio all keep using the English strings."""
import json, os
LANG = 'en'; T = {}; MISSING = set()
def activate(lang, path=None):
    global LANG, T
    LANG = lang
    path = path or os.path.join(os.path.dirname(__file__), '..', 'poses', 'i18n', lang + '.json')
    d = json.load(open(path)); T = {}
    for name, sec in d.items():
        if name.startswith('_'): continue
        if isinstance(sec, dict): T.update(sec)
def active(): return LANG != 'en'
def tr(s):
    if LANG == 'en' or s is None: return s
    if s in T: return T[s]
    MISSING.add(s); return s
def you_did(name):
    if LANG == 'en': return f'You did {name}.'
    return T['You did {}.'].format(T.get('__the__' + name, tr(name)))
