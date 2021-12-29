import json, sys, traceback

try: # errors end up in error.txt
    # Load in the export (dropped onto CCG_placeholders.py)
    with open(sys.argv[1]) as f:
        export = json.load(f)

    # Figure out where our GIDs start
    # Since this should be run after the schedule for the season has been
    # generated, FBGM's "schedule" already has games for us
    GID = max([x["gid"] for x in export["schedule"]])+1
    # Figure out CCG week; just the last week the game generated + 1
    # The game calls them "days" because all of the other GM games are bolted
    # onto BBGM's framework, and basketball isn't played in weeks.
    WEEK = max([x["day"] for x in export["schedule"]])+1

    # Get our conferences
    # Conferences are in gameAttributes as per the manual:
    # https://football-gm.com/manual/customization/game-attributes/#confs-divs
    # But for leagues in progress, this stores a history of conferences, so we
    # need the latest one.
    CONFS = export["gameAttributes"]["confs"][-1]["value"]

    # Little logging facility (useful for finding bugs)
    _log = []
    def log(*args): _log.append(" ".join(map(str,args)))

    # Now generate the placeholders.
    # Simple 0 to n, where n is the number of conferences times 2, minus one
    TEAM = 0
    for conference in CONFS:
        log("Creating placeholder CCG for",conference["name"],"Conference")
        game = {}
        game["homeTid"] = TEAM
        game["awayTid"] = TEAM+1
        TEAM += 2
        game["day"] = WEEK
        game["gid"] = GID
        GID += 1 # GID increases by 1 without gaps
        log(game)
        export["schedule"].append(game) # put it on the schedule

    with open("output.json","w") as f:
        json.dump(export,f)
    with open("output.txt","w") as f:
        f.write("\n".join(_log))
except:
    with open("error.txt","w") as f:
        traceback.print_exc(file=f)
