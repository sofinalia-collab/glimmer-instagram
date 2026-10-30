# Publicare automată — săptămâna 31.10–06.11.2026

Programul: `posts/schedule.json` (o zi = o listă de elemente). Totul se publică zilnic la 08:40 (Europe/Chisinau),
pe contul Instagram glimmer3947 (Windsor.ai, connector `instagram`, account `17841468641081785`).
Publicarea fără aprobare suplimentară a fost cerută explicit pentru această săptămână.

Respectă RULES.md (imagini de produs doar de pe cosmeticshop.md/glimmer).

Pași la fiecare rulare:
1. Ia ziua de azi (Europe/Chisinau) din `schedule.json`; publică doar elementele cu `status: "pending"`.
2. Verifică că fiecare URL de imagine/video răspunde 200 (repo-ul trebuie să fie public).
3. Pentru `image_post`: deschide `price_check_urls` și compară prețurile cu cele din `caption`.
   Dacă diferă, actualizează prețurile în caption înainte de publicare; dacă produsul nu e în stoc, nu publica și raportează.
4. Publică: story → `create_story`, image_post → `create_image_post`, reel → `create_video_post` (share_to_feed: true, cover_url).
5. Marchează `status: "published"` + `media_id`, commit și push.
6. După 2026-11-06 nu mai publica nimic; dezactivează rutina.
