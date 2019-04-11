import os
import argparse
import datetime
import logging
import smtplib
import praw
from email.message import EmailMessage
from email.mime.image import MIMEImage
from email.headerregistry import Address

from templates import body_template


logger = logging.getLogger(__file__)
logger.setLevel(logging.DEBUG)
Formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
Handler = logging.FileHandler(os.path.join('bot.log'))
Handler.setFormatter(Formatter)
logger.addHandler(Handler)


def parse_args():
    """A helper function to parse command line arguments."""

    parser = argparse.ArgumentParser(description='Reddit submission daily highlights command line arguments')

    parser.add_argument('--reddit_config', metavar='CONFIG',  type=str, required=True, 
                        help='specify config section for Reddit config file, e.g. praw.ini')
    parser.add_argument('--subreddits', nargs='*', type=str, metavar='STRING', required=True, 
                        help='A list of subreddits')
    
    parser.add_argument('--limit', metavar='INT', type=int, default=10,
                        help='maximum num of posts per subreddit')
    parser.add_argument('--score', metavar='INT', type=int, default=50,
                        help='minimun score on a particular submission')
    parser.add_argument('--num_comments', metavar='INT', type=int, default=20,
                        help='minimun num of comments on a particular submission')

    parser.add_argument('--from_address', type=str, metavar='EMAIL', required=True, 
                        help='email addr from which to send contents')
    parser.add_argument('--from_address_pass', type=str, metavar='EMAIL_PASS', required=True, 
                        help='password for email addr from which to send contents')
    parser.add_argument('--to_address', nargs='*', type=str, metavar='EMAIL', required=True, 
                        help='email addr to which to send contents')

    args = parser.parse_args()
    logger.debug(args)

    return args


def get_reddit_posts(subreddits, limit, score, num_comments):
    """Collect submissions related data, including title, link, current score, the number of comments, etc.
    
    Params:
    -------
    subreddits: list
        a list of praw.Reddit.subreddit instances
    limit: int
        maximum number of submissions per subreddit
    score: int
        the minimal threshold of *score* 
    num_comments: int
        the minimal threshold of *number of comments*
    
    Return:
    -------
    data: dict
        all the submissions related data
    
    """
    
    data = {}
    for subreddit in subreddits:
        data[subreddit.display_name] = []
        for submission in subreddit.hot(limit=limit):
            if (submission.stickied is False) and (submission.score >= score or submission.num_comments >= num_comments):
                post = {}
                post['title'] = submission.title
                post['shortlink'] = submission.shortlink
                post['score'] = submission.score
                post['num_comments'] = submission.num_comments
                data[subreddit.display_name].append(post)
    
    return data


def create_email_message(from_address, to_address, subject, body):
    """Create a EmailMessage object for sending emails.
    
    Params:
    -------
    from_address: string
        a sending email address
    to_address: list of string
        a list of receiving email addresses
    subject: string
        email subject
    body: string
        email body
    
    Return:
    -------
    msg: EmailMessage
        a email message ready to send via smtp
    """
    
    msg = EmailMessage()
    msg['From'] = from_address
    msg['To'] = to_address
    msg['Subject'] = subject
    
    msg.add_alternative(body, subtype='html')
    
    with open('logo.png', 'rb') as img:
        msg.get_payload()[0].add_related(img.read(), 'image', 'jpeg', cid='logo')

    return msg


if __name__ == '__main__':
    args = parse_args()
    
    reddit = praw.Reddit(args.reddit_config)
    subreddits = [reddit.subreddit(subreddit) for subreddit in args.subreddits]
    data = get_reddit_posts(subreddits, args.limit, args.score, args.num_comments)
    logger.debug('Reddit submissions fetched.')
    
    mail_user, mail_domain = args.from_address.split('@')
    mail_host = "smtp." + mail_domain
    mail_pass = args.from_address_pass
    
    from_address = Address(mail_user, mail_user, mail_domain)
    to_address = [Address(e.split('@')[0], e.split('@')[0], e.split('@')[1]) for e in args.to_address]
    now = datetime.datetime.now().strftime('%Y-%m-%d')
    subject = f'Reddit Daily Digest ({now})'

    msg = create_email_message(
        from_address=from_address,
        to_address=to_address,
        subject=subject,
        body=body_template.render(data=data)
    )

    # Sends the emails
    with smtplib.SMTP_SSL(mail_host, 465) as smtp_server:
        smtp_server.login(mail_user, mail_pass)
        smtp_server.send_message(msg)

    logger.debug('Email sent successfully.')