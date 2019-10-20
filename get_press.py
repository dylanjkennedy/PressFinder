import requests
import csv
import sys

# When given an api-key and an opponent, make a csv
# of all plays in which a receiver is in press coverage
# and make each play with which reciever is in press
# if multiple are, create multiple rows
# string, string -> csv
def mainloop():
    args = sys.argv
    key = args[1]
    opponent = args[2]

    params = get_params(key)
    games = get_games(opponent, params)
    output = games_to_plays(games, opponent, params)

    #save_to_csv(output)
    save_to_txt(output, opponent + '_press.txt')

# Turn an api key into a jwt key and format as header
# str -> {str: str}
def get_params (key):
    params = {'x-api-key':key}
    r = requests.post('https://api.profootballfocus.com/auth/login', headers = params)
    jwt = r.json()['jwt']
    params = {'Authorization':'Bearer ' + jwt}
    return params

# For a given opponent, return all game ids in which they played in 2019
# str, {str: str} -> listof str
def get_games (opponent, params):
    r = requests.get('https://api.profootballfocus.com/v1/video/ncaa/games', headers = params)
    
    games = []
    for game in r.json()['games']:
        if game['away_team'] == opponent or game['home_team'] == opponent:
            if game['season'] == 2019:
                games.append(str(game['id']))
    return games

# For a list of games, create a dictionary indexed by WR, containing a list of tuples
# The first element in the tuple is the game id, the next is the play id
# listof str, str, str -> {str : listof (str,str)}
def games_to_plays (games, opponent, params):
    wr_dict = {}
    for game in games:
        r = requests.get('https://api.profootballfocus.com/v1/video/ncaa/games/'+game+'/plays', headers = params)
        plays = r.json()['plays']
        for play in plays:
            if 'press_players' in play.keys() and play['run_pass'] is 'P' and not play['screen']:
                wrs = get_players_in_press(play['press_players'], opponent)
                for wr in wrs:
                    if wr not in wr_dict:
                        wr_dict[wr] = []
                    #wr_dict[wr].append((play['game_id'],play['play_id']))
                    # Uder does not seem to require game ID
                    wr_dict[wr].append(str(play['play_id']))
    return wr_dict
                    
# Parse the press string to return which players
# (from the team we care about) are in press coverage
# str, str -> listof str
def get_players_in_press (press_info, opponent):

    # If no players are in press,
    if press_info == None:
        return []
    matchups = press_info.split(';')
    
    # We only want the player after the '>' since that indicates they were covered
    # We also want to remove the leading space, so we use [1:]
    # Finally we only want to log the WRs from the right team
    pressed = [match.split('>')[1][1:] for match in matchups if opponent in match.split('>')[1]]
    return pressed

# Take the dictionary and turn it into a csv
# We'll repeat the player on every line for clarity in final document
# {str : listof (str, str)} -> csv
def save_to_csv (output):
    header = ['Player','Game Id', 'Play Id']
    csv_list = [header]
    for player in output:
        for play in output[player]:
            csv_list.append([player, play[0], play[1]])

    with open('press.csv', 'w', newline ='') as f:
        writer = csv.writer(f)
        writer.writerows(csv_list)

# Take the dictionary and turn it into a txt
# This is an attempt to reformat into a more usable form
# {str : listof (str, str)} -> csv
def save_to_txt (output, filename):
    header = ['Player','Game Id', 'Play Id']
    txt_string = 'Player \t Play Ids\n'
    for player in output:
        print(output[player])
        txt_string += player + '\t' + ','.join(output[player]) + '\n'

    with open(filename, 'w', newline ='') as f:
        f.write(txt_string)

mainloop()

    


        
 
