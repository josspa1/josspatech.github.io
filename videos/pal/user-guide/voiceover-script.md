# PAL Reviewer Walkthrough — voiceover script

**Voice:** Microsoft `en-US-AndrewNeural` (edge-tts)  
**Output:** `audio/slide-0.mp3` through `audio/slide-13.mp3`

```bash
pip install edge-tts
cd videos/pal/walkthrough
```

Generate all slides (run from `walkthrough/`):

```bash
edge-tts --voice en-US-AndrewNeural --text "Welcome to Pocket Allowance Ledger — PAL for short. If you received this build on iPhone, you installed through TestFlight. On Android, open Google Play Internal testing and install from there. This walkthrough uses the pre-seeded Reyes demo household so you can evaluate PAL in twenty to forty minutes without setup." --write-media audio/slide-0.mp3

edge-tts --voice en-US-AndrewNeural --text "The demo household is already loaded. Family name Reyes. Kids Maya, about eight, and Jacob, about six. Family password for kid web is reyes — lowercase. Kid PIN for both children is one-two-three-four. Open Settings and scroll to Reviewer guide for the full credential card." --write-media audio/slide-1.mp3

edge-tts --voice en-US-AndrewNeural --text "Open PAL on the parent phone. The Home tab shows today's contracts as large Done buttons — one tap records the behavior and awards a gold token. This is the core parent flow on busy evenings." --write-media audio/slide-2.mp3

edge-tts --voice en-US-AndrewNeural --text "Tap Done on a contract — for example Maya's morning routine. Watch the coin animation land. Tokens update immediately so kids see feedback in the companion once you confirm their reports." --write-media audio/slide-3.mp3

edge-tts --voice en-US-AndrewNeural --text "Open the Balances tab. Each child shows in-hand tokens versus banked savings. Maya has saving-growth maintenance operations enabled in the demo so you can see cadence coaching. Jacob's row stays simpler — no sibling leaderboards or shame metrics." --write-media audio/slide-4.mp3

edge-tts --voice en-US-AndrewNeural --text "Kid web runs on your home Wi-Fi only — not the public internet. Open Settings, then Kid web. PAL shows a LAN address and QR code when the local server is active. Phone and kid browser must share the same network." --write-media audio/slide-5.mp3

edge-tts --voice en-US-AndrewNeural --text "Keep PAL open in the foreground while kids use the link — the local server pauses if the app is backgrounded. On iPhone, tap Allow when iOS asks for Local Network access. Copy the URL or scan the QR on a Chromebook or tablet browser." --write-media audio/slide-6.mp3

edge-tts --voice en-US-AndrewNeural --text "Kids sign in once per browser session. Enter family password reyes, tap Maya, enter PIN one-two-three-four. The companion shows assignments in warm, kid-facing language — tokens and rewards, not banking UI." --write-media audio/slide-7.mp3

edge-tts --voice en-US-AndrewNeural --text "From kid web, Maya taps I did it on a finished job. Coins wait for your approval in the parent app — delayed verification is intentional. Kids get immediate visual feedback; you stay in control of what counts." --write-media audio/slide-8.mp3

edge-tts --voice en-US-AndrewNeural --text "Switch back to the parent app. Open Approvals to confirm or decline the kid report. Optionally let Maya request a reward from kid web, then approve or decline here. Nothing auto-redeems without you." --write-media audio/slide-9.mp3

edge-tts --voice en-US-AndrewNeural --text "Open Reports for charts, first-week versus now comparisons, and coaching cards. Thinning and saving-growth suggestions appear as nudges — parents must confirm. PAL never auto-applies schedule changes." --write-media audio/slide-10.mp3

edge-tts --voice en-US-AndrewNeural --text "Open Contracts to review seeded behavioral contracts. Tap into detail for thinning schedules, extinction-burst coaching on young contracts, and token amounts. Optionally start New contract from a template or from scratch." --write-media audio/slide-11.mp3

edge-tts --voice en-US-AndrewNeural --text "Evaluate fidelity of token-economy language versus chore-tracker UX. Notice extinction-burst callouts on Home for young contracts. Confirm schedule thinning and saving cadence stay literature-first with parent confirm gates." --write-media audio/slide-12.mp3

edge-tts --voice en-US-AndrewNeural --text "PAL is not kid banking, not a chatbot coach, and not cloud sync in this build. Ages under six, debit cards, and PocketBudJet bridges are explicitly out of scope. Questions or fidelity notes: support at josspatech dot com. Thank you for reviewing Pocket Allowance Ledger." --write-media audio/slide-13.mp3
```
