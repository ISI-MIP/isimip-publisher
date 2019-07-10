import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from isimip_publisher.utils import order_dict
from isimip_publisher.utils.checksum import get_checksum

from isimip_publisher.database.models import Base, File


def init_database_session():
    engine = create_engine(os.getenv('DATABASE'))

    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    return Session()


def insert_file(config, session, metadata, file):
    # filter metadata according to config
    metadata = order_dict({key: value for key, value in metadata.items() if key in list(config['db_metadata'])})
    file = File(
        name=os.path.basename(file),
        path=file,
        checksum=get_checksum(file),
        attributes=metadata
    )
    session.add(file)
