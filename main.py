#python 
#isaac murphy 
import local, argparse, sys, pickle

usage = f'utility program for reading template emails\n\
            {sys.argv[0]}\n'

parser = argparse.ArgumentParser(usage = usage)
subparsers = parser.add_subparsers(dest='mode',
                                 help='train and test a model or test a pretrained one, \
                                consult the online help of each particular mode for more information')

init_parser = subparsers.add_parser('init')#to run once during setup 
init_parser.add_argument("--query", type=str, default = 'in:inbox', help = 'query to search for emails. must match gmail query syntax (https://support.google.com/mail/answer/7190?hl=en)')
init_parser.add_argument('--keywords', type = str, default = 'Subject', help= 'keywords to search for in emails. multiple keywords must be seperated by commas')
init_parser.add_argument('--save_as', type = str, default = 'email_manager.pickle', help='file name to save email manager as after initializing. default = email_manager.pickle')

update_parser = subparsers.add_parser('update')#to run for an update
update_parser.add_argument("--query", type=str, default = 'in:inbox', help = 'query to search for emails. must match gmail query syntax (https://support.google.com/mail/answer/7190?hl=en)')
update_parser.add_argument('--save_as', type = str, default = 'email_manager.pickle', help='file name to save email manager as after initializing. default = email_manager.pickle')
update_parser.add_argument('--load_from', type = str, default = 'email_manager.pickle', help='file to load an existing manager from')

args = parser.parse_args()

if args.mode == 'init':
    targets = [arg.strip() for arg in args.keywords.split(',')]
    manager = local.mail_manager(*targets)
    manager(query=args.query)
    #todo: what data to display? 
    manager.save(args.save_as)

elif args.mode == 'update': 
    with open(args.load_from, 'rb') as infile: 
        manager = pickle.load(infile)
    manager(args.query)
    manager.save(args.save_as)
    


