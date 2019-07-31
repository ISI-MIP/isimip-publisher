import logging
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from isimip_publisher.database.models import Base, Dataset, File

from isimip_publisher.utils import order_dict
from isimip_publisher.utils.checksum import get_checksum, get_checksum_type

logger = logging.getLogger(__name__)


def init_database_session():
    engine = create_engine(os.getenv('DATABASE'))

    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    return Session()


def insert_file(session, metadata, file_path, version):
    name = os.path.basename(file_path)
    checksum = get_checksum(file_path)
    checksum_type = get_checksum_type()
    attributes = order_dict(metadata)

    # check if the file is already in the database
    file = session.query(File).filter(File.path == file_path, File.version == version).one_or_none()

    if file:
        if file.checksum == checksum:
            # the file has not change update row
            if file.attributes != attributes:
                file.attributes = attributes
                logger.debug('update %s', name)
            else:
                logger.debug('skip %s', name)

        else:
            # the file has been changed, but the version is the same, this is not ok
            raise RuntimeError('%s has been changed but the version is the same' % name)
    else:
        # insert a new row for this file
        logger.debug('insert file %s', name)
        file = File(
            name=name,
            version=version,
            path=file_path,
            checksum=checksum,
            checksum_type=checksum_type,
            attributes=attributes
        )
        session.add(file)


def insert_dataset(session, dataset_name, dataset_files, version):

    dataset = session.query(Dataset).filter(Dataset.name == dataset_name, Dataset.version == version).one_or_none()

    if dataset:
        raise RuntimeError('A dataset with the name %s and the version %s already exists' % (dataset_name, version))
    else:
        # insert a new row for this file
        logger.debug('insert dataset %s', dataset_name)
        dataset = Dataset(
            name=dataset_name,
            version=version,
            attributes={}
        )
        session.add(dataset)
        session.commit()

        for dataset_file in dataset_files:
            logger.debug('update file %s with dataset_id=%s', dataset_file, dataset.id)
            file = session.query(File).filter(File.name == dataset_file, File.version == version)
            file.dataset_id = dataset.id

        session.commit()
