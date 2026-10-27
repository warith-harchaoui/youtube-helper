# YouTube Helper

[🇫🇷](https://github.com/warith-harchaoui/youtube-helper/blob/main/LISEZMOI.md) · [🇬🇧](https://github.com/warith-harchaoui/youtube-helper/blob/main/README.md)

[![CI](https://github.com/warith-harchaoui/youtube-helper/actions/workflows/ci.yml/badge.svg)](https://github.com/warith-harchaoui/youtube-helper/actions/workflows/ci.yml) [![License: BSD-3-Clause](https://img.shields.io/badge/License-BSD%203--Clause-blue.svg)](https://github.com/warith-harchaoui/youtube-helper/blob/main/LICENSE) [![Python](https://img.shields.io/badge/python-3.10%E2%80%933.13-blue.svg)](#) [![Local-first](https://img.shields.io/badge/privacy-local--first-2f6f5e.svg)](#la-promesse)

`YouTube Helper` fait partie d'une collection de bibliothèques appelée `AI Helpers`, développée pour bâtir des applications d'intelligence artificielle.

## La promesse

**Local-first par conception.** youtube-helper s'exécute entièrement sur votre machine : il ne récupère que les médias que vous demandez ; vos données ne partent jamais vers un service tiers. Aucune télémétrie, aucun compte, aucun verrouillage propriétaire dans le cloud. Vous gardez la main sur toute la chaîne. Fait partie de la suite [AI Helpers](https://github.com/warith-harchaoui/ai-helpers) : la souveraineté sur vos données grâce à l'open source local-first.

*(youtube-helper accède bien à Internet : il télécharge les médias depuis le site source que vous lui indiquez. La promesse porte sur l'absence d'exfiltration et de télémétrie, rien vous concernant, ni vos requêtes, n'est envoyé ailleurs que vers le site qui héberge le média demandé.)*

[🌍 AI Helpers](https://deraison.ai/ai-helpers)

[![logo](https://raw.githubusercontent.com/warith-harchaoui/youtube-helper/main/assets/logo.png)](https://deraison.ai/ai-helpers)

YouTube Helper est une bibliothèque Python de fonctions utilitaires pour télécharger vidéos, audio et vignettes depuis des plateformes comme YouTube, Vimeo et DailyMotion. Le téléchargement proprement dit passe par `yt-dlp`, un outil libre qui sait déjà parler à des centaines de sites vidéo, chacun avec ses propres particularités ; youtube-helper l'enveloppe dans une interface Python unique, pour qu'on n'ait jamais à apprendre ces particularités soi-même.
Elle gère aussi le post-traitement : conversion ou fusion de fichiers média avec `ffmpeg`, l'outil en ligne de commande de référence pour lire, convertir et combiner audio et vidéo.

YouTube Helper est éprouvé en production. Chaque changement passe par des tests automatisés et une intégration continue avant d'atteindre PyPI ; les versions suivent le [versionnage sémantique](https://semver.org/lang/fr/) (actuellement `v2.7.0`). [`podcast-helper`](https://github.com/warith-harchaoui/podcast-helper), un autre paquet publié de la suite, s'appuie directement dessus en production. YouTube Helper repose lui-même sur [`os-helper`](https://github.com/warith-harchaoui/os-helper) (le socle commun que chaque bibliothèque de la suite utilise pour la journalisation et la gestion des fichiers), sur [`audio-helper`](https://github.com/warith-harchaoui/audio-helper) et sur [`video-helper`](https://github.com/warith-harchaoui/video-helper) pour l'étape de conversion qui suit la récupération du média brut par `yt-dlp`. C'est ce que « éprouvé en production » veut dire ici : pas une promesse, mais un graphe de dépendances sur lequel repose déjà du code publié, dans les deux sens autour de ce paquet.

## Documentation

[💻 Documentation](https://deraison.ai/ai-helpers/docs/youtube-helper-doc/)

[🗺️ Paysage](https://github.com/warith-harchaoui/youtube-helper/blob/main/PAYSAGE.md)

[📋 Exemples](https://github.com/warith-harchaoui/youtube-helper/blob/main/EXEMPLES.md)

## Fonctionnalités

Fonctions de **téléchargement (sur disque)**, dans `youtube_helper.main` :
- `download_video(url, output_path, max_height)` / `download_audio(url, output_path, target_sample_rate)` / `download_thumbnail(url, output_path)` : chacune renvoie le chemin qu'elle a écrit.
- `video_url_meta_data(url)` / `is_valid_video_url(url)` pour interroger les métadonnées sans télécharger.
- `default_ytdlp_options(...)` et `height_capped_format(max_height)` pour personnaliser les options yt-dlp.

**Catalogue de flux et résolution d'URL directe**, dans `youtube_helper.streaming` :
- `resolve_direct_url(url, prefer="audio"|"video")` → un raccourci "donne-moi une URL directe prête à passer à ffmpeg".
- `list_video_streams(url)` → énumère chaque format vidéo trouvé par yt-dlp (codec, résolution, fps, bitrate, …).
- `pick_video_stream(url, prefer_codec=, prefer_format=, max_fps=, language=, cookies_from_browser=)` → sélecteur contraint, retourne un `VideoStreamInfo` prêt à alimenter `video_helper.extract_frames`.
- `extract_frames_stream(url, ..., **extract_frames_kwargs)` → composition en un appel de `pick_video_stream` + `video_helper.extract_frames` ; câble les headers tout seul et transmet n'importe quel kwarg d'`extract_frames` (`destination`, `device`, `batch_size`, `output_width`, `frame_step`, …). Le chemin le plus court d'une URL YouTube / Vimeo / Twitch vers des frames prêtes pour le ML.
- Le catalogue et le sélecteur de flux audio vivent volontairement dans **podcast-helper** (propriétaire unique du streaming PCM audio).

**Métadonnées d'engagement sans API**, dans `youtube_helper.branding` :
- `channel_info(url)` / `channel_videos(url, max_videos, include_shorts, include_lives)` : instantané de chaîne et liste paginée de vidéos, avec métriques d'engagement normalisées sur un schéma multiplateforme.
- `video_engagement(url)` / `engagement_batch([urls])` : vues, likes, commentaires par vidéo et nombre d'abonnés de la chaîne, avec une variante en lot tolérante aux erreurs.
- `video_subtitles(url, output_dir, langs=("fr","en"))` : téléchargement automatique de sous-titres.
- `video_comments(url, max_count, cookies_from_browser="firefox"|"chrome"|...)` : échantillon de commentaires.
- `is_short(meta)` / `ensure_recent_ytdlp(min_version)` : fonctions utilitaires.
- Bâti uniquement sur les métadonnées publiques de yt-dlp : **pas d'API Google Data, pas d'API Vimeo, pas d'OAuth, pas de quota.** En clair, les API officielles des plateformes demandent d'enregistrer une application, d'obtenir des identifiants par OAuth (la poignée de main qui prouve à la plateforme que l'application a le droit d'agir au nom d'un utilisateur), puis de rester sous un quota (un plafond strict du nombre de requêtes autorisées par jour). Lire la même page publique qu'un navigateur affiche n'exige rien de tout cela : ni compte à créer, ni clé à demander, ni plafond quotidien à redouter.

## Installation

**Prérequis** : **Python 3.10-3.13**, **git**, **yt-dlp** et **ffmpeg**, multiplateforme :

- 🍎 **macOS** ([Homebrew](https://brew.sh)) : `brew install python git yt-dlp ffmpeg`
- 🐧 **Ubuntu/Debian** : `sudo apt update && sudo apt install -y python3 python3-pip git yt-dlp ffmpeg`
- 🪟 **Windows** (PowerShell) : `winget install Python.Python.3.12 Git.Git yt-dlp.yt-dlp Gyan.FFmpeg`

**Optionnel — Tor** (uniquement nécessaire pour le dernier palier de l'échelle de [résilience du téléchargement](#résilience-du-téléchargement)) :

- 🍎 **macOS** ([Homebrew](https://brew.sh)) : `brew install tor && brew services start tor`
- 🐧 **Ubuntu/Debian** : `sudo apt update && sudo apt install -y tor` (le service systemd du paquet démarre automatiquement ; sinon `sudo systemctl enable --now tor`)
- 🪟 **Windows** : `choco install tor` ([Chocolatey](https://chocolatey.org)), puis lancez `tor` dans un terminal — ou installez le [Tor Browser](https://www.torproject.org/download/) et définissez `YOUTUBE_HELPER_TOR_PROXY=socks5h://127.0.0.1:9150` (son proxy embarqué écoute sur le port 9150, pas le 9050 par défaut du démon autonome)

On recommande de travailler dans un environnement Python. Si vous ne savez pas en créer un, voir [🥸 Conseils techniques](https://deraison.ai/4ml/#install).

### Depuis PyPI (recommandé)

```bash
pip install youtube-helper

# Surfaces optionnelles
pip install "youtube-helper[api]"       # surface HTTP FastAPI
pip install "youtube-helper[mcp]"       # la même appli, plus le point d'entrée MCP
```

### Depuis les sources (sans PyPI)

```bash
git clone https://github.com/warith-harchaoui/youtube-helper.git
cd youtube-helper
pip install -e .

# Surfaces optionnelles
pip install -e ".[api]"
```

## Prise en main rapide

Sonder les métadonnées d'une URL sans rien télécharger, récupérer la vidéo,
puis en extraire la seule piste audio :

```python
import os

import audio_helper as ah
import os_helper as osh
import video_helper as vh
import youtube_helper as yth

osh.verbosity(0)

youtube_url = "https://www.youtube.com/watch?v=YE7VzlLtp-4"  # Big Buck Bunny

folder = "yt_tests"
osh.make_directory(folder)

# Aucun téléchargement ici. Le résultat est l'info dict de yt-dlp lui-même :
# `title`, `channel`, `duration`, `view_count`, `formats` et le reste y sont
# tous ; `title` et `description` sont en plus ramenés à des chaînes, car
# certains extracteurs les omettent et faisaient planter tous les appelants.
meta = yth.video_url_meta_data(youtube_url)
print(meta["title"], "—", meta["channel"], f"({meta['duration']}s)")

# Chaque download_* renvoie le chemin qu'elle a réellement écrit.
video = yth.download_video(youtube_url, os.path.join(folder, "big-buck-bunny.mp4"))
audio = yth.download_audio(youtube_url, os.path.join(folder, "big-buck-bunny.mp3"))

print(vh.video_dimensions(video))
# {'width': 1920, 'height': 1080, 'duration': 596.458333, 'frame_rate': 24.0, 'has_sound': True}

print(ah.get_audio_duration(audio))
# 596.474195
```

Ces deux dernières sorties sont mesurées sur les fichiers d'essai `yt_tests/`
de ce dépôt. La durée est celle du film et ne bougera pas ; la résolution,
elle, n'est pas une constante : `download_video` sans `max_height` prend le
meilleur format disponible du jour. Passez `max_height=720` — ou définissez
`YOUTUBE_HELPER_MAX_HEIGHT` — quand il vous faut un plafond prévisible.

`audio_helper.load_audio` est volontairement absente ci-dessus : elle décode
vers un tenseur torch et réclame donc `audio-helper[demucs]`, que ce paquet
n'installe pas. `get_audio_duration` fonctionne sur l'installation de base.

Pour le catalogue complet de recettes (téléchargements, catalogue de flux et
sélecteur, résolveur d'URL directe, composition avec `video-helper`,
métadonnées de branding, sous-titres, commentaires et ligne de commande), voir
[📋 EXEMPLES.md](https://github.com/warith-harchaoui/youtube-helper/blob/main/EXEMPLES.md).

## Résilience du téléchargement

Tous les appels yt-dlp du paquet passent par un même goulot,
`main._run_ytdlp` : les fonctions de téléchargement, celles de branding ainsi
que le catalogue et les résolveurs de `streaming`. C'est là que vit l'échelle
de replis, pour qu'un palier ajouté profite à tout le paquet plutôt qu'à un
seul module. Quand l'approche normale se fait bloquer (limitation de débit,
détection de bot, bannissement d'IP), la requête est rejouée sur des paliers
de plus en plus intrusifs :

1. **Normal** : la requête par défaut, telle que configurée par
   `default_ytdlp_options`.
2. **User-Agent navigateur** : nouvelle tentative avec un User-Agent Chrome
   de bureau complet et à jour, ainsi que les en-têtes correspondants.
   Surchargeable via la variable d'environnement `YOUTUBE_HELPER_USER_AGENT`.
3. **Un autre client YouTube** : `web_embedded`, puis `tv`, `android_vr`, puis
   `mweb` — une tentative chacun. YouTube sert plusieurs applications et ne
   leur applique pas les mêmes contrôles : une vidéo refusée à un client passe
   souvent pour un autre. Ce palier précède les deux suivants parce qu'il ne
   coûte rien, ne lit les données privées de personne et ne passe par aucun
   tiers ; `web_embedded` n'expose en plus aucun flux HLS, ce qui compte car
   YouTube bride le HLS fragmenté bien plus durement qu'un format https
   direct. Surchargez la chaîne via `YOUTUBE_HELPER_PLAYER_CLIENTS`
   (séparée par des virgules, vide désactive le palier) ou épinglez un client
   avec `default_ytdlp_options(player_clients=[...])` : dans ce cas l'échelle
   respecte votre choix.
4. **Cookies du navigateur** (opt-in, ignoré par défaut) : nouvelle
   tentative avec les cookies de session récupérés directement dans le
   profil d'un navigateur local (mécanisme `--cookies-from-browser` de
   yt-dlp). En pratique, c'est ce palier qui fait vraiment sauter le
   contrôle « Confirmez que vous n'êtes pas un robot » de YouTube — un
   User-Agent navigateur seul n'y suffit pas, ni Tor (les nœuds de sortie
   Tor sont eux-mêmes souvent signalés). Lire le trousseau de cookies
   d'une autre application est suffisamment intrusif pour que cela ne se
   produise jamais silencieusement : définissez
   `YOUTUBE_HELPER_COOKIES_FROM_BROWSER` avec un nom de navigateur reconnu
   par yt-dlp (`chrome`, `firefox`, `edge`, `brave`, `opera`, `vivaldi`,
   `safari`, `whale`, `chromium`) pour l'activer. Le trousseau de cookies
   de Safari nécessite en plus l'accès complet au disque (Full Disk
   Access) accordé au processus/terminal appelant sur macOS, sans quoi
   l'extraction lève « Operation not permitted » ; Chrome/Firefox n'ont
   besoin d'aucune autorisation particulière.
5. **Tor** : nouvelle tentative via un proxy SOCKS Tor local. Tor fait
   passer la requête par une chaîne de relais avant qu'elle n'atteigne le
   site visé, si bien que le site voit une adresse IP différente, sans
   rapport avec la vôtre ; un blocage fondé sur votre IP ne s'applique
   alors plus. Un proxy SOCKS est simplement un point de relais local
   auquel un programme peut confier son trafic plutôt que de se connecter
   directement, c'est ainsi qu'une application transmet ses requêtes à
   Tor. Configuré par défaut en `socks5h://127.0.0.1:9050` (la résolution
   DNS, c'est-à-dire la traduction d'un nom de site en adresse IP, passe
   elle aussi par Tor, pour que le nom du site lui-même ne fuite jamais
   hors du tunnel). Nécessite un démon Tor (le processus en arrière-plan
   qui fait tourner la chaîne de relais) lancé localement : voir les
   commandes d'installation par OS dans la section
   [Installation](#installation). Surchargeable via
   `YOUTUBE_HELPER_TOR_PROXY`. Conservé en dernier recours pour les
   environnements sans navigateur connecté auprès duquel emprunter des
   cookies — les nœuds de sortie Tor étant eux-mêmes souvent signalés, ce
   n'est pas un correctif fiable en premier lieu pour ce contrôle
   anti-robot.

Si tous les paliers échouent, l'erreur d'origine de la dernière tentative
est levée.

**Toute lecture est bornée.** Le même goulot fixe le `socket_timeout` de
yt-dlp à 30 secondes, surchargeable via `YOUTUBE_HELPER_SOCKET_TIMEOUT`.
Laissé à lui-même, yt-dlp hérite du défaut de Python, à savoir aucun délai du
tout : une connexion à demi fermée par le serveur distant est alors attendue
indéfiniment — une récupération de sous-titres a été observée à 0 % de CPU
pendant neuf minutes, ses sockets en `CLOSE_WAIT` ; seul un `kill` y a mis
fin. Le dégât va plus loin qu'un appel lent : tous les paliers ci-dessus ne
s'exécutent qu'une fois la tentative *revenue*. Une lecture non bornée
neutralise donc l'échelle entière ; la bibliothèque paraît figée au lieu de
dégradée. C'est la borne qui rend les replis atteignables.

**Un fragment perdu échoue bruyamment.** Le défaut de yt-dlp est d'abandonner
un fragment HLS/DASH indisponible une fois ses tentatives épuisées, puis de
finaliser le conteneur quand même : ce qui atterrit sur le disque est un
fichier valide et lisible, qui annonce honnêtement sa durée raccourcie, si
bien qu'aucune vérification en aval ne s'en plaint. Ce paquet passe plutôt
`skip_unavailable_fragments=False` et porte `fragment_retries` à 25, les
échecs constatés sur le terrain relevant du bridage passager plutôt que de la
donnée manquante. Définissez `YOUTUBE_HELPER_ALLOW_LOSSY_FRAGMENTS=1` pour
restaurer le comportement d'origine de yt-dlp, `YOUTUBE_HELPER_FRAGMENT_RETRIES`
pour régler la patience.

## Usage légal et éthique

YouTube Helper est un wrapper léger autour de `yt-dlp` et `ffmpeg`. Vous êtes responsable de la manière dont vous l'utilisez. Ne téléchargez et ne traitez que des contenus que vous possédez, qui sont dans le domaine public, sous licence permissive (par ex. Creative Commons) ou pour lesquels vous avez une autorisation explicite du détenteur des droits. Respectez les Conditions d'Utilisation de chaque plateforme et les lois applicables en matière de droit d'auteur, de vie privée et de protection des données. Les auteurs fournissent cette bibliothèque pour des usages légitimes : archivage personnel, accessibilité, recherche, contenus dont vous détenez les droits, pas pour contourner des contrôles d'accès ou redistribuer du contenu protégé.

## Exposition multi-surface

`youtube-helper` n'est pas seulement une bibliothèque : les mêmes
fonctions sont exposées via une interface en ligne de commande (CLI,
un programme qu'on pilote en tapant des commandes plutôt qu'en écrivant
du Python), une surface HTTP FastAPI (ces mêmes fonctions accessibles par
le réseau comme un petit service web), des outils MCP (le Model Context
Protocol, une norme qui permet à un agent d'intelligence artificielle
d'appeler directement les fonctions d'un programme, de la même façon
qu'un humain les appellerait en ligne de commande) et une interface
graphique dans le navigateur (une page à cliquer). Quatre portes
d'entrée vers le même code sous-jacent, pour qu'un script, un service
web, un agent d'IA et un humain devant son navigateur accèdent tous à
la même logique de téléchargement.

```bash
# Bibliothèque Python (par défaut)
import youtube_helper as yth

# Ligne de commande (installée automatiquement)
youtube-helper metadata     --url https://www.youtube.com/watch?v=YE7VzlLtp-4
youtube-helper audio        --url https://www.youtube.com/watch?v=YE7VzlLtp-4 --output out.mp3
youtube-helper resolve      --url https://www.youtube.com/watch?v=YE7VzlLtp-4 --prefer audio
youtube-helper channel-info --url https://www.youtube.com/@blender

# Surface HTTP FastAPI (nécessite l'extra [api])
pip install "youtube-helper[api]"
uvicorn youtube_helper.api:app --port 8000
# → doc OpenAPI sur http://localhost:8000/docs

# Interface graphique navigateur (nécessite l'extra [api]) : collez une URL,
# choisissez audio ou vidéo
uvicorn youtube_helper.api:app --port 8000
# → ouvrez http://localhost:8000/gui  (ou simplement http://localhost:8000/)

# Outils MCP (nécessite l'extra [mcp]) : même appli, plus un point d'entrée /mcp
pip install "youtube-helper[mcp]"
youtube-helper-mcp
```

Il n'y a qu'une seule ligne de commande, bâtie avec `click` :
`youtube-helper` porte quinze sous-commandes et la surface HTTP les reflète
une à une, si bien qu'un nom d'option appris au terminal est le nom du champ
dans le corps JSON. La liste complète est dans les
[📋 exemples](https://github.com/warith-harchaoui/youtube-helper/blob/main/EXEMPLES.md).

**Banc de téléchargement (GUI)** (`GET /gui`) : une page unique autonome
(Tailwind via CDN + JS vanilla, sans étape de build). Collez une URL YouTube (ou
tout site supporté par yt-dlp), choisissez **audio** (avec une fréquence
d'échantillonnage) ou **vidéo**, cliquez sur Télécharger et le résultat se joue
en ligne avec un lien de téléchargement. La page POST vers les mêmes endpoints
`/audio` / `/video` : zéro logique serveur en plus. Local-first, la page ne
parle qu'à votre API locale.

Voir [TRIGGERS.md](https://github.com/warith-harchaoui/youtube-helper/blob/main/TRIGGERS.md) pour le catalogue exhaustif des déclencheurs.

Image Docker :

```bash
docker build -t youtube-helper .
docker run --rm -p 8000:8000 youtube-helper
```

Un plan de GUI plus riche (bibliothèque vidéo, comparateur de chaînes,
downloader batch) est dans [GUI.md](https://github.com/warith-harchaoui/youtube-helper/blob/main/GUI.md).

### En tant que skill d'agent

`skills/youtube-helper/` empaquette youtube-helper comme **skill Claude** *et* skill
**OpenCode**, pour qu'un agent puisse s'en saisir à votre place. Voir
[`skills/README.md`](https://github.com/warith-harchaoui/youtube-helper/blob/main/skills/README.md) pour l'installer (liens
symboliques vers `~/.claude/skills/` et `~/.opencode/skills/`) et
[`TRIGGERS.md`](https://github.com/warith-harchaoui/youtube-helper/blob/main/TRIGGERS.md) pour le catalogue exhaustif des
déclencheurs — `scripts/check_triggers.py` maintient la description du skill
alignée dessus ; la suite de tests échoue si une capacité cesse d'être
nommée.

## Version Rust

Un crate compagnon, [`youtube-helper-rs`](https://github.com/warith-harchaoui/youtube-helper-rs),
encapsule le même binaire `yt-dlp` depuis Rust plutôt que depuis Python —
`fetch_metadata` et `download_audio`, rien de plus pour l'instant (pas de
téléchargement vidéo, de miniatures, de catalogue de flux, de métadonnées
de chaîne, de sous-titres ni de repli Tor, tous présents ici). L'intérêt :
un fin wrapper `std::process::Command` avec des résultats typés et une
énumération d'erreurs `thiserror`, pour qu'un programme Rust qui invoque
déjà `yt-dlp` obtienne une gestion d'erreurs cohérente et typée, sans le
moindre runtime Python dans l'image de déploiement.

## Auteur
 - [Warith HARCHAOUI](https://linkedin.com/in/warith-harchaoui)

## Remerciements
Remerciements chaleureux à [Mohamed Chelali](https://mchelali.github.io) et [Bachir Zerroug](https://www.linkedin.com/in/bachirzerroug) pour nos échanges fructueux.

## Licence

Ce projet est distribué sous licence BSD-3-Clause. Voir le fichier [LICENSE](https://github.com/warith-harchaoui/youtube-helper/blob/main/LICENSE) pour les détails.
