import requests
import json
import random

URL = "http://localhost:5000"
TTNN_GAME_ID = 8

username = raw_input("Who are you? ")
print("Hello " + username)

r = requests.get(URL + "/user-info",
    data = {
        "username":username,
    })

user_id = r.json()["id"]


class GameInfo:
    def __init__(self):
        self.rounds = []

    def player_list(self, players):
        l = []
        for p in players:
            if p["id"] != user_id:
                l.append(p["username"])
        return l

    def display_current_rounds(self):
        r = requests.get(URL + "/rounds",
            data = {
                "game_id" : TTNN_GAME_ID,
                "user_id" : user_id,
            })

        self.rounds = r.json()["rounds"]

        print("\n\n")
        if len(self.rounds) == 0:
            print("(currently no game)")
        else:
            print("Games:")
            count = 0
            for r in self.rounds:
                print(str(count) + ". " + ", ".join(self.player_list(r["players"])))
                count += 1

    def delete_round(self, number):
        if number >= 0 and number < len(self.rounds):
            round = self.rounds[number]
            r = requests.post(URL + "/delete-round",
                data = {
                    "id" : round["id"],
                })

    def play_round(self, number):
        if number >= 0 and number < len(self.rounds):
            round = self.rounds[number]
            r = requests.get(URL + "/moves",
                data = {
                    "round_id" : round["id"],
                })

            moves = r.json()["moves"]
            if len(moves) == 0:
                print "(no moves)"
            else:
                for move in moves:
                    print move["content"]

            new_move_content = raw_input("new move (or hit return to skip): ")

            if new_move_content != "":
                r = requests.post(URL + "/new-move",
                    data = {
                        "round_id" : round["id"],
                        "user_id" : user_id,
                        "content" : new_move_content,
                    })


gameInfo = GameInfo()

def get_an_opponent_id():
    opponent_id = 0
    while opponent_id == 0:
        op_username = raw_input("enter a username for your opponent: ")

        r = requests.get(URL + "/user-info",
            data = {
                "username":op_username,
            })

        if r.status_code == 200:
            if r.json()["id"]:
                opponent_id = int(r.json()["id"])
        else:
            print("Getting info for user " + op_username + " didn't work.  Try again?")
    return opponent_id


while True:
    gameInfo.display_current_rounds()
    print("")
    print("    \n".join([
        "n <username>  New game with opponent <username>",
        "d <number>    Delete game <number>",
        "p <number>    Play game <number>"]) + "\n")

    command = raw_input("> ")

    sc = command.split()

    if len(sc) == 2:
        if sc[0] == 'd':
            number = int(sc[1])
            gameInfo.delete_round(number)

        if sc[0] == 'n':
            op_username = sc[1]

            r = requests.get(URL + "/user-info",
                data = {
                    "username":op_username,
                })

            if r.status_code == 200:
                if r.json()["id"]:
                    opponent_id = int(r.json()["id"])

                requests.post(URL + "/new-round",
                    data = {
                        "game_id" : TTNN_GAME_ID,
                        "user_id" : user_id,
                        "players" : " ".join(map(str, [user_id, opponent_id])),
                    })
            else:
                print("Getting info for user " + op_username + " didn't work.  Try again?")

        if sc[0] == 'p':
            number = int(sc[1])
            gameInfo.play_round(number)








