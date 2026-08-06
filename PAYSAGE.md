# Paysage

🇫🇷 Français · [🇬🇧 LANDSCAPE.md](https://github.com/warith-harchaoui/youtube-helper/blob/main/LANDSCAPE.md)

Outils Python (et apparentés) voisins et concurrents dans l'espace
« télécharger et inspecter de la vidéo / audio en ligne », comparés à
`youtube-helper`. Les notes vont de ⭐ (1) à ⭐⭐⭐⭐⭐ (5), évaluées sur la
tâche visée par `youtube-helper` — le téléchargement quotidien YouTube /
Vimeo / DailyMotion / Twitch et les métadonnées d'engagement sans API,
pour le personal branding et les pipelines d'IA. Un outil optimisé pour
un tout autre usage (par ex. l'archivage miroir, la ré-diffusion par
torrent) n'est pas pénalisé — la note reflète seulement l'adéquation à
*ce* créneau.

## En un coup d'œil

<!-- TABLE:START -->
| Téléchargement de médias | Multi-plateforme | Téléchargement média | Résolveur d'URL directe | Sélecteur de flux | Engagement sans API | Multi-surface | Prêt pour Docker | Ergonomie pipeline IA |
| --- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **youtube-helper** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| yt-dlp | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ |
| youtube-dl | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐⭐ | ⭐⭐ | ⭐⭐ |
| pytube | ⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐ | ⭐⭐ | ⭐⭐⭐ |
| pytubefix | ⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐ | ⭐⭐ | ⭐⭐⭐ |
| streamlink | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐ | ⭐⭐ | ⭐⭐⭐ | ⭐⭐ |
| gallery-dl | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ | ⭐⭐ |
| scrapetube | ⭐ | ⭐ | ⭐ | ⭐ | ⭐⭐⭐ | ⭐ | ⭐⭐ | ⭐⭐⭐ |
| youtube-comment-downloader | ⭐ | ⭐ | ⭐ | ⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐⭐ | ⭐⭐⭐ |
| google-api-python-client | ⭐ | ⭐ | ⭐ | ⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ | ⭐⭐ |
<!-- TABLE:END -->

## Carte de positionnement

<!-- FIGURE:START -->
Représentation 2D du tableau ci-dessus.

![Carte de positionnement](https://raw.githubusercontent.com/warith-harchaoui/youtube-helper/main/assets/paysage.png)

La carte est un résumé en 2D des 8 critères : à lire comme une forme, pas comme un classement. « youtube-helper » se situe dans le coin en haut à droite. Les axes se lisent **Horizontal — Utilisabilité ↔ Polyvalence** et **Vertical — Accessibilité ↔ Intégration**.
<!-- FIGURE:END -->

## Positionnement

`youtube-helper` se place volontairement à l'intersection de la
**couverture brute de yt-dlp** et de l'**ergonomie des pipelines d'IA /
personal branding**. Il ne cherche pas à concurrencer yt-dlp sur
l'ampleur des extracteurs (il *est* yt-dlp sous le capot). Ce qu'il
ajoute :

- **Formes de retour normalisées** — les métriques d'engagement suivent
  le même schéma sur YouTube / Vimeo / DailyMotion / Twitch, si bien que
  le code en aval n'a pas besoin de branches par site. C'est l'écart
  derrière la note « info dict brut » de yt-dlp : la donnée est là, mais
  non normalisée.
- **Résolveur d'URL directe + catalogue de flux + sélecteur** — transforme
  la liste `formats` brute de yt-dlp en un objet de première classe avec
  des filtres codec / fps / langue, prêt à passer à
  `ffmpeg` / `video-helper.extract_frames`.
- **Métadonnées de branding sans API** — instantanés au niveau de la
  chaîne, engagement par vidéo, échantillons de commentaires,
  téléchargements de sous-titres sans toucher à l'API Google Data (pas
  d'OAuth, pas de quota, pas de valse client_id / secret).
  `google-api-python-client` obtient la note maximale sur l'engagement
  justement parce qu'il est canonique, mais il ne renvoie aucun fichier
  média et coûte OAuth + quota.
- **Surfaces multiples** — les mêmes opérations sont disponibles comme
  bibliothèque Python, CLI argparse, CLI click et surface HTTP FastAPI.
  `yt-dlp` vous donne les deux premières ; les deux dernières sont
  propres à ce wrapper.
- **Prêt pour Docker** — un seul `docker run` et vous avez un serveur
  HTTP local pour n'importe quelle URL prise en charge par yt-dlp.

## Quand choisir quoi

- **`youtube-helper`** — téléchargement + métadonnées d'engagement pour
  les pipelines d'IA / personal branding, surtout quand on veut le même
  outillage en bibliothèque, CLI et HTTP.
- **`yt-dlp`** (direct) — vous possédez déjà le pipeline et il vous faut
  seulement l'info dict brut / les fichiers, sans couche de normalisation.
- **`youtube-dl`** — chemins de code hérités ; le jeu d'extracteurs a
  dérivé, la migration vers `yt-dlp` est fortement recommandée.
- **`pytube` / `pytubefix`** — Python pur, sans dépendance yt-dlp, mais
  limité à YouTube et légèrement en retard sur les mises à jour
  d'extracteurs (`pytubefix` est le fork maintenu).
- **`google-api-python-client`** — vous avez besoin des compteurs
  canoniques de vues / likes / abonnés, de données de rétention /
  d'analytics ou vous payez déjà le coût OAuth + quota.
- **`streamlink`** — flux de travail orienté direct ; vous voulez passer
  une URL live directement à un lecteur sans enregistrer.
- **`gallery-dl`** — téléchargements en masse de galeries d'images /
  médias sur de nombreux sites ; la couverture est large mais l'outil
  n'est pas pensé pour les flux vidéo ni les métadonnées d'engagement.
- **`scrapetube`** — vous n'avez besoin que d'énumérer les identifiants
  de vidéos d'une chaîne / playlist / recherche sans l'API Data, sans
  téléchargement.
- **`youtube-comment-downloader`** — vous n'avez besoin que d'aspirer en
  masse les commentaires d'une vidéo sans toucher à l'API Data, rien
  d'autre.
