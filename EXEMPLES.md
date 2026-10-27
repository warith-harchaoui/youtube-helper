# Exemples YouTube Helper

🇫🇷 Français · [🇬🇧 EXAMPLES.md](https://github.com/warith-harchaoui/youtube-helper/blob/main/EXAMPLES.md)

Recettes pratiques pour les trois couches de `youtube-helper` : les fonctions
de téléchargement, le catalogue de flux avec ses résolveurs, puis les
métadonnées d'engagement sans API.

Chaque extrait de cette page accède au réseau, c'est la raison d'être du
paquet. Aucune sortie ci-dessous n'a été inventée : là où une valeur est
affichée, elle a été mesurée localement et annoncée comme telle ; là où elle ne
pouvait pas l'être, le commentaire nomme la *forme* de la réponse au lieu de
deviner un chiffre. Les compteurs de vues et les listes de formats changent
d'heure en heure : un chiffre recopié serait périmé avant d'être lu.

---

## Table des matières

1. [Mise en place](#mise-en-place)
2. [Téléchargements sur disque](#1-téléchargements-sur-disque)
3. [Catalogue de flux et sélecteur](#2-catalogue-de-flux-et-sélecteur)
4. [Résolveur d'URL directe](#3-résolveur-durl-directe)
5. [Composition avec video-helper](#4-composition-avec-video-helper)
6. [Métadonnées d'engagement sans clé d'API](#5-métadonnées-dengagement-sans-clé-dapi)
7. [Sous-titres, commentaires et chaînes](#6-sous-titres-commentaires-et-chaînes)
8. [Ligne de commande](#ligne-de-commande)
9. [Dépannage](#dépannage)

---

## Mise en place

```bash
pip install youtube-helper
```

Cela embarque automatiquement `os-helper`, `audio-helper` et `video-helper`.
Il vous reste à mettre `yt-dlp` et `ffmpeg` sur le PATH — `brew install yt-dlp ffmpeg`
sur macOS, voir le [LISEZMOI](https://github.com/warith-harchaoui/youtube-helper/blob/main/LISEZMOI.md#installation)
pour les autres plateformes.

Tous les extraits Python ci-dessous supposent ces imports :

```python
import youtube_helper as yth
import os_helper as osh

osh.verbosity(2)  # pour que les osh.info(...) internes à la bibliothèque sortent sur stdout
```

Une seule URL sert de fil rouge, [Big Buck Bunny](https://www.youtube.com/watch?v=YE7VzlLtp-4)
sur la chaîne Blender, parce qu'elle est sous licence Creative Commons et donc
réellement téléchargeable pendant la lecture :

```python
URL = "https://www.youtube.com/watch?v=YE7VzlLtp-4"
```

## 1. Téléchargements sur disque

La surface d'origine de `youtube-helper` : récupérer un fichier en stockage
local. Chaque fonction renvoie le chemin qu'elle a écrit, directement
réutilisable.

```python
video = yth.download_video(URL, "bunny.mp4")
audio = yth.download_audio(URL, "bunny.mp3")
thumb = yth.download_thumbnail(URL, "bunny.jpg")

# Sans chemin de sortie, le nom est dérivé du titre de la vidéo.
meme_video_nommee_seule = yth.download_video(URL)

# Plafonnez la hauteur quand la destination ne peut pas avaler un fichier
# arbitrairement gros. Un plafond privilégie aussi les formats https directs
# plutôt que le HLS que YouTube bride : c'est donc en général plus rapide.
plus_petit = yth.download_video(URL, "bunny-720.mp4", max_height=720)

# Sonde de métadonnées légère, sans téléchargement : l'info dict de yt-dlp.
meta = yth.video_url_meta_data(URL)
print(meta["title"], meta["duration"], meta["channel"])  # str, int (secondes), str

# Cette URL est-elle seulement exploitable par yt-dlp ? Ne lève jamais.
yth.is_valid_video_url(URL)  # True / False
```

Sans `output_path`, l'écriture se fait dans `<titre-ascii>.mp4` (ou `.mp3`, ou
l'extension de la vignette) à côté de votre répertoire de travail, en chemin
absolu. Les trois fonctions sont idempotentes : si ce fichier existe déjà et
qu'il est un média valide, l'appel le journalise et le renvoie au lieu de
retélécharger.

`download_audio` ne repasse par `audio-helper` que si la sortie de yt-dlp ne
porte pas déjà l'extension demandée — et `target_sample_rate` s'applique lors
de cette conversion. Une cible `.wav` ou `.m4a` obtient donc bien la fréquence
nommée :

```python
yth.download_audio(URL, "bunny-16k.wav", target_sample_rate=16000)
```

tandis que demander `.mp3`, ce que yt-dlp rend de toute façon, recopie le
fichier tel quel, à la fréquence qu'avait la source.

## 2. Catalogue de flux et sélecteur

Là où `download_*` écrit un fichier, le catalogue et le sélecteur rendent une
**URL média directe** accompagnée des en-têtes qu'elle exige : un décodeur en
aval (PyAV, ffmpeg, `video_helper.extract_frames`) peut alors la lire sans
repasser par yt-dlp.

```python
# Énumère tous les formats vidéo que yt-dlp trouve, du pire au meilleur.
streams = yth.list_video_streams(URL)
for s in streams[:5]:
    print(
        f"{s['format_id']:6} {s['width']}x{s['height']} {s['fps']}fps "
        f"{s['vcodec']:14} {s['ext']:6} ~{s['vbr_kbps']:.0f} kbps"
    )
```

Chaque entrée est un `VideoStreamInfo` portant ces clés : `format_id`, `url`,
`headers`, `ext`, `container`, `vcodec`, `acodec`, `width`, `height`, `fps`,
`vbr_kbps`, `filesize_bytes`, `is_live`, `protocol`, `language`, `note`. Les
formats purement audio sont écartés : c'est le catalogue *vidéo*. YouTube
publie des dizaines de lignes pour une vidéo populaire et les fait tourner ; les
valeurs exactes de `format_id` ne valent donc pas la peine d'être retenues.

```python
# Choisit l'unique meilleur flux satisfaisant vos contraintes.
pick = yth.pick_video_stream(
    URL,
    prefer_codec="h264",  # correspondance par sous-chaîne ; "h264" et "avc1" sont alias
    prefer_format="mp4",  # égalité stricte sur ext
    max_fps=30,  # écarte tout ce qui va plus vite
)
pick["url"]  # URL média directe, prête pour ffmpeg
pick["headers"]  # les en-têtes que ffmpeg doit envoyer avec
```

Chaque contrainte non-`None` est un filtre dur appliqué au catalogue ci-dessus,
et le candidat le mieux classé des survivants gagne. Si le catalogue est vide,
ou si tout se fait filtrer, `pick_video_stream` lève `ValueError` au lieu de
renvoyer en silence quelque chose que vous n'avez pas demandé.

**À propos de l'audio** : un catalogue et un sélecteur audio équivalents vivent
volontairement dans **podcast-helper** (seul propriétaire du streaming PCM
audio), pas ici.

## 3. Résolveur d'URL directe

Quand le catalogue est superflu et qu'il ne faut qu'**une** URL prête pour
ffmpeg :

```python
out = yth.resolve_direct_url(URL, prefer="video")  # ou prefer="audio"
out["url"]  # str — mp4 progressif, manifeste HLS .m3u8 ou DASH .mpd
out["container"]  # "mp4" / "webm" / "hls" / "dash" / "audio"
out["is_live"]  # bool
out["headers"]  # dict[str, str] — à passer à ffmpeg via -headers
out["has_audio"]  # bool — voir ci-dessous
```

Plus grossier que `pick_video_stream` (aucun filtrage de codec, de format ni
de fps), mais en un seul appel.

Attention à `has_audio`. Avec `prefer="audio"` il vaut toujours `True`, mais
avec `prefer="video"` il tombe à `False` dès que le site n'offre que des flux
vidéo seuls — ce qui est désormais la réponse normale de YouTube, qui a retiré
les flux progressifs de la plupart des vidéos. Quand il vous faut les deux
pistes depuis une même page, résolvez deux fois et laissez ffmpeg prendre une
entrée de chaque :

```python
v = yth.resolve_direct_url(URL, prefer="video")
if not v["has_audio"]:
    a = yth.resolve_direct_url(URL, prefer="audio")
    # ffmpeg -headers ... -i v["url"] -headers ... -i a["url"] -c copy out.mp4
```

## 4. Composition avec video-helper

Tout l'intérêt du catalogue et du sélecteur : donner l'URL directe et ses
en-têtes à `video_helper.extract_frames` pour décoder sans retélécharger la
page.

### Composition en deux temps (bas niveau)

```python
import video_helper as vh

pick = yth.pick_video_stream(URL, prefer_codec="h264", max_fps=30)

for frame in vh.extract_frames(
    pick["url"],
    http_headers=pick["headers"],
    start_instant=10.0,
    end_instant=20.0,
    frame_interval=1.0,
    destination="torch",
    device="mps",
    batch_size=10,
    layout="image",
):
    # frame.shape == (10, 3, H, W), RGB uint8, sur MPS
    embeddings = model(frame)
```

### Composition en un appel : `extract_frames_stream`

`extract_frames_stream` regroupe les deux temps en un seul appel : elle exécute
`pick_video_stream` en interne, insère automatiquement les `http_headers` du
résolveur et transmet tel quel chaque mot-clé d'`extract_frames`.

```python
for frame in yth.extract_frames_stream(
    URL,
    # contraintes du sélecteur
    prefer_codec="h264",
    prefer_format="mp4",
    max_fps=30,
    # transmis tel quel à extract_frames
    start_instant=10.0,
    end_instant=20.0,
    frame_interval=1.0,
    destination="torch",
    device="mps",
    batch_size=10,
    layout="image",
):
    embeddings = model(frame)
```

Le même code pilote un pipeline CPU en numpy (le défaut) ou un pipeline GPU en
torch, selon les seuls réglages de `destination`, `device` et `batch_size`. Le
sélecteur n'est invoqué qu'une fois : le flux résolu sert pour toute
l'itération.

> **À noter** : `extract_frames_stream` requiert une version de `video-helper`
> avec `is_valid_video_file` compatible URL et `video_dimensions(http_headers=)` ;
> le `pyproject.toml` de youtube-helper épingle `video-helper>=2.0.0,<3` pour ça.

## 5. Métadonnées d'engagement sans clé d'API

`youtube_helper.branding` extrait les signaux d'engagement publics du
dictionnaire de métadonnées de yt-dlp lui-même : **aucune API Google Data,
aucune API Vimeo, aucun OAuth, aucun quota.**

```python
# Instantané d'une seule vidéo, sur le schéma normalisé.
meta = yth.video_engagement(URL)
print(meta["view_count"], meta["like_count"], meta["comment_count"])  # trois entiers
print(meta["kind"])  # "short" / "long" / "live"

# Instantané de chaîne : abonnés, vues totales, nombre de vidéos.
ch = yth.channel_info("https://www.youtube.com/@Blender")
print(ch["title"], ch["follower_count"], ch["video_count"])

# Liste des vidéos de la chaîne avec l'engagement de chacune.
# Lent par construction : un appel yt-dlp par vidéo, donc plafonnez.
videos = yth.channel_videos(
    "https://www.youtube.com/@Blender",
    max_videos=20,
    include_shorts=True,
    include_lives=False,
)
for v in videos:
    print(f"{v['upload_date']}  {v['view_count']:>10,}  {v['title']}")

# Engagement en lot sur une liste d'URL : tolérant — une entrée morte revient
# en stub portant "_error" plutôt que d'interrompre tout le lot.
for entry in yth.engagement_batch([URL, "https://www.youtube.com/watch?v=removed"]):
    if "_error" in entry:
        print(f"ignorée {entry['url']} : {entry['_error']}")
    else:
        print(entry["title"], entry["view_count"])
```

**Schéma normalisé** — les mêmes vingt champs, que la source soit YouTube,
Vimeo, DailyMotion ou une VOD Twitch :

```text
id, url, title, description, upload_date (ISO AAAA-MM-JJ),
duration_seconds, view_count, like_count, comment_count,
channel, channel_id, channel_url, channel_follower_count,
tags, categories, thumbnail, availability, live_status,
extractor, kind  # "short" / "long" / "live"
```

Notez les renommages : la durée s'appelle `duration_seconds` et non `duration`
comme chez yt-dlp, l'URL de la page s'appelle `url` et non `webpage_url`. Tout
compteur que l'extracteur n'a pas fourni revient à `0` plutôt qu'à `None` :
l'arithmétique en aval n'a donc jamais à s'en prémunir.

## 6. Sous-titres, commentaires et chaînes

```python
# Sous-titres automatiques. Renvoie {langue: chemin}, en chemins ABSOLUS :
# output_dir est résolu avant l'écriture. Les langues sans rien de disponible
# sont ignorées en silence, le dictionnaire peut donc être plus petit que
# `langs` — voire vide.
subs = yth.video_subtitles(URL, output_dir="captions", langs=("fr", "en"), auto_only=True)
# par ex. {"en": "/repertoire/de/travail/captions/YE7VzlLtp-4.en.vtt"}

# Commentaires : YouTube exige de plus en plus des cookies de navigateur.
comments = yth.video_comments(
    URL,
    max_count=50,
    cookies_from_browser="firefox",  # ou "chrome" / "safari" : lit votre session
)
for c in comments[:3]:
    print(f"@{c['author']} ({c['like_count']}) : {c['text'][:80]}")
```

Chaque commentaire porte `id`, `parent`, `author`, `author_id`, `text`,
`like_count`, `timestamp`, `iso_date`, `is_favorited`. Sur YouTube, `parent`
vaut la chaîne `"root"` pour un commentaire de premier niveau et l'identifiant
du parent pour une réponse : c'est le champ sur lequel regrouper pour
reconstituer les fils.

Pour demander « est-ce un Short ? », lisez `kind` sur le dictionnaire
normalisé :

```python
yth.video_engagement(URL)["kind"] == "short"
```

`is_short` est aussi exportée, mais elle lit les clés **brutes** de yt-dlp
(`duration`, `webpage_url`) : passez-lui donc `video_url_meta_data(url)` et non
le dictionnaire normalisé de `video_engagement`. Sur ce dernier, son test des
60 s ne peut pas se déclencher, puisque le champ s'y nomme `duration_seconds` :

```python
yth.is_short(yth.video_url_meta_data(URL))  # True / False
```

## Ligne de commande

Une seule ligne de commande, bâtie avec `click`, installée sous le nom
`youtube-helper` par `pip install youtube-helper`. Quinze sous-commandes,
chaque argument en option nommée. La surface FastAPI reprend les mêmes noms
un à un :

```bash
youtube-helper metadata       --url https://www.youtube.com/watch?v=YE7VzlLtp-4
youtube-helper valid          --url https://www.youtube.com/watch?v=YE7VzlLtp-4
youtube-helper video          --url ... --output bunny.mp4 --max-height 720
youtube-helper audio          --url ... --output bunny.mp3 --sample-rate 16000
youtube-helper thumbnail      --url ... --output bunny.jpg
youtube-helper resolve        --url ... --prefer audio
youtube-helper list-streams   --url ... --no-video-only
youtube-helper pick-stream    --url ... --prefer-codec h264 --prefer-format mp4 --max-fps 30
youtube-helper channel-info   --url https://www.youtube.com/@Blender
youtube-helper channel-videos --url https://www.youtube.com/@Blender --max-videos 20 --no-shorts
youtube-helper engagement     --url ...
youtube-helper engagement-batch --urls URL1 --urls URL2
youtube-helper subtitles      --url ... --output-dir captions --langs en --langs fr
youtube-helper comments       --url ... --max 50 --cookies-from-browser firefox
youtube-helper ytdlp-version  --min-version 2024.12.23
```

Tout ce qui lit, plutôt que de télécharger, écrit du JSON sur stdout : la
sortie se branche donc directement sur `jq`.

```bash
youtube-helper pick-stream --url "$URL" --prefer-codec h264 | jq -r .url
```

`valid` encode aussi sa réponse dans le code de sortie (`0` valide, `1` non),
ce qui en fait une garde utilisable en shell. Une erreur de la bibliothèque
devient un `Error: ...` d'une ligne sur stderr, plus un code 1, jamais une
trace Python.

Deux invocations ne demandent aucun réseau : de quoi vérifier votre
installation tout de suite. `ytdlp-version` annonce le yt-dlp réellement
appelé et prévient sur stderr s'il est plus ancien que la version nommée.

```console
$ python -m youtube_helper.cli ytdlp-version
2026.06.09

$ python -m youtube_helper.cli ytdlp-version --min-version 2099.01.01
youtube-helper: yt-dlp 2026.06.09 is older than 2099.01.01 — consider `pip install -U yt-dlp`.
2026.06.09
```

Et la liste des sous-commandes elle-même :

```console
$ python -m youtube_helper.cli --help
Usage: python -m youtube_helper.cli [OPTIONS] COMMAND [ARGS]...

  YouTube Helper — download and inspect media from yt-dlp-supported sites.

  Downloads video, audio or thumbnails, resolves a page URL to a direct
  ffmpeg-ready media URL, browses the stream catalog, and pulls no-API
  engagement metadata on YouTube, Vimeo, DailyMotion, Twitch VOD, SoundCloud
  and anything else yt-dlp handles.

Options:
  -V, --version  Show the version and exit.
  -h, --help     Show this message and exit.

Commands:
  audio             Download only the audio track to disk.
  channel-info      Channel-level snapshot (subs, total views, video count).
  channel-videos    List channel videos with normalised engagement metadata.
  comments          Fetch top comments for a video.
  engagement        Single-video engagement snapshot.
  engagement-batch  Multi-URL engagement snapshot (tolerant of dead...
  list-streams      List every video format yt-dlp finds for a URL.
  metadata          Dump yt-dlp metadata for a video URL as JSON.
  pick-stream       Pick one best video stream matching the given...
  resolve           Resolve a URL to a direct ffmpeg-ready media URL...
  subtitles         Download subtitles (auto or manual) for a video into...
  thumbnail         Download the video's thumbnail to disk.
  valid             Check whether a URL is a valid video URL for yt-dlp...
  video             Download the video (best video + audio) to disk.
  ytdlp-version     Print installed yt-dlp version; warn if stale.
```

Ces trois blocs sont des captures mot pour mot : voilà pourquoi leur ligne
d'usage affiche `python -m youtube_helper.cli`. Cette forme fonctionne même
quand le script de console manque ; les deux sont sinon interchangeables.
Chaque sous-commande accepte `-h` pour ses propres options.

## Dépannage

- **Un téléchargement reste figé.** Il ne devrait pas : tous les appels yt-dlp
  du paquet fixent `socket_timeout` à 30 s, si bien qu'une connexion à demi
  fermée échoue et que l'échelle de replis prend le relais. Montez ou baissez
  la valeur via `YOUTUBE_HELPER_SOCKET_TIMEOUT` si 30 s ne convient pas à
  votre lien. La seule chose à ne pas faire est de la supprimer : les paliers
  de repli ne s'exécutent qu'une fois la tentative revenue, donc une lecture
  non bornée les neutralise tous d'un coup.
- **« Confirmez que vous n'êtes pas un robot ».** L'échelle réessaie déjà en
  `web_embedded`, `tv`, `android_vr` puis `mweb` avant de vous demander quoi
  que ce soit. Si les quatre sont refusés, définissez
  `YOUTUBE_HELPER_COOKIES_FROM_BROWSER=firefox` (ou `chrome`, `safari`, …)
  pour laisser yt-dlp emprunter une session connectée : c'est le palier qui
  fait réellement sauter le contrôle. Tor est tenté en dernier et ne corrige
  pas ce cas de façon fiable, ses nœuds de sortie étant eux-mêmes souvent
  signalés.
- **Expiration des URL.** Les URL média directes de yt-dlp expirent, en
  général sous une à six heures pour YouTube. Pour un travail de longue durée,
  résolvez-les à nouveau périodiquement ou matérialisez un fichier local avec
  `download_video`.
- **Flux en direct.** `pick["is_live"] == True` signale une `pick["url"]` qui
  est en général un manifeste HLS `.m3u8`. ffmpeg et PyAV les gèrent
  nativement, avec trois limites : pas de retour en arrière, pas de sémantique
  `frame_indices`/`frame_times`, enfin un hwaccel parfois instable sur du HLS
  découpé en chunks. `filesize_bytes` vaut toujours `0` pour un format en
  direct.
- **Fraîcheur de yt-dlp.** YouTube fait tourner son schéma de signature
  souvent. `yth.ensure_recent_ytdlp(min_version="2024.12.23")` prévient quand
  le yt-dlp installé est trop ancien ; `pip install -U yt-dlp` corrige la
  plupart des erreurs de « déchiffrement cassé ».
- **Authentification.** Les vidéos réservées aux membres, à accès limité par
  âge ou privées demandent des cookies. Passez
  `cookies_from_browser="firefox"` (ou `"chrome"`, `"safari"`) aux fonctions de
  catalogue, de sélection et de branding ; yt-dlp lit alors la session active
  du navigateur. Sur macOS, Safari exige en plus l'accès complet au disque
  accordé à votre terminal, sans quoi l'extraction lève « Operation not
  permitted ».
- **Les commentaires reviennent vides.** Les fils de commentaires YouTube
  demandent presque toujours `cookies_from_browser` désormais. Sans ce
  paramètre, attendez-vous à une liste vide ou à une erreur 403.
- **Une vidéo arrive plus courte qu'elle ne devrait.** Pas ici : ce paquet
  refuse d'ignorer un fragment HLS/DASH indisponible et porte
  `fragment_retries` à 25, si bien qu'une perte de fragment lève au lieu de
  tronquer en silence. Si vous définissez
  `YOUTUBE_HELPER_ALLOW_LOSSY_FRAGMENTS=1`, vous avez choisi de revenir à la
  troncature silencieuse de yt-dlp.
