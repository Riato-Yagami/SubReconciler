import re

def normalize(text):
    """Normalize text for similarity comparison"""
    text = text.replace("\n", " ")
    text = text.replace("…", "")
    text = text.replace("’", "'")     # unify apostrophes
    text = text.replace("“", '"').replace("”", '"')
    text = text.replace("—", "-")
    text = text.lower().strip()
    # optionally remove trailing punctuation differences
    text = re.sub(r'[^\w\s]', '', text)
    return text
