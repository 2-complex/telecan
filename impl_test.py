import implementation
import json
import database
import os


if os.path.isfile("temp.db"):
    os.remove("temp.db")

db = database.Database("sqlite:///temp.db")
impl = implementation.Implementation(db.models, db.session)

impl.delete_all_rounds()

blob = json.loads(impl.new_user( "Sir Humphrey Applegate", "Jazz123", "humpy@number10.co.uk" ))
assert(blob['success'] == True)
humphrey_id = blob['id']

blob = json.loads(impl.user_info( "Sir Humphrey Applegate" ))
assert(blob['id'] == humphrey_id)
assert(blob['username'] == "Sir Humphrey Applegate")
assert(blob['email'] == "humpy@number10.co.uk")

r = impl.sign_in("Sir Humphrey Applegate", "Jazz123")
assert(r.success)
assert(len(r.key) > 10)
assert(json.loads(r.blob)["user_id"] == humphrey_id)

r = impl.sign_in("Sir Humphrey Applegate", "WrongPassword")
assert(not r.success)
assert(r.key == "")
assert(not json.loads(r.blob).has_key("user_id"))
assert(json.loads(r.blob)["success"] == False)

blob = json.loads(impl.new_user( "Sybil Fawlty", "Splendid11", "saucysibs@ft.co.uk" ))
assert(blob['success'] == True)
sybil_id = blob['id']

blob = json.loads(impl.new_user( "Sybil Fawlty", "Splendid11", "saucysibs2@ft.co.uk" ))
assert(blob['success'] == False)

blob = json.loads(impl.new_user( "Sybil", "Splendid11", "saucysibs@ft.co.uk" ))
assert(blob['success'] == False)

blob = json.loads(impl.new_user( "Sybil ", "Splendid11", "saucysibs@ft.co.uk" ))
assert(blob['success'] == False)

blob = json.loads(impl.new_user( "  Leading whitespace", "Splendid12", "uniqueprobably12341234@ft.com" ))
assert(blob['success'] == False)
assert(blob['reason'] == "Username invalid.")

blob = json.loads(impl.new_user( "Trailing whitespace   ", "Splendid12", "uniqueprobably12341234@ft.com" ))
assert(blob['success'] == False)
assert(blob['reason'] == "Username invalid.")

blob = json.loads(impl.new_user( "(contains paren", "Splendid12", "uniqueprobably12341234@ft.com" ))
assert(blob['success'] == False)
assert(blob['reason'] == "Username invalid.")

blob = json.loads(impl.new_user( "", "Splendid12", "uniqueprobably12341234@ft.com" ))
assert(blob['success'] == False)
assert(blob['reason'] == "Username invalid.")

blob = json.loads(impl.new_user( "Jack the Ripper", "Jack123", "lessthanlightning@bleakstreet.co.uk" ))
assert(blob['success'] == True)
jack_id = blob['id']

blob = json.loads(impl.delete_user("23gwgwe\n\n\n"))
assert(blob['success'] == False)

blob = json.loads(impl.delete_user("0"))
assert(blob['success'] == False)


blob = json.loads(impl.delete_user(jack_id))
assert(blob['success'] == True)
assert(blob['deleted']==[jack_id])

blob = json.loads(impl.delete_user(str(jack_id)))
assert(blob['success'] == False)

assert( sybil_id > 0 and humphrey_id > 0 and sybil_id != humphrey_id )

print( "humphrey_id = " + str(humphrey_id) )
print( "sybil_id = " + str(sybil_id) )

blob = json.loads( impl.new_game(humphrey_id, "Chess", "A Musical from the 80s") )
assert(blob['success'] == True)
chess_id = blob['id']

blob = json.loads( impl.new_game(humphrey_id, "Chess", "A DIFFERENT Musical with the same name from the 80s") )
assert(blob['success'] == False)

blob = json.loads( impl.games({"username":"Sir Humphrey Applegate"}) )
assert(len(blob['games']) == 1)
assert(blob['games'][0]['title'] == u"Chess")

blob = json.loads( impl.new_game(sybil_id, "Checkers", "Dog given to Nixon as bribe") )
assert(blob['success'] == True)
checkers_id = blob['id']

print("chess_id = " + str(chess_id))
print("checkers_id = " + str(checkers_id))

blob = json.loads( impl.new_game(1000, "Checkers", "A game.  A freakin game.") )
assert(blob['success'] == False)

blob = json.loads(impl.delete_game(checkers_id))
assert(blob['success'] == True)
assert(blob['deleted']==[checkers_id])

blob = json.loads(impl.delete_game(checkers_id))
assert(not blob['success'])

blob = json.loads( impl.new_round(sybil_id, chess_id, ','.join(map(str, [humphrey_id, sybil_id]))) )
assert(blob['success'] == True)
chess_round_id = blob['id']
print("chess_round_id = " + str(chess_round_id))

blob = json.loads( impl.rounds({"game_id":chess_id}) )
assert(len(blob['rounds']) == 1)
assert(blob['rounds'][0]['game_id'] == chess_id)

blob = json.loads( impl.new_round(sybil_id, chess_id, ','.join(map(str, [humphrey_id]))) )
assert(blob['success'] == True)
wrong_round_id = blob['id']

blob = json.loads(impl.new_round(sybil_id, chess_id, "asdf"))
assert(blob['success'] == False)

blob = json.loads(impl.new_round(1000, chess_id, str(humphrey_id)))
assert(blob['success'] == False)

blob = json.loads(impl.new_round(sybil_id, 1000, str(humphrey_id)))
assert(blob['success'] == False)


blob = json.loads( impl.delete_round(wrong_round_id) )
assert(blob['success'] == True)
assert(blob['deleted']==[wrong_round_id])
print("deleted rounds: "+str(wrong_round_id))

blob = json.loads( impl.delete_round(wrong_round_id) )
assert(blob['success'] == False)

blob = json.loads( impl.new_move(chess_round_id, sybil_id, "Knight to C3") )
assert(blob['success'] == True)

blob = json.loads( impl.new_move(chess_round_id, humphrey_id, "Pawn to J4") )
assert(blob['success'] == True)

blob = json.loads( impl.new_move(chess_round_id, sybil_id, "You sunk my battleship") )
assert(blob['success'] == True)

blob = json.loads( impl.moves({"round_id":chess_round_id}) )
assert( blob['moves'][0]['content'] == "Knight to C3" )
assert( blob['moves'][1]['content'] == "Pawn to J4" )
assert( blob['moves'][2]['content'] == "You sunk my battleship" )

print( blob['moves'][0]['content'] )
print( blob['moves'][1]['content'] )
print( blob['moves'][2]['content'] )

assert( list(db.models.Game.query.all()) != [] )
assert( list(db.models.Round.query.all()) != [] )
assert( list(db.models.Move.query.all()) != [] )

blob = json.loads( impl.delete_game(chess_id) )

assert( list(db.models.Game.query.all()) == [] )
assert( list(db.models.Round.query.all()) == [] )
assert( list(db.models.Move.query.all()) == [] )


print("PASS")

