import json, sys, traceback

# Gets the schedule dict from the export. For testing and examination purposes.
# The schedule includes all of the games that are yet to be played.

try:
    # Load in the export (dropped onto the script)
    with open(sys.argv[1]) as f:
        export = json.load(f)

    # Export the schedule
    with open("output.json","w") as f:
        json.dump(export["schedule"],f)
except:
    with open("error.txt","w") as f:
        traceback.print_exc(file=f)
