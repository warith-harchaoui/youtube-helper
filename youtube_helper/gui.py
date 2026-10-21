"""
YouTube Helper — minimal single-page GUI ("download bench").

Module summary
--------------
This module holds the self-contained HTML document served by the FastAPI app
at ``GET /gui`` (see :mod:`youtube_helper.api`). It is deliberately
build-step-free: one string of HTML + Tailwind (via CDN) + vanilla ES-module
JavaScript. There is no bundler, no framework, no npm.

Where the words live
--------------------
In the markup, in English. Each one is wrapped as ``{{_("…")}}`` in the HTML,
or listed in :data:`_JS_NAME_TO_SOURCE` for the script, and
:class:`os_helper.Catalog` translates it through the compiled ``gettext``
catalogues under ``locales/`` (CODING.md 21.3).

English is the msgid, so it needs no catalogue and cannot fall out of sync with
one; a string the French catalogue has not caught up with renders as readable
English instead of as a key. The cost is the mirror image: rewording the
English here orphans its French entry, and gettext would quietly serve the
English. ``tests/test_i18n.py`` exists to catch that — it hands every source
string to :meth:`os_helper.Catalog.problems`, so an orphaned translation is a
red build rather than a half-reverted page.

:func:`render_gui` resolves a language and returns the finished page.

Why a separate module
---------------------
Keeping the (long) HTML out of :mod:`youtube_helper.api` keeps the route
definitions readable and mirrors the AI Helpers suite convention. Other repos
copy this file almost verbatim: swap the form fields and the target endpoints,
keep the plumbing.

What the page does
------------------
- Paste a YouTube (or any yt-dlp-supported) URL — kept client-side until Run.
- Choose *audio* or *video*, and (for audio) a target sample rate.
- POST a JSON request to the SAME FastAPI endpoints the CLI surface
  uses (``/audio`` / ``/video``) — the GUI adds zero new server logic.
- Show a progress indicator while the (potentially long) download runs, then a
  download link and an inline ``<audio>`` / ``<video>`` player for the result.

Local-first
-----------
Everything runs against the local FastAPI app. youtube-helper fetches only the
media the user asks for from the source site; nothing is uploaded to a third
party, there is no telemetry and no account.

Author
------
Warith Harchaoui, Ph.D. — https://linkedin.com/in/warith-harchaoui/
"""

from __future__ import annotations

import functools
import html
import json
import re
from pathlib import Path

import os_helper as osh

# Inside the package, not beside it: a file one level up is not package data
# and does not travel in the wheel. best-engine shipped exactly that bug —
# `pip install` gave a package whose every GUI string raised FileNotFoundError.
_LOCALES_DIR = Path(__file__).resolve().parent / "locales"

#: The gettext domain, and therefore each ``.mo`` file's stem.
_DOMAIN = "youtube_helper"

#: The language served when the request names one we cannot render.
_DEFAULT_LANGUAGE = "fr"


@functools.lru_cache(maxsize=1)
def _catalog() -> osh.Catalog:
    """Resolve the catalogue directory once, through the suite's shared loader."""
    return osh.Catalog.from_package(_LOCALES_DIR, _DOMAIN, default_language=_DEFAULT_LANGUAGE)


def supported_languages() -> tuple[str, ...]:
    """Language codes the GUI can render: English plus every compiled catalogue."""
    return _catalog().languages


def default_language() -> str:
    """The language an unknown or absent ``?lang=`` falls back to."""
    return _catalog().default_language


# The language toggle is computed, not translated. Its three parts all mean
# "the other language", which is data rather than copy: a msgid of
# ``/gui?lang=fr`` whose translation is ``/gui?lang=en`` would be nonsense, and
# `Catalog.problems` would rightly treat it as prose that had drifted.
#
#: Flag shown for a language — the flag of that language, not of the page.
_FLAGS: dict[str, str] = {"fr": "🇫🇷", "en": "🇬🇧"}

#: How each language names itself. Deliberately NOT translated: a French page
#: offering English says "English version" in English, which is what a reader
#: scanning for their own language actually looks for.
_ENDONYMS: dict[str, str] = {"fr": "Version française", "en": "English version"}


# The inline script's strings. The JS names are the contract between this
# module and the script below; the English beside each one is the msgid, so
# the script's copy lives in the same place as the markup's and is checked
# by the same test. Injected as JSON, which is the one encoding an
# apostrophe cannot break out of — and French copy is full of them.
_JS_NAME_TO_SOURCE: dict[str, str] = {
    "needUrl": "Paste a media URL first.",
    "downloading": "Downloading… this can take a while for long videos.",
    "errorPrefix": "Error ",
    "done": "Done.",
    "requestFailed": "Request failed: ",
}


#: One ``{{_("…")}}`` site in the template. Non-greedy and newline-free, so a
#: run of them on one line stays separate and an unterminated one is left
#: alone rather than swallowing the rest of the page.
_SOURCE_RE = re.compile(r'\{\{_\("(.*?)"\)\}\}')

_GUI_TEMPLATE: str = r"""<!doctype html>
<html lang="{{LANG}}" class="h-full">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{{_("YouTube Helper — Download Bench")}}</title>
  <!-- Tailwind via CDN: keeps the page a single self-contained file, no build. -->
  <script src="https://cdn.tailwindcss.com"></script>
  <style>
    /* Respect users who ask for reduced motion (accessibility baseline). */
    @media (prefers-reduced-motion: reduce) { * { transition: none !important; animation: none !important; } }
  </style>
</head>
<body class="h-full bg-slate-50 text-slate-900 antialiased">
  <div class="mx-auto max-w-3xl px-4 py-8">
    <header class="mb-6">
      <a href="{{LANG_HREF}}" aria-label="{{LANG_ARIA}}"
         class="float-right text-xl hover:opacity-70">{{LANG_FLAG}}</a>
      <h1 class="text-2xl font-semibold tracking-tight">{{_("YouTube Helper — Download Bench")}}</h1>
      <p class="mt-1 text-sm text-slate-600">
        {{_("Paste a YouTube (or any yt-dlp-supported) URL, pick audio or video, run it on the local API, then play the result and download it.")}}
        <span class="font-medium">{{_("Local-first")}}</span> {{_("— nothing is uploaded to a third party.")}}
      </p>
    </header>

    <!-- 1) URL input. Kept entirely client-side until you press Run. -->
    <section class="mb-5">
      <label for="url" class="block text-sm font-medium mb-1">{{_("Media URL")}}</label>
      <input id="url" type="url" inputmode="url"
             placeholder="https://www.youtube.com/watch?v=YE7VzlLtp-4"
             class="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm
                    focus:outline-none focus:ring-2 focus:ring-blue-500" />
      <p class="mt-1 text-xs text-slate-500">
        {{_("Works with YouTube, Vimeo, DailyMotion, Twitch VOD, SoundCloud, and any other site yt-dlp supports.")}}
      </p>
    </section>

    <!-- 2) Kind selector: audio or video. Toggles the audio-only fields. -->
    <section class="mb-5">
      <label for="kind" class="block text-sm font-medium mb-1">{{_("What to download")}}</label>
      <select id="kind"
              class="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm
                     focus:outline-none focus:ring-2 focus:ring-blue-500">
        <option value="audio">{{_("audio — best audio track, re-encoded to mp3")}}</option>
        <option value="video">{{_("video — best video + audio, muxed to mp4")}}</option>
      </select>
    </section>

    <!-- 3) Per-kind parameter fields. Shown/hidden by the data-kinds list. -->
    <section id="params" class="mb-5 grid grid-cols-2 gap-3">
      <!-- Sample rate only applies to the audio path (video keeps source A/V). -->
      <div data-kinds="audio">
        <label for="sample_rate" class="block text-xs font-medium mb-1">{{_("sample rate (Hz)")}}</label>
        <select id="sample_rate"
                class="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm">
          <option value="16000">{{_("16000 — speech / STT")}}</option>
          <option value="22050">22050</option>
          <option value="44100" selected>{{_("44100 — CD quality (default)")}}</option>
          <option value="48000">{{_("48000 — video-grade")}}</option>
        </select>
      </div>
    </section>

    <!-- 4) Run button + status line (progress lives here; downloads can be long). -->
    <section class="mb-6">
      <button id="run"
              class="rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold text-white
                     hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500
                     disabled:opacity-50">
        {{_("Download")}}
      </button>
      <span id="status" class="ml-3 text-sm text-slate-600" role="status" aria-live="polite"></span>
    </section>

    <!-- 5) Result: inline player + download link. -->
    <section class="rounded-xl border border-slate-200 bg-white p-4">
      <h2 class="mb-2 text-sm font-medium">{{_("Result")}}</h2>
      <!-- Only one of these players is shown at a time, per the chosen kind. -->
      <audio id="out-audio" controls class="w-full" hidden></audio>
      <video id="out-video" controls class="w-full rounded-lg" hidden></video>
      <div id="out-empty" class="text-sm text-slate-500">{{_("Nothing downloaded yet.")}}</div>
      <a id="download"
         class="mt-3 inline-block text-sm font-medium text-blue-600 hover:underline"
         hidden download>{{_("Download result")}}</a>
    </section>
  </div>

  <script type="module">
    // Every human-readable string the script writes comes from the locale
    // file, injected as JSON so an apostrophe cannot break out of it.
    const T = {{T_JSON}};

    // --- tiny DOM helpers -------------------------------------------------
    const $ = (id) => document.getElementById(id);
    const status = (msg) => { $("status").textContent = msg; };

    // --- kind -> visible fields ------------------------------------------
    const kindSelect = $("kind");
    // Show only the parameter blocks whose data-kinds list contains the kind.
    function syncParams() {
      const kind = kindSelect.value;
      for (const el of document.querySelectorAll("#params [data-kinds]")) {
        el.hidden = !el.dataset.kinds.split(" ").includes(kind);
      }
    }
    kindSelect.addEventListener("change", syncParams);
    syncParams();

    // --- run: POST the JSON request to the existing /audio or /video route.
    // Both endpoints stream the resulting file back as bytes; we wrap the blob
    // in an object URL and hand it to the matching player + download link.
    $("run").addEventListener("click", async () => {
      const url = $("url").value.trim();
      // Guard: no point hitting the API without a URL.
      if (!url) { status(T.needUrl); return; }

      const kind = kindSelect.value;
      // Build the JSON body the FastAPI DownloadBody model expects.
      const body = { url };
      if (kind === "audio") body.sample_rate = parseInt($("sample_rate").value, 10);

      // Reset the result area before a fresh run.
      const outAudio = $("out-audio");
      const outVideo = $("out-video");
      const dl = $("download");
      outAudio.hidden = true; outVideo.hidden = true; dl.hidden = true;
      $("out-empty").hidden = true;

      // Downloads can take a while (yt-dlp + ffmpeg remux). Show a live hint
      // and disable the button so the user does not fire twice.
      status(T.downloading);
      $("run").disabled = true;
      try {
        // The endpoint path IS the kind: /audio or /video.
        const res = await fetch("/" + kind, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(body),
        });
        if (!res.ok) {
          // Surface the API's error text (truncated) rather than a bare status.
          const txt = await res.text();
          status(T.errorPrefix + res.status + ": " + txt.slice(0, 200));
          $("out-empty").hidden = false;
          return;
        }
        // Binary response: wrap in an object URL for the player + link.
        const blob = await res.blob();
        const objUrl = URL.createObjectURL(blob);
        if (kind === "audio") {
          outAudio.src = objUrl; outAudio.hidden = false;
          dl.download = "audio.mp3";
        } else {
          outVideo.src = objUrl; outVideo.hidden = false;
          dl.download = "video.mp4";
        }
        dl.href = objUrl;
        dl.hidden = false;
        status(T.done);
      } catch (err) {
        // Network / CORS / abort: report it, restore the empty hint.
        status(T.requestFailed + err);
        $("out-empty").hidden = false;
      } finally {
        $("run").disabled = false;
      }
    });
  </script>
</body>
</html>
"""


def render_gui(lang: str = "") -> str:
    """Render the single-page GUI in the requested language.

    Parameters
    ----------
    lang : str
        Two-letter language code. Anything outside the locale file's
        a compiled catalogue — including the empty string — falls back
        to ``meta.default_locale``, so an unknown ``?lang=`` never 500s.

    Returns
    -------
    str
        The complete HTML document for that language.

    Examples
    --------
    >>> "<!doctype html>" in render_gui("en")
    True
    >>> render_gui("tlh") == render_gui(default_language())
    True
    """
    cat = _catalog()
    resolved = cat.resolve(lang)
    translate = cat.translator_for(resolved).gettext

    # The other language, for the toggle. With two languages this is "the one
    # that is not current"; with more it is the next one round, which keeps the
    # flag a cycle rather than a dead end.
    languages = cat.languages
    other = languages[(languages.index(resolved) + 1) % len(languages)]

    def _render_source(match: re.Match[str]) -> str:
        """Translate one ``{{_("…")}}`` site and escape it for HTML.

        Escaping is not optional: these land in attributes (placeholder, alt,
        aria, title) as readily as in text nodes, and a French apostrophe in an
        attribute would close it early.
        """
        return html.escape(translate(match.group(1)), quote=True)

    page = _SOURCE_RE.sub(_render_source, _GUI_TEMPLATE)
    page = page.replace("{{LANG}}", html.escape(resolved, quote=True))
    page = page.replace("{{LANG_HREF}}", html.escape(f"/gui?lang={other}", quote=True))
    page = page.replace("{{LANG_FLAG}}", _FLAGS.get(other, other.upper()))
    page = page.replace("{{LANG_ARIA}}", html.escape(_ENDONYMS.get(other, other), quote=True))

    # The script's strings go in as JSON rather than as substituted text: it is
    # the encoding that cannot be broken out of by an apostrophe, and French
    # copy is full of them.
    table = {name: translate(source) for name, source in _JS_NAME_TO_SOURCE.items()}
    return page.replace("{{T_JSON}}", json.dumps(table, ensure_ascii=False))


def __getattr__(name: str) -> str:
    """Serve ``GUI_HTML`` on first access rather than building it at import.

    The module-level constant used to BE the page, and importers still reach
    for it. Assigning it eagerly would read and parse the locale file on every
    import of this package, including in callers that never serve the GUI — and
    a module-level ``__getattr__`` only fires for names that are NOT otherwise
    defined, so the name is deliberately left unbound rather than set to a
    placeholder.
    """
    if name == "GUI_HTML":
        return render_gui()
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
