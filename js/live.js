/* Live broadcast section + first-visit pop-up.
 *
 * Configuration lives inline per page in window.LIVE_CONFIG (one block per
 * language). ON CEREMONY DAY you only edit that config — no code changes here:
 *   1. Paste each ceremony's YouTube link into its `url` (watch/live/share URL
 *      or bare video id — all forms accepted).
 *   2. Set `live:true` for whichever broadcast is on air now (adds the "EN DIRECT"
 *      badge and lets it drive the pop-up).
 *   3. Set `popup:true` to arm the first-visit pop-up; set it back to false after.
 * Leaving a `url` empty keeps that ceremony in the "coming soon" state.
 */
(function () {
  var cfg = window.LIVE_CONFIG;
  if (!cfg || !Array.isArray(cfg.broadcasts)) return;
  var t = cfg.i18n || {};

  // Pull the 11-char video id out of any YouTube URL form (watch?v=, youtu.be/,
  // /live/, /embed/, /shorts/) or accept a bare id. Returns '' if none.
  function ytId(u) {
    if (!u) return '';
    u = String(u).trim();
    var m = u.match(/(?:youtu\.be\/|youtube\.com\/(?:watch\?v=|live\/|embed\/|shorts\/|v\/))([\w-]{6,})/);
    if (m) return m[1];
    if (/^[\w-]{6,}$/.test(u)) return u;          // already a bare id
    return '';
  }

  /* ---------------- section cards (one per broadcast) ---------------- */
  var list = document.getElementById('live-list');
  if (list) {
    list.textContent = '';                        // drop the <noscript> fallback
    cfg.broadcasts.forEach(function (b) {
      var card = document.createElement('article');
      card.className = 'live-item';

      var h = document.createElement('h3');
      h.textContent = b.label || '';
      var id = ytId(b.url);
      if (b.live && id) {
        var badge = document.createElement('span');
        badge.className = 'live-badge';
        badge.textContent = t.liveBadge || 'LIVE';
        h.appendChild(document.createTextNode(' '));
        h.appendChild(badge);
      }
      card.appendChild(h);

      if (b.when) {
        var w = document.createElement('p');
        w.className = 'live-when';
        w.textContent = b.when;
        card.appendChild(w);
      }

      if (id) {                                   // embed the player on the page
        var box = document.createElement('div');
        box.className = 'live-embed';
        var ifr = document.createElement('iframe');
        ifr.src = 'https://www.youtube.com/embed/' + id + '?rel=0';
        ifr.title = b.label || 'Live';
        ifr.allow = 'accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share';
        ifr.setAttribute('allowfullscreen', '');
        ifr.loading = 'lazy';
        box.appendChild(ifr);
        card.appendChild(box);

        var yt = document.createElement('a');     // fallback link for blocked embeds
        yt.className = 'live-yt';
        yt.href = 'https://www.youtube.com/watch?v=' + id;
        yt.target = '_blank';
        yt.rel = 'noopener';
        yt.textContent = t.openYt || 'Open on YouTube';
        card.appendChild(yt);
      } else {                                    // coming-soon placeholder
        var soon = document.createElement('div');
        soon.className = 'live-soon';
        var ic = document.createElement('span');
        ic.className = 'live-ic';
        ic.setAttribute('aria-hidden', 'true');
        ic.textContent = '▶';                // ▶
        var msg = document.createElement('div');
        var s1 = document.createElement('strong');
        s1.textContent = t.soon || 'Coming soon';
        msg.appendChild(s1);
        if (t.soonNote) {
          var s2 = document.createElement('p');
          s2.className = 'live-pending';
          s2.textContent = t.soonNote;
          msg.appendChild(s2);
        }
        soon.appendChild(ic);
        soon.appendChild(msg);
        card.appendChild(soon);
      }
      list.appendChild(card);
    });
  }

  /* ---------------- promotion: auto-banner + first-visit pop-up ---------------- */
  // Anything on air? (a broadcast marked live:true with a usable url)
  var liveOne = cfg.broadcasts.filter(function (b) { return b.live && ytId(b.url); })[0];
  if (!liveOne) return;                           // nothing live -> no banner, no pop-up

  function gotoLive() {
    var sec = document.getElementById('live');
    if (sec) sec.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  // Auto-promote banner: surfaces at the very top whenever a ceremony is streaming.
  // Independent of the pop-up — it stays until the viewer dismisses it (for the session).
  var banner = document.getElementById('live-banner');
  if (banner) {
    var BKEY = 'togbeyLiveBanner';
    var hidden = false;
    try { hidden = sessionStorage.getItem(BKEY) === '1'; } catch (e) {}
    if (!hidden) {
      var label = banner.querySelector('[data-live-banner]');
      if (label && t.bannerText) label.textContent = t.bannerText;
      var go = banner.querySelector('[data-live-banner-go]');
      var bx = banner.querySelector('[data-live-banner-close]');
      if (go) go.addEventListener('click', gotoLive);
      if (bx) bx.addEventListener('click', function () {
        document.body.classList.remove('live-on');   // also restores the nav offset
        try { sessionStorage.setItem(BKEY, '1'); } catch (e) {}
      });
      document.body.classList.add('live-on');        // reveals the banner + shifts the nav down
    }
  }

  // First-visit pop-up: only when explicitly armed via cfg.popup.
  var scrim = document.getElementById('live-modal');
  if (!(cfg.popup && scrim)) return;

  var KEY = 'togbeyLivePopup';                    // show at most once per session
  try { if (sessionStorage.getItem(KEY) === '1') return; } catch (e) {}

  var titleEl = scrim.querySelector('[data-live-title]');
  var bodyEl  = scrim.querySelector('[data-live-body]');
  var watch   = scrim.querySelector('[data-live-watch]');
  var dismiss = scrim.querySelector('[data-live-dismiss]');
  var closeX  = scrim.querySelector('.modal-x');
  if (titleEl && t.popupTitle)   titleEl.textContent = t.popupTitle;
  if (bodyEl  && t.popupBody)    bodyEl.textContent  = t.popupBody;
  if (watch   && t.popupWatch)   watch.textContent   = t.popupWatch;
  if (dismiss && t.popupDismiss) dismiss.textContent = t.popupDismiss;

  function close() {
    scrim.classList.remove('open');
    try { sessionStorage.setItem(KEY, '1'); } catch (e) {}
    document.removeEventListener('keydown', onKey);
    setTimeout(function () { scrim.hidden = true; }, 260);
  }
  function onKey(e) { if (e.key === 'Escape' || e.key === 'Esc') close(); }

  if (watch) watch.addEventListener('click', function () { close(); gotoLive(); });
  if (dismiss) dismiss.addEventListener('click', close);
  if (closeX) closeX.addEventListener('click', close);
  scrim.addEventListener('click', function (e) { if (e.target === scrim) close(); });
  document.addEventListener('keydown', onKey);

  scrim.hidden = false;
  requestAnimationFrame(function () { scrim.classList.add('open'); });
})();
