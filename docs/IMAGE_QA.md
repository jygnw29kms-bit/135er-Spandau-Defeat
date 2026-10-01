# Public image QA gate

Status: **binding for public repository media**.

No screenshot, gallery, render, reference image or preview is committed to the public README before a manual full-resolution inspection.

## Reject immediately

Reject an image if any of the following is visible:
- blur, mushy detail or failed upscale
- broken contact-sheet crops or mosaic artifacts
- corrupted blocks, banding or obvious generation failure
- stretched or wrong aspect ratio
- unreadable labels or UI
- misleading engine attribution
- placeholder or fake gameplay presented as in-engine
- image quality clearly below the surrounding repository presentation

## Gameplay capture rule

A gameplay image must be captured from the actual running target engine:
- UE5/Lyra image -> UE5/Lyra runtime
- Source 2 image -> Source 2/CS2 runtime

Reference or concept imagery must not be used as a substitute for gameplay screenshots.

## Publication workflow

1. Generate or capture locally.
2. Open the original at 100% zoom.
3. Check sharpness, artifacts, framing and aspect ratio.
4. Verify engine/source attribution.
5. Verify the README rendering path.
6. Only then stage and commit.

If there is any doubt, the image stays unpublished.
