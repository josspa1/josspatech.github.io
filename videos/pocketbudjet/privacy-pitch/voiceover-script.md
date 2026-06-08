# PocketBudJet Privacy Pitch — Voiceover Script

**Voice:** Microsoft `en-US-AndrewNeural` (edge-tts)  
**Pronunciation:** say "Pocket Budget" in audio.

```bash
pip install edge-tts
cd videos/pocketbudjet/privacy-pitch
mkdir -p audio
```

```bash
edge-tts --voice en-US-AndrewNeural --text "Your budgeting app should put you in control. With Pocket Budget, connecting a bank is your choice — never a requirement." --write-media audio/slide-0.mp3

edge-tts --voice en-US-AndrewNeural --text "Many budget apps force a bank login before you can even start. Pocket Budget never forces it — import yourself free, or connect a bank with paid Premium via Teller when you want automation." --write-media audio/slide-1.mp3

edge-tts --voice en-US-AndrewNeural --text "Share from your bank app, import CSV or PDF, scan receipts, use a WiFi scanner, or type manually. Bank sync is optional and requires paid Premium — not the 21-day trial." --write-media audio/slide-2.mp3

edge-tts --voice en-US-AndrewNeural --text "Your data lives in the app's private storage on your device. Backups and cloud sync are optional — you pick the provider, and the payload is AES-256 encrypted with a key only you know. No ads. No data selling. Ever." --write-media audio/slide-3.mp3

edge-tts --voice en-US-AndrewNeural --text "Export in six formats with Premium. Free with no expiration for core budgeting, 21-day Premium trial with no card, or subscribe at nine ninety-nine a month or seventy-four ninety-nine a year. Your data stays yours." --write-media audio/slide-4.mp3
```
