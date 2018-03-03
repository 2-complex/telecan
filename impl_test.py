
import implementation
import json
import database
import update_database
import os

if os.path.isfile("temp.db"):
    os.remove("temp.db")

db = database.Database("sqlite:///temp.db")
impl = implementation.Implementation(db.models, db.session)

blob = json.loads(impl.new_user( "Sir Humphrey Applegate", "Jazz123", "humpy@number10.co.uk" ))
assert(blob['success'])
humphrey_id = blob['id']

blob = json.loads(impl.new_user( "Sybil Fawlty", "Splendid11", "saucysibs@ft.co.uk" ))
assert(blob['success'])
sybil_id = blob['id']

blob = json.loads(impl.new_user( "Sybil Fawlty", "Splendid11", "saucysibs2@ft.co.uk" ))
assert(blob['success'] == False)

blob = json.loads(impl.new_user( "Sybil", "Splendid11", "saucysibs@ft.co.uk" ))
assert(blob['success'] == False)


assert( sybil_id > 0 and humphrey_id > 0 and sybil_id != humphrey_id )

print( "humphrey_id = " + str(humphrey_id) )
print( "sybil_id = " + str(sybil_id) )

blob = json.loads( impl.new_game(humphrey_id, "Chess", "A Musical from the 80s") )
assert(blob['success'])
chess_id = blob['id']

blob = json.loads( impl.new_game(sybil_id, "Checkers", "Dog given to Nixon as bribe") )
assert(blob['success'])
checkers_id = blob['id']

print("chess_id = " + str(chess_id))
print("checkers_id = " + str(checkers_id))


blob = json.loads( impl.new_round(sybil_id, chess_id, ','.join(map(str, [humphrey_id, sybil_id]) ) ) )
assert(blob['success'])
chess_round_id = blob['id']

print("chess_round_id = " + str(chess_round_id))

blob = json.loads( impl.new_move(chess_round_id, sybil_id, "Knight to C3") )
assert(blob['success'])

blob = json.loads( impl.new_move(chess_round_id, humphrey_id, "Pawn to J4") )
assert(blob['success'])

blob = json.loads( impl.new_move(chess_round_id, sybil_id, "You sunk my battleship") )
assert(blob['success'])

blob = json.loads( impl.moves(chess_round_id) )
assert( blob['moves'][0]['content'] == "Knight to C3" )
assert( blob['moves'][1]['content'] == "Pawn to J4" )
assert( blob['moves'][2]['content'] == "You sunk my battleship" )

print( blob['moves'][-1]['content'] )

print("PASS")

