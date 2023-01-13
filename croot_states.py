try:
    import traceback, json, sys, platform, codecs, pandas

    def get_export_path():
        if platform.system()=="Darwin":
            return input("Enter path to export: ")
        else:
            return sys.argv[1]

    # Load in the export
    with codecs.open(get_export_path(),encoding="utf-8") as f:
        export = json.load(f)

    # constants to modify
    # how many croots do we want?
    HOW_MANY_CROOTS = 275

    # earliest season with "undrafted players" (recruits)
    DRAFT_YEAR = 2**64 # start with something ridiculous
    for player in export["players"]:
        # TID -2 is undrafted, if they're not undrafted then we don't care
        if player["tid"]!=-2: continue
        # if their draft year is less than the draft year we have, run it
        if player["draft"]["year"]<DRAFT_YEAR:
            DRAFT_YEAR = player["draft"]["year"]

    # now gather all of those players into a list
    croots = []
    for player in export["players"]:
        if player["tid"]==-2 and player["draft"]["year"]==DRAFT_YEAR: croots.append(player)

    # sort by valueFuzz
    croots.sort(key=lambda x: x["valueFuzz"],reverse=True)

    # now make the output
    output = []
    for i, player in enumerate(croots[:HOW_MANY_CROOTS],1):
        output.append([i,player["nameAbbrev"],player["ratings"][-1]["pos"],player["ratings"][-1]["ovr"],player["ratings"][-1]["pot"],"",player])
