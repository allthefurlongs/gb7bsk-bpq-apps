import sys
import os
import json
import sqlite3

user_call = sys.stdin.readline().rstrip()
user_call = user_call.upper()

with open('wall.json') as f:
    conf = json.load(f)
wall_fn = conf['wall_file']
msgs_per_page = conf['msgs_per_page']
current_page = 0  # Page count starts from 0 to simplify sql 'limit' maths

def prompt():
    # Note we number pages from 0 internaly, so +1 to make it clearer for the user
    print(f"\n(Page {current_page+1}) [N]ext Page, [P]ost a message, [S]et page no., [C]hange number of messages per page, [Q]uit:")
    sys.stdout.flush()

def print_messages():
    messages = cur.execute(f"select timestamp, callsign, message from wall order by timestamp desc limit {current_page * msgs_per_page}, {msgs_per_page}")
    messages = messages.fetchall()
    if len(messages) == 0 and current_page == 0:
        print('(No messages yet)')
    elif len(messages) == 0 and current_page > 0:
        print('(No messages on this page)')
    else:
        for msg in messages:
            print(f"{msg['timestamp']}: <{msg['callsign']}> {msg['message']}")

create_db = not os.path.isfile(wall_fn)
walldb = sqlite3.connect(wall_fn)
try:
    walldb.row_factory = sqlite3.Row  # Return dictionary style results when querying sqlite
    cur = walldb.cursor()
    if create_db:
        cur.execute("create table wall (timestamp datetime default current_timestamp, callsign varchar(20) not null, message varchar(250) not null)")
        cur.execute("create index timestamp on wall (timestamp desc)")
        walldb.commit()
    print("")
    print("GB7BSK Message Wall")
    print("")
    print_messages()
    prompt()
    while True:
        input = sys.stdin.readline().rstrip().upper()
        if input == 'Q':
            print("Qutting wall, returning to node.")
            exit()
        elif input == 'C':
            print("Enter new number of messages to display per page:")
            num = sys.stdin.readline().rstrip()
            try:
                num = int(num)
                msgs_per_page = num
                current_page = 0
                print(f"Messages per page set to: {msgs_per_page}")
                print_messages()
                prompt()
            except (ValueError, TypeError):
                print("Invalid input.")
                prompt()
        elif input == 'N':
            current_page += 1
            print_messages()
            prompt()
        elif input == 'S':
            print("Enter page number:")
            num = sys.stdin.readline().rstrip()
            try:
                current_page = int(num) - 1  # We number internally from 0
                print_messages()
                prompt()
            except (ValueError, TypeError):
                print("Invalid input.")
                prompt()
        elif input == 'P':
            print("Enter your one-line message, 250 chars max:")
            new_msg = sys.stdin.readline().rstrip()
            if len(new_msg) > 0 and not new_msg.startswith('*** Disconnected from Stream'):
                cur.execute('insert into wall (callsign, message) values (?, ?)', (user_call, new_msg))
                walldb.commit()
                print("Message posted.")
                msgs_per_page = conf['msgs_per_page']
                current_page = 0
                print_messages()
            else:
                print("Empty message, not posted")
            prompt()
        else:
            print("Unrecognised option.")
            prompt()
finally:
    walldb.close()
