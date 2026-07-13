(function () {
  var current = 0;
  var playing = false;
  var voiceEnabled = true;
  var slideAudio = null;
  var timer = null;
  var CHANGE_BUFFER_MS = 400;
  var SAME_BUFFER_MS = 100;
  var FALLBACK_WPM_MS = 380;
  var MIN_FALLBACK_MS = 1500;
  var MAX_FALLBACK_MS = 12000;
  var slides = document.querySelectorAll('.slide');
  var dots = document.querySelectorAll('.dot');
  var paras = document.querySelectorAll('.transcript-para');
  var playBtn = document.getElementById('playPauseBtn');
  var voiceBtn = document.getElementById('voiceBtn');
  var speedLabel = document.getElementById('speedLabel');
  var tapStart = document.getElementById('tapToStart');
  var recordMode = /[?&]record=1/.test(location.search);
  if (recordMode) document.body.classList.add('record-mode');

  function slideImgKey(i) {
    var s = slides[i];
    if (!s) return '';
    var img = s.querySelector('img[src]');
    if (img) return img.getAttribute('src') || '';
    return 'placeholder:' + i;
  }

  function advanceDelayMs(fromIndex) {
    var idx = fromIndex !== undefined ? fromIndex : current;
    var next = idx < LAST_SLIDE ? idx + 1 : 0;
    return slideImgKey(idx) === slideImgKey(next) ? SAME_BUFFER_MS : CHANGE_BUFFER_MS;
  }

  function estimateReadMs(i) {
    if (typeof NARRATION !== 'undefined' && NARRATION[i]) {
      var words = String(NARRATION[i]).split(/\s+/).filter(Boolean).length;
      return Math.min(MAX_FALLBACK_MS, Math.max(MIN_FALLBACK_MS, words * FALLBACK_WPM_MS));
    }
    return 4000;
  }

  function goTo(i) {
    current = Math.max(0, Math.min(i, LAST_SLIDE));
    if (window.PBJWalkthrough && window.PBJWalkthrough.clearTapPulse) {
      window.PBJWalkthrough.clearTapPulse();
    }
    slides.forEach(function (s, j) { s.classList.toggle('active', j === current); });
    dots.forEach(function (d, j) { d.classList.toggle('active', j === current); });
    paras.forEach(function (p, j) { p.classList.toggle('current', j === current); });
    if (window.syncTranscriptSlide) window.syncTranscriptSlide(current);
  }

  function scheduleAdvance(ms) {
    clearTimeout(timer);
    timer = setTimeout(function () {
      if (!playing) return;
      goTo(current + 1 > LAST_SLIDE ? 0 : current + 1);
      playSlide();
    }, ms);
  }

  function scheduleNoVoiceAdvance(i) {
    scheduleAdvance(estimateReadMs(i) + advanceDelayMs(i));
  }

  function playSlideAudio(i) {
    if (!voiceEnabled) { scheduleNoVoiceAdvance(i); return; }
    if (slideAudio) { slideAudio.pause(); slideAudio = null; }
    slideAudio = new Audio(AUDIO_BASE + 'slide-' + i + '.mp3');
    slideAudio.onended = function () { scheduleAdvance(advanceDelayMs(i)); };
    slideAudio.onerror = function () { scheduleNoVoiceAdvance(i); };
    slideAudio.play().catch(function () { scheduleNoVoiceAdvance(i); });
  }

  function playSlide() {
    goTo(current);
    if (playing && window.PBJWalkthrough && window.PBJWalkthrough.scheduleTapPulse) {
      window.PBJWalkthrough.scheduleTapPulse(current);
    }
    if (playing && voiceEnabled) playSlideAudio(current);
    else if (playing) scheduleNoVoiceAdvance(current);
  }

  function startPlayback() {
    playing = true;
    if (tapStart) tapStart.classList.add('hidden');
    playBtn.innerHTML = '&#10074;&#10074;';
    speedLabel.textContent = 'Playing';
    playSlide();
  }

  playBtn.addEventListener('click', function () {
    if (!playing) startPlayback();
    else {
      playing = false;
      playBtn.innerHTML = '&#9654;';
      speedLabel.textContent = 'Paused';
      clearTimeout(timer);
      if (slideAudio) slideAudio.pause();
      if (window.PBJWalkthrough && window.PBJWalkthrough.clearTapPulse) {
        window.PBJWalkthrough.clearTapPulse();
      }
    }
  });
  if (tapStart) tapStart.addEventListener('click', startPlayback);
  voiceBtn.addEventListener('click', function () {
    voiceEnabled = !voiceEnabled;
    voiceBtn.classList.toggle('muted', !voiceEnabled);
  });
  dots.forEach(function (d) { d.addEventListener('click', function () { goTo(+d.dataset.slide); }); });
  document.querySelectorAll('.chapter-btn').forEach(function (b) {
    b.addEventListener('click', function () {
      document.querySelectorAll('.chapter-btn').forEach(function (x) { x.classList.remove('active'); });
      b.classList.add('active');
      goTo(+b.dataset.slide);
    });
  });
  document.addEventListener('keydown', function (e) {
    if (e.key === 'ArrowRight') goTo(current + 1);
    if (e.key === 'ArrowLeft') goTo(current - 1);
  });
  goTo(0);
  if (window.initWalkthroughSlides) window.initWalkthroughSlides();
})();
