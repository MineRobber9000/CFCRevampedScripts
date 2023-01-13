import json, sys, traceback, random, csv, platform

def get_export_path():
    if platform.system()=="Darwin":
        return input("Enter path to export: ")
    else:
        return sys.argv[1]

def confRecord(team):
    if (team["wonConf"]+team["lostConf"])==0: return 0
    return team["wonConf"]/(team["wonConf"]+team["lostConf"])

def divRecord(team):
    if (team["wonDiv"]+team["lostDiv"])==0: return 0
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

def dictcopy(d):
    ret = dict()
    ret.update(d)
    return ret

try: # errors end up in error.txt
    # Load in the export (dropped onto CCG_schedule.py)
    with open(get_export_path()) as f:
        export = json.load(f)

    # Load in bowl game tie-ins
    with open("tie-ins.txt") as f:
        bowlgames = list(csv.reader(f))

    # Figure out which season we're in
    SEASON = export["gameAttributes"]["season"]
    # Figure out CCG week; just the last week in the schedule (since you already
    # ran the placeholders script)
    # The game calls them "days" because all of the other GM games are bolted
    # onto BBGM's framework, and basketball isn't played in weeks.
    WEEK = max([x["day"] for x in export["schedule"]])

    # Get our conferences
    # Conferences are in gameAttributes as per the manual:
    # https://football-gm.com/manual/customization/game-attributes/#confs-divs
    # But for leagues in progress, this stores a history of conferences, so we
    # need the latest one.
    CONFS = export["gameAttributes"]["confs"] #[-1]["value"]
    # Same with divisions.
    DIVS = export["gameAttributes"]["divs"] #[-1]["value"]

    # Little logging facility (useful for finding bugs)
    _log = []
    def log(*args): _log.append(" ".join(map(str,args)))

    # Now generate the games.
    # Simple 0 to n, where n is the number of conferences times 2, minus one
    TEAM = 0
    for conference in CONFS:
        log("Scheduling proper CCG for",conference["name"],"Conference")
        # Find the placeholder we wanna update
        game = None
        for _game in export["schedule"]:
            if _game["homeTid"]==TEAM and _game["awayTid"]==TEAM:
                game = _game
                break
        assert game!=None,"Cannot find placeholder game to replace"
        # Now we need the two divisions that are in this conference
        divs = [div for div in DIVS if div["cid"]==conference["cid"]]
        # goddamnit archi3
        #assert len(divs)==2, f"Should be 2 divs per conference ({conference['name']} has {len(divs)} div(s))"
        if len(divs)==2:
            # Create a list of this season's teams
            div1teams = []
            div2teams = []
            for team in export["teams"]:
                if team["did"] not in [div["did"] for div in divs]: continue # if not in either division, ignore
                if not any([season["season"]==SEASON for season in team["seasons"]]): continue # if not active, ignore
                if team["did"]==divs[0]["did"]: # 1st division
                    div1teams.append(max(team["seasons"],key=lambda season: season["season"])) # most recent should be this season
                else: # 2nd division (if the team was in neither division we wouldn't be here)
                    div2teams.append(max(team["seasons"],key=lambda season: season["season"])) # most recent should be this season
            # Sort by conf record, then div record
            # H2H will only be resolved if it is relevant
            # reverse=True ensures the best team is divXteams[0]
            div1teams.sort(key=lambda team: (divRecord(team),confRecord(team)),reverse=True)
            div2teams.sort(key=lambda team: (divRecord(team),confRecord(team)),reverse=True)
            # Now to determine the participants
            div1team = None
            # Only teams in running are the "top" team and those tied with them
            div1topteams = [dictcopy(team) for team in div1teams if confRecord(team)==confRecord(div1teams[0]) and divRecord(team)==divRecord(div1teams[0])]
            # There can only be one
            while len(div1topteams)>1:
                # I'm not sure how one would fairly run a head-to-head tiebreaker, but random chance can't be that unfair, can it?
                # Pick 2 random teams
                team1, team2 = random.sample(div1topteams,2)
                # Run their head to head
                winnerTid = headToHead(team1["tid"],team2["tid"],export,SEASON)
                # Loser is removed from the running
                if winnerTid==team1["tid"]:
                    div1topteams.remove(team2)
                else:
                    div1topteams.remove(team1)
            div1team = div1topteams[0]
            # Now for 2nd division
            div2team = None
            # Only teams in running are the "top" team and those tied with them
            div2topteams = [dictcopy(team) for team in div2teams if confRecord(team)==confRecord(div2teams[0]) and divRecord(team)==divRecord(div2teams[0])]
            # There can only be one
            while len(div2topteams)>1:
                # I'm not sure how one would fairly run a head-to-head tiebreaker, but random chance can't be that unfair, can it?
                # Pick 2 random teams
                team1, team2 = random.sample(div2topteams,2)
                # Run their head to head
                winnerTid = headToHead(team1["tid"],team2["tid"],export,SEASON)
                # Loser is removed from the running
                if winnerTid==team1["tid"]:
                    div2topteams.remove(team2)
                else:
                    div2topteams.remove(team1)
            div2team = div2topteams[0]
            # we now have the top teams in either division
            # now figure out who hosts whom
            participants = [div1team, div2team]
            participants.sort(key=lambda team: (divRecord(team),confRecord(team)),reverse=True)
            if confRecord(participants[0])==confRecord(participants[1]):
                h2h = headToHead(participants[0]["tid"],participants[1]["tid"],export,SEASON)
                participants.sort(key=lambda team: team["tid"]==h2h,reverse=True) # winner of h2h gets home field advantage
            game["homeTid"]=participants[0]["tid"]
            game["awayTid"]=participants[1]["tid"]
            log(participants[1]["region"],"at",participants[0]["region"])
        elif len(divs)==1:
            div1teams = []
            for team in export["teams"]:
                if team["did"] not in [div["did"] for div in divs]: continue # if not in either division, ignore
                if not any([season["season"]==SEASON for season in team["seasons"]]): continue # if not active, ignore
                if team["did"]==divs[0]["did"]: # 1st division
                    div1teams.append(max(team["seasons"],key=lambda season: season["season"])) # most recent should be this season
            # Sort by conf record, then div record
            # H2H will only be resolved if it is relevant
            # reverse=True ensures the best team is divXteams[0]
            div1teams.sort(key=lambda team: (divRecord(team),confRecord(team)),reverse=True)
            # now figure out who hosts whom
            participants = div1teams[:2]
            participants.sort(key=lambda team: (divRecord(team),confRecord(team)),reverse=True)
            if confRecord(participants[0])==confRecord(participants[1]):
                h2h = headToHead(participants[0]["tid"],participants[1]["tid"],export,SEASON)
                participants.sort(key=lambda team: team["tid"]==h2h,reverse=True) # winner of h2h gets home field advantage
            game["homeTid"]=participants[0]["tid"]
            game["awayTid"]=participants[1]["tid"]
            log(participants[1]["region"],"at",participants[0]["region"])
        else:
            raise Exception(divs)

    # Now schedule bowl game placeholders
    WEEK += 1 # week after CCGs
    # Figure out where GIDs start
    GID = max([x["gid"] for x in export["schedule"]])+1
    for game in bowlgames:
        game = {}
        game["homeTid"] = TEAM
        game["awayTid"] = TEAM
        game["day"] = WEEK
        game["gid"] = GID
        GID += 1
        export["schedule"].append(game)

    with open("output.json","w") as f:
        json.dump(export,f)
    with open("output.txt","w") as f:
        f.write("\n".join(_log))
except:
    with open("error.txt","w") as f:
        traceback.print_exc(file=f)
