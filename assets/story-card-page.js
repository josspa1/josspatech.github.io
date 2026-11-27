/**
 * Shared story-card web viewer for /cvc/card/{id} and /hhh/card/{id}.
 * Text-only PocketBase record — no photo bytes. Renders in the browser language.
 * © 2026 JosspaTech. All Rights Reserved.
 */
(function () {
  'use strict';

  var PB = 'https://josspatech.pockethost.io/api/collections/story_cards/records';

  var STORE = {
    cvc: {
      play: 'com.josspatech.cts',
      apple: '6778571307',
      product: 'https://josspatech.com/cvc/',
      name: "Curator's Vault: Classics",
      accent: '#1B4D3E',
    },
    hhh: {
      play: 'com.josspatech.handyhorology',
      apple: '6778570480',
      product: 'https://josspatech.com/hhh/',
      name: 'Handy Horology',
      accent: '#0C3358',
    },
  };

  /**
   * UI chrome only — identification/story come from the card / translations_json.
   * en + es/de/fr/it/pt/zh/hi UI chrome (APPLY_TRANSLATIONS 2026-11-27).
   */
  var UI = {
    en: {
      unavailable: 'This card is no longer available.',
      download: 'Get the app to keep this piece in your collection.',
      openApp: 'Open in app',
      expertise: 'Expertise',
      loading: 'Loading…',
      missing: 'We could not find this card.',
    },
    es: {
      unavailable: 'Esta tarjeta ya no está disponible.',
      download: 'Descarga la app para guardar esta pieza en tu colección.',
      openApp: 'Abrir en la app',
      expertise: 'Experiencia',
      loading: 'Cargando…',
      missing: 'No hemos encontrado esta tarjeta.',
    },
    de: {
      unavailable: 'Diese Karte ist nicht mehr verfügbar.',
      download: 'Hol dir die App, um dieses Stück in deiner Sammlung zu behalten.',
      openApp: 'In der App öffnen',
      expertise: 'Fachwissen',
      loading: 'Wird geladen …',
      missing: 'Diese Karte konnten wir nicht finden.',
    },
    fr: {
      unavailable: 'Cette carte n\'est plus disponible.',
      download: 'Téléchargez l\'application pour conserver cette pièce dans votre collection.',
      openApp: 'Ouvrir dans l\'application',
      expertise: 'Expertise',
      loading: 'Chargement…',
      missing: 'Nous n\'avons pas trouvé cette carte.',
    },
    it: {
      unavailable: 'Questa scheda non è più disponibile.',
      download: 'Scarica l\'app per conservare questo pezzo nella tua collezione.',
      openApp: 'Apri nell\'app',
      expertise: 'Esperienza',
      loading: 'Caricamento…',
      missing: 'Non abbiamo trovato questa scheda.',
    },
    pt: {
      unavailable: 'Este cartão não está mais disponível.',
      download: 'Baixe o app para guardar esta peça na sua coleção.',
      openApp: 'Abrir no app',
      expertise: 'Perícia',
      loading: 'Carregando…',
      missing: 'Não encontramos este cartão.',
    },
    zh: {
      unavailable: '此卡片已不可用。',
      download: '下载应用，将这件藏品收入您的收藏。',
      openApp: '在应用中打开',
      expertise: '专业评分',
      loading: '加载中…',
      missing: '未找到这张卡片。',
    },
    hi: {
      unavailable: 'यह कार्ड अब उपलब्ध नहीं है।',
      download: 'इस चीज़ को अपने कलेक्शन में रखने के लिए ऐप पाएँ।',
      openApp: 'ऐप में खोलें',
      expertise: 'विशेषज्ञता',
      loading: 'लोड हो रहा है…',
      missing: 'हमें यह कार्ड नहीं मिला।',
    },
  };

  var PLAY_HL = {
    en: '',
    es: 'es-419',
    de: 'de-DE',
    fr: 'fr-FR',
    pt: 'pt-BR',
    it: 'it-IT',
    zh: 'zh-CN',
    hi: 'hi-IN',
  };

  var APPLE_L = {
    en: '',
    es: 'es-MX',
    de: '',
    fr: '',
    pt: 'pt-BR',
    it: '',
    zh: 'zh-Hans-CN',
    hi: 'hi-IN',
  };

  var APPLE_STORE = {
    en: 'us',
    es: 'us',
    de: 'de',
    fr: 'fr',
    pt: 'us',
    it: 'it',
    zh: 'us',
    hi: 'in',
  };

  function browserLang() {
    try {
      var q = new URLSearchParams(location.search || '').get('lang');
      if (q) {
        var q2 = String(q).toLowerCase().slice(0, 2);
        if (q2 === 'zh') return 'zh';
        if (UI[q2] || PLAY_HL[q2]) return q2;
      }
    } catch (e) {}
    var raw = (navigator.language || navigator.userLanguage || 'en').toLowerCase();
    var two = raw.slice(0, 2);
    if (two === 'zh') return 'zh';
    if (UI[two]) return two;
    return 'en';
  }

  function parsePath() {
    var m = location.pathname.match(/^\/(cvc|hhh)\/card\/([^\/]+)\/?$/i);
    if (!m) return null;
    return { app: m[1].toLowerCase(), id: decodeURIComponent(m[2]) };
  }

  function playUrl(app, lang) {
    var id = STORE[app].play;
    var hl = PLAY_HL[lang] || '';
    return 'https://play.google.com/store/apps/details?id=' + id + (hl ? '&hl=' + hl : '');
  }

  function appleUrl(app, lang) {
    var id = STORE[app].apple;
    var store = APPLE_STORE[lang] || 'us';
    var l = APPLE_L[lang] || '';
    var base = 'https://apps.apple.com/' + store + '/app/id' + id;
    return l ? base + '?l=' + l : base;
  }

  function appScheme(app, id) {
    return app + '://card/' + encodeURIComponent(id);
  }

  function el(tag, attrs, children) {
    var node = document.createElement(tag);
    if (attrs) {
      Object.keys(attrs).forEach(function (k) {
        if (k === 'text') node.textContent = attrs[k];
        else if (k === 'html') node.innerHTML = attrs[k];
        else node.setAttribute(k, attrs[k]);
      });
    }
    (children || []).forEach(function (c) {
      if (c) node.appendChild(c);
    });
    return node;
  }

  function renderShell(app, lang) {
    document.documentElement.lang = lang;
    document.body.innerHTML = '';
    document.body.style.cssText =
      'margin:0;font-family:DM Sans,Segoe UI,sans-serif;background:#F7F5F0;color:#0F2E25;min-height:100vh;';
    var wrap = el('main', {
      style:
        'max-width:440px;margin:0 auto;padding:28px 20px 48px;display:flex;flex-direction:column;gap:18px;',
    });
    wrap.id = 'story-card-root';
    document.body.appendChild(wrap);
    wrap.appendChild(
      el('p', {
        id: 'sc-status',
        text: (UI[lang] || UI.en).loading,
        style: 'opacity:0.7;margin:40px 0;text-align:center;',
      }),
    );
    return wrap;
  }

  function pickLocalized(row, lang) {
    var map = {};
    try {
      map = JSON.parse(row.translations_json || '{}') || {};
    } catch (e) {
      map = {};
    }
    var hit = map[lang];
    if (hit && typeof hit === 'object') {
      return {
        maker: hit.maker || row.maker || '',
        title: hit.title || row.title || '',
        storyExcerpt: hit.storyExcerpt || hit.story_excerpt || row.story_excerpt || '',
        identification: hit.identification || {},
      };
    }
    var ident = {};
    try {
      ident = JSON.parse(row.identification_json || '{}') || {};
    } catch (e2) {
      ident = {};
    }
    return {
      maker: row.maker || '',
      title: row.title || '',
      storyExcerpt: row.story_excerpt || '',
      identification: ident,
    };
  }

  function showUnavailable(wrap, lang, softMissing) {
    var ui = UI[lang] || UI.en;
    wrap.innerHTML = '';
    wrap.appendChild(
      el('h1', {
        text: softMissing ? ui.missing : ui.unavailable,
        style: 'font-family:Playfair Display,Georgia,serif;font-size:28px;margin:48px 0 12px;text-align:center;',
      }),
    );
  }

  function showCard(wrap, app, lang, row, loc) {
    var ui = UI[lang] || UI.en;
    var cfg = STORE[app];
    wrap.innerHTML = '';

    var card = el('article', {
      style:
        'background:#fff;border-radius:16px;overflow:hidden;box-shadow:0 12px 40px rgba(12,51,88,0.12);',
    });
    var body = el('div', { style: 'padding:22px 22px 8px;' });
    body.appendChild(
      el('div', {
        text: loc.maker || cfg.name,
        style: 'font-size:24px;font-weight:700;color:' + cfg.accent + ';',
      }),
    );
    if (loc.title) {
      body.appendChild(
        el('div', {
          text: loc.title,
          style: 'font-size:17px;color:#556B60;margin-top:4px;font-weight:600;',
        }),
      );
    }
    var detailBits = [row.year, row.catalog_ref, row.category].filter(Boolean);
    if (detailBits.length) {
      body.appendChild(
        el('div', {
          text: detailBits.join(' · '),
          style: 'font-size:13px;color:#586862;margin-top:10px;line-height:1.35;',
        }),
      );
    }
    if (loc.storyExcerpt) {
      body.appendChild(
        el('p', {
          text: loc.storyExcerpt,
          style: 'font-size:14px;margin-top:16px;line-height:1.45;',
        }),
      );
    }
    card.appendChild(body);

    if (row.expertise_score !== null && row.expertise_score !== undefined && row.expertise_score !== '') {
      card.appendChild(
        el('div', {
          text: ui.expertise + ': ' + String(Math.round(Number(row.expertise_score))),
          style: 'font-size:12px;color:#556B60;margin:12px 22px 0;font-weight:600;',
        }),
      );
    }

    card.appendChild(
      el('div', {
        style: 'margin-top:20px;padding:14px 22px;background:' + cfg.accent + ';color:#fff;',
        text: cfg.name,
      }),
    );
    wrap.appendChild(card);

    wrap.appendChild(
      el('p', {
        text: ui.download,
        style: 'text-align:center;line-height:1.45;margin:8px 0 0;',
      }),
    );

    var stores = el('div', {
      style: 'display:flex;flex-direction:column;gap:10px;margin-top:8px;',
    });
    stores.appendChild(
      el('a', {
        href: playUrl(app, lang),
        text: 'Google Play',
        style:
          'display:block;text-align:center;padding:12px;border-radius:10px;background:#111;color:#fff;text-decoration:none;font-weight:600;',
        target: '_blank',
        rel: 'noopener',
      }),
    );
    stores.appendChild(
      el('a', {
        href: appleUrl(app, lang),
        text: 'App Store',
        style:
          'display:block;text-align:center;padding:12px;border-radius:10px;background:#0C3358;color:#fff;text-decoration:none;font-weight:600;',
        target: '_blank',
        rel: 'noopener',
      }),
    );
    stores.appendChild(
      el('a', {
        href: appScheme(app, row.id),
        text: ui.openApp,
        style:
          'display:block;text-align:center;padding:12px;border-radius:10px;border:1px solid ' +
          cfg.accent +
          ';color:' +
          cfg.accent +
          ';text-decoration:none;font-weight:600;',
      }),
    );
    wrap.appendChild(stores);
  }

  function boot() {
    var path = parsePath();
    var lang = browserLang();
    if (!path || !STORE[path.app]) {
      document.body.textContent = 'Not found';
      return;
    }
    var wrap = renderShell(path.app, lang);
    fetch(PB + '/' + encodeURIComponent(path.id))
      .then(function (r) {
        if (r.status === 404) return { __missing: true };
        if (!r.ok) throw new Error('http ' + r.status);
        return r.json();
      })
      .then(function (row) {
        if (row.__missing) {
          showUnavailable(wrap, lang, true);
          return;
        }
        if (row.deleted === true || row.deleted === 'true' || row.deleted === 1) {
          showUnavailable(wrap, lang, false);
          return;
        }
        if (row.app && String(row.app).toLowerCase() !== path.app) {
          showUnavailable(wrap, lang, true);
          return;
        }
        showCard(wrap, path.app, lang, row, pickLocalized(row, lang));
      })
      .catch(function () {
        showUnavailable(wrap, lang, true);
      });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot);
  } else {
    boot();
  }
})();
