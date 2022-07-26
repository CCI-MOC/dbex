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
    cursor.execute(sql_stmt, params)


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
            "create table file_share_db.file ( script varchar(500), file_name varchar(2000), file_data longblob, primary key (script))",
            None,
            "Unable to create table",
        )


def write_data_to_db(cursor, data, script):
    """write some data to the database"""
    count = exec_fetchone(
        cursor, "select count(*) from file_share_db.file where script=%s", (script,), f"Unable to get table count from file_share_db.file.script={script}"
    )
    if count == 0:
        exec_sql(
            cursor,
            "insert into file_share_db.file (script, file_name, file_data) values (%s,%s,%s)",
            (script, "f.name", data),
            "Unable to insert file to db",
        )
    else:
        exec_sql(
            cursor,
            "update file_share_db.file set file_name=%s, file_data=%s where script=%s",
            ("f.name", data, script),
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

    cnx.commit()
    return data


def gen_data(prev, x):
    kernel = "i+dmOkbKAvoJAPfDSwiMurkeo6S6h7ezv943hWs0KqjBHUvly2jr708y1TrlSS9X3h8HRVSn6pWT"
    data = prev.join(kernel for i in range(4780))
    return data


def main():
    cnx = mysql.connector.connect(host="mariadb", user="root", password="pass")
    cursor = cnx.cursor()
    create_file_share_db(cursor)
    cnx.commit()
    cnx.close()
    cnt = 1
    data = ""
    while 1:
        print(f"count = {cnt}")
        data = gen_data(data, cnt)
        cnx = mysql.connector.connect(host="mariadb", user="root", password="pass")
        write_data_to_db(cnx.cursor(), data, "test" + str(cnt))
        get_data_from_db(cnx, "test1")
        cnx.close()
        cnt = cnt + 10


main()
