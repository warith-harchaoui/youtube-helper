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

| Acquisition de médias | Multi-plateforme | Téléchargement média | Résolveur d'URL directe | Sélecteur de flux | Engagement sans API | Multi-surface | Prêt pour Docker | Ergonomie pipeline IA |
| --- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **youtube-helper** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| yt-dlp | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ |
| youtube-dl | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐⭐ | ⭐⭐ | ⭐⭐ | ⭐⭐ |
| pytube | ⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐⭐ | ⭐⭐ | ⭐⭐⭐ |
| pytubefix | ⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐⭐ | ⭐⭐ | ⭐⭐⭐ |
| YouTube Data API | ⭐ | ⭐ | ⭐ | ⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ | ⭐⭐ |
| Playwright / Selenium | ⭐⭐⭐ | ⭐⭐ | ⭐ | ⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐⭐ | ⭐ |
| you-get | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐⭐ | ⭐⭐ | ⭐⭐ | ⭐⭐ |
| streamlink | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐ | ⭐⭐ | ⭐⭐⭐ | ⭐⭐ |
| youtube_transcript_api | ⭐ | ⭐ | ⭐ | ⭐ | ⭐⭐ | ⭐⭐ | ⭐⭐ | ⭐⭐⭐ |
| ArchiveBox | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ |

## Carte de positionnement

Une ACP du tableau ci-dessus, projetée sur deux axes lisibles. La référence est placée en haut à droite ; plus on va vers le haut et la droite, plus l'outil est fort sur ces dimensions.

![Carte de positionnement](https://raw.githubusercontent.com/warith-harchaoui/youtube-helper/main/assets/paysage.png)

La carte positionne les outils selon un axe horizontal allant d'une interaction minimale sans interface à une efficacité directe, et un axe vertical variant du téléchargement immédiat à une intégration fluide. La référence **youtube-helper** se situe en haut à droite, où l'efficacité et l'intégration sont maximisées, confirmant son statut de meilleur outil. **yt-dlp** se distingue par son innovation, positionné vers la droite, tandis que **ArchiveBox** incarne la fiabilité, proche de la zone haute. Les outils comme **streamlink** et **pytubefix** occupent des positions intermédiaires, reflétant un équilibre entre performance et adaptabilité. Le classement global met en avant une progression de la fiabilité à l'innovation, avec **youtube-helper** en tête, suivi de **yt-dlp** et **ArchiveBox**, soulignant une tendance vers des solutions plus intégrées et fiables.

- **Horizontal — Interaction sans Interface ↔ Efficacité directe** (58% de variance)
- **Vertical — Téléchargement direct ↔ Intégration fluide** (21% de variance)


## Positionnement

`youtube-helper` se place volontairement à l'intersection de la
**couverture brute de yt-dlp** et de l'**ergonomie des pipelines d'IA /
personal branding**. Il ne cherche pas à concurrencer yt-dlp sur
l'ampleur des extracteurs (il *est* yt-dlp sous le capot). Ce qu'il
apporte :

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
  d'OAuth, pas de quota, pas de valse client_id / secret). L'`API
  YouTube Data` obtient la note maximale sur l'engagement justement parce
  qu'elle est canonique, mais elle ne renvoie aucun fichier média et coûte
  OAuth + quota.
- **Surfaces multiples** — les mêmes opérations sont disponibles comme
  bibliothèque Python, CLI argparse, CLI click, surface HTTP FastAPI et
  outils MCP. `yt-dlp` vous donne les deux premières ; les trois
  dernières sont propres à cet emballage.
- **Prêt pour Docker** — un seul `docker run` et vous avez un serveur
  HTTP + MCP local pour n'importe quelle URL prise en charge par yt-dlp.

## Quand choisir quoi

- **`youtube-helper`** — téléchargement + métadonnées d'engagement pour
  les pipelines d'IA / personal branding, surtout quand on veut le même
  outillage en bibliothèque, CLI, HTTP et MCP.
- **`yt-dlp`** (direct) — vous possédez déjà le pipeline et il vous faut
  seulement l'info dict brut / les fichiers, sans couche de normalisation.
- **`youtube-dl`** — chemins de code hérités ; le jeu d'extracteurs a
  dérivé, la migration vers `yt-dlp` est fortement recommandée.
- **`pytube` / `pytubefix`** — Python pur, sans dépendance yt-dlp, mais
  limité à YouTube et légèrement en retard sur les mises à jour
  d'extracteurs (`pytubefix` est le fork maintenu).
- **API YouTube Data** — vous avez besoin des compteurs canoniques de
  vues / likes / abonnés, de données de rétention / d'analytics, ou vous
  payez déjà le coût OAuth + quota.
- **Playwright / Selenium** — le site n'expose pas d'extracteur et vous
  devez scraper la page rendue.
- **`you-get`** — un téléchargeur multi-sites large quand yt-dlp n'est pas
  envisageable ; la couverture est vaste mais inférieure à yt-dlp.
- **`streamlink`** — flux de travail orienté direct ; vous voulez passer
  une URL live directement à un lecteur sans enregistrer.
- **`youtube_transcript_api`** — vous n'avez besoin que des
  transcriptions, sans téléchargement ni autres métadonnées.
- **ArchiveBox** — vous construisez une archive personnelle d'URL avec une
  interface auto-hébergée, pas un pipeline natif code.
