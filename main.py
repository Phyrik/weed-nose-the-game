import socket
import sys
import time
import urllib.request
import os
import threading

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

def checkTypes():
    global sendersTypeChosen

    for sender, status in sendersTypeChosen.items():
        if status == False:
            return False
    return True

def listenForTypeChoice(s):
    global players
    global sendersTypeChosen

    for player in players:
        sendersTypeChosen[player["address"][0]] = False

    msg, msgType, msgSender = recvMessage(s)

    if msgType == "s":
        if msg == "crystals chosen":
            for player in players:
                if player["address"][0] == msgSender:
                    sendersTypeChosen[player["address"][0]] = True

def game(s):
    global host
    global sendersTypeChosen
    global players
    global emergencySocketStop

    print("Game starting...")
    if host:
        thread = threading.Thread(target=listenForTypeChoice, args=[s])
        thread.start()
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
        print("Shining metal armour appears on your body and a stallin at your side.")
        charType = "knight"

    if host:
        print("Waiting for other players to choose a crystal...")
        while True:    
            crystalsChosen = checkTypes()
            if crystalsChosen == True:
                break
        for player in players:
            if player["address"][0] != "host":
                player["socket"].send(byteEncodeAndAddHeader("crystals chosen", "s"))
    if not host:
        s.sendall(byteEncodeAndAddHeader("type chosen", "s"))
        print("Waiting for other players to choose a crystal...")
        msg, msgType, msgSender = recvMessage(s)
        if msg == "crystals chosen" and msgType == "s":
            pass
        else:
            print("Malformed message received from host. Exitting game.")
            emergencySocketStop = True
            sys.exit()

    # all players' crystals chosen, continue game

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

input("Your mum walks up to you. She says, \"You are finally awake. Your quest begins now.\" (press ENTER to continue)")
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