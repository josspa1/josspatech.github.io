(function () {
  var current = 0;
  var playing = false;
  var voiceEnabled = true;
  var slideAudio = null;
  var timer = null;
  var SLIDE_MS = 8000;
  var slides = document.querySelectorAll('.slide');
  var dots = document.querySelectorAll('.dot');
  var paras = document.querySelectorAll('.transcript-para');
  var playBtn = document.getElementById('playPauseBtn');
  var voiceBtn = document.getElementById('voiceBtn');
  var speedLabel = document.getElementById('speedLabel');
  var tapStart = document.getElementById('tapToStart');
  var recordMode = /[?&]record=1/.test(location.search);
  if (recordMode) document.body.classList.add('record-mode');

  function goTo(i) {
    current = Math.max(0, Math.min(i, LAST_SLIDE));
    slides.forEach(function (s, j) { s.classList.toggle('active', j === current); });
    dots.forEach(function (d, j) { d.classList.toggle('active', j === current); });
    paras.forEach(function (p, j) { p.classList.toggle('current', j === current); });
    if (window.syncTranscriptSlide) window.syncTranscriptSlide(current);
  }

  function resetTimer() {
    clearTimeout(timer);
    timer = setTimeout(function () {
      if (playing) goTo(current + 1 > LAST_SLIDE ? 0 : current + 1);
      if (playing) playSlide();
    }, SLIDE_MS);
  }

  function playSlideAudio(i) {
    if (!voiceEnabled) { resetTimer(); return; }
    if (slideAudio) { slideAudio.pause(); slideAudio = null; }
    slideAudio = new Audio(AUDIO_BASE + 'slide-' + i + '.mp3');
    slideAudio.onended = resetTimer;
    slideAudio.onerror = resetTimer;
    slideAudio.play().catch(resetTimer);
  }

  function playSlide() {
    goTo(current);
    if (playing && voiceEnabled) playSlideAudio(current); else resetTimer();
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
    else { playing = false; playBtn.innerHTML = '&#9654;'; speedLabel.textContent = 'Paused'; clearTimeout(timer); if (slideAudio) slideAudio.pause(); }
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
