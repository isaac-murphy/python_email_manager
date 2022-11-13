#python 
#isaac murphy 

from __future__ import print_function

import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

#for reading emails 
import base64, email 
from bs4 import BeautifulSoup
from collections import defaultdict
import pandas as pd

#to save objects
import pickle 

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']


class mail_scraper():
    '''an object that fetches and decodes emails through gmail api'''

    def __init__(self):
        self.creds = None
        if os.path.exists('token.json'):
            self.creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                self.creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.json', 'w') as token:
                token.write(self.creds.to_json())
        #build the relevent service (gmail api)
        try:
            self.service = build('gmail', 'v1', credentials=self.creds)
        except HttpError as error:
            # TODO(developer) - Handle errors from gmail API.
            print(f'An error occurred: {error}')               

    def fetch(self, query:str):
        self.emails = []
        results = self.service.users().messages().list(userId = 'me', q = query).execute()
        #print('==DEBUG: ', results['messages'])
        for message in results['messages']: 
            self.emails.append(self._decode(message['id']))
        #self.emails.append(results)


    def _decode(self, message_id):
        message = self.service.users().messages().get(userId='me', id=message_id).execute()
        #print('eeeeeeeeDEBUG: ', message.keys())
        payload = message['payload']
        #print('eeeeeDEBUG ', payload.keys())
        headers = payload['headers']
        #print('++DEBUG: ', len(payload))
        #get subject and sender name 
        for d in headers:
            if d['name'] == 'Subject':
                subject = d['value']
            if d['name'] == 'From':
                sender = d['value']

        # The Body of the message is in Encrypted format. So, we have to decode it.
        # Get the data and decode it with base 64 decoder.
        #print('++DEBUG: ', len(payload.get('parts')))
        message_body = ''
        body = payload.get('body')
        if body['size'] > 0: #if the message body is not empty
            body_text = body['data']
            body_text = body_text.replace("-","+").replace("_","/") #prepare for decoding
            body_text = base64.b64decode(body_text) #decode 
            body_text = BeautifulSoup(body_text, 'lxml') #parse into readible format and extract text 
            body_text = body_text.text
            message_body+='\n'+body_text
            #print('body taxt\n', body_text)
        
        #need to get 'parts' from email if the email was forwarded
        if payload.get('parts'):
            parts_text = payload.get('parts')[0]['body']['data']
            parts_text = parts_text.replace("-","+").replace("_","/")
            parts_text = base64.b64decode(parts_text)
            parts_text = BeautifulSoup(parts_text, 'lxml')
            parts_text = parts_text.text
            message_body += '\n' + parts_text
            #print('fwd: \n', parts_text)
        
        return (f'{subject}\n{sender}\n{message_body}')


class mail_parser():
    ''' a parser for emails. constructed with any number of keywords, it can parse a message to 
    return the lines of text which start with one of the keywords
    currently functional for gmail format emails. may struggle with email sent from other apps due 
    to different formatting (specifically: mail for windows app)'''

    def __init__(self, *target_words):
        self.targets = target_words

    def extract_line(self, message, keyword):
        return message[message.find(keyword):message.find('\r', message.find(keyword))]

    def extract_without_keyword(self, message, keyword):
        line = ''
        try: line = (self._split_snip(self.extract_line(message, keyword)))[1]
        except: print('error parsing keyword: ', keyword)
        return line

    def parse(self, message:str):
        lines = [self.extract_without_keyword(message, arg) for arg in self.targets]
        return lines
        
    def read_to_df(self, messages:list):
        data    = [self.parse(message) for message in messages]
        df      = pd.DataFrame(columns = self.targets, data = data)
        return df
        

    def _split_snip(self, snip:str):
        
        key = snip[:snip.find(':')]
        content = snip[snip.find(':')+1:].strip()

        return key, content

class mail_manager(): 
    '''a manager class to handle a parser and a scraper. will be able to save itself in json format'''

    def __init__(self, *parser_args): 
        self.p_args = [arg for arg in parser_args]
        self.scraper    = mail_scraper()
        self.parser     = mail_parser(*self.p_args)
        self.saved_data = pd.DataFrame(columns=parser_args)

    def get_emails(self, query): 
        return self.scraper.fetch(query = query)
    
    def read_emails(self, email_list): 
        return self.parser.read_to_df(email_list)

    def update(self, df): 
        self.saved_data = pd.merge(self.saved_data, df, how = 'outer')

    def __call__(self, query):
        self.get_emails(query)
        #print('downloaded and decoded: ', self.scraper.emails)
        df = self.read_emails(self.scraper.emails)
        print('new data\n', df)
        self.update(df)

    def save(self, filename): 
        '''saves the object as a pickle file'''
        with open(filename, 'wb') as outfile:
            pickle.dump(self, outfile)




