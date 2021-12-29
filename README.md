# CFC Revamped

Some scripts I wrote for CFC Revamped, a college football league in FBGM. [Check them out!](https://discord.gg/g8KPQhCRQR)

# Running the scripts

Drag and drop the export onto the script to run the script on the export. So far I've written `CCG_placeholders.py`, but that's because that one's kind of important.

 - `CCG_placeholders.py` - Adds placeholder games to the last week of the schedule for the conference championship games to go in. Run before the end of the season.
 - `CCG_schedule.py` - Schedules said CCG games. Each conference is assumed to have 2 divisions, and the CCG is between the two division champs. It also adds the placeholders for bowl week.
 - `BOWL_schedule.py` - Schedules bowl games independently of the playoffs. Takes `tie_ins.txt`, which describes the tie-ins, and `at_large.txt`, which describes the at-large playoff teams (so we don't accidentally schedule them for a bowl game).
 - `PLAYOFFS_schedule.py` - Schedules the playoffs correctly, containing at-large bids and the conference champs.

To run a season, run `CCG_placeholders.py` on the initial season-start export. Then, once you've simulated the regular season, run `CCG_schedule.py` on a new export. After the conference championship week, run `BOWL_schedule.py` on a new export. Finally, run `PLAYOFFS_schedule.py` on the playoffs export.

If there are any errors, let me know (I'll want the `error.txt`, as that will tell me what the error was).
