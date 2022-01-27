try: # errors end up in error.txt
    import csv, platform, sys, traceback
    from collections import defaultdict

    def get_sheet_path():
        if platform.system()=="Darwin":
            print("Remember to remove the header from the sheet (exported as CSV).")
            return input("Enter path to sheet: ")
        else:
            return sys.argv[1]

    croots = []
    with open(get_sheet_path()) as f:
        for row in csv.reader(f):
            if row[5]=="": break
            # Overall Rank, Name, Position, Committed To
            croots.append((int(row[0]),row[1],row[2],row[5]))

    # split out croots by team
    croots_by_team = defaultdict(list)

    for croot in croots:
        croots_by_team[croot[3]].append(croot)

    # now this is where you go to toy with the ranking logic
    # basically, the concept here is that we're only counting
    # recruits in the top 300. you get 100% of the points for
    # your top croot (300 for #1, 299 for #2, etc.), but that
    # percentage decays exponentially, so the formula doesn't
    # overly favor teams with more croots. that being said,
    # having more croots will still help.

    # change this number to tweak the percentage of decay
    DECAY = 0.75

    scores = defaultdict(int)
    for team in croots_by_team:
        croots_by_team[team].sort(key=lambda c: c[0])
        for i, croot in enumerate(croots_by_team[team]):
            if croot[0]>300: continue
            scores[team]+=(301-croot[0])*(DECAY**i)

    # now let's take the teams and sort them by their scores
    # this will tell us who had the best class by rank
    # note that for teams that didn't croot, or only crooted
    # below 300, there is no score for them. this is because
    # they didn't croot highly enough to even break the top
    # however many.

    teams = list(scores.keys())
    teams.sort(key=lambda t: scores[t],reverse=True)

    # output to file
    with open("output.txt","w") as f:
        for rank, team in enumerate(teams,1):
            print(f"{rank}. {team} ({scores[team]:0.4f})",file=f)
except:
    with open("error.txt","w") as f:
        traceback.print_exc(file=f)
