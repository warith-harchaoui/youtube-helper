"""
YouTube Helper — minimal single-page GUI ("download bench").

Module summary
--------------
This module holds nothing but the self-contained HTML document served by the
FastAPI app at ``GET /gui`` (see :mod:`youtube_helper.api`). It is deliberately
build-step-free: one string of HTML + Tailwind (via CDN) + vanilla ES-module
JavaScript. There is no bundler, no framework, no npm — the whole page is a
static asset the API returns verbatim.

Why a separate module
---------------------
Keeping the (long) HTML out of :mod:`youtube_helper.api` keeps the route
definitions readable and mirrors the AI Helpers suite convention (audio-helper's
``gui.py`` is the canonical template). Other repos copy this file almost
verbatim: swap the form fields and the target endpoints, keep the plumbing.

What the page does
------------------
- Paste a YouTube (or any yt-dlp-supported) URL — kept client-side until Run.
- Choose *audio* or *video*, and (for audio) a target sample rate.
- POST a JSON request to the SAME FastAPI endpoints the CLI and MCP surfaces
  use (``/audio`` / ``/video``) — the GUI adds zero new server logic.
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

# The entire GUI is this one HTML string. It is returned as-is by the
# ``/gui`` route. Tailwind is pulled from a CDN so there is no build step;
# the JavaScript is a single inline ES module talking to the existing API.
GUI_HTML: str = r"""<!doctype html>
<html lang="en" class="h-full">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>YouTube Helper — Download Bench</title>
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
      <h1 class="text-2xl font-semibold tracking-tight">YouTube Helper — Download Bench</h1>
      <p class="mt-1 text-sm text-slate-600">
        Paste a YouTube (or any yt-dlp-supported) URL, pick audio or video,
        run it on the local API, then play the result and download it.
        <span class="font-medium">Local-first</span> — nothing is uploaded to a third party.
      </p>
    </header>

    <!-- 1) URL input. Kept entirely client-side until you press Run. -->
    <section class="mb-5">
      <label for="url" class="block text-sm font-medium mb-1">Media URL</label>
      <input id="url" type="url" inputmode="url"
             placeholder="https://www.youtube.com/watch?v=YE7VzlLtp-4"
             class="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm
                    focus:outline-none focus:ring-2 focus:ring-blue-500" />
      <p class="mt-1 text-xs text-slate-500">
        Works with YouTube, Vimeo, DailyMotion, Twitch VOD, SoundCloud, and any
        other site yt-dlp supports.
      </p>
    </section>

    <!-- 2) Kind selector: audio or video. Toggles the audio-only fields. -->
    <section class="mb-5">
      <label for="kind" class="block text-sm font-medium mb-1">What to download</label>
      <select id="kind"
              class="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm
                     focus:outline-none focus:ring-2 focus:ring-blue-500">
        <option value="audio">audio — best audio track, re-encoded to mp3</option>
        <option value="video">video — best video + audio, muxed to mp4</option>
      </select>
    </section>

    <!-- 3) Per-kind parameter fields. Shown/hidden by the data-kinds list. -->
    <section id="params" class="mb-5 grid grid-cols-2 gap-3">
      <!-- Sample rate only applies to the audio path (video keeps source A/V). -->
      <div data-kinds="audio">
        <label for="sample_rate" class="block text-xs font-medium mb-1">sample rate (Hz)</label>
        <select id="sample_rate"
                class="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm">
          <option value="16000">16000 — speech / STT</option>
          <option value="22050">22050</option>
          <option value="44100" selected>44100 — CD quality (default)</option>
          <option value="48000">48000 — video-grade</option>
        </select>
      </div>
    </section>

    <!-- 4) Run button + status line (progress lives here; downloads can be long). -->
    <section class="mb-6">
      <button id="run"
              class="rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold text-white
                     hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500
                     disabled:opacity-50">
        Download
      </button>
      <span id="status" class="ml-3 text-sm text-slate-600" role="status" aria-live="polite"></span>
    </section>

    <!-- 5) Result: inline player + download link. -->
    <section class="rounded-xl border border-slate-200 bg-white p-4">
      <h2 class="mb-2 text-sm font-medium">Result</h2>
      <!-- Only one of these players is shown at a time, per the chosen kind. -->
      <audio id="out-audio" controls class="w-full" hidden></audio>
      <video id="out-video" controls class="w-full rounded-lg" hidden></video>
      <div id="out-empty" class="text-sm text-slate-500">Nothing downloaded yet.</div>
      <a id="download"
         class="mt-3 inline-block text-sm font-medium text-blue-600 hover:underline"
         hidden download>Download result</a>
    </section>
  </div>

  <script type="module">
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
      if (!url) { status("Paste a media URL first."); return; }

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
      status("Downloading… this can take a while for long videos.");
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
          status("Error " + res.status + ": " + txt.slice(0, 200));
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
        status("Done.");
      } catch (err) {
        // Network / CORS / abort: report it, restore the empty hint.
        status("Request failed: " + err);
        $("out-empty").hidden = false;
      } finally {
        $("run").disabled = false;
      }
    });
  </script>
</body>
</html>
"""
