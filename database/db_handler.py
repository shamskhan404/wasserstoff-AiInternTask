from sqlalchemy import create_engine, Column, Integer, String, Text, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

Base = declarative_base()

class Email(Base):
    __tablename__ = 'emails'
    id = Column(String, primary_key=True)
    sender = Column(String)
    recipient = Column(String)
    subject = Column(String)
    body = Column(Text)
    timestamp = Column(String)
    processed = Column(Boolean, default=False)
    in_reply_to = Column(String, ForeignKey('emails.id'), nullable=True)
    thread_id = Column(String, nullable=True)  # To group emails in a thread
    has_attachment = Column(Boolean, default=False) # To indicate if an email has attachments

    replies = relationship("Email", backref="parent", remote_side=[id])

engine = create_engine('sqlite:///emails.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

def store_email(email_data):
    session = Session()

    valid_keys = ['id', 'sender', 'recipient', 'subject', 'body', 'timestamp', 'in_reply_to', 'thread_id', 'has_attachment']
    filtered_data = {k: v for k, v in email_data.items() if k in valid_keys}
    email = Email(**filtered_data)
    session.merge(email)
    session.commit()
    session.close()


def get_latest_unprocessed_email():
    session = Session()
    email = session.query(Email).filter_by(processed=False).order_by(Email.timestamp).first()
    session.close()
    if email:
        return {
            'id': email.id,
            'sender': email.sender,
            'recipient': email.recipient,
            'subject': email.subject,
            'body': email.body,
            'timestamp': email.timestamp,
            'in_reply_to': email.in_reply_to,
            'thread_id': email.thread_id,
            'has_attachment': email.has_attachment
        }
    return None

def mark_email_as_processed(email_id):
    session = Session()
    email = session.query(Email).filter_by(id=email_id).first()
    if email:
        email.processed = True
        session.commit()
    session.close()

def store_attachment_info(email_id, has_attachment):
    session = Session()
    email = session.query(Email).filter_by(id=email_id).first()
    if email:
        email.has_attachment = has_attachment
        session.commit()
    session.close()