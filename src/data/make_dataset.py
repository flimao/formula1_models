# -*- coding: utf-8 -*-
import os
import subprocess as sbp
import click
import logging
from pathlib import Path
# import requests
from sqlalchemy import create_engine, text, URL
import sqlparse
from dotenv import find_dotenv, load_dotenv
from tqdm import tqdm


@click.command()
@click.argument('input_filepath', type = click.Path(exists=True))
@click.argument('output_filepath', type = click.Path())
@click.argument('db_filename',
                    type = click.Path(file_okay=True),
                    default = Path('f1db.sql.gz')
                )
def main(input_filepath, output_filepath, db_filename):
    """ Runs data processing scripts to turn raw data from (../raw) into
        cleaned data ready to be analyzed (saved in ../processed).
    """
    logger = logging.getLogger(__name__)
    logger.info('making final data set from raw data')

    # download
    logger.info('downloading Ergast F1 DB')
    cmd_str = rf'wget -N -P {input_filepath} https://ergast.com/downloads/{db_filename}'
    sbp.run(cmd_str, shell = True)

    # extract
    logger.info('extracting Ergast F1 DB from file')
    cmd_str = rf'gunzip -k {Path(input_filepath, db_filename)}'
    cmd_str += rf' && mv -f {Path(input_filepath, db_filename.with_suffix(""))} {output_filepath}'
    sbp.run(cmd_str, shell = True)
    sql_script_fn = Path(output_filepath, db_filename.with_suffix(""))

    # load MySQL dump onto DB
    dbname = os.getenv("ERGASTF1_DB_NAME")
    logger.info(f"Populating MySQL database '{dbname}'")
    db_url = URL.create(
        'mysql+pymysql',
        username = os.getenv("ERGASTF1_DB_USERNAME"),
        password = os.getenv("ERGASTF1_DB_PASSWORD"),
        host = os.getenv("ERGASTF1_DB_HOSTNAME"),
        database = dbname,
    )

    # first reset database
    ergast_engine = create_engine(db_url, echo = False)
    with ergast_engine.connect() as ergastdb:
        ergastdb.execute(text(f"DROP DATABASE IF EXISTS {dbname};"))
        ergastdb.execute(text(f"CREATE DATABASE {dbname};"))

    # load queries
    ergast_engine = create_engine(db_url, echo = False)
    with ergast_engine.connect() as ergastdb:
        with open(sql_script_fn, 'r') as scriptobj:
            script = scriptobj.read()
            queries = sqlparse.split(
                sqlparse.format(script, strip_comments = False)
            )
            for query in tqdm(queries, desc = 'SQL Statements'):
                ergastdb.execute(text(query))


if __name__ == '__main__':
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    # not used in this stub but often useful for finding various files
    project_dir = Path(__file__).resolve().parents[2]

    # find .env automagically by walking up directories until it's found, then
    # load up the .env entries as environment variables
    load_dotenv(find_dotenv())

    main()
