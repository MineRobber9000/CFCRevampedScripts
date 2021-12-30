import json, sys, traceback, random, csv, functools, platform

def get_export_path():
    if platform.system()=="Darwin":
        return input("Enter path to export: ")
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

def dictcopy(d):
    ret = dict()
    ret.update(d)
    return ret

try: # errors end up in error.txt
    # Load in the export (dropped onto BOWL_schedule.py)
    with open(get_export_path()) as f:
        export = json.load(f)

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
    # Figure out first playoffs week; just the last week in the schedule (since
    # you're running this on the playoffs export)
    # The game calls them "days" because all of the other GM games are bolted
    # onto BBGM's framework, and basketball isn't played in weeks.
    WEEK = max([x["day"] for x in export["schedule"]])

    # Little logging facility (useful for finding bugs)
    _log = []
    def log(*args): _log.append(" ".join(map(str,args)))

    # Start by figuring out our conference champs
    CCG_WEEK = WEEK - 2 # playoffs start 2 weeks after the CCG week
    conference_champs = []
    for game in export["games"]:
        if game["season"]!=SEASON: continue
        if game["day"]!=CCG_WEEK: continue
        winnerTid = game["won"]["tid"]
        for team in export["teams"]:
            if not team["seasons"]: continue
            team = team["seasons"][-1]
            if team["tid"]==winnerTid:
                conference_champs.append(team)
                break

    # Conference champions sorted by overall record
    conference_champs.sort(key=functools.cmp_to_key(compareTeams(True)),reverse=True)

    atlarge_bids = []
    for region in atlarge:
        for team in export["teams"]:
            if not team["seasons"]: continue
            team = team["seasons"][-1]
            if team["region"]==region:
                atlarge_bids.append(team)
                break

    # Atlarge bids also sorted by overall record
    atlarge_bids.sort(key=functools.cmp_to_key(compareTeams(True)),reverse=True)

    # Conference champs are top 5 seeds, followed by the atlarges
    teams = conference_champs + atlarge_bids

    # Now to assemble the playoff series
    playoffSeries = None
    for series in export["playoffSeries"]:
        if series["season"] == SEASON:
            playoffSeries = series
            break
    assert playoffSeries is not None, "Could not find playoff series; are you sure you simmed to playoffs?"

    for series in playoffSeries["series"][0]:
        hometeam = teams[series["home"]["seed"]-1]
        awayteam = teams[series["away"]["seed"]-1]
        game = None
        for _game in export["schedule"]:
            if _game["homeTid"]==series["home"]["tid"] and _game["awayTid"]==series["away"]["tid"]:
                game=_game
                break
        series["home"]["tid"]=hometeam["tid"]
        series["home"]["cid"]=hometeam["cid"]
        game["homeTid"]=hometeam["tid"]
        series["away"]["tid"]=awayteam["tid"]
        series["away"]["cid"]=awayteam["cid"]
        game["awayTid"]=awayteam["tid"]

    with open("output.json","w") as f:
        json.dump(export,f)
except:
    with open("error.txt","w") as f:
        traceback.print_exc(file=f)
finally:
    with open("output.txt","w") as f:
        f.write("\n".join(_log))
