# Cloud Backup Setup — Voiceover Script

**Voice:** Microsoft en-US-AndrewNeural (edge-tts), professional/authoritative tone
**Pronunciation rule:** TTS always says "Pocket Budget" — never "PocketBudJet" or "PBJ"
**Output folder:** `audio/slide-0.mp3` through `audio/slide-5.mp3`

---

## Slide 0 — Why Cloud Backup Matters
Your phone can break, get lost, or be replaced. Cloud Backup keeps your Pocket Budget data — and any receipts you chose to keep — safe in a cloud account you already own. Pocket Budget never stores your data on its own servers. It's your cloud, your account, your control.

## Slide 1 — Open Settings
Open Pocket Budget, tap Settings at the bottom, then tap Storage and Backup. That's the one place where everything about your device storage, local backups, and cloud backups lives.

## Slide 2 — Tap the Cloud Tab
At the top of Storage and Backup you'll see four tabs: Storage, Data, Backup, and Cloud. Tap Cloud. This is where you connect the cloud you want Pocket Budget to use.

## Slide 3 — Pick Your Cloud Provider
Pick the one you already use: Google Drive, OneDrive, Dropbox, or iCloud on iPhone. Any of them work the same — Pocket Budget just needs one place to put your backup. If you use more than one cloud, you can connect several and Pocket Budget will back up to all of them.

## Slide 4 — Sign In
Tap the provider and Pocket Budget takes you to the official sign-in screen for that service. Pocket Budget only asks for permission to write to its own backup folder — it cannot read any of your other files.

## Slide 5 — You're Done
Once you're connected, Pocket Budget backs up automatically — weekly by default, or whenever you add new transactions. Any receipts you chose to keep are safely tucked into the same backup folder. If something happens to your phone, you install Pocket Budget on a new device, sign back into the same cloud, and your data — including every kept receipt — comes right back.

---

## Generation command (run on your machine)

```bash
cd "C:\Users\jossp\Documents\GitHub\josspatech.github.io\videos\pocketbudjet\cloud-backup-setup"
mkdir audio 2>nul

# Slide 0
edge-tts --voice en-US-AndrewNeural --text "Your phone can break, get lost, or be replaced. Cloud Backup keeps your Pocket Budget data -- and any receipts you chose to keep -- safe in a cloud account you already own. Pocket Budget never stores your data on its own servers. It's your cloud, your account, your control." --write-media audio/slide-0.mp3

# Slide 1
edge-tts --voice en-US-AndrewNeural --text "Open Pocket Budget, tap Settings at the bottom, then tap Storage and Backup. That's the one place where everything about your device storage, local backups, and cloud backups lives." --write-media audio/slide-1.mp3

# Slide 2
edge-tts --voice en-US-AndrewNeural --text "At the top of Storage and Backup you'll see four tabs: Storage, Data, Backup, and Cloud. Tap Cloud. This is where you connect the cloud you want Pocket Budget to use." --write-media audio/slide-2.mp3

# Slide 3
edge-tts --voice en-US-AndrewNeural --text "Pick the one you already use: Google Drive, OneDrive, Dropbox, or iCloud on iPhone. Any of them work the same -- Pocket Budget just needs one place to put your backup. If you use more than one cloud, you can connect several and Pocket Budget will back up to all of them." --write-media audio/slide-3.mp3

# Slide 4
edge-tts --voice en-US-AndrewNeural --text "Tap the provider and Pocket Budget takes you to the official sign-in screen for that service. Pocket Budget only asks for permission to write to its own backup folder -- it cannot read any of your other files." --write-media audio/slide-4.mp3

# Slide 5
edge-tts --voice en-US-AndrewNeural --text "Once you're connected, Pocket Budget backs up automatically -- weekly by default, or whenever you add new transactions. Any receipts you chose to keep are safely tucked into the same backup folder. If something happens to your phone, you install Pocket Budget on a new device, sign back into the same cloud, and your data -- including every kept receipt -- comes right back." --write-media audio/slide-5.mp3
```

The page will work without the MP3s — narration cards still show the text and slides auto-advance every 8 seconds when audio is missing. Add the MP3s when you can.
