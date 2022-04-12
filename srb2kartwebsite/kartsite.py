### SRB2Kart website
# This file contains all routes and all functions for the website.
# The goal is to split up everything into dedicated modules and stuff. Long live laziness.
# For now, take this giant file.

# import modules
import os
import json

from sys import platform, exit
from datetime import datetime

from flask import Flask, redirect, url_for, render_template, request
from flask_discord import DiscordOAuth2Session, Unauthorized

from forms import SkinShopForm

# set up flask app
app = Flask(__name__)

# load config from JSON
if os.path.exists("config.json"):
    with open("config.json", "r") as configFile:
        jsonData = json.load(configFile)
    configFile.close()

    app.secret_key = jsonData["secretKey"]
    app.config["DISCORD_CLIENT_ID"] = int(jsonData["discord"]["clientID"])
    app.config["DISCORD_CLIENT_SECRET"] = jsonData["discord"]["clientSecret"]
    app.config["DISCORD_REDIRECT_URI"] = jsonData["discord"]["redirectURI"]
    app.config["DISCORD_BOT_TOKEN"] = jsonData["discord"]["botToken"]
    scoreLocations = jsonData["scoreLocations"]

    kartUsersFile = jsonData["kartUsersFile"]
    skinInfoFile = jsonData["skinInfoFile"]
    skinShopPointsRequired = jsonData["skinShopPointsRequired"]
    mapsFile = jsonData["mapsFile"]
    pointsFile = jsonData["pointsFile"]
    transactionLog = jsonData["transactionLog"]
else:
    print("config.json does not yet exist. Please create the file and enter the correct details. See config.json.example for more information.")
    exit(1)


os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "true"      # !! Only in development environment.
discord = DiscordOAuth2Session(app)

######################################
# FUNCTIONS
def getKartScore(playerName):
    """Return a dictionary with a player's score from the pre-defined scorekeeper files and their total score."""
    playerScoreTotal = 0
    playerScoreDict = {}
    maxScore = 0    # good programming here
    minScore = 9999999999999999
    
    for server in scoreLocations:
        with open(scoreLocations[server], "r") as openFile:
            for line in openFile:
                lineSplit = line.split(";")
                
                if playerName == lineSplit[0]:
                    print(f"[Kart scores] {playerName}: {int(lineSplit[1])} points on {server}")
                    playerScoreTotal += int(lineSplit[1])
                    playerScoreDict[server] = int(lineSplit[1])

                    break   # we're done

    # also add the player's total points, min and max points as a dict key
    playerScoreDict["totalScore"] = playerScoreTotal

    return playerScoreDict

def reservePoints(form, skinData, userName, reservedPoints):
    """Takes a form from the skin shop and writes data in a JSON file.
    Donated points go towards skin files. Current reserved poitns must be passed to this function."""

    # match the chosen skin to a skin file
    if form.skinsRadio.data in skinData:
        skinFile = skinData[form.skinsRadio.data]['file']
    else:
        print(f"[Reserve Points] Couldn't match {form.skinsRadio.data} to a file")
        return 1

    ## add or update the skinfile with the donated points from the user and server
    try:
        if isinstance(reservedPoints["files"][skinFile], dict):
            print("[Reserve Points] Skin file already exists in data.")
            
    except:
        print("[Reserve Points] Skin file not present in data, adding it.")
        reservedPoints["files"][skinFile] = {'totalPoints': 0}
    
    # check if the user already donated points here
    try:
        if isinstance(reservedPoints["files"][skinFile][userName], dict):
            print("[Reserve Points] User previously had points donated")
    except:
            print(f"[Reserve Points] First time user donates for {skinFile}")
            reservedPoints["files"][skinFile][userName] = {}

    # check if the server the user's donating from is present and update points, otherwise add them
    try:
        reservedPoints["files"][skinFile][userName][form.chosenServer.data] += int(form.pointsDonating.data)
        print(f"[Reserve Points] {userName} donates {form.pointsDonating.data} from {form.chosenServer.data} totalling {reservedPoints['files'][skinFile][userName][form.chosenServer.data]}")
    except:
        print(f"[Reserve Points] User donates {form.pointsDonating.data} for {skinFile}")
        reservedPoints["files"][skinFile][userName][form.chosenServer.data] = int(form.pointsDonating.data)

    # keep track of the amount of points the player has donated lmao
    # because i'm a dumbass i do it like this
    try:
        reservedPoints["players"][userName]["servers"][form.chosenServer.data] += int(form.pointsDonating.data)
        reservedPoints["players"][userName]["filesDonatedTo"].append(form.skinsRadio.data)
        doneReserving = True
    except: 
        print("[Reserve points player] Player has no points donated towards specified server")
        doneReserving = False

    if doneReserving == False:
        try:
            reservedPoints["players"][userName]["servers"][form.chosenServer.data] = int(form.pointsDonating.data)
            reservedPoints["players"][userName]["filesDonatedTo"].append(form.skinsRadio.data)
            doneReserving = True
        except: 
            print("[Reserve points player] Player has no points donated yet")
            doneReserving = False

    if doneReserving == False:
        try:
            reservedPoints["players"][userName] = {"servers": {form.chosenServer.data: int(form.pointsDonating.data)}, "filesDonatedTo": [form.skinsRadio.data]}
        except:
            print("[Reserve points player] I have fallen and I can't get up.")
    
    # also update the total points counter
    reservedPoints["files"][skinFile]['totalPoints'] = reservedPoints["files"][skinFile]['totalPoints'] + int(form.pointsDonating.data)
    
    # and add the points to the skinPoints dict
    reservedPoints["skinPoints"][form.skinsRadio.data] = reservedPoints["files"][skinFile]['totalPoints']

    # write the data to disk
    with open(pointsFile, "w") as file:
        json.dump(reservedPoints, file, indent=4)
        file.close()
    return 0

def loadReservedPoints(pointsFile):
    # first we load the reserved points to use in other functions
    # when points are changed the file should immediately be overwritten
        try:
            with open(pointsFile, "r") as file:
                reservedPoints = json.load(file)
            file.close()

            print("[Load reserved points] Loaded reserved points succesfully from disk.")
            return reservedPoints
        except:
            print("[Load reserved points] Couldn't load reserved points from disk. Using initial values and (re)creating file.")
            reservedPoints = { "files": {}, "players": {}, "skinPoints": {} }
            
            # write initial values to disk
            with open(pointsFile, "w") as file:
                json.dump(reservedPoints, file, indent=4)
            file.close()

            return reservedPoints

#####################################
# FLASK ROUTES
@app.route("/login/")
def login():
    return discord.create_session(scope=["identify"])

@app.route("/logout/")
def logout():
    discord.revoke()
    return redirect(url_for("home"))

@app.route("/")
def index():
    return redirect(url_for("home"))


@app.route("/callback/")
def callback():
    discord.callback()
    return redirect(url_for("home"))


@app.errorhandler(Unauthorized)
def redirect_unauthorized(e):
    return redirect(url_for("login"))

@app.route("/home/")
def home():
    
    try:
        # get data from the discord user
        if discord.authorized:
            discordUser = discord.fetch_user()
        else:
            # create a user with blank data
            class blankUser:
                name = "Log in"
                id = 0
                avatar_url = None
                discriminator = ''
            discordUser = blankUser

    except:
        return redirect(url_for("logout"))
    
    return render_template("home.html",
        discordUser=discordUser, 
    )

@app.route("/maps/")
def maps():
    
    try:
        # get data from the discord user
        if discord.authorized:
            discordUser = discord.fetch_user()
        else:
            # create a user with blank data
            class blankUser:
                name = "Log in"
                id = 0
                avatar_url = None
                discriminator = ''
            discordUser = blankUser

    except:
        return redirect(url_for("logout"))

    # retrieve user bindings
    if os.path.exists(kartUsersFile) and discord.authorized:
        with open(kartUsersFile, "rt") as kartUsersData:
            try:
                kartUsers = json.load(kartUsersData)
            except:
                print("Couldn't load kart users file. Does it have data and is the syntax correct?")
                userName = None

        kartUsersData.close()

        if str(discordUser.id) in kartUsers['kartUsers']:
            print(f"[Discord <> Kart bind] Matched {discordUser.name} to {kartUsers['kartUsers'][str(discordUser.id)]['playerName']}")
            userName = kartUsers['kartUsers'][str(discordUser.id)]['playerName']
        else:
            print(f"[Discord <> Kart bind] Could not match {discordUser.name}. Using empty data for profile")
            userName = None
    elif not os.path.exists(kartUsersFile):
        print("[Discord <> Kart bind] No kart users file exists. Unable to match any users.")
        userName = None
    elif not discord.authorized:
        userName = None
    
    # get data from maps json
    if os.path.exists(mapsFile):
        with open (mapsFile, "r") as mapFile:
            mapData = json.load(mapFile)
    else:
        print("[Map info] No map info file exists.")
        mapData = {}

    return render_template("maps.html",
        discordUser=discordUser,
        mapData=mapData,
        userName = userName
    )

@app.route("/skinshop/", methods=["GET", "POST"])
def skinshop():
    """Renders a page and form in which users can donate points towards skin files."""

    # load reserved points from disk
    reservedPoints = loadReservedPoints(pointsFile)

    # get data from the discord user
    if discord.authorized:
        discordUser = discord.fetch_user()
    else:
        # create a user with blank data
        class blankUser:
            name = "Log in"
            id = 0
            avatar_url = None
            discriminator = ''
        discordUser = blankUser

    # retrieve user bindings
    if os.path.exists(kartUsersFile):
        with open(kartUsersFile, "rt") as kartUsersData:
            try:
                kartUsers = json.load(kartUsersData)
            except:
                print("Couldn't load kart users file. Does it have data and is the syntax correct?")
                userName = None

        kartUsersData.close()

        if str(discordUser.id) in kartUsers['kartUsers']:
            print(f"[Discord <> Kart bind] Matched {discordUser.name} to {kartUsers['kartUsers'][str(discordUser.id)]['playerName']}")
            userName = kartUsers['kartUsers'][str(discordUser.id)]['playerName']
        else:
            print(f"[Discord <> Kart bind] Could not match {discordUser.name}. Using empty data for profile")
            userName = None
    else:
        print("[Discord <> Kart bind] No kart users file exists. Unable to match any users.")
        userName = None
    # get the user's score
    if userName != None: playerScore = getKartScore(userName)
    else: playerScore = {"totalScore": 0}
    
    # get data from the skins and add possible choices to the form
    if os.path.exists(skinInfoFile):
        with open (skinInfoFile, "r") as skinFile:
            skinData = json.load(skinFile)
    else:
        print("[Skin info] No skin info file exists.")
        skinData = {"no skins found": {
            "realname": "no skins found",
            "facewant": "pibardy",
            "kartspeed": "-",
            "kartweight": "-",
            "prefcolor": "none",
            "file": "no file"
        }}

    # do some formatting
    scoreBuffer = {}    # used to track individual server points
    serverList = []     # used in the form to give server options
    for server in playerScore:
        if server != 'totalScore':
            scoreBuffer[server] = playerScore[server]
            serverList.append(server)
    
    # determine if the player already reserved points for stuff and deduct that amount from their available amount of points
    if userName in reservedPoints["players"]:
        print(f"[Point donation] {userName} donated points previously")
        for server in reservedPoints["players"][userName]["servers"]:
            scoreBuffer[server] -= reservedPoints["players"][userName]["servers"][server]

    # set up the form to be used in the template
    form = SkinShopForm(request.form)
    form.chosenServer.choices = serverList

    # add the possible skin choices to the form, needs to be done before validation
    for skin in skinData:
        form.skinsRadio.choices.append([skin, str(skinData[skin]['realname'].replace("_", " "))])

    if request.method == "POST" and form.validate_on_submit():
        print("[Form] Form validated succesfully.")
        print("[Form] User donating:", userName)
        print("[Form] Points donated:", form.pointsDonating.data)
        print("[Form] Chosen server:", form.chosenServer.data)
        print("[Form] Chosen skin:", form.skinsRadio.data)

        # stupid workaround cuz im lazy
        validRequest = False
        # make sure the user chose a valid skin. you never know
        if form.skinsRadio.data not in skinData:
            print("[Form error] User somehow gave an invalid skin to donate to")
            errorMessage = f"{form.skinsRadio.data} is not a valid skin to donate points to."
            successMessage = None
        # make sure the user gave a valid amount of points
        elif form.pointsDonating.data > scoreBuffer[form.chosenServer.data]:
            print("[Form error] User donated too much points")
            errorMessage = f"You do not have {form.pointsDonating.data} points available on {form.chosenServer.data}. Check the amount you're donating and/or select the correct server."
            successMessage = None
        elif form.pointsDonating.data <= 0:
            print(f"[Form error] User donated a bad amount of points ({form.pointsDonating.data})")
            errorMessage = f"You can't donate {form.pointsDonating.data} points."
            successMessage = None
        else:
            errorMessage = None
            validRequest = True

        # reserve the points
        if validRequest == True and reservePoints(form, skinData, userName, reservedPoints) == 0:
            skinName = str(skinData[form.skinsRadio.data]['realname']).replace("_", " ")
            print(f"[Form] {userName} donated {form.pointsDonating.data} points from {form.chosenServer.data} towards {skinName} (from {skinData[form.skinsRadio.data]['file']}).")
            successMessage = f"You donated {form.pointsDonating.data} points from {form.chosenServer.data} towards {skinName} (from {skinData[form.skinsRadio.data]['file']})."

            # deduct the points from the user's scoreBuffer
            scoreBuffer[form.chosenServer.data] -= int(form.pointsDonating.data)

            # write to the transaction log
            with open(transactionLog, "a") as tL:
                tL.write(f"{datetime.now().strftime('%d/%m/%Y %H:%M:%S')};{userName};{form.pointsDonating.data};{form.chosenServer.data};{skinName};{skinData[form.skinsRadio.data]['file']}\n")
            tL.close()

        else:
            if errorMessage == None:
                errorMessage = "Your points could not be reserved. Reload the page and try again. Please notify Aqua if this error persists."
                successMessage = None

    elif request.method == "POST" and not form.validate_on_submit():
        print("[Invalid form] Form failed to validate.") 
        print("[Invalid form] User donating:", userName)
        print("[Invalid form] Points donated:", form.pointsDonating.data)
        print("[Invalid form] Chosen server:", form.chosenServer.data)
        print("[Invalid form] Chosen skin:", form.skinsRadio.data)

        # make sure the user donates a valid amount of points
        if form.pointsDonating.data == 0:
            print("[Invalid form] User donated 0 points")
            errorMessage = "You can't donate 0 points."
            successMessage = None
        elif form.skinsRadio.data == None:
            print("[Invalid form] User did not select a skin")
            errorMessage = "Select a skin to donate points to."
            successMessage = None
        else: 
            errorMessage = "An unknown error occured. Reload the page and try again. Please notify Aqua if this error persists."
            successMessage = None
    else: 
        errorMessage = None
        successMessage = None

    # add reserved points to skins if they already have some
    for skin in skinData:
        if skinData[skin]['file'] in reservedPoints["files"]:
            #print("Matched", skinData[skin]['file'])
            skinData[skin]['reservedPoints'] = f"{reservedPoints['files'][skinData[skin]['file']]['totalPoints']} points"
        else:
            skinData[skin]['reservedPoints'] = '-- no points --'

    # sort the skins top 5 and pass it on
    sortedSkins = sorted(reservedPoints["skinPoints"].items(), key=lambda item: item[1], reverse=True)

    # render the page and serve it
    return render_template(
        'skinshop.html', 
        form=form, 
        discordUser=discordUser, 
        userName=userName, 
        playerScore=playerScore,
        scoreBuffer=scoreBuffer,
        reservedPoints=reservedPoints,
        skinShopPointsRequired=skinShopPointsRequired,
        skinData=skinData,
        errorMessage=errorMessage,
        successMessage=successMessage,
        sortedSkins = sortedSkins,
        template="form-template"
        )
    # FR: add search

if __name__ == "__main__":
    #app.run(host='0.0.0.0', debug=True)
    #app.run(host='0.0.0.0', port=28962, debug=True)
    app.run(host='0.0.0.0')
