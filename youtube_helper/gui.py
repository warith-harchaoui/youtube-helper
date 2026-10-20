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
Not here. Every human-readable string comes from ``locales/i18n.yaml`` through
:class:`os_helper.Locales`, the loader shared across the suite (CODING.md
21.3). The markup below is tokenised — ``{{TOKEN}}`` in HTML, and a ``T``
object injected for the script — so one template serves every language and a
translator never touches Python.

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
from pathlib import Path

import os_helper as osh

# Inside the package, not beside it: a file one level up is not package data
# and does not travel in the wheel. best-engine shipped exactly that bug —
# `pip install` gave a package whose every GUI string raised FileNotFoundError.
_LOCALES_PATH = Path(__file__).resolve().parent / "locales" / "i18n.yaml"

#: The section of the locale file this module reads.
_GUI_SECTION = "gui"


@functools.lru_cache(maxsize=1)
def _locales() -> osh.Locales:
    """Parse ``locales/i18n.yaml`` once, through the suite's shared loader."""
    return osh.Locales.from_path(_LOCALES_PATH)


def supported_languages() -> tuple[str, ...]:
    """Language codes the GUI can render, as declared by the locale file."""
    return tuple(_locales().supported_locales)


def default_language() -> str:
    """The language an unknown or absent ``?lang=`` falls back to."""
    return _locales().default_locale


# Two vocabularies meet here: the template's tokens and the locale file's
# semantic keys. These maps bridge them. `_HTML_TOKEN_TO_KEY` fills {{TOKEN}}
# placeholders; `_JS_NAME_TO_KEY` builds the `const T = {...}` the script reads.
_HTML_TOKEN_TO_KEY: dict[str, str] = {
    "PAGE_TITLE": "page_title",
    "HERO_TITLE": "hero_title",
    "HERO_P": "hero_subtitle",
    "LOCAL_BADGE": "local_first_badge",
    "LOCAL_TAIL": "local_first_tail",
    "URL_LABEL": "url_label",
    "URL_PLACEHOLDER": "url_placeholder",
    "URL_HINT": "url_hint",
    "KIND_LABEL": "kind_label",
    "KIND_AUDIO": "kind_audio",
    "KIND_VIDEO": "kind_video",
    "SR_LABEL": "sample_rate_label",
    "SR_16000": "sample_rate_16000",
    "SR_44100": "sample_rate_44100",
    "SR_48000": "sample_rate_48000",
    "RUN_BUTTON": "run_button",
    "RESULT_H2": "result_heading",
    "RESULT_EMPTY": "result_empty",
    "DOWNLOAD_LINK": "download_link",
    "LANG_HREF": "lang_toggle_href",
    "LANG_FLAG": "lang_toggle_flag",
    "LANG_ARIA": "lang_toggle_aria",
}

_JS_NAME_TO_KEY: dict[str, str] = {
    "needUrl": "js_need_url",
    "downloading": "js_downloading",
    "errorPrefix": "js_error_prefix",
    "done": "js_done",
    "requestFailed": "js_request_failed",
}


# The document template. Human-facing text is tokenised as {{TOKEN}} (HTML) or
# read from the injected `T` object (JavaScript), so this markup is shared by
# every language.
_GUI_TEMPLATE: str = r"""<!doctype html>
<html lang="{{LANG}}" class="h-full">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{{PAGE_TITLE}}</title>
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
      <h1 class="text-2xl font-semibold tracking-tight">{{HERO_TITLE}}</h1>
      <p class="mt-1 text-sm text-slate-600">
        {{HERO_P}}
        <span class="font-medium">{{LOCAL_BADGE}}</span> {{LOCAL_TAIL}}
      </p>
    </header>

    <!-- 1) URL input. Kept entirely client-side until you press Run. -->
    <section class="mb-5">
      <label for="url" class="block text-sm font-medium mb-1">{{URL_LABEL}}</label>
      <input id="url" type="url" inputmode="url"
             placeholder="{{URL_PLACEHOLDER}}"
             class="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm
                    focus:outline-none focus:ring-2 focus:ring-blue-500" />
      <p class="mt-1 text-xs text-slate-500">
        {{URL_HINT}}
      </p>
    </section>

    <!-- 2) Kind selector: audio or video. Toggles the audio-only fields. -->
    <section class="mb-5">
      <label for="kind" class="block text-sm font-medium mb-1">{{KIND_LABEL}}</label>
      <select id="kind"
              class="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm
                     focus:outline-none focus:ring-2 focus:ring-blue-500">
        <option value="audio">{{KIND_AUDIO}}</option>
        <option value="video">{{KIND_VIDEO}}</option>
      </select>
    </section>

    <!-- 3) Per-kind parameter fields. Shown/hidden by the data-kinds list. -->
    <section id="params" class="mb-5 grid grid-cols-2 gap-3">
      <!-- Sample rate only applies to the audio path (video keeps source A/V). -->
      <div data-kinds="audio">
        <label for="sample_rate" class="block text-xs font-medium mb-1">{{SR_LABEL}}</label>
        <select id="sample_rate"
                class="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm">
          <option value="16000">{{SR_16000}}</option>
          <option value="22050">22050</option>
          <option value="44100" selected>{{SR_44100}}</option>
          <option value="48000">{{SR_48000}}</option>
        </select>
      </div>
    </section>

    <!-- 4) Run button + status line (progress lives here; downloads can be long). -->
    <section class="mb-6">
      <button id="run"
              class="rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold text-white
                     hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500
                     disabled:opacity-50">
        {{RUN_BUTTON}}
      </button>
      <span id="status" class="ml-3 text-sm text-slate-600" role="status" aria-live="polite"></span>
    </section>

    <!-- 5) Result: inline player + download link. -->
    <section class="rounded-xl border border-slate-200 bg-white p-4">
      <h2 class="mb-2 text-sm font-medium">{{RESULT_H2}}</h2>
      <!-- Only one of these players is shown at a time, per the chosen kind. -->
      <audio id="out-audio" controls class="w-full" hidden></audio>
      <video id="out-video" controls class="w-full rounded-lg" hidden></video>
      <div id="out-empty" class="text-sm text-slate-500">{{RESULT_EMPTY}}</div>
      <a id="download"
         class="mt-3 inline-block text-sm font-medium text-blue-600 hover:underline"
         hidden download>{{DOWNLOAD_LINK}}</a>
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
        ``meta.supported_locales`` — including the empty string — falls back
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
    resolved = lang if lang in supported_languages() else default_language()
    loc = _locales()

    page = _GUI_TEMPLATE.replace("{{LANG}}", html.escape(resolved, quote=True))
    for token, key in _HTML_TOKEN_TO_KEY.items():
        # Escape every value: these land in attributes (placeholder, aria,
        # href) as readily as in text nodes, and a stray quote would break out
        # of the attribute it sits in.
        value = html.escape(loc.text(_GUI_SECTION, key, resolved), quote=True)
        page = page.replace("{{" + token + "}}", value)

    # The script's strings go in as JSON rather than as substituted text: it is
    # the encoding that cannot be broken out of by an apostrophe, and French
    # copy is full of them.
    table = {name: loc.text(_GUI_SECTION, key, resolved) for name, key in _JS_NAME_TO_KEY.items()}
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
