# PocketBudJet App Overview — Voiceover Script

**Voice:** Microsoft `en-US-AndrewNeural` (edge-tts) — natural male, conversational  
**Pronunciation:** say "Pocket Budget" in audio; "PocketBudJet" on screen.

Regenerate from this folder:

```bash
pip install edge-tts
cd videos/pocketbudjet/app-overview
mkdir -p audio
```

```bash
edge-tts --voice en-US-AndrewNeural --text "The moment you launch Pocket Budget, your dashboard shows your net worth, income versus expenses, and budget progress. All in real time." --write-media audio/slide-0.mp3

edge-tts --voice en-US-AndrewNeural --text "Every transaction, budget category, and savings goal in one place — on your phone, on your terms." --write-media audio/slide-1.mp3

edge-tts --voice en-US-AndrewNeural --text "Share statements from your bank app, import CSV or PDF files, scan receipts, or type manually. Optional bank sync via Teller is available with paid Premium — never required to get started." --write-media audio/slide-2.mp3

edge-tts --voice en-US-AndrewNeural --text "Premium unlocks the debt payoff engine: snowball or avalanche, your debt-free date, and how much interest you'll save." --write-media audio/slide-3.mp3

edge-tts --voice en-US-AndrewNeural --text "Premium includes the AI Financial Coach — plain-English insights from aggregated summaries, not raw transaction dumps. Opt in when you want it." --write-media audio/slide-4.mp3

edge-tts --voice en-US-AndrewNeural --text "Try Premium free for 21 days with no card, then subscribe at nine ninety-nine a month or seventy-four ninety-nine a year. Thirty-six Premium features including household WiFi sync." --write-media audio/slide-5.mp3
```
