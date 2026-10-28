# HAI101 social assets (Instagram)

Everything here is generated from `src/data.js` by `social/build/social.py`, in the posters' style.
Rebuild after any change to dates, venues, speakers or titles:

    python social/build/social.py          # everything
    DAY=2 python social/build/social.py    # one day only

All images are 1080 px wide JPEGs: feed and carousel slides are 1080 x 1350 (4:5), stories are
1080 x 1920 (9:16) with the top and bottom 250 px kept clear of copy for Instagram's overlays.
Each folder has a `caption.txt` with ready-to-paste captions, hashtags and alt text.

YouTube thumbnails (1280 x 720, one per recorded talk, Industry Day included) come from `social/build/thumbs.py`
into `social/youtube/thumbs/a/` (split card, linen) and `social/youtube/thumbs/b/` (dark). Rebuild them the same
way (`VARIANT=b` for one variant). The big words are the shorter half of an "A: B" title; `HOOKS` in the script
overrides any talk.

Recording frames (the background under the slides and the camera in the talk videos) come from
`social/build/frames.py` into `social/youtube/frames/`, one PNG per talk on the dark ground: an empty box for the
slides (left), one for the camera (top right), the title and the speaker below it. They are 3840 x 2160 (4K) so
they stay sharp in a 4K edit and on YouTube's 4K ladder; the layout is designed at 1920 x 1080 and `SCALE=1`
writes that size instead. Put the frame at the bottom of the OBS scene or the edit (scaled to fit the canvas),
then the slides and the camera on top at the rects in `frames/zones.txt`, which lists them for both sizes
(at 1080p: slides 1344 x 756, camera 488 x 274). The two boxes share the width: `CAM=520` widens the camera box
and narrows the slides box.

## What is where

| Folder | Files | Use |
| --- | --- | --- |
| `series/carousel/` | 5 slides | Announcement carousel: cover, the question, three Fridays, line-up, attend |
| `series/story-announce.jpg` | story | Series announcement story (add a link sticker to socialscience.ai) |
| `series/story-lineup.jpg` | story | All the speakers |
| `day<N>/carousel/` | 7-8 slides | Cover, one slide per speaker, programme, register (QR to that day's Luma) |
| `day<N>/story-day.jpg` | story | The day's programme, headed with the date |
| `day<N>/story-tomorrow.jpg` | story | The same, headed "Tomorrow" |
| `day<N>/stories/spotlight-*.jpg` | stories | One speaker spotlight per talk |

Slides inside a carousel folder are numbered in posting order. Any speaker slide also works as a
single feed post. The series assets are date-free, so they can be reposted before each Friday.

## Suggested schedule

| When | Post |
| --- | --- |
| Now | `series/carousel` as a feed post; `series/story-announce` to stories, link sticker to socialscience.ai |
| 10-14 days before each Friday | `day<N>/carousel` as a feed post, Luma link in bio |
| The week before | One `day<N>/stories/spotlight-*` per day, link sticker to that day's Luma |
| Two days before | `series/story-lineup` or repost the day carousel to stories |
| The day before | `day<N>/story-tomorrow` |
| On the morning | `day<N>/story-day`, then photos from the room during the day |
| After each Friday | Thank-you story with a room photo, pointing to the next date |

## Notes

- "ON SCREEN" marks speakers who join by video and are shown in the room; the captions say so too.
- Keep "link in bio" pointing at socialscience.ai, and update it to the Luma page in the week before each Friday.
- Captions use the Luma links from `src/data.js`; check them if an event is recreated.
