import socket
import multiplayer
import sys
import time
import urllib.request

PORT = 1234
HEADERSIZE = 20
TYPEHEADERSIZE = 1
SENDERHEADERSIZE = 15
FULLHEADERSIZE = 36
prompt = "> "
players = []
host = False
emergencySocketStop = False

def game():
    print("Game starting...")
    input()

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

                finalMessage = fullMsg[FULLHEADERSIZE:].decode("utf-8")

                newMsg = True
                fullMsg = b''

                #print("sb6")
                #print((finalMessage, msgType))
                return (finalMessage, msgType)
        else:
            return (None, None)


gender = input("Are you a (m)ale or a (f)emale. PS: anything in brackets is an option you can answer with\n> ")

input("Your mum walks up to you. She says, \"You are finally awake. Your quest begins now.\" (press ENTER to continue)")
answer = input("You walk into town. Do you want to (h)ost or (j)oin a game?\n> ")

if answer == "h" or answer == "host":
    host = True

    s = multiplayer.Socket(True, socket.gethostname(), PORT)
    players.append({"socket": "host", "address": "host"})
    print("Send this info to the people you want to join the game: IP - " + socket.gethostbyname(socket.gethostname()) + " Port - " + str(PORT))
    s.s.listen(5)
    while len(players) < 4:
        try:
            clientsocket, address = s.s.accept()
            players.append({"socket": clientsocket, "address": address})
            print("Player joined!")
        except:
            continue

    for player in players:
        if player["address"] != "host":
            player["socket"].send(byteEncodeAndAddHeader("lobby full", "c"))

    game()

if answer == "j" or answer == "join":
    host = False

    ip = input("Enter the IP the host gave you.\n> ")
    port = input("Enter the port the host gave you.\n> ")

    s = multiplayer.Socket(False, ip, port)

    msgRecvd, msgRecvdType = recvMessage(s.s)
    if msgRecvd == "lobby full" and msgRecvdType == "s":
        game()
    else:
        print("Connection error. Malformed message from host.")
        time.sleep(2)
        emergencySocketStop = True
        sys.exit()