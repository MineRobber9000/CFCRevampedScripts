try: # errors end up in error.txt
    import colley, json, sys, platform, traceback, codecs

    def get_export_path():
        if platform.system()=="Darwin":
            return input("Enter path to export: ")
        else:
            return sys.argv[1]

    # Load in the export (dropped onto CCG_schedule.py)
    with codecs.open(get_export_path(),encoding="utf-8") as f:
        export = json.load(f)

    # Figure out which season we're in
    SEASON = export["gameAttributes"]["season"]

    teams = {}
    for team in export["teams"]:
        if not any([season["season"]==SEASON for season in team["seasons"]]): continue # if not active, ignore
        season = max(team["seasons"],key=lambda season: season["season"])
        teams[season["tid"]]=season

    games = []
    for game in export["games"]:
        if game["season"]!=SEASON: continue
        games.append(colley.Game(game["won"]["tid"],game["lost"]["tid"],game["won"]["pts"],game["lost"]["pts"],overtimes=game["overtimes"]))

    rankings = colley.process(games,weight_fn=lambda game: 0.75**game.kwargs["overtimes"],margin=True)

    with open("rankings.txt","w") as f:
        for rank, team in enumerate(rankings,1):
            team, score = team
            team = teams[team]
            f.write(f"#{rank} {team['region']} ({team['won']}-{team['lost']}, {team['wonConf']}-{team['lostConf']} in conference, score: {score:0.3f})\n")
            print(f"#{rank} {team['region']} ({team['won']}-{team['lost']}, {team['wonConf']}-{team['lostConf']} in conference, score: {score:0.3f})")
except:
    with open("error.txt","w") as f:
        traceback.print_exc(file=f)
