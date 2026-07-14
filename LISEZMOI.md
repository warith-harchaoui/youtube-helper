# YouTube Helper

[🇫🇷](LISEZMOI.md) · [🇬🇧](README.md)

[![CI](https://github.com/warith-harchaoui/youtube-helper/actions/workflows/ci.yml/badge.svg)](https://github.com/warith-harchaoui/youtube-helper/actions/workflows/ci.yml) [![License: BSD-3-Clause](https://img.shields.io/badge/License-BSD%203--Clause-blue.svg)](LICENSE) [![Python](https://img.shields.io/badge/python-3.10%E2%80%933.13-blue.svg)](#)

`YouTube Helper` fait partie d'une collection de bibliothèques appelée `AI Helpers`, développée pour bâtir des applications d'intelligence artificielle.

[🌍 AI Helpers](https://harchaoui.org/warith/ai-helpers)

[![logo](assets/logo.png)](https://harchaoui.org/warith/ai-helpers)

YouTube Helper est une bibliothèque Python qui fournit des fonctions utilitaires pour télécharger des vidéos, de l'audio et des vignettes depuis des plateformes comme YouTube, Vimeo et DailyMotion grâce à `yt-dlp`.
Elle supporte également les tâches de post-traitement comme la conversion ou la fusion de fichiers média avec `ffmpeg`.

# Documentation

[💻 Documentation](https://harchaoui.org/warith/ai-helpers/docs/youtube-helper-doc/)

[📋 Exemples](https://github.com/warith-harchaoui/youtube-helper/blob/main/EXAMPLES.md)

# Installation

**Prérequis** — **Python 3.10–3.13** et **git**, **ffmpeg**, multiplateforme :

- 🍎 **macOS** ([Homebrew](https://brew.sh)) : `brew install python git ffmpeg`
- 🐧 **Ubuntu/Debian** : `sudo apt update && sudo apt install -y python3 python3-pip git ffmpeg`
- 🪟 **Windows** (PowerShell) : `winget install Python.Python.3.12 Git.Git Gyan.FFmpeg`

Puis installer le paquet :


## Installer le paquet

Nous recommandons l'utilisation d'environnements Python. Consultez ce lien si vous ne savez pas comment faire :

[🥸 Conseils techniques](https://harchaoui.org/warith/4ml/#install)

### Installer `yt-dlp` et `ffmpeg`

Pour installer YouTube Helper, vous devez installer les dépendances suivantes :

- Sous macOS 🍎

Récupérez [brew](https://brew.sh) et installez les paquets nécessaires :
```bash
brew install yt-dlp
brew install ffmpeg
```

- Sous Ubuntu 🐧
```bash
sudo apt install yt-dlp
sudo apt install ffmpeg
```

- Sous Windows 🪟
  - `yt-dlp` : téléchargez [yt-dlp depuis son dépôt](https://github.com/yt-dlp/yt-dlp) et suivez les instructions.
  - `ffmpeg` : allez sur le [site FFmpeg](https://ffmpeg.org/download.html) et suivez les instructions. Il faut ajouter manuellement FFmpeg au PATH système.

## Installer `YouTube Helper` :
```bash
pip install --force-reinstall --no-cache-dir git+https://github.com/warith-harchaoui/youtube-helper.git@v1.3.3
```

# Utilisation

Pour le catalogue complet d'exemples (téléchargements, catalogue de flux / picker, résolveur d'URL directe, composition avec `video-helper`, métadonnées de branding, sous-titres et commentaires), voir [📋 EXAMPLES.md](EXAMPLES.md).

Démarrage rapide — télécharger une vidéo, extraire les métadonnées, et télécharger l'audio :

```python
import youtube_helper as yth
import video_helper as vh
import audio_helper as ah
import os_helper as osh
import os

osh.verbosity(0)

# URL YouTube d'exemple
youtube_url = "https://www.youtube.com/watch?v=YE7VzlLtp-4"

folder = "yt_tests"
os.makedirs(folder, exist_ok=True)

# Télécharger une vidéo
video = "big-buck-bunny.mp4"
video = os.path.join(folder, video)
yth.download_video(youtube_url, video)

# Extraire les métadonnées depuis l'URL de la vidéo
metadata = yth.video_url_meta_data(youtube_url)
print(metadata["title"])
# Big Buck Bunny

print(metadata["duration"])
# 597

print(metadata["description"])
# Big Buck Bunny tells the story of a giant rabbit with a heart bigger than himself…

print(metadata["channel"])
# Blender

details = vh.video_dimensions(video)
print(details)
# {'width': 1280, 'height': 720, 'duration': 596.458, 'frame_rate': 24.0, 'has_sound': True}

# Télécharger l'audio depuis la vidéo
audio = "big-buck-bunny.mp3"
audio = os.path.join(folder, audio)
yth.download_audio(youtube_url, audio)

audio, sample_rate = ah.load_audio(audio)
print(sample_rate)
# 44100
```

# Usage légal et éthique

YouTube Helper est un wrapper léger autour de `yt-dlp` et `ffmpeg`. Vous êtes responsable de la manière dont vous l'utilisez. Ne téléchargez et ne traitez que des contenus que vous possédez, qui sont dans le domaine public, sous licence permissive (par ex. Creative Commons), ou pour lesquels vous avez une autorisation explicite du détenteur des droits. Respectez les Conditions d'Utilisation de chaque plateforme et les lois applicables en matière de droit d'auteur, de vie privée et de protection des données. Les auteurs fournissent cette bibliothèque pour des usages légitimes : archivage personnel, accessibilité, recherche, contenus dont vous détenez les droits — pas pour contourner des contrôles d'accès ou redistribuer du contenu protégé.

# Fonctionnalités

**Téléchargements (sur disque)** — `youtube_helper.main`
- `download_video(url, output_path)` / `download_audio(url, output_path)` / `download_thumbnail(url, output_path)`.
- `video_url_meta_data(url)` / `is_valid_video_url(url)` pour des sondes de métadonnées légères.
- `default_ytdlp_options(verbose, ...)` pour personnaliser les options yt-dlp.

**Catalogue de flux & résolution d'URL directe** — `youtube_helper.streaming`
- `resolve_direct_url(url, prefer="audio"|"video")` → un raccourci "donne-moi une URL directe prête à passer à ffmpeg".
- `list_video_streams(url)` → énumère chaque format vidéo trouvé par yt-dlp (codec, résolution, fps, bitrate, …).
- `pick_video_stream(url, prefer_codec=, prefer_format=, max_fps=, language=, cookies_from_browser=)` → picker contraint, retourne un `VideoStreamInfo` prêt à alimenter `video_helper.extract_frames`.
- `extract_frames_stream(url, ..., **extract_frames_kwargs)` → composition en un appel de `pick_video_stream` + `video_helper.extract_frames`, câble les headers automatiquement, forwarde n'importe quel kwarg d'`extract_frames` (`destination`, `device`, `batch_size`, `output_width`, `frame_step`, …). Le chemin le plus court d'une URL YouTube / Vimeo / Twitch vers des frames prêtes pour le ML.
- Le catalogue / picker de flux audio vit volontairement dans **podcast-helper** (propriétaire unique du streaming PCM audio).

**Métadonnées d'engagement sans API** — `youtube_helper.branding`
- `channel_info(url)` / `channel_videos(url, max_videos, include_shorts, include_lives)` — snapshot de chaîne + liste paginée de vidéos avec métriques d'engagement normalisées, schéma multi-plateforme.
- `video_engagement(url)` / `engagement_batch([urls])` — vues / likes / commentaires par vidéo et nombre d'abonnés de la chaîne, variante batch tolérante.
- `video_subtitles(url, output_dir, langs=("fr","en"))` — téléchargement automatique de sous-titres.
- `video_comments(url, max_count, cookies_from_browser="firefox"|"chrome"|...)` — échantillon de commentaires.
- `is_short(meta)` / `ensure_recent_ytdlp(min_version)` — utilitaires.
- Bâti uniquement sur les métadonnées publiques de yt-dlp — **pas d'API Google Data, pas d'API Vimeo, pas d'OAuth, pas de quota.**

# Exposition multi-surface

`youtube-helper` n'est pas seulement une bibliothèque — les mêmes
fonctions sont exposées comme CLI, comme surface HTTP FastAPI et comme
outils MCP :

```bash
# Bibliothèque Python (par défaut)
import youtube_helper as yth

# CLI argparse (installée automatiquement)
youtube-helper metadata     --url https://www.youtube.com/watch?v=YE7VzlLtp-4
youtube-helper audio        --url https://www.youtube.com/watch?v=YE7VzlLtp-4 --output out.mp3
youtube-helper resolve      --url https://www.youtube.com/watch?v=YE7VzlLtp-4 --prefer audio
youtube-helper channel-info --url https://www.youtube.com/@blender

# Jumeau CLI click (nécessite l'extra [cli])
pip install 'youtube-helper[cli] @ git+https://github.com/warith-harchaoui/youtube-helper.git@v1.3.3'
youtube-helper-click metadata --url https://www.youtube.com/watch?v=YE7VzlLtp-4

# Surface HTTP FastAPI (nécessite l'extra [api])
pip install 'youtube-helper[api] @ git+https://github.com/warith-harchaoui/youtube-helper.git@v1.3.3'
uvicorn youtube_helper.api:app --port 8000
# → doc OpenAPI sur http://localhost:8000/docs

# Outils MCP au-dessus de FastAPI (nécessite les extras [api,mcp])
pip install 'youtube-helper[api,mcp] @ git+https://github.com/warith-harchaoui/youtube-helper.git@v1.3.3'
youtube-helper-mcp                # sert FastAPI + MCP sur le port 8000
```

Image Docker :

```bash
docker build -t youtube-helper .
docker run --rm -p 8000:8000 youtube-helper
```

Un plan innovant de GUI (bibliothèque vidéo, comparateur de chaînes,
downloader batch) est dans [GUI.md](GUI.md).

L'analyse du paysage concurrentiel (yt-dlp, pytubefix, YouTube Data API,
streamlink, ArchiveBox, …) est dans [LANDSCAPE.md](LANDSCAPE.md).

# Auteur
 - [Warith HARCHAOUI](https://linkedin.com/in/warith-harchaoui)

# Remerciements
Remerciements chaleureux à [Mohamed Chelali](https://mchelali.github.io) et [Bachir Zerroug](https://www.linkedin.com/in/bachirzerroug) pour nos échanges fructueux.
