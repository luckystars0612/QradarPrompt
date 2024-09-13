from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.formatted_text import FormattedText
from prompt_toolkit.shortcuts import print_formatted_text, PromptSession
from prompt_toolkit.styles import Style
from prompt_toolkit.lexers import SimpleLexer
from pygments import highlight
from pygments.lexers.shell import BashLexer
from pygments.formatters import TerminalFormatter
import logging
import subprocess
import csv
import datetime
from helper import *
import sys
sys.path.insert(0, './model_bots')
from Qradar import Qradar


def run_oscommand(command:str):

    try:
    # Running the command with shell=True to allow piping
        result = subprocess.run(command, shell=True, capture_output=True, text=True, check=True)
        highlighted_output = highlight(result.stdout, BashLexer(), TerminalFormatter())
        print(highlighted_output)

    
    except subprocess.CalledProcessError as e:
        # This exception is raised if the command returns a non-zero exit status
        print_formatted_text(FormattedText([('ansired', f"Command failed with error:\n{e}")]))
        print_formatted_text(FormattedText([('ansired', f"Standard error:\n{e.stderr}")]))

    except Exception as e:
        # General exception handling for any other issues
        print_formatted_text(FormattedText([('ansired', f"An unexpected error occurred: {e}")]))
    
class PromtQradar(Qradar):

    def __init__(self) -> None:
        Qradar.__init__(self)
        self.fields = list()
    
    def get_fields_events(self) -> list:
        try:
            url = '/ariel/databases/events'
            response = self._search_(url)
            fields_name = []
            with open('utils/fields.txt', 'w') as file:
                for field in response['columns']:
                    if all(ord(char) < 128 for char in field['name']):
                        fields_name.append(field['name'])
                        file.write(field['name'] + '\n')
                file.close()
            return fields_name
        except Exception as e:
            logging.log(logging.ERROR,f'{e}\nError in utils.py get_fields_events()')

    def define_fields(self) -> list:
        return [line.strip() for line in open("utils/fields.txt", 'r')]

    def prompt(self) -> None:
        aql_fields = self.define_fields()
        aql_completer = WordCompleter(aql_fields, ignore_case=True)
        history = InMemoryHistory()
        style = Style.from_dict({
            'prompt': 'ansicyan bold',
            'input': 'ansigreen'
        })

        session = PromptSession(
            message=FormattedText([('class:prompt', '> ')]),
            completer=aql_completer,
            history=history,
            style=style,
            lexer=SimpleLexer(style='class:input')
        )

        while True:
            try:
                query = session.prompt()
                
                if query.lower() == 'exit':
                    break

                # Send the API request to QRadar
                query = process_input(query)
                self.run_query(query)
 
            except KeyboardInterrupt:
                break
            except EOFError:
                break
    
    def export_csv(self, data: list, filename: str = 'default') -> str:
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S")
        csv_file = f"results/{current_time}_{filename}.csv"

        # Extract keys for CSV header
        # if len(data) != 0:
        keys = data[0].keys()
        try:
            with open(csv_file, 'w', encoding='utf-8' ,newline='') as output_file:
                # Create a CSV writer object
                dict_writer = csv.DictWriter(output_file, fieldnames=keys)
                # Write the header
                dict_writer.writeheader()
                # Write the data
                dict_writer.writerows(data)
            return csv_file
        except Exception as e:
            logging.log(logging.ERROR,f'{e}\nError in utils.py export_csv()')

    def run_query(self,query:dict) -> None:
        
        if query['baql'] == True:
            response = self._ariel_search_(query['query'])
            # Write result to CSV file
            if response:
                file_name = self.export_csv(response, 'AQLSearch')
                print_formatted_text(FormattedText([('ansiblue', f"Search completed, result is saved to {file_name}")]))
            else:
                print_formatted_text(FormattedText([('ansired', "Wrong format query")]))
        elif query['baql'] == False:
            if query['query'] == 'rm':
                try:
                    delete_files("results")
                except Exception as e:
                    logging.log(logging.ERROR,f'{e}\nError in helper.py delete_files()')
            if query['query'].startswith('note'):
                try:
                    cmd,offense_id,note = query['query'].strip().split(':',2)
                    response = self._add_note_offense(offense_id,note)
                    if response:
                        print_formatted_text(FormattedText([('ansiblue', f"Note is added to offense {offense_id}")]))
                    else:
                        print_formatted_text(FormattedText([('ansired', f"Error on adding note to offense {offense_id}")]))
                except Exception as e:
                    logging.log(logging.ERROR,f'{e}\nError in utils.py run_query()')
        elif query['baql'] == 'unk':
            # print_formatted_text(FormattedText([('ansired', "Unknown format query or command")]))
            run_oscommand(query['query'])

a = PromtQradar()
a.prompt()