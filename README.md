__python email manager__

The python email manager is a programmed designed to help read and manage large volumes of template emails - think automated IT reports or site diagnostics. The general idea is to automatically retrieve emails through the gmail api, parse for information given specific keywords, and store the data in an easy-to-read format. 

This library contains two main classes: email_scraper and email_parser, as well as a manager class which combines the two. 

- email_scraper handles email retrieval and decryption. When an instance is created, it uses the gmail api to sign the user into their account. given a query in gmail query syntax (https://support.google.com/mail/answer/7190?hl=en), it will download all messages matching that query and decode them into a readable string format. 
- email_parser reads messages and looks for user-provided keywords. when it finds a keyword, it stores the data from the following line. when reading a batch of emails, it stores the information from each email as a row in a pandas dataframe 
- email_manager uses the previous two classes, and also contains methods to save itself and data from pervious sessions as a .pickle object. this allows users to maintain a long-term database of relevent information which can be easily updated. 

This project is still in development and may contain bugs. The google app used for the api is still private and requires approval for new users to join. 
