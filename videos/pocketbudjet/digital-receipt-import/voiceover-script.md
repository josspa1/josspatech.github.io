# Digital Receipt Import — Voiceover Script

**Voice:** Microsoft en-US-AndrewNeural (edge-tts), professional/authoritative tone
**Pronunciation rule:** TTS always says "Pocket Budget" — never "PocketBudJet" or "PBJ"
**Output folder:** `audio/slide-0.mp3` through `audio/slide-6.mp3`

---

## Slide 0 — The Download-Arrow Workflow
A lot of stores email you a PDF receipt instead of a paper one. Pocket Budget can pull those into your budget without scanning your whole inbox. You just download the PDF to your phone the normal way, and Pocket Budget handles the rest.

## Slide 1 — Open the Receipt Email
Open the email from the store. Scroll down to the attachment. Here we're showing Gmail — you'll see the file name, the size, and a download arrow right next to the PDF. Other email apps like Outlook, Apple Mail, Yahoo, or Proton look a little different, but every one of them has a way to save the attachment to your phone.

## Slide 2 — Tap the Download Arrow
Tap the download arrow. In Gmail it sits right on the attachment. In other email apps, you may need to tap the attachment first to reveal the save or download icon — sometimes it's behind a share button. The icon changes, but every email app lets you save a file to your phone. You're just saving it. Not opening it, not sharing it.

## Slide 3 — The PDF Saves Locally
Your phone puts the file in your Downloads folder. Nothing leaves your device. No cloud upload, no sharing with anyone. The PDF just sits on your phone waiting for Pocket Budget to grab it.

## Slide 4 — Open Pocket Budget
Open Pocket Budget. Tap the gold plus button at the bottom center of the Transactions screen, then tap Import receipts. Only a few taps to get there — and from then on, one tap is all you need.

## Slide 5 — Automatic Discovery
Pocket Budget checks your Downloads folder for receipts you haven't imported yet. PDFs, photos of paper receipts, even plain-text receipt emails you saved — if it's in there and it's new, Pocket Budget will find it. Files you've already imported or told Pocket Budget to skip won't show up again.

## Slide 6 — Confirm, Then Choose: Keep a Copy?
Pocket Budget reads the PDF and shows you a draft with the merchant, date, and total. Tweak anything you want, tap confirm, and it's in your budget. Then Pocket Budget asks: do you want to keep a copy of the receipt? Say yes and the full PDF goes to your own Cloud Backup — iCloud, Google Drive, or Dropbox. A small thumbnail always stays on your phone so you can see what the receipt looks like at a glance. If Cloud Backup isn't set up yet, Pocket Budget walks you through it — because without it, kept receipts could be lost if something happens to your phone.

---

## Generation command (run on your machine)

```bash
cd "C:\Users\jossp\Documents\GitHub\josspatech.github.io\videos\pocketbudjet\digital-receipt-import"
mkdir audio 2>nul

# Slide 0
edge-tts --voice en-US-AndrewNeural --text "A lot of stores email you a PDF receipt instead of a paper one. Pocket Budget can pull those into your budget without scanning your whole inbox. You just download the PDF to your phone the normal way, and Pocket Budget handles the rest." --write-media audio/slide-0.mp3

# Slide 1
edge-tts --voice en-US-AndrewNeural --text "Open the email from the store. Scroll down to the attachment. Here we're showing Gmail -- you'll see the file name, the size, and a download arrow right next to the PDF. Other email apps like Outlook, Apple Mail, Yahoo, or Proton look a little different, but every one of them has a way to save the attachment to your phone." --write-media audio/slide-1.mp3

# Slide 2
edge-tts --voice en-US-AndrewNeural --text "Tap the download arrow. In Gmail it sits right on the attachment. In other email apps, you may need to tap the attachment first to reveal the save or download icon -- sometimes it's behind a share button. The icon changes, but every email app lets you save a file to your phone. You're just saving it. Not opening it, not sharing it." --write-media audio/slide-2.mp3

# Slide 3
edge-tts --voice en-US-AndrewNeural --text "Your phone puts the file in your Downloads folder. Nothing leaves your device. No cloud upload, no sharing with anyone. The PDF just sits on your phone waiting for Pocket Budget to grab it." --write-media audio/slide-3.mp3

# Slide 4
edge-tts --voice en-US-AndrewNeural --text "Open Pocket Budget. Tap the gold plus button at the bottom center of the Transactions screen, then tap Import receipts. Only a few taps to get there -- and from then on, one tap is all you need." --write-media audio/slide-4.mp3

# Slide 5
edge-tts --voice en-US-AndrewNeural --text "Pocket Budget checks your Downloads folder for receipts you haven't imported yet. PDFs, photos of paper receipts, even plain-text receipt emails you saved -- if it's in there and it's new, Pocket Budget will find it. Files you've already imported or told Pocket Budget to skip won't show up again." --write-media audio/slide-5.mp3

# Slide 6
edge-tts --voice en-US-AndrewNeural --text "Pocket Budget reads the PDF and shows you a draft with the merchant, date, and total. Tweak anything you want, tap confirm, and it's in your budget. Then Pocket Budget asks: do you want to keep a copy of the receipt? Say yes and the full PDF goes to your own Cloud Backup -- iCloud, Google Drive, or Dropbox. A small thumbnail always stays on your phone so you can see what the receipt looks like at a glance. If Cloud Backup isn't set up yet, Pocket Budget walks you through it -- because without it, kept receipts could be lost if something happens to your phone." --write-media audio/slide-6.mp3
```

The page will work without the MP3s — narration cards still show the text and slides auto-advance every 8 seconds when audio is missing. Add the MP3s when you can.
