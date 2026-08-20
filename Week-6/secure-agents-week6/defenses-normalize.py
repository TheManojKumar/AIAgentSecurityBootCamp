# defenses-normalize.py — close the encoding-injection gap Garak found
#
# Garak's encoding probe smuggles injections past a keyword screen using base64,
# hex, rot13, unicode escapes, etc. Normalize/decode BEFORE the guardrail so the
# screen sees the real payload.
import base64
import binascii
import codecs
import re
import unicodedata
from tracing import init_tracing

init_tracing("week6-defenses-normalize")


def _try_base64(s: str) -> str:

    # Log this function call in Magenta color
    print('\033[95m', "=================================================================")
    print('\033[95m', "Calling _try_base64 ...")
    print('\033[95m', "=================================================================")

    try:
        # only decode long-ish base64-looking runs
        for m in re.findall(r"[A-Za-z0-9+/]{16,}={0,2}", s):
            try:
                dec = base64.b64decode(m, validate = True).decode("utf-8", "ignore")
                if dec.isprintable():
                    s += " " + dec
            except (binascii.Error, ValueError):
                pass
    except Exception:
        pass
    return s


def normalize(text: str) -> str:
    """Return an expanded string with likely-encoded payloads decoded inline,
    so downstream screening sees the plaintext intent."""

    # Log this function call in Magenta color
    print('\033[95m', "=================================================================")
    print('\033[95m', "Calling normalize ...")
    print('\033[95m', "=================================================================")

    s = unicodedata.normalize("NFKC", text)
    # rot13
    try:
        s += " " + codecs.decode(s, "rot13")
    except Exception:
        pass
    # hex escapes
    for m in re.findall(r"(?:[0-9a-fA-F]{2}\s?){8,}", s):
        try:
            s += " " + bytes.fromhex(m.replace(" ", "")).decode("utf-8", "ignore")
        except ValueError:
            pass
    s = _try_base64(s)
    return s
