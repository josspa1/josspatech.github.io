/* How-to player: one animated, narrated clip per feature + a read-along transcript.
   data-howto = folder holding langs.json and <lang>/chapters.json */
(function () {
  var root = document.querySelector('[data-howto]');
  if (!root) return;
  var base = root.getAttribute('data-howto').replace(/\/?$/, '/');
  var nav = root.querySelector('.howto-chapters');
  var video = root.querySelector('video');
  var startBtn = root.querySelector('.howto-start');
  var list = root.querySelector('.howto-steps');
  var title = root.querySelector('.howto-transcript h3');
  var count = root.querySelector('.howto-transcript .count');
  var prev = root.querySelector('[data-prev]');
  var next = root.querySelector('[data-next]');
  var pos = root.querySelector('[data-pos]');
  var langBox = root.querySelector('.howto-lang');
  var chapters = [], cur = -1, rows = [], started = false, userScroll = 0, lang = 'en';

  var UI = {
    en: { name: 'English', chapter: 'Chapter {a} of {b}', steps: '{n} steps', play: 'Tap to play', prev: 'Previous', next: 'Next', lang: 'Language', pause: 'Pause', resume: 'Play' },
    es: { name: 'Español', chapter: 'Capítulo {a} de {b}', steps: '{n} pasos', play: 'Toca para ver', prev: 'Anterior', next: 'Siguiente', lang: 'Idioma', pause: 'Pausa', resume: 'Reproducir' },
    zh: { name: '中文', chapter: '第 {a} 章，共 {b} 章', steps: '{n} 个步骤', play: '点按播放', prev: '上一章', next: '下一章', lang: '语言', pause: '暂停', resume: '播放' },
    de: { name: 'Deutsch', chapter: 'Kapitel {a} von {b}', steps: '{n} Schritte', play: 'Zum Abspielen tippen', prev: 'Zurück', next: 'Weiter', lang: 'Sprache', pause: 'Pause', resume: 'Abspielen' },
    fr: { name: 'Français', chapter: 'Chapitre {a} sur {b}', steps: '{n} étapes', play: 'Touchez pour lire', prev: 'Précédent', next: 'Suivant', lang: 'Langue', pause: 'Pause', resume: 'Lecture' },
    pt: { name: 'Português', chapter: 'Capítulo {a} de {b}', steps: '{n} passos', play: 'Toque para assistir', prev: 'Anterior', next: 'Próximo', lang: 'Idioma', pause: 'Pausar', resume: 'Continuar' },
    it: { name: 'Italiano', chapter: 'Capitolo {a} di {b}', steps: '{n} passaggi', play: 'Tocca per guardare', prev: 'Precedente', next: 'Successivo', lang: 'Lingua', pause: 'Pausa', resume: 'Riproduci' },
    hi: { name: 'हिन्दी', chapter: 'अध्याय {a} / {b}', steps: '{n} चरण', play: 'चलाने के लिए टैप करें', prev: 'पिछला', next: 'अगला', lang: 'भाषा', pause: 'रोकें', resume: 'चलाएँ' }
  };
  var pauseBtn = document.createElement('button');
  pauseBtn.type = 'button';
  next.parentNode.insertBefore(pauseBtn, next);
  function pauseLabel() {
    pauseBtn.innerHTML = video.paused ? '&#9654; ' : '&#10074;&#10074; ';
    pauseBtn.appendChild(document.createTextNode(ui(video.paused ? 'resume' : 'pause')));
  }
  function togglePause() {
    if (video.paused) begin(); else video.pause();
  }
  pauseBtn.addEventListener('click', togglePause);
  video.addEventListener('play', pauseLabel);
  video.addEventListener('pause', pauseLabel);
  function ui(k, vars) {
    var s = (UI[lang] || UI.en)[k] || UI.en[k];
    for (var v in vars || {}) s = s.replace('{' + v + '}', vars[v]);
    return s;
  }

  list.parentElement.addEventListener('scroll', function () { userScroll = Date.now(); }, { passive: true });

  function setHash() {
    if (!history.replaceState || cur < 0) return;
    history.replaceState(null, '', '#' + (lang === 'en' ? '' : lang + '/') + chapters[cur].id);
  }

  function load(i, play) {
    if (i < 0 || i >= chapters.length) return;
    cur = i;
    var ch = chapters[i], dir = base + lang + '/';
    Array.prototype.forEach.call(nav.children, function (b, k) { b.classList.toggle('active', k === i); });
    video.src = dir + ch.src;
    video.poster = ch.poster ? dir + ch.poster : '';
    title.textContent = ch.title;
    count.textContent = ui('chapter', { a: i + 1, b: chapters.length }) + ' · ' + ui('steps', { n: ch.steps.length });
    pos.textContent = (i + 1) + ' / ' + chapters.length;
    prev.disabled = i === 0;
    next.disabled = i === chapters.length - 1;
    list.innerHTML = '';
    rows = ch.steps.map(function (s, k) {
      var row = document.createElement('div');
      row.className = 'howto-step';
      row.innerHTML = '<span class="n">' + (k + 1) + '</span><span class="t"></span>';
      row.querySelector('.t').textContent = s.text;
      row.addEventListener('click', function () {
        video.currentTime = s.start + 0.01;
        begin();
      });
      list.appendChild(row);
      return row;
    });
    setHash();
    if (play) begin();
  }

  function begin() {
    started = true;
    startBtn.classList.add('hidden');
    var p = video.play();
    if (p && p.catch) p.catch(function () { startBtn.classList.remove('hidden'); });
  }

  function sync() {
    if (cur < 0) return;
    var t = video.currentTime, steps = chapters[cur].steps;
    for (var k = 0; k < rows.length; k++) {
      var on = t >= steps[k].start && t < steps[k].end;
      rows[k].classList.toggle('active', on);
      rows[k].classList.toggle('past', t >= steps[k].end);
      if (on && Date.now() - userScroll > 2500) {
        var box = list.parentElement, r = rows[k];
        var top = r.offsetTop - box.offsetTop;
        if (top < box.scrollTop + 40 || top + r.offsetHeight > box.scrollTop + box.clientHeight - 40) {
          box.scrollTop = Math.max(0, top - 60);
        }
      }
    }
  }

  function chrome() {
    startBtn.querySelector('.label').textContent = ui('play');
    prev.innerHTML = '&#9664; ';
    prev.appendChild(document.createTextNode(ui('prev')));
    next.textContent = ui('next') + ' ';
    next.insertAdjacentHTML('beforeend', '&#9654;');
    pauseLabel();
  }

  function openLang(code, wantId) {
    lang = code;
    if (langBox) {
      var sel = langBox.querySelector('select');
      if (sel) sel.value = code;
      var lab = langBox.querySelector('label span');
      if (lab) lab.textContent = ui('lang');
    }
    chrome();
    var keepId = wantId || (cur >= 0 && chapters[cur] ? chapters[cur].id : '');
    fetch(base + code + '/chapters.json', { cache: 'no-cache' }).then(function (r) { return r.json(); }).then(function (data) {
      chapters = data.chapters || [];
      nav.innerHTML = '';
      chapters.forEach(function (ch, i) {
        var b = document.createElement('button');
        b.type = 'button';
        b.textContent = ch.title;
        b.addEventListener('click', function () { load(i, started); });
        nav.appendChild(b);
      });
      var idx = 0;
      chapters.forEach(function (ch, i) { if (ch.id === keepId) idx = i; });
      load(idx, false);
    });
  }

  video.addEventListener('timeupdate', sync);
  video.addEventListener('seeked', sync);
  video.addEventListener('play', function () { startBtn.classList.add('hidden'); });
  video.addEventListener('ended', function () {
    if (cur < chapters.length - 1) load(cur + 1, true);
  });
  startBtn.addEventListener('click', begin);
  prev.addEventListener('click', function () { load(cur - 1, started); });
  next.addEventListener('click', function () { load(cur + 1, started); });

  fetch(base + 'langs.json', { cache: 'no-cache' }).then(function (r) { return r.json(); }).catch(function () { return { langs: ['en'] }; }).then(function (d) {
    var langs = (d.langs || ['en']).filter(function (c) { return UI[c]; });
    var h = (location.hash || '').replace('#', '').split('/');
    var hashLang = h.length > 1 ? h[0] : '';
    var wantId = h[h.length - 1];
    var pick = 'en';
    if (langs.indexOf(hashLang) >= 0) pick = hashLang;
    else {
      var nl = (navigator.language || 'en').slice(0, 2).toLowerCase();
      if (langs.indexOf(nl) >= 0) pick = nl;
    }
    if (langBox) {
      if (langs.length < 2) langBox.style.display = 'none';
      else {
        var sel = document.createElement('select');
        langs.forEach(function (c) {
          var o = document.createElement('option');
          o.value = c;
          o.textContent = UI[c].name;
          sel.appendChild(o);
        });
        sel.addEventListener('change', function () { openLang(sel.value); });
        var lab = document.createElement('label');
        lab.innerHTML = '<span></span> ';
        lab.appendChild(sel);
        langBox.appendChild(lab);
      }
    }
    openLang(pick, wantId);
  });
})();
