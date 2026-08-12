# Exemples YouTube Helper

Recettes pratiques pour les trois couches de `youtube-helper`. Chaque
extrait suppose :

```python
import youtube_helper as yth
import os_helper as osh

osh.verbosity(2)   # so osh.info(...) calls surface on stdout
```

et que `yt-dlp` et `ffmpeg` sont installés (`brew install yt-dlp ffmpeg`
sur macOS : installez `brew` grâce à [brew.sh](https://brew.sh/)).

---

## Table des matières

1. [Installation](#installation)
2. [Téléchargements (sur disque)](#téléchargements-sur-disque)
3. [Catalogue de flux et sélecteur](#catalogue-de-flux-et-sélecteur)
4. [Résolveur d'URL directe](#résolveur-durl-directe)
5. [Composition avec video-helper](#composition-avec-video-helper)
6. [Branding : métadonnées d'engagement sans clé d'API](#branding--métadonnées-dengagement-sans-clé-dapi)
7. [Sous-titres, commentaires, chaînes](#sous-titres-commentaires-chaînes)
8. [Pièges à connaître](#pièges-à-connaître)

---

## Installation

```bash
pip install --force-reinstall --no-cache-dir \
  youtube-helper
```

Embarque automatiquement `os-helper`, `audio-helper` et `video-helper`.
Il vous reste à mettre `yt-dlp` et `ffmpeg` sur le PATH (voir le README).

## Téléchargements (sur disque)

La surface d'origine de `youtube-helper` : récupérer un fichier en
stockage local.

```python
yth.download_video("https://www.youtube.com/watch?v=YE7VzlLtp-4", "bunny.mp4")
yth.download_audio("https://www.youtube.com/watch?v=YE7VzlLtp-4", "bunny.mp3")
yth.download_thumbnail("https://www.youtube.com/watch?v=YE7VzlLtp-4", "bunny.jpg")

# Sonde de métadonnées légère (sans téléchargement)
meta = yth.video_url_meta_data("https://www.youtube.com/watch?v=YE7VzlLtp-4")
print(meta["title"], meta["duration"])
# Big Buck Bunny 596
```

## Catalogue de flux et sélecteur

Là où `download_*` écrit un fichier, les fonctions de catalogue et de
sélection vous rendent une **URL média directe** accompagnée de ses
en-têtes : un décodeur en aval (PyAV, ffmpeg, `video_helper.extract_frames`)
peut alors la lire sans repasser par yt-dlp.

```python
# Énumère tous les formats vidéo que yt-dlp trouve.
streams = yth.list_video_streams("https://www.youtube.com/watch?v=YE7VzlLtp-4")
for s in streams[:5]:
    print(f"{s['format_id']:6} {s['width']}x{s['height']} {s['fps']}fps "
          f"{s['vcodec']:14} {s['ext']:6} ~{s['vbr_kbps']:.0f} kbps")
# 160     256x144   30.0 avc1.42c00c   mp4    ~  110 kbps
# 278     256x144   30.0 vp09.00.11... webm   ~  102 kbps
# ...

# Choisit celui qui correspond à vos contraintes : le meilleur candidat yt-dlp parmi les correspondances.
pick = yth.pick_video_stream(
    "https://www.youtube.com/watch?v=YE7VzlLtp-4",
    prefer_codec="h264",   # also matches "avc1.xxx"
    prefer_format="mp4",
    max_fps=30,
)
# pick est un VideoStreamInfo :
#   {"format_id": "22", "url": "https://...mp4", "headers": {...},
#    "width": 1280, "height": 720, "fps": 30.0, "vcodec": "avc1.64001F",
#    "acodec": "mp4a.40.2", "is_live": False, ...}
```

**À propos de l'audio** : un catalogue et un sélecteur audio équivalents
vivent volontairement dans **podcast-helper** (seul propriétaire du
streaming PCM audio), pas ici.

## Résolveur d'URL directe

Quand le catalogue est superflu et qu'il ne faut qu'**une** URL prête
pour ffmpeg :

```python
out = yth.resolve_direct_url(
    "https://www.youtube.com/watch?v=YE7VzlLtp-4",
    prefer="video",   # or "audio" for the cheapest audio-only path
)
# {"url": "https://...", "container": "mp4", "is_live": False,
#  "headers": {"User-Agent": "...", ...}}
```

Plus grossier que `pick_video_stream` (aucun filtrage de codec, de
format ni de fps), mais en un seul appel.

## Composition avec video-helper

Tout l'intérêt du catalogue et du sélecteur : donner l'URL directe et
ses en-têtes à `video_helper.extract_frames` pour décoder sans
retélécharger la page.

### Composition en deux temps (bas niveau)

```python
import video_helper as vh

pick = yth.pick_video_stream("https://www.youtube.com/watch?v=YE7VzlLtp-4",
                             prefer_codec="h264", max_fps=30)

for frame in vh.extract_frames(
    pick["url"],
    http_headers=pick["headers"],
    start_instant=10.0, end_instant=20.0,
    frame_interval=1.0,
    destination="torch", device="mps", batch_size=10, layout="image",
):
    # frame.shape == (10, 3, H, W), RGB uint8, on MPS
    embeddings = model(frame)
```

### Composition en un appel : `extract_frames_stream` (v1.2.0)

`extract_frames_stream` regroupe les deux temps en un seul appel : elle
exécute `pick_video_stream` en interne, insère automatiquement les
`http_headers` du résolveur ; elle transmet tel quel chaque argument de
`extract_frames`.

```python
for frame in yth.extract_frames_stream(
    "https://www.youtube.com/watch?v=YE7VzlLtp-4",
    # contraintes du sélecteur
    prefer_codec="h264", prefer_format="mp4", max_fps=30,
    # transmis tel quel à extract_frames
    start_instant=10.0, end_instant=20.0, frame_interval=1.0,
    destination="torch", device="mps", batch_size=10, layout="image",
):
    embeddings = model(frame)
```

Le même code pilote un pipeline CPU en numpy (le défaut) ou un pipeline
GPU en torch, selon les seuls réglages de `destination`, `device` et
`batch_size`. Le sélecteur n'est invoqué qu'une fois : le flux résolu
sert pour toute l'itération.

> **À noter** : `extract_frames_stream` requiert une version de `video-helper`
> avec `is_valid_video_file` compatible URL et `video_dimensions(http_headers=)` ;
> le `pyproject.toml` de youtube-helper épingle `video-helper>=2.0.0,<3` pour ça.

## Branding : métadonnées d'engagement sans clé d'API

`youtube_helper.branding` extrait les signaux d'engagement publics à
partir du dictionnaire de métadonnées de yt-dlp lui-même : aucune API
Google Data, aucune API Vimeo, aucun OAuth, aucun quota.

```python
# Instantané pour une seule vidéo
meta = yth.video_engagement("https://www.youtube.com/watch?v=YE7VzlLtp-4")
print(meta["view_count"], meta["like_count"], meta["comment_count"])
# 412309876 1893422 156003
print(meta["kind"])   # "short" / "long" / "live"
# long

# Instantané de chaîne : abonnés, vues totales, nombre de vidéos
ch = yth.channel_info("https://www.youtube.com/@Blender")
print(f"{ch['title']}: {ch['follower_count']:,} subscribers, "
      f"{ch['video_count']:,} videos")
# Blender: 1,920,000 subscribers, 487 videos

# Liste des vidéos de la chaîne avec engagement par vidéo (paginé, lent car un appel par vidéo)
videos = yth.channel_videos(
    "https://www.youtube.com/@Blender",
    max_videos=20,
    include_shorts=True,
    include_lives=False,
)
for v in videos:
    print(f"{v['upload_date']}  {v['view_count']:>10,} views  {v['title']}")
    # 2026-06-20    132,485 views  Blender Conference 2026 — call for talks
    # 2026-06-12  1,840,201 views  Cycles X — what's new in 4.5
    # ...

# Engagement en lot sur une liste d'URL : tolérant aux erreurs (URL invalide → stub _error)
batch = yth.engagement_batch([url1, url2, url3])
for entry in batch:
    if "_error" in entry:
        print(f"skip {entry['url']}: {entry['_error']}")
        # skip https://www.youtube.com/watch?v=removed: Video unavailable
    else:
        print(entry["title"], entry["view_count"])
        # Big Buck Bunny 412309876
```

**Schéma normalisé** (mêmes champs, que la source soit YouTube, Vimeo,
DailyMotion ou une VOD Twitch) :

```
id, url, title, description, upload_date (ISO YYYY-MM-DD),
duration_seconds, view_count, like_count, comment_count,
channel, channel_id, channel_url, channel_follower_count,
tags, categories, thumbnail, availability, live_status,
extractor, kind  # "short" / "long" / "live"
```

## Sous-titres, commentaires, chaînes

```python
# Sous-titres automatiques → {langue: chemin_vtt}
subs = yth.video_subtitles(
    "https://www.youtube.com/watch?v=YE7VzlLtp-4",
    output_dir="captions",
    langs=("fr", "en"),
    auto_only=True,
)
# {"en": "captions/YE7VzlLtp-4.en.vtt"}

# Commentaires : YouTube exige de plus en plus des cookies de navigateur pour les fils de commentaires.
comments = yth.video_comments(
    "https://www.youtube.com/watch?v=YE7VzlLtp-4",
    max_count=50,
    cookies_from_browser="firefox",   # ou "chrome" / "safari" : lit votre session active
)
for c in comments[:3]:
    print(f"@{c['author']} ({c['like_count']} ♥): {c['text'][:80]}")
    # @alice_dev (842 ♥): Bunny still holds up after 20 years. Render in Cycles X now?
    # @rab_animator (519 ♥): Where can I get the .blend file? Was archived on...
    # @kid_pixels (308 ♥): My 6yo watches this on loop. Eternal classic.

# Heuristique : s'agit-il d'un Short ou d'un extrait vertical ?
yth.is_short(yth.video_engagement(url))   # True / False
```

## Pièges à connaître

- **Expiration des URL** : les URL média directes fournies par yt-dlp
  expirent, en général sous une à six heures pour YouTube. Pour un job
  de longue durée, résolvez-les à nouveau périodiquement ou utilisez
  `download_video` pour matérialiser un fichier local.
- **Flux en direct** : `pick["is_live"] == True` signale en général une
  `pick["url"]` de type manifeste HLS `.m3u8`. ffmpeg et PyAV les gèrent
  nativement, avec trois limites : pas de retour en arrière, pas de
  sémantique `frame_indices`/`frame_times` et un hwaccel parfois
  instable avec du HLS découpé en chunks. La future
  `extract_frames_stream` refusera `speed != 1.0` en direct (on ne peut
  pas avancer plus vite que le direct lui-même).
- **Fraîcheur de yt-dlp** : YouTube fait tourner son schéma de signature
  souvent. `yth.ensure_recent_ytdlp(min_version="2024.12.23")` prévient
  quand le yt-dlp installé est trop ancien ; `pip install -U yt-dlp`
  corrige la plupart des erreurs de « déchiffrement cassé ».
- **Authentification** : les vidéos réservées aux membres, à accès
  limité par âge ou privées demandent des cookies. Passez
  `cookies_from_browser="firefox"` (ou `"chrome"`, `"safari"`) aux
  fonctions de catalogue, de sélection et de branding ; yt-dlp lit alors
  la session active du navigateur.
- **Extraction des commentaires** : les fils de commentaires YouTube
  demandent presque toujours `cookies_from_browser` désormais. Sans ce
  paramètre, attendez-vous à une liste vide ou à une erreur 403.
