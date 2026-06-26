#!/usr/bin/env python3
"""Align user-guide shell with import walkthrough gold standard."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
path = ROOT / "videos" / "user-guide" / "index.html"
html = path.read_text(encoding="utf-8")

# --- CSS: video-section -> walkthrough ---
html = html.replace(".video-section", ".walkthrough")
html = html.replace("body.record-mode .walkthrough { padding: 1.5rem 2rem; min-height: 100vh; }", 
    "body.record-mode nav, body.record-mode .breadcrumbs, body.record-mode .hero,\n"
    " body.record-mode .cta-section, body.record-mode footer { display: none !important; }\n"
    " body.record-mode .walkthrough { padding: 1.5rem 2rem; min-height: 100vh; background: var(--background); }")

# Replace transcript CSS with narration-card pattern (import)
transcript_css = re.search(
    r" \.narration-panel \{[\s\S]*? \.transcript-body a \{[^\}]+\}\n",
    html,
)
if transcript_css:
    narration_css = """ .narration-panel {
 flex: 1; min-width: 280px; min-height: 0;
 max-height: 580px; overflow-y: auto; scroll-behavior: smooth;
 padding-right: 0.35rem; align-self: stretch;
 }
 .narration-panel-heading {
 font-family: 'Playfair Display', serif; font-size: 1.15rem; font-weight: 700;
 color: var(--navy); margin-bottom: 0.75rem; padding-bottom: 0.5rem;
 border-bottom: 2px solid var(--gold);
 }
 .narration-panel::-webkit-scrollbar { width: 6px; }
 .narration-panel::-webkit-scrollbar-thumb {
 background: rgba(26,79,122,0.25); border-radius: 3px;
 }
 .narration-card {
 background: var(--background); border-radius: 16px; padding: 1.2rem 1.5rem;
 margin-bottom: 0.6rem; border-left: 5px solid transparent;
 opacity: 0.5; transform: scale(0.98); transition: all 0.35s ease;
 cursor: pointer;
 }
 .narration-card.active {
 opacity: 1; transform: scale(1); background: var(--white);
 border-left-color: var(--gold);
 box-shadow: 0 4px 16px rgba(0,0,0,0.06);
 }
 .narration-step-badge {
 display: inline-block; background: var(--navy); color: white;
 font-weight: 700; font-size: 0.75rem; padding: 3px 10px; border-radius: 20px;
 margin-bottom: 0.4rem;
 }
 .narration-card h3 {
 font-family: 'Playfair Display', serif; font-size: 1.1rem; font-weight: 700;
 color: var(--navy); margin-bottom: 0.3rem;
 }
 .narration-card p { color: var(--slate); font-size: 0.9rem; line-height: 1.5; }
 .narration-timer {
 height: 3px; background: var(--gold); border-radius: 2px;
 margin-top: 0.6rem; width: 0%; transition: width linear;
 }
 .narration-card.active .narration-timer { width: 100%; }
"""
    html = html[: transcript_css.start()] + narration_css + html[transcript_css.end() :]

# Add phone-frame::before if missing
if ".phone-frame::before" not in html:
    html = html.replace(
        " aspect-ratio: 9 / 19.5; max-height: 580px;\n }\n .slideshow",
        " aspect-ratio: 9 / 19.5; max-height: 580px;\n }\n .phone-frame::before { display: none; }\n .slideshow",
    )

# --- HTML shell ---
html = html.replace('<div class="walkthrough">', '<section class="walkthrough">', 1)

html = html.replace(
    '<div class="narration-panel" id="narrationPanel">\n <div class="transcript-body" id="transcriptBody"></div>\n </div>',
    '<div class="narration-panel" id="narrationPanel">\n <p class="narration-panel-heading">Transcript — read along as you watch</p>\n </div>',
)

# Fix DOM: remove premature phone-column close before progress-dots
html = html.replace(
    "</div>\n </div>\n </div>\n </div>\n <div class=\"progress-dots\"",
    "</div>\n </div>\n </div>\n <div class=\"progress-dots\"",
    1,
)

# Close walkthrough section properly (replace trailing video-section close)
html = re.sub(
    r"(</div>\n </div>\n </div>\n)\n\n <div class=\"cta-section\">",
    r"\1 </section>\n\n <div class=\"cta-section\">",
    html,
    count=1,
)

# --- JS: import-style narration cards ---
script_match = re.search(r"<script>\n \(function\(\) \{", html)
if not script_match:
    raise SystemExit("script start not found")
script_end = html.find("</script>", script_match.start())

narration_match = re.search(
    r"const NARRATION = \[([\s\S]*?)\];\s*\n NARRATION\.forEach",
    html[script_match.start() : script_end],
)
if not narration_match:
    raise SystemExit("NARRATION block not found")
narration_block = "const NARRATION = [" + narration_match.group(1) + "];"

new_script = f"""<script>
 var goTo;
 (function() {{
 var recordParams = new URLSearchParams(location.search);
 var recordMode = recordParams.get('record') === '1';
 var previewMode = recordParams.get('preview') === '1';
 var fastMode = recordParams.get('fast') === '1';
 if (recordMode) document.body.classList.add('record-mode');
 const SLIDE_DURATION = fastMode ? 2000 : 8000;
 const LAST_SLIDE = previewMode ? 26 : 88;
 const CHAPTER_STARTS = [0, 10, 15, 16, 26, 27, 30, 34, 38, 41, 47, 54, 58, 60, 62, 65, 66, 68, 71, 74, 77, 79, 81, 82, 83, 84, 86, 88];
 const slides = document.querySelectorAll('.slide');
 const dotsContainer = document.getElementById('dots');
 const playPauseBtn = document.getElementById('playPauseBtn');
 const speedLabel = document.getElementById('speedLabel');
 const tapToStart = document.getElementById('tapToStart');
 const chapterBtns = document.querySelectorAll('.chapter-btn');
 const narrationPanel = document.getElementById('narrationPanel');
 let cards = [];
 let current = 0, playing = true, timer = null;
 let audioUnlocked = false;
 let audioElement = null, voiceEnabled = true, advanceTimeout = null;

 {narration_block.strip()}

 const audioPaths = [];
 NARRATION.forEach(function(_, i) {{ audioPaths.push('audio/slide-' + i + '.mp3'); }});

 function titleForSlide(index, text) {{
 var slide = slides[index];
 if (slide) {{
 var img = slide.querySelector('img[alt]');
 if (img && img.getAttribute('alt')) return img.getAttribute('alt');
 }}
 var first = text.split(/[.!?]/)[0].trim();
 if (first.length > 72) first = first.slice(0, 69) + '...';
 return first || ('Slide ' + (index + 1));
 }}

 function buildNarrationCards() {{
 NARRATION.forEach(function(text, index) {{
 var card = document.createElement('div');
 card.className = 'narration-card' + (index === 0 ? ' active' : '');
 card.setAttribute('data-index', String(index));
 card.onclick = function() {{ goTo(index); }};

 var badge = document.createElement('span');
 badge.className = 'narration-step-badge';
 badge.textContent = index === LAST_SLIDE ? 'Done' : ('Slide ' + (index + 1));

 var h3 = document.createElement('h3');
 h3.textContent = titleForSlide(index, text);

 var p = document.createElement('p');
 p.textContent = text;

 var timerBar = document.createElement('div');
 timerBar.className = 'narration-timer';

 card.appendChild(badge);
 card.appendChild(h3);
 card.appendChild(p);
 card.appendChild(timerBar);
 narrationPanel.appendChild(card);
 }});
 cards = document.querySelectorAll('.narration-card');
 }}

 buildNarrationCards();

 const voiceBtn = document.createElement('button');
 voiceBtn.className = 'voice-btn';
 voiceBtn.innerHTML = '&#128264;';
 voiceBtn.title = 'Toggle voice narration';
 voiceBtn.setAttribute('aria-label', 'Toggle voice narration');
 document.querySelector('.playback-controls').appendChild(voiceBtn);

 voiceBtn.addEventListener('click', function() {{
 voiceEnabled = !voiceEnabled;
 voiceBtn.innerHTML = voiceEnabled ? '&#128264;' : '&#128263;';
 voiceBtn.classList.toggle('muted', !voiceEnabled);
 if (!voiceEnabled) {{
 stopAudio();
 if (playing) resetTimer();
 }} else {{
 clearInterval(timer);
 playSlideAudio(current);
 }}
 }});

 function stopAudio() {{
 if (audioElement) {{
 audioElement.onended = null;
 audioElement.onerror = null;
 audioElement.pause();
 audioElement.currentTime = 0;
 audioElement.removeAttribute('src');
 audioElement.load();
 audioElement = null;
 }}
 clearTimeout(advanceTimeout);
 advanceTimeout = null;
 }}

 function stopAllAudio() {{
 playing = false;
 clearInterval(timer);
 timer = null;
 stopAudio();
 document.querySelectorAll('audio').forEach(function(a) {{
 a.onended = null;
 a.onerror = null;
 a.loop = false;
 a.pause();
 a.currentTime = 0;
 a.removeAttribute('src');
 a.load();
 }});
 if (window.speechSynthesis) {{ try {{ window.speechSynthesis.cancel(); }} catch (e) {{}} }}
 }}

 function playSlideAudio(index) {{
 stopAudio();
 if (!voiceEnabled || !playing) return;
 var src = audioPaths[index];
 if (!src) return;
 audioElement = new Audio(src);
 audioElement.loop = false;
 audioElement.volume = 1.0;
 audioElement.onended = function() {{
 if (!playing || !voiceEnabled) return;
 advanceTimeout = setTimeout(function() {{
 if (!playing || !voiceEnabled) return;
 if (current < LAST_SLIDE) next();
 else {{ playing = false; playPauseBtn.innerHTML = '&#9654;'; speedLabel.textContent = 'Finished'; }}
 }}, 1200);
 }};
 audioElement.onerror = function() {{
 if (!playing) return;
 advanceTimeout = setTimeout(function() {{
 if (!playing) return;
 if (current < LAST_SLIDE) next();
 }}, SLIDE_DURATION);
 }};
 var _p = audioElement.play();
 if (_p !== undefined) {{
 _p.then(function() {{
 if (!audioUnlocked) {{
 audioUnlocked = true;
 tapToStart.classList.add('hidden');
 playPauseBtn.innerHTML = '&#10074;&#10074;';
 speedLabel.textContent = 'Auto-playing';
 }}
 }}).catch(function() {{
 if (!audioUnlocked) {{
 playing = false;
 playPauseBtn.innerHTML = '&#9654;';
 speedLabel.textContent = 'Tap to play';
 }} else if (playing) {{
 advanceTimeout = setTimeout(function() {{
 if (!playing) return;
 if (current < LAST_SLIDE) next();
 }}, SLIDE_DURATION);
 }}
 }});
 }}
 }}

 function updateChapterActive(slideIdx) {{
 chapterBtns.forEach(function(btn) {{ btn.classList.remove('active'); }});
 var active = chapterBtns[0];
 for (var i = CHAPTER_STARTS.length - 1; i >= 0; i--) {{
 if (slideIdx >= CHAPTER_STARTS[i]) {{ active = chapterBtns[i]; break; }}
 }}
 active.classList.add('active');
 }}

 slides.forEach(function(_, i) {{
 var dot = document.createElement('div');
 dot.className = 'dot' + (i === 0 ? ' active' : '');
 dot.addEventListener('click', function() {{ goTo(i); }});
 dotsContainer.appendChild(dot);
 }});

 goTo = function(index) {{
 slides[current].classList.remove('active');
 cards[current].classList.remove('active');
 dotsContainer.children[current].classList.remove('active');
 cards[current].querySelector('.narration-timer').style.transition = 'none';
 cards[current].querySelector('.narration-timer').style.width = '0%';

 current = index;
 slides[current].classList.add('active');
 cards[current].classList.add('active');
 dotsContainer.children[current].classList.add('active');
 updateChapterActive(current);

 var timerBar = cards[current].querySelector('.narration-timer');
 requestAnimationFrame(function() {{
 timerBar.style.transition = 'width ' + (SLIDE_DURATION / 1000) + 's linear';
 timerBar.style.width = '100%';
 }});
 if (narrationPanel && cards[current]) {{
 cards[current].scrollIntoView({{ behavior: 'smooth', block: 'center' }});
 }}
 if (playing && current === LAST_SLIDE) speedLabel.textContent = 'Last step';
 else if (playing) speedLabel.textContent = 'Auto-playing';
 if (voiceEnabled) {{ clearInterval(timer); playSlideAudio(current); }}
 else if (playing) {{ resetTimer(); }}
 }};

 function next() {{
 if (current < LAST_SLIDE) goTo(current + 1);
 else {{ playing = false; playPauseBtn.innerHTML = '&#9654;'; speedLabel.textContent = 'Finished'; stopAudio(); clearInterval(timer); }}
 }}

 function resetTimer() {{
 clearInterval(timer); clearTimeout(advanceTimeout);
 timer = setInterval(function() {{
 if (current < LAST_SLIDE) next();
 else {{ clearInterval(timer); playing = false; playPauseBtn.innerHTML = '&#9654;'; speedLabel.textContent = 'Finished'; }}
 }}, SLIDE_DURATION);
 }}

 chapterBtns.forEach(function(btn) {{
 btn.addEventListener('click', function() {{
 var idx = parseInt(btn.getAttribute('data-slide'), 10);
 if (!isNaN(idx)) goTo(idx);
 }});
 }});

 playPauseBtn.addEventListener('click', function() {{
 if (!audioUnlocked) {{ startPlayback(); return; }}
 playing = !playing;
 if (playing) {{
 playPauseBtn.innerHTML = '&#10074;&#10074;';
 speedLabel.textContent = 'Auto-playing';
 if (voiceEnabled) playSlideAudio(current); else resetTimer();
 var tb = cards[current].querySelector('.narration-timer');
 tb.style.transition = 'none'; tb.style.width = '0%';
 requestAnimationFrame(function() {{
 tb.style.transition = 'width ' + (SLIDE_DURATION / 1000) + 's linear';
 tb.style.width = '100%';
 }});
 }} else {{
 playPauseBtn.innerHTML = '&#9654;';
 speedLabel.textContent = 'Paused';
 stopAudio(); clearInterval(timer); clearTimeout(advanceTimeout);
 var tb = cards[current].querySelector('.narration-timer');
 var w = getComputedStyle(tb).width;
 tb.style.transition = 'none'; tb.style.width = w;
 }}
 }});

 function startPlayback() {{
 if (audioUnlocked) return;
 audioUnlocked = true;
 tapToStart.classList.add('hidden');
 playing = true;
 playPauseBtn.innerHTML = '&#10074;&#10074;';
 speedLabel.textContent = 'Auto-playing';
 playSlideAudio(current);
 }}
 tapToStart.addEventListener('click', startPlayback);

 if (!navigator.maxTouchPoints) {{
 audioUnlocked = true;
 if (tapToStart) tapToStart.classList.add('hidden');
 }}

 if (window.PBJWalkthrough && window.PBJWalkthrough.registerTeardown) {{
 window.PBJWalkthrough.registerTeardown(stopAllAudio);
 }} else {{
 window.__pbjTeardownQueue = window.__pbjTeardownQueue || [];
 window.__pbjTeardownQueue.push(stopAllAudio);
 }}

 function jumpFromHash() {{
 var hash = location.hash || '';
 var m = hash.match(/^#chapter=(\\d+)$/);
 if (m) {{
 var slide = parseInt(m[1], 10);
 if (!isNaN(slide) && slide >= 0 && slide <= LAST_SLIDE) {{
 if (!audioUnlocked) startPlayback();
 goTo(slide);
 }}
 }}
 }}
 window.addEventListener('hashchange', jumpFromHash);

 goTo(0);
 jumpFromHash();
 if (recordMode && !audioUnlocked) startPlayback();
 else if (recordMode && playing) {{
 playPauseBtn.innerHTML = '&#10074;&#10074;';
 speedLabel.textContent = 'Auto-playing';
 if (voiceEnabled) playSlideAudio(current); else resetTimer();
 }}
 }})();
</script>"""

html = html[: script_match.start()] + new_script + html[script_end + len("</script>") :]

path.write_text(html, encoding="utf-8", newline="\n")
print("Refactored", path)
