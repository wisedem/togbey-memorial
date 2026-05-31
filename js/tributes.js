/* Tribute wall + post-submit thank-you modal.
   Shared by index.html (FR) and en/index.html (EN); language is read from <html lang>.
   All user-derived text is inserted with textContent (never innerHTML) — XSS-safe. */
(function () {
  'use strict';
  var lang = (document.documentElement.lang || 'fr').slice(0, 2).toLowerCase();
  var FR = lang === 'fr';

  /* ===================== 1. Public tribute wall ===================== */
  (function wall() {
    var section = document.getElementById('tributes');
    var mount = document.getElementById('tribute-wall');
    if (!section || !mount) return;

    fetch('/tributes.json?v=' + Date.now(), { cache: 'no-store' })
      .then(function (r) { if (!r.ok) throw new Error('http ' + r.status); return r.json(); })
      .then(function (data) {
        if (!Array.isArray(data)) return;                       // malformed -> stay hidden
        // Every approved message shows on BOTH language pages, in sync — no language filter.
        var entries = data.filter(function (e) {
          return e && typeof e.message === 'string' && e.message.trim();
        });
        if (!entries.length) return;                            // empty -> stay hidden

        entries.forEach(function (e) { mount.appendChild(buildCard(e)); });
        section.hidden = false;
        revealCards(section);
      })
      .catch(function () { /* network/parse error -> section stays hidden, looks intentional */ });

    function buildCard(e) {
      var card = document.createElement('figure');
      card.className = 'card tribute-card reveal';

      var msg = document.createElement('blockquote');
      msg.className = 'tribute-msg';
      msg.textContent = e.message;                              // XSS-safe
      card.appendChild(msg);

      var foot = document.createElement('figcaption');
      foot.className = 'tribute-by';

      var nm = document.createElement('span');
      nm.className = 'tribute-name';
      nm.textContent = e.name || (FR ? 'Anonyme' : 'Anonymous');
      foot.appendChild(nm);

      var bits = [];
      if (e.place) bits.push(String(e.place));
      if (e.date) bits.push(formatDate(e.date));
      if (bits.length) {
        var meta = document.createElement('span');
        meta.className = 'tribute-meta';
        meta.textContent = bits.join(' · ');                    // XSS-safe
        foot.appendChild(meta);
      }
      card.appendChild(foot);
      return card;
    }

    function formatDate(iso) {
      var d = new Date(iso);
      if (isNaN(d.getTime())) return String(iso);
      try { return d.toLocaleDateString(FR ? 'fr-FR' : 'en-GB',
              { year: 'numeric', month: 'long', day: 'numeric' }); }
      catch (_) { return String(iso); }
    }

    function revealCards(section) {
      var wrap = section.querySelector('.reveal');
      if (wrap) wrap.classList.add('in');
      requestAnimationFrame(function () {
        var cards = section.querySelectorAll('.tribute-card.reveal');
        Array.prototype.forEach.call(cards, function (c, i) {
          setTimeout(function () { c.classList.add('in'); }, 60 * i);  // gentle stagger
        });
      });
    }
  })();

  /* ===================== 2. Thank-you modal (Cognito afterSubmit) ===================== */
  (function modal() {
    var scrim = document.getElementById('thanks-modal');
    if (!scrim) return;
    var closeBtn = scrim.querySelector('.modal-x');
    var publicNote = document.getElementById('thanks-public');
    var lastFocus = null;

    function open(isPublic) {
      if (publicNote) publicNote.hidden = !isPublic;
      scrim.hidden = false;
      lastFocus = document.activeElement;
      requestAnimationFrame(function () { scrim.classList.add('open'); });
      if (closeBtn) closeBtn.focus();
      document.addEventListener('keydown', onKey);
    }
    function close() {
      scrim.classList.remove('open');
      document.removeEventListener('keydown', onKey);
      setTimeout(function () { scrim.hidden = true; }, 260);
      if (lastFocus && lastFocus.focus) lastFocus.focus();
    }
    function onKey(e) { if (e.key === 'Escape' || e.key === 'Esc') close(); }

    if (closeBtn) closeBtn.addEventListener('click', close);
    scrim.addEventListener('click', function (e) { if (e.target === scrim) close(); });

    // expose for manual testing: window.__thanks(true|false)
    window.__thanks = open;

    // Detect the public-sharing consent in the submitted entry without depending on the
    // exact field name: scan keys whose name suggests sharing/public for a "yes"-like value.
    function isPublic(entry) {
      if (!entry || typeof entry !== 'object') return false;
      var keyRx = /(share|public|publi|partag)/i;
      function yes(v) {
        if (v === true) return true;
        if (typeof v === 'string') {
          var s = v.trim().toLowerCase();
          return s === 'yes' || s === 'oui' || s === 'true' || s === 'public' || s === 'publique';
        }
        return false;
      }
      for (var k in entry) {
        if (Object.prototype.hasOwnProperty.call(entry, k) && keyRx.test(k) && yes(entry[k])) return true;
      }
      return false;
    }

    // Register the Cognito handler once the global is available (timing not guaranteed).
    var tries = 0;
    (function bind() {
      if (window.Cognito && typeof window.Cognito.on === 'function') {
        window.Cognito.on('afterSubmit', function (event) {
          var pub = false;
          try {
            var d = event && event.data ? event.data : event;
            pub = isPublic(d && d.entry);
          } catch (_) {}
          open(pub);
        });
        return;
      }
      if (tries++ < 100) setTimeout(bind, 100);  // poll ~10s, then give up silently
    })();
  })();
})();
