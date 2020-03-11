from sqlalchemy import create_engine, engine_from_config, \
     MetaData, Table, Column, Integer, String, DateTime, \
     Boolean, ForeignKey, ForeignKeyConstraint, Float, Time, Date, UniqueConstraint, \
     not_, and_, or_, select, join, outerjoin, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from sqlalchemy.dialects.mysql import BIGINT, BINARY, \
    BOOLEAN, BIT, CHAR, DATE, DATETIME, DECIMAL, FLOAT, \
    INTEGER, NCHAR, NUMERIC, NVARCHAR,REAL, SMALLINT, \
    TEXT, TIME, TIMESTAMP, TINYINT, VARBINARY, VARCHAR

metadata=MetaData()

#defines the database structure
artefact_types=Table('artefact_types', metadata,
                     Column('id', INTEGER(11), primary_key=True, autoincrement=True, unique=True),
                     Column('name', VARCHAR(45), nullable=False, unique=True),
                     mysql_engine='InnoDB')
                     
body_part=Table('body_part', metadata,
                     Column('id', INTEGER(11), primary_key=True, autoincrement=True, unique=True),
                     Column('name', VARCHAR(45), nullable=False, unique=True),
                     mysql_engine='InnoDB')

laterality=Table('laterality', metadata,
                     Column('id', INTEGER(11), primary_key=True, autoincrement=True, unique=True),
                     Column('direction', VARCHAR(15), nullable=False, unique=True),
                     mysql_engine='InnoDB')

patients=Table('patients', metadata,
                     Column('id', INTEGER(11), primary_key=True, autoincrement=True, unique=True),
                     Column('name', VARCHAR(15), nullable=False, unique=True),
                     mysql_engine='InnoDB')

positions=Table('positions', metadata,
                     Column('id', INTEGER(11), primary_key=True, autoincrement=True, unique=True),
                     Column('position', VARCHAR(45), nullable=False, unique=True),
                     mysql_engine='InnoDB')

studies=Table('studies', metadata,
                     Column('id', INTEGER(11), primary_key=True, autoincrement=True, unique=True),
                     Column('patient_id', INTEGER(11), ForeignKey("patients.id"), nullable=False),
                     Column('study_uid', VARCHAR(75), nullable=False, unique=True),
                     mysql_engine='InnoDB')

images=Table('images', metadata,
                     Column('image_uid', VARCHAR(75), primary_key=True, unique=True),
                     Column('study_id', INTEGER(11), ForeignKey("studies.id"), nullable=False),
                     Column('position_id', INTEGER(11), ForeignKey("positions.id"), nullable=False),
                     Column('laterality_id', INTEGER(11), ForeignKey("laterality.id"), nullable=False),
                     Column('body_part_imaged_id', INTEGER(11), ForeignKey("body_part.id"), nullable=False),
                     Column('implant_in_header', BOOLEAN, nullable=False),
                     mysql_engine='InnoDB')

image_artefacts=Table('image_artefacts', metadata,
                     #Having 2 pks makes a unique constraint across two columns. Could also specify the unique
                     #across both using indexes, but that leaves a unique 'id' column that needs to be auto-incremented
                     #which is 1) slower and 2) if something tries to get inserted but fails (duplicate) then id
                     #still auto-increments
                     #https://weblogs.sqlteam.com/jeffs/2007/08/23/composite_primary_keys/
                     Column('image_uid', VARCHAR(75), ForeignKey("images.image_uid"), nullable=False, primary_key=True), 
                     Column('artefact_id', INTEGER(11), ForeignKey("artefact_types.id"), nullable=False, primary_key=True),                     
                     mysql_engine='InnoDB')
