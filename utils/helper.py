import logging
import sys
import datetime
import subprocess
import os
sys.path.insert(0, './model_bots')
from Qradar import Qradar

q = Qradar()

def check_aql(query:str) -> bool:

    normal_aql = False
    if "select" in query or "SELECT" in query:
        normal_aql = True
    return normal_aql

def process_input(query:str) -> None:

    # select * from events
    # offense_id: fields : groupby_fields
    bool_aql_query = True
    if check_aql(query):
        return {'baql': bool_aql_query, 'query': query}
    else:
        if query.startswith('rm') or query.startswith('note'):
            bool_aql_query = False
            return {'baql': bool_aql_query, 'query': query}
        else:
            try:
                if ":" in query:
                    offense_id, event_fields, groupby_fields = query.strip().split(":")
                else:
                    offense_id = query
                    event_fields = None
                    groupby_fields = None
                offense = q._get_offense_detail_(offense_id)
                output_query = define_query(offense_id, offense, event_fields,groupby_fields)
                print(output_query)
                return {'baql': bool_aql_query, 'query': output_query}
            except Exception as e:
                return {'baql': 'unk','query': query}
                # logging.log(logging.ERROR,f'{e}\nError in helper.py process_input()')
    

def define_query(offense_id:int,offense:dict,event_fields:str=None, groupby_fields:str=None) -> str:

    start_time = offense['start_time']
    last_time = offense['last_updated_time']
    if last_time == start_time:
        dt = datetime.datetime.fromtimestamp(last_time/1000)
        dt+=datetime.timedelta(seconds=1)
        last_time = int(dt.timestamp()*1000)

    if event_fields:
        if groupby_fields:
            query = f'SELECT DATEFORMAT("starttime", \'dd/MM/yyyy hh:mm:ss a\') as \'Start time\',LOGSOURCENAME(logsourceid) as \'Log Source\',sourceip as \'Source IP\', sourceport as \'Source Port\', destinationip as \'Dest IP\', destinationport as \'Destination Port\', {event_fields} FROM events WHERE INOFFENSE({offense_id}) GROUP BY {groupby_fields} START {start_time} STOP {last_time}'
        else:
            query = f'SELECT DATEFORMAT("starttime", \'dd/MM/yyyy hh:mm:ss a\') as \'Start time\',LOGSOURCENAME(logsourceid) as \'Log Source\',sourceip as \'Source IP\', sourceport as \'Source Port\', destinationip as \'Dest IP\', destinationport as \'Destination Port\', {event_fields} FROM events WHERE INOFFENSE({offense_id}) START {start_time} STOP {last_time}'

    else:
        if groupby_fields:
            query = f'SELECT DATEFORMAT("starttime", \'dd/MM/yyyy hh:mm:ss a\') as \'Start time\',LOGSOURCENAME(logsourceid) as \'Log Source\',sourceip as \'Source IP\', sourceport as \'Source Port\', destinationip as \'Dest IP\', destinationport as \'Destination Port\', {groupby_fields} FROM events WHERE INOFFENSE({offense_id}) GROUP BY {groupby_fields} START {start_time} STOP {last_time}'
        else:
            query = f'SELECT DATEFORMAT("starttime", \'dd/MM/yyyy hh:mm:ss a\') as \'Start time\',LOGSOURCENAME(logsourceid) as \'Log Source\',sourceip as \'Source IP\', sourceport as \'Source Port\', destinationip as \'Dest IP\', destinationport as \'Destination Port\' FROM events WHERE INOFFENSE({offense_id}) START {start_time} STOP {last_time}'
            #query = f'SELECT * FROM events WHERE INOFFENSE({offense_id}) START {start_time} STOP {last_time}'
        
    return query

def get_shell_type() -> str:
    # Check if the SHELL environment variable is set
    if 'SHELL' in os.environ:
        shell_path = os.environ['SHELL'].lower()

        if 'bash' in shell_path:
            return 'bash'
        elif 'powershell' in shell_path:
            return 'powershell'

    # Check if the COMSPEC environment variable is set
    if 'COMSPEC' in os.environ:
        return 'cmd'

    # Additional checks for PowerShell
    if 'PSModulePath' in os.environ:
        return 'powershell'

    return 'unknown'
        
def delete_files(dir:str) -> None:
    
    shell_type = get_shell_type()
    if shell_type == 'bash':
        # Bash Shell
        subprocess.run(['rm', '-f', f'{dir}/*.csv'])
    elif shell_type == 'cmd':
        # CMD (Command Prompt)
        subprocess.run(['cmd', '/c', 'del', '/Q', f'{dir}\\*.csv'])
    elif shell_type == 'powershell':
        # Alternatively, you can use PowerShell
        subprocess.run(['powershell', 'Remove-Item', '-Path', f'{dir}\\*.csv', '-Force'])
    else:
        print("Unsupported platform")
#process_input("130820")