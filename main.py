import socket
import sys
import time
import urllib.request
import os
import threading
import keyboard

PORT = 1234
HEADERSIZE = 20
TYPEHEADERSIZE = 1
SENDERHEADERSIZE = 15
FULLHEADERSIZE = 36
prompt = "> "
players = []
host = False
emergencySocketStop = False
sendersTypeChosen = {}
teleporter = [
    "The town",
    "Home",
    "The market"
]
yourJob = None
allJobs = {
    "1": {"id": 1, "text": "Collect the ancient runes of time from the castle in the west."},
    "2": {"id": 2, "text": "Extract the crystal of Horath from the ruins of Hagrot."},
    "3": {"id": 3, "text": "Get me a cake from the market."},
}

def game(s):
    global host
    global sendersTypeChosen
    global players
    global emergencySocketStop
    global teleporter
    global allJobs
    global job

    print("Game starting...")
    time.sleep(1)
    os.system("cls")

    crystal = input("A strange man approaches you. He unrolls a piece of leather showing four crystals. One (orange), one (purple), one (blue), and one (green). He says, \"I see you are new to the town. Want a crystal to get you ready for what may lie ahead? If so, which one?\"\n> ")

    if crystal == "orange":
        print("You grow taller. A beard appears on your face and a staff appears in your hand. The man hands you a pointy hat and tells you to put it on, so you do.")
        charType = "wizard"
    if crystal == "purple":
        print("You become slightly shorter and more plump. The man hands you a pair of welding goggles which you put on.")
        charType = "engineer"
    if crystal == "blue":
        print("The man hands you a wand and a cloak which you put on.")
        charType = "mage"
    if crystal == "green":
        print("Shining metal armour appears on your body and a stallion at your side.")
        charType = "knight"

    answer = input("Would you mind running some errands for me? It will pocket you some money! (y)/(n)\n> ")

    if answer == "yes" or answer == "y":
        print("Thanks! Here is a list of all the jobs that I need done around here.")
    if answer == "no" or answer == "n":
        print("What's that? I'll assume its a yes, I'm hard of hearing you see. Here's a list of the stuff I need done.")

    print("""
    1. Collect the ancient runes of time from the castle in the west.
    2. Extract the crystal of Horath from the ruins of Hagrot.
    3. Get me a cake from the market.
    """)
    addPlaceToTeleporter("The castle in the west")
    addPlaceToTeleporter("The ruins of Hagrot")

    job = int(input("Choose a job from above by typing its number.\n> "))

    if job == 1:
        newJob(allJobs["1"])
    if job == 2:
        newJob(allJobs["2"])
    if job == 3:
        newJob(allJobs["3"])
    if job == None:
        askStartingJobAgain()

    answer = input("Now open up the teleporter by typing '/teleport'.\n> ")

    if answer == "/teleport":
        printTeleporter()
        print("To use the teleporter use the up and down arrow keys to select where you want to teleport to. To exit the teleporter, click escape. If you ever want to go back to the teleporter, type '/teleport'. Whenever you start moving the pointer, this message will dissapear.")

def teleportTo(place):
    global prompt

    os.system("cls")

    if place == "The town":
        print("""You have arrived in the town. What would you like to do?
        
        - Go shopping
        - Trade items
        """)
        answer = input(prompt)

def moveTeleporterPointer(newPosition):
    global teleporter
    underflow = False
    overflow = False

    os.system("cls")

    for place in teleporter:
        if newPosition > len(teleporter) - 1:
            overflow = True
            if teleporter.index(place) == 0:
                print("> " + place)
                continue
            print("  " + place)
            continue
        if newPosition < 0:
            underflow = True
            if teleporter.index(place) == len(teleporter) - 1:
                print("> " + place)
                continue
            print("  " + place)
            continue
        if teleporter.index(place) == newPosition:
            print("> " + place)
            continue
        print("  " + place)

    if underflow == True:
        return len(teleporter) - 1
    if overflow == True:
        return 0
    return newPosition

def printTeleporter():
    global teleporter
    global prompt

    pointerLine = 0

    os.system("cls")

    print("> " + teleporter[0])
    for place in teleporter:
        if place == teleporter[0]: continue
        print("  " + place)

    while True:
        if keyboard.is_pressed("up"):
            pointerLine -= 1
            pointerLine = moveTeleporterPointer(pointerLine)
        if keyboard.is_pressed("down"):
            pointerLine += 1
            pointerLine = moveTeleporterPointer(pointerLine)
        if keyboard.is_pressed("enter"):
            # handle teleporting to place
            placeToGoTo = teleporter[pointerLine]
            teleportTo(placeToGoTo)
            pass
        if keyboard.is_pressed("esc"):
            os.system("cls")
            print(prompt)
            return

def askStartingJobAgain():
    global newJob

    job = int(input("Please type either 1, 2, or 3 to choose a job.\n> "))

    if job == 1:
        newJob(allJobs["1"])
    if job == 2:
        newJob(allJobs["2"])
    if job == 3:
        newJob(allJobs["3"])
    else:
        askStartingJobAgain()

def newJob(job):
    global yourJob

    if yourJob != None:
        print("You can't have two jobs at the same time!")
        return

    yourJob = job

def addPlaceToTeleporter(place):
    global teleporter

    teleporter.append(place)
    print(place + " has been added to your teleporter!")

def byteEncodeAndAddHeader(msg, msgType):
    msg = bytes(msg, "utf-8")
    msg = bytes(f"{len(msg):<{HEADERSIZE}}", "utf-8") + bytes(msgType, "utf-8") + bytes(f"{socket.gethostbyname(socket.gethostname()):<{SENDERHEADERSIZE}}", "utf-8") + msg
    return msg

def recvMessage(s):
    global host
    global players
    global emergencySocketStop

    fullMsg = b''
    newMsg = True

    while True:
        if emergencySocketStop == False:
            if not host:
                try:
                    msg = s.recv(16)
                    #print("sb1")
                except OSError:
                    #print("sb15")
                    continue
            if host:
                try:
                    for player in players:
                        if player["address"] != "host":
                            msg = player["socket"].recv(4096)
                    #print("sb1")
                except OSError:
                    #print("sb15")
                    continue
            #print("sb2")
            if newMsg:
                #print("sb3")
                try:
                    msgLen = int(msg[:HEADERSIZE])
                except:
                    print("There was a problem receiving the message.")
                newMsg = False

            fullMsg += msg
            #print("sb4")

            if len(fullMsg) - FULLHEADERSIZE == msgLen:
                #print("sb5")
                msgType = fullMsg.decode("utf-8")[HEADERSIZE]

                msgSender = fullMsg.decode("utf-8")[HEADERSIZE+TYPEHEADERSIZE:HEADERSIZE+TYPEHEADERSIZE+SENDERHEADERSIZE]

                finalMessage = fullMsg[FULLHEADERSIZE:].decode("utf-8")

                newMsg = True
                fullMsg = b''

                #print("sb6")
                #print((finalMessage, msgType))
                return (finalMessage, msgType, msgSender)
        else:
            return (None, None, None)


gender = input("Are you a (m)ale or a (f)emale. PS: anything in brackets is an option you can answer with\n> ")

input("Your mum walks up to you. She says, \"You are finally awake. You better head outside.\" (press ENTER to continue)")
answer = input("You walk into town. Do you want to (h)ost or (j)oin a game?\n> ")

if answer == "h" or answer == "host":
    lobbySize = int(input("How many players do you want to be in your group, including you?\n> "))

    host = True

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((socket.gethostname(), PORT))
    players.append({"socket": "host", "address": "host"})
    print("Send this info to the people you want to join the game: IP - " + socket.gethostbyname(socket.gethostname()) + " Port - " + str(PORT))
    s.listen(5)
    while len(players) < lobbySize:
        try:
            clientsocket, address = s.accept()
            players.append({"socket": clientsocket, "address": address})
            print("Player joined!")
        except:
            continue

    for player in players:
        if player["address"] != "host":
            player["socket"].send(byteEncodeAndAddHeader("lobby full", "s"))

    game(s)

if answer == "j" or answer == "join":
    host = False

    ip = input("Enter the IP the host gave you.\n> ")
    port = input("Enter the port the host gave you.\n> ")

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((ip, int(port)))

    msgRecvd, msgRecvdType, msgRecvdSender = recvMessage(s)
    if msgRecvd == "lobby full" and msgRecvdType == "s":
        game(s)
    else:
        print("Malformed message received from host. Exitting game.")
        time.sleep(2)
        emergencySocketStop = True
        sys.exit()