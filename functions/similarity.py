import difflib
from functions.normalize import normalize

def similarity(a, b):
    """Return similarity ratio [0.0, 1.0]"""
    return difflib.SequenceMatcher(None, normalize(a), normalize(b)).ratio()
