import json, sys, traceback, random, csv, functools

def get_export_path():
    if platform.system()=="Darwin":
        return raw_input("Enter path to export: ")
    else:
        return sys.argv[1]

def overallRecord(team):
    return team["won"]/(team["won"]+team["lost"])

def confRecord(team):
    return team["wonConf"]/(team["wonConf"]+team["lostConf"])

def divRecord(team):
    return team["wonDiv"]/(team["wonDiv"]+team["lostDiv"])

def headToHead(t1,t2,export,season):
    t1g = 0
    t2g = 0
    # For each game in the export
    for game in export["games"]:
        # If it didn't happen this season ignore it
        if game["season"]!=season: continue
        # If t1 won and t2 lost, then count it for t1
        if game["won"]["tid"]==t1 and game["lost"]["tid"]==t2:
            t1g+=1
        # and vice versa
        if game["lost"]["tid"]==t1 and game["won"]["tid"]==t2:
            t2g+=1
    if t1g>t2g: # if t1 has won more games
        return t1 # t1 wins the tiebreaker
    elif t2g>t1g: # if t2 has won more games
        return t2 # t2 wins the tiebreaker
    # coin flip
    return random.choice([t1,t2])

def compareTeams(useOverall=False):
    def _comp(t1,t2):
        if useOverall:
            if overallRecord(t1)>overallRecord(t2):
                return 1
            elif overallRecord(t2)>overallRecord(t1):
                return -1
        if confRecord(t1)>confRecord(t2):
            return 1
        elif confRecord(t2)>confRecord(t1):
            return -1
        if divRecord(t1)>divRecord(t2):
            return 1
        elif divRecord(t2)>divRecord(t1):
            return -1
        return 1 if headToHead(t1["tid"],t2["tid"],export,SEASON)==t1["tid"] else -1
    return _comp

def determine_tiein(confteams,tiein,export,bowlgames,already_scheduled,recurse=True):
    if tiein[0]=="None":
        if not recurse: return None # don't infinite loop
        # Create frankenlist
        allteams = []
        for conf in confteams:
            for team in confteams[conf]:
                # skip teams we've already scheduled
                if team["tid"] in already_scheduled: continue
                qualifies=True
                for bowl in bowlgames:
                    # If they would qualify for a different bowl, don't add them here
                    if determine_tiein(confteams,bowl[1:3],export,bowlgames,already_scheduled,False)==team: qualifies=False
                    if determine_tiein(confteams,bowl[3:],export,bowlgames,already_scheduled,False)==team: qualifies=False
                if qualifies: allteams.append(team)
        # Sort by overall record, then conf, div, etc.
        allteams.sort(key=functools.cmp_to_key(compareTeams(True)),reverse=True)
        # Now return the best team
        return allteams[0]
    else: # Specific conference tie-in
        assert tiein[0] in confteams, f"Unknown conference {tiein[0]}, did you misspell it?"
        index = int(tiein[1])-1
        return confteams[tiein[0]][index]

def dictcopy(d):
    ret = dict()
    ret.update(d)
    return ret

try: # errors end up in error.txt
    # Load in the export (dropped onto BOWL_schedule.py)
    with open(sys.argv[1]) as f:
        export = json.load(f)

    # Load in bowl game tie-ins
    with open("tie-ins.txt") as f:
        bowlgames = list(csv.reader(f))

    # Load in at-large playoff bids
    with open("at-large.txt") as f:
        atlarge = []
        for l in f:
            l = l.strip() # strip whitespace
            if not l: continue # skip empty lines
            # make sure the team name is spelled correctly so we can find the team
            assert l in [team["region"] for team in export["teams"]], "Unknown team "+l
            atlarge.append(l)

    # Figure out which season we're in
    SEASON = export["gameAttributes"]["season"]
    # Figure out bowl week; just the last week in the schedule (since you already
    # ran the CCG scheduler script)
    # The game calls them "days" because all of the other GM games are bolted
    # onto BBGM's framework, and basketball isn't played in weeks.
    WEEK = max([x["day"] for x in export["schedule"]])

    # Get our conferences
    # Conferences are in gameAttributes as per the manual:
    # https://football-gm.com/manual/customization/game-attributes/#confs-divs
    # But for leagues in progress, this stores a history of conferences, so we
    # need the latest one.
    CONFS = export["gameAttributes"]["confs"][-1]["value"]
    # Same with divisions.
    DIVS = export["gameAttributes"]["divs"][-1]["value"]

    # Little logging facility (useful for finding bugs)
    _log = []
    def log(*args): _log.append(" ".join(map(str,args)))

    # First, figure out who *isn't* going bowling of the top teams.
    # Winners of CCGs, plus the at-large bids, are not going bowling
    # (they're going to the playoffs)
    no_bowls = []
    # Winners of CCGs
    CCG_WEEK = WEEK - 1 # week before bowls
    for game in export["games"]:
        # if it's not this season ignore
        if game["season"]!=SEASON: continue
        # if it's not CCG week ignore
        if game["day"]!=CCG_WEEK: continue
        # Whoever won gets added to the list of no-bowls
        no_bowls.append(game["won"]["tid"])
    # At-large bids
    for team in export["teams"]:
        if not team["seasons"]: continue
        # Some monkey business to make sure we've got the team's latest name, in case any teams change location
        team = team["seasons"][-1]
        # if they're inactive, ignore
        if team["season"]!=SEASON: continue
        if team["region"] in atlarge:
            no_bowls.append(team["tid"])

    # Now figure out which conference has which teams and in which order
    CONFERENCE_TEAMS = {}
    for conference in CONFS:
        teams = []
        for team in export["teams"]:
            if not team["seasons"]: continue
            # latest values
            team = team["seasons"][-1]
            # if they're in the conference, and not one of the playoff teams, add 'em to the list
            if team["cid"]==conference["cid"] and team["tid"] not in no_bowls:
                teams.append(team)
        # Sort by confRecord, divRecord, h2h, coin flip
        teams.sort(key=functools.cmp_to_key(compareTeams(False)),reverse=True)
        CONFERENCE_TEAMS[conference["name"]]=teams

    # Now to handle tie-ins
    TEAM = 0
    already_scheduled = []
    for bowl in bowlgames:
        log("Scheduling",bowl[0])
        tiein1, tiein2 = bowl[1:3], bowl[3:]
        # Now comes the fun part
        # Find the placeholder to replace
        game = None
        for _game in export["schedule"]:
            if _game["homeTid"]==TEAM and _game["awayTid"]==TEAM:
                game=_game
                break
        assert game is not None, "Could not find placeholder game to replace"
        # Assign matchup
        team1 = determine_tiein(CONFERENCE_TEAMS,tiein1,export,bowlgames,already_scheduled)
        already_scheduled.append(team1["tid"])
        team2 = determine_tiein(CONFERENCE_TEAMS,tiein2,export,bowlgames,already_scheduled)
        already_scheduled.append(team2["tid"])
        participants = [team1,team2]
        # Sort by overall record, then conf, div, etc. (better team gets HFA)
        participants.sort(key=functools.cmp_to_key(compareTeams(True)),reverse=True)
        log(participants[1]["region"],"at",participants[0]["region"])
        game["homeTid"]=participants[0]["tid"]
        game["awayTid"]=participants[1]["tid"]

    # No need to schedule playoff placeholders, the game will do that for us

    with open("output.json","w") as f:
        json.dump(export,f)
except:
    with open("error.txt","w") as f:
        traceback.print_exc(file=f)
finally:
    with open("output.txt","w") as f:
        f.write("\n".join(_log))
