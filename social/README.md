# HAI101 social assets (Instagram)

Everything here is generated from `src/data.js` by `social/build/social.py`, in the posters' style.
Rebuild after any change to dates, venues, speakers or titles:

    python social/build/social.py          # everything
    DAY=2 python social/build/social.py    # one day only

All images are 1080 px wide JPEGs: feed and carousel slides are 1080 x 1350 (4:5), stories are
1080 x 1920 (9:16) with the top and bottom 250 px kept clear of copy for Instagram's overlays.
Each folder has a `caption.txt` with ready-to-paste captions, hashtags and alt text.

## What is where

| Folder | Files | Use |
| --- | --- | --- |
| `series/carousel/` | 5 slides | Announcement carousel: cover, the question, three Fridays, line-up, attend |
| `series/story-announce.jpg` | story | Series announcement story (add a link sticker to socialscience.ai) |
| `series/story-lineup.jpg` | story | All twelve speakers |
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
