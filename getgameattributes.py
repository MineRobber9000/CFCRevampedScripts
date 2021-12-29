import json, sys, traceback

# Gets the gameAttributes dict from the export. For testing and examination purposes.
# gameAttributes handles a lot of stuff in game.
# For an explanation of some of the more useful/interesting ones:
# https://football-gm.com/manual/customization/game-attributes/

try:
    # Load in the export (dropped onto the script)
    with open(sys.argv[1]) as f:
        export = json.load(f)

    # Export the gameAttributes (confs, divs, etc.)
    with open("output.json","w") as f:
        json.dump(export["gameAttributes"],f)
except:
    with open("error.txt","w") as f:
        traceback.print_exc(file=f)
