# HHH User Manual Coverage

**Live URL:** https://josspatech.com/videos/user-guide-hhh/  
**PDF:** https://josspatech.com/docs/handyhorology/HandyHorology_UserGuide.pdf  
**MP4:** https://josspatech.com/videos/user-guide-hhh/handy-horology-helper-user-guide.mp4  
**Slide count:** 18  
**Chapter pills:** 13  

## Summary

| PNG OK | 4 |
| PNG interim (reuse) | 6 |
| PNG missing (placeholder) | 8 |

## Locales

English only for v1. HHH app supports 7 display languages in Settings; locale folders deferred (PBJ has 8).

## Regenerate

```powershell
cd josspatech.github.io
python scripts/capture-hhh-manual-screenshots.py
python scripts/build-hhh-user-manual-slides.py
python scripts/gen-user-guide-hhh-en-audio.py --force
node scripts/render-user-guide-hhh-video.js
python scripts/build-hhh-user-guide-pdf.py
```

