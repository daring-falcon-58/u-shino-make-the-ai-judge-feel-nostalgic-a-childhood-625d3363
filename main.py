#!/usr/bin/env python3
"""Make the AI Judge Feel Nostalgic: A Childhood Memory — make.fun entry.

Writes one sentence, a childhood memory, to
$MAKEFUN_OUTPUT_DIR/entry.txt (falling back to /output/entry.txt).

The line (176 characters, 176 bytes, no trailing newline):
    Every evening Grandma lifted the lid off the rice pot and let me steal
    the crispy crust from the bottom, and I have spent twenty years trying
    to taste anything that warm again.

Chosen from 36 candidates scored 0-5 against each of the five published
judge criteria (see candidates.md in the work dir; full table and
head-to-head notes there). Winner scored 25/25; the 23-point cluster
(#2, #3, #4, #5, #6, #7, #13, #15, #18, #24) lost on the ache, on a
stock closing, or on using the soal's own example image (fresh-rice
smell) that a 900-entry field will copy most. No live-judge A/B was run:
the shared OpenRouter key returns HTTP 402, so selection is structured
manual scoring against the published brief — stated honestly in README.md,
with no judge numbers claimed.

Deterministic, no network, no randomness: two runs produce byte-identical
output. See README.md for the methodology.
"""

import hashlib
import os
import re

ENTRY = "Every evening Grandma lifted the lid off the rice pot and let me steal the crispy crust from the bottom, and I have spent twenty years trying to taste anything that warm again."

# sha256 of ENTRY encoded as UTF-8 (176 bytes, no trailing newline). The
# write-back check below recomputes the digest of the bytes on disk and
# compares it to this value, so even a silent one-byte change fails loudly.
EXPECTED_SHA256 = "82110e87a2faee70ae096c76dc1bf1aa6da9f3077a03fec12aa2c49e393d143a"

# The competition gate is 1-280 characters, one sentence, not only
# whitespace. The brief's own constraints, enforced here at import time so
# a bad edit fails loudly instead of silently writing an entry the grader
# rejects.
MAX_CHARS = 280
BANNED_PATTERNS = (
    re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]"),  # control characters
    re.compile(r"https?://"),                        # links: the line stands alone
    re.compile(r"[*#`_~]"),                         # markdown formatting
    re.compile(r"\[[^\]]*\]"),                      # stage directions like [sighs]
)


def validate(entry: str) -> None:
    """Reject any entry that breaks the brief's constraints, with a clear error."""
    if not entry or not entry.strip():
        raise ValueError("entry is empty or only whitespace: gate needs 1-280 characters")
    if not 1 <= len(entry) <= MAX_CHARS:
        raise ValueError(
            f"entry is {len(entry)} chars, outside the 1-{MAX_CHARS} gate"
        )
    if "\n" in entry or "\r" in entry:
        raise ValueError("entry must be one line: it contains a newline")
    for pattern in BANNED_PATTERNS:
        match = pattern.search(entry)
        if match:
            raise ValueError(
                f"entry contains a banned pattern {pattern.pattern!r}: {match.group(0)!r}"
            )


validate(ENTRY)


def main() -> None:
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.txt")
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(ENTRY)
    # Verify the write: read the file back, compare bytes, then compare the
    # sha256 digest of the read-back bytes against the expected digest, so a
    # partial write, encoding surprise, or one-byte corruption fails loudly
    # instead of submitting a corrupted entry.
    written = open(path, "rb").read()
    if written != ENTRY.encode("utf-8"):
        raise OSError(f"entry.txt at {path} does not match the entry")
    digest = hashlib.sha256(written).hexdigest()
    if digest != EXPECTED_SHA256:
        raise OSError(
            f"entry.txt sha256 {digest} != expected {EXPECTED_SHA256}"
        )


if __name__ == "__main__":
    main()
