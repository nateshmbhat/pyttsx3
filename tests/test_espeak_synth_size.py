"""Regression tests for issue #448: the espeak driver told espeak_Synth the
text buffer was ``len(text) * 10`` bytes.

espeak-ng copies exactly ``size`` bytes from the caller's pointer into its
internal utterance buffer, so the oversized value made every ``say()`` read up
to 9x the utterance length past the end of the Python ``bytes`` object —
silently for short texts (Valgrind flags the sweep through adjacent heap), and
as a hard interpreter segfault for large texts whose allocation is mmap-backed
(the over-read runs off the end of the mapping).

Both tests fail on the pre-fix driver and pass with ``size = len(text) + 1``:

* ``test_synth_reports_true_buffer_size`` asserts the size argument itself —
  red/green without needing a crash;
* ``test_large_utterance_does_not_segfault`` is the crash demonstration: a
  subprocess speaks a 2 MB utterance; pre-fix it dies with SIGSEGV before
  producing any output.
"""

from __future__ import annotations

import subprocess
import sys
from unittest import mock

import pytest

pytestmark = pytest.mark.skipif(
    sys.platform in ("win32", "cygwin", "darwin"),
    reason="the espeak driver's ctypes binding is only used on Linux/other",
)


def test_synth_reports_true_buffer_size() -> None:
    """``Synth`` must pass the real buffer size (bytes + NUL) to espeak_Synth.

    espeak-ng allocates ``size + 1`` bytes internally and copies ``size``
    bytes from the caller's buffer, so any value larger than the actual
    allocation reads out of bounds.  A NUL-terminated UTF-8 ``bytes`` of
    length n occupies n + 1 bytes — the same value ``Synth_Mark`` passes.
    """
    _espeak = pytest.importorskip("pyttsx3.drivers._espeak", reason="libespeak-ng not installed")
    utterance = b"hello"

    with mock.patch.object(_espeak, "cSynth") as spy:
        _espeak.Synth(utterance.decode("utf-8"))

    assert spy.call_count == 1
    text, size = spy.call_args[0][0], spy.call_args[0][1]
    assert text == utterance
    assert size == len(utterance) + 1


def test_large_utterance_does_not_segfault() -> None:
    """A 2 MB utterance must not crash the interpreter (issue #448).

    Pre-fix, ``espeak_Synth`` was told the buffer was 20 MB and its internal
    copy of the input ran ~18 MB past the mmap-backed ``bytes`` object —
    SIGSEGV. That copy is the very first thing ``espeak_Synth`` does, before
    any audio is produced, so the crash happens before the synth callback ever
    fires. The child runs in AUDIO_OUTPUT_RETRIEVAL mode with a callback that
    returns 1 (abort) on the first buffer, so on the fixed driver it stops
    almost immediately instead of synthesizing all 2 MB — keeping the passing
    case fast while still exercising the full-size copy.

    The child exits via ``os._exit(0)`` the instant it survives the synth call.
    espeak keeps a background worker thread alive, and on Python 3.14 that
    thread's local-storage teardown aborts interpreter finalization (SIGABRT,
    ``gilstate_tss_set: failed to set current tstate``) — unrelated to the
    over-read this test guards, and it would otherwise mask a clean pass as a
    crash.  A real regression still dies *inside* ``Synth`` (SIGSEGV, returncode
    -11) long before that exit is reached, so the check keeps its teeth.
    """
    pytest.importorskip("pyttsx3.drivers._espeak", reason="libespeak-ng not installed")

    child = """
import os
import sys

from pyttsx3.drivers import _espeak

rate = _espeak.Initialize(_espeak.AUDIO_OUTPUT_RETRIEVAL, 1000)
assert rate != -1, "espeak failed to initialize"

def on_synth(wav, numsamples, events):
    return 1  # abort synthesis after the first buffer

_espeak.SetSynthCallback(on_synth)   # module wraps + keeps the C callback alive
# Pre-fix, size = len(text) * 10 = 20 MB -> out-of-bounds copy -> SIGSEGV here,
# before on_synth is ever called.
_espeak.Synth("x" * 2_000_000, flags=_espeak.CHARS_UTF8)
print("OK: survived the 2 MB utterance")
sys.stdout.flush()
# Surviving Synth is the whole assertion.  Skip interpreter finalization (and
# espeak's background-thread TSS teardown, which aborts on Python 3.14) so the
# probe reports the synth result, not an unrelated shutdown wart.
os._exit(0)
"""
    result = subprocess.run(
        [sys.executable, "-c", child],
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )

    assert result.returncode == 0, (
        f"child exited with {result.returncode} "
        f"(negative means killed by that signal; -11 is SIGSEGV)\n"
        f"stdout: {result.stdout!r}\nstderr: {result.stderr!r}"
    )
    assert "OK: survived the 2 MB utterance" in result.stdout
