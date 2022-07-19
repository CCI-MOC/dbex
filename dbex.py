#!/usr/bin/python3
import os
import sys
import argparse
import json
import pprint
import mysql.connector

# define the database
# Add data


def exec_sql(cursor, sql_stmt, params, error_msg):
    """executes a simple sql statement"""
    try:
        cursor.execute(sql_stmt, params)
    except Exception as err:
        print(f"{str(err)} \n {error_msg}")
        sys.exit()


def exec_fetchall(cursor, sql_stmt, params, error_msg):
    """executes the sql statmement and fetches all in a list"""
    exec_sql(cursor, sql_stmt, params, error_msg)
    try:
        result = cursor.fetchall()
    except Exception as err:
        print(f"{str(err)} \n {error_msg}")
        sys.exit()
    return result


def exec_fetchone(cursor, sql_stmt, params, error_msg):
    """executes the sql stmt and fetches the first one in the result list"""
    exec_sql(cursor, sql_stmt, params, error_msg)
    try:
        result = cursor.fetchone()
    except Exception as err:
        print(f"{str(err)} \n {error_msg}")
        sys.exit()
    if result:
        return result[0]
    else:
        return None


def create_file_share_db(cursor):
    """As a work-a-round for RWM, share config files though the database"""
    count = exec_fetchone(
        cursor, "select count(*) from information_schema.tables where table_schema='file_share_db'", None, f"Unable to get table count from file_share_db"
    )
    if count < 1:
        exec_sql(cursor, "drop database if exists file_share_db", None, "Unable to drop database")
        exec_sql(cursor, "create database file_share_db default character set 'utf8'", None, "Unable to create database")
        exec_sql(
            cursor,
            "create table file_share_db.file ( script varchar(500), file_name varchar(2000), file_data blob, primary key (script))",
            None,
            "Unable to create table",
        )


def write_data_to_db(cursor, script):
    """write some data to the database"""
    text_data = "The quick brown fox jumped over the lazy dog."

    count = exec_fetchone(
        cursor,
        "select count(*) from file_share_db.file where script=%s",
        (script,),
        f"Unable to get table count from file_share_db.file.script={script}",
    )
    if count == 0:
        exec_sql(
            cursor,
            "insert into file_share_db.file (script, file_name, file_data) values (%s,%s,%s)",
            (script, "f.name", text_data),
            "Unable to insert file to db",
        )
    else:
        exec_sql(
            cursor,
            "update file_share_db.file set file_name=%s, file_data=%s where script=%s",
            ("f.name", text_data, script),
            "Unable to update file to db",
        )


def get_data_from_db(cnx, script):
    """As a work-a-round for RWM, share config files though the database"""
    print(f"get {script} from database")
    cursor = cnx.cursor()

    print(f"select file_name, file_data from file_share_db.file where script='{script}'")
    data = exec_fetchall(
        cursor,
        "select file_name, file_data from file_share_db.file where script=%s",
        (script,),
        "Unable to select file from db",
    )
    print("{script} -> {data[0][1]")
    if data and isinstance(data, list):
        rec = data[0]
        with open(rec[0], "wb+") as fp:
            fp.write(rec[1])

    cnx.commit()


def main():
    cnx = mysql.connector.connect(host="mariadb", user="root", password="pass")
    cursor = cnx.cursor()
    create_file_share_db(cursor)
    write_data_to_db(cursor, "test1")
    cnx.commit()
    cnx.close()

    while 1:
        cnx = mysql.connector.connect(host="mariadb", user="root", password="pass")
        get_data_from_db(cnx.cursor(), "test1")
        cnx.close()
