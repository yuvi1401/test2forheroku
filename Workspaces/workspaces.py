import asyncio

import psycopg2
from flask import send_file
from cryptography.fernet import Fernet
from werkzeug import secure_filename

from Utils.db_ops import get_workspace_id, get_user_id, is_user_admin
from dbconfig import user, password, database


def delete_workspace(delete_request):
    connection = None
    workspace_deleted = False
    res = {}

    deleted_by = delete_request['deleted_by']
    workspace = delete_request['workspace']
    loop = asyncio.new_event_loop()
    workspace_id = loop.run_until_complete(get_workspace_id(workspace))

    loop = asyncio.new_event_loop()
    deleted_by_id = loop.run_until_complete(get_user_id(deleted_by))

    try:
        if (workspace_id == -1 | deleted_by_id == -1):
            res['error'] = 'Could not locate workspace or user deleting the workspace'
        else:
            connection = psycopg2.connect(
                user=user,
                password=password,
                database=database)
            cursor = connection.cursor()

            loop = asyncio.new_event_loop()
            admin_status = loop.run_until_complete(is_user_admin(deleted_by_id, workspace_id))

            if (admin_status == 0):
                res['error'] = 'User is not an admin of the workspace'
            else:
                delete_workspace_sql = "delete from workspaces where workspace_id=%s"
                cursor.execute(delete_workspace_sql, (workspace_id,))
                connection.commit()
                count = cursor.rowcount

                if (count != 0):

                    workspace_deleted = True

    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgreSQL", error)

        res['error'] = error


    finally:
        # closing database connection.
        if (connection):
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")

        res['workspace_deleted'] = workspace_deleted
        return res


def update_admin(workspace, admin_request):
    workspace_admin_updated = False
    connection = None

    res = {}

    username = admin_request['username']
    admin_username = admin_request['admin_username']
    make_admin = admin_request['make_admin']

    loop = asyncio.new_event_loop()
    workspace_id = loop.run_until_complete(get_workspace_id(workspace))

    loop = asyncio.new_event_loop()
    user_id = loop.run_until_complete(get_user_id(username))

    loop = asyncio.new_event_loop()
    admin_id = loop.run_until_complete(get_user_id(admin_username))

    try:

        if (workspace_id == -1 | admin_id == -1 | user_id == -1):
            res['error'] = 'Invalid input. Check username, admin and workspace are correct'
        else:
            connection = psycopg2.connect(
                user=user,
                password=password,
                database=database)
            cursor = connection.cursor()

            loop = asyncio.new_event_loop()
            admin_status = loop.run_until_complete(is_user_admin(admin_id, workspace_id))

            if (admin_status == 0):
                res['error'] = 'Admin is not actual admin of workspace'
            else:
                if (make_admin == 'True'):
                    make_admin_bool = True;
                else:
                    make_admin_bool = False;

                update_admin_sql = "update workspace_users set is_admin=%s where workspace_id=%s" \
                                   "and user_id=%s"
                cursor.execute(update_admin_sql, (make_admin_bool, workspace_id, user_id))
                connection.commit()
                count = cursor.rowcount
                if (count == 0):
                    res['error'] = 'Could not make user as admin'
                else:
                    workspace_admin_updated = True

    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgreSQL", error)
        res['error'] = str(error)

    finally:
        # closing database connection.
        if (connection):
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")


        res['workspace_admin_updated'] = workspace_admin_updated
        return res


def create_workspace_only(data):

    res = {}
    workspace_added = False
    connection = None


    try:
        workspace_name = data['name']
        admin = data['admin'];
        loop = asyncio.new_event_loop()
        admin_id = loop.run_until_complete(get_user_id(admin))


        if (admin_id == -1):

            res['error'] = 'Could not find user in the system so cannot add workspace for user'
        else:
            connection = psycopg2.connect(
                user=user,
                password=password,
                database=database)

            insert_workspace_name = "insert into workspaces (name) values (%s) returning workspace_id"

            cursor = connection.cursor()
            cursor.execute(insert_workspace_name, (workspace_name,))

            connection.commit()
            count = cursor.rowcount
            if (count == 0):
                res['error'] = 'Could not add workspace into the system'
            else:
                new_workspace_id = cursor.fetchone()[0]
                admin_added = add_user_to_workspace([admin_id], new_workspace_id, True)

                if (admin_added != 0):
                    workspace_added = True

                else:
                    res['error'] = 'Workspace created but could not set admin. Contact support'

    except (Exception, psycopg2.Error) as error:
        print('Error while conecting to PostgresQL', error)
        res['error'] = error
    finally:

        if (connection):
            # close the connection and the cursor
            cursor.close()
            connection.close()
            print("PostgresSQL connection is closed")

        res['workspace_added'] = workspace_added

        return res


def create_workspace_with_users(data):
    users = data['users'];
    admin = data['admin'];
    workspace = data['name'];

    res = {}
    users_added = False
    connection = None


    try:
        connection = psycopg2.connect(
            database=database)

        cursor = connection.cursor()

        insert_workspace_sql = "insert into workspaces (name) values (%s) " \
                               "returning workspace_id"
        cursor.execute(insert_workspace_sql, (workspace,))

        connection.commit()

        count = cursor.rowcount
        if (count == 0):
            res['error'] = 'Could not create the workspace'
        else:
            new_workspace_id = cursor.fetchone()[0]
            loop = asyncio.new_event_loop()
            admin_id = loop.run_until_complete(get_user_id(admin))
            admin_added = add_user_to_workspace([admin_id], new_workspace_id, True);
            if (admin_added == 0):
                res['error'] = 'Workspace added but could not set admin to workspace.'
            else:
                user_id_list = []
                for user in users:
                    loop = asyncio.new_event_loop()
                    single_user_id = loop.run_until_complete(get_user_id(user['username']))
                    user_id_list.append(single_user_id)
                users_added = add_user_to_workspace(user_id_list, new_workspace_id);

                if (users_added != len(users)):
                    res['error'] = 'Some users could not be added to workspace. Try again'
                else:
                    users_added = True

    except (Exception, psycopg2.Error) as error:
        print('Error while conecting to PostgresQL', error)
        res['error'] = str(error)
    finally:
        if (connection):
            # close the connection and the cursor
            cursor.close()
            connection.close()
            print("PostgresSQL connection is closed")

        res['users_added'] = users_added
        return res


def add_user_to_workspace(list_of_ids, workspace_id, is_admin=False):
    try:
        connection = psycopg2.connect(
            user=user,
            password=password,
            database=database)

        cursor = connection.cursor()
        insert_user_to_workspace_sql = "insert into workspace_users (user_id, workspace_id, is_admin) " \
                                       "values (%s,%s,%s) returning user_id"

        count = 0
        for user_id in list_of_ids:
            if (user_id != -1):
                cursor.execute(insert_user_to_workspace_sql, (user_id, workspace_id, is_admin))
                connection.commit()
                count += cursor.rowcount

    except (Exception, psycopg2.Error) as error:
        print('Error while connecting to PostgresQL', error)
        return 0
    finally:
        if (connection):
            # close the connection and the cursor
            cursor.close()
            connection.close()
            print("PostgresSQL connection is closed")

    return 'workspace added'

    return count


def delete_user_from_workspace(data):
    res = {}
    user_deleted = False
    connection = None

    try:
        # check if admin_username is the same as the workspace_admins
        username = data['username']
        admin_username = data['admin_username']
        workspace_name = data['workspace_name']

        connection = psycopg2.connect(
            user=user,
            password=password,
            database=database)

        cursor = connection.cursor()
        select_user = "select user_id from users where username = (%s)"
        cursor.execute(select_user, [username])
        user_id = cursor.fetchone()
        count = cursor.rowcount
        if (count == 0):
            res["error"] = "User does not exist in the system"
        else:
            cursor.execute(select_user, [admin_username])
            admin_id = cursor.fetchone()
            count = cursor.rowcount
            if (count == 0):
                res["error"] = "Admin does not exist in the system"
            else:
                select_workspace_id = "select workspace_id from workspaces where name = (%s)"
                cursor.execute(select_workspace_id, [workspace_name])
                workspace_id = cursor.fetchone()
                count = cursor.rowcount
                if (count == 0):
                    res["error"] = "Workspace does not exist in the system"

                else:
                    select_admin_boolean = "select is_admin from workspace_users where user_id = (%s) and workspace_id = (%s)"
                    cursor.execute(select_admin_boolean, (admin_id, workspace_id))
                    admin_boolean = cursor.fetchone()
                    count = cursor.rowcount
                    if (count == 0) | (not admin_boolean):
                        res["error"] = "Given admin is not actual admin of workspace"
                    else:
                        delete_user = "delete from workspace_users where user_id =(%s) and workspace_id = (%s)"
                        cursor.execute(delete_user, (user_id, workspace_id))
                        connection.commit()
                        count = cursor.rowcount
                        if (count != 0):
                            user_deleted = True
                        else:
                            res["error"] = "Could not remove user from workspace"


    except (Exception, psycopg2.Error) as error:
        print('Error while conecting to PostgresQL', error)

        res['error'] = str(error)

    finally:

        if (connection):
            # close the connection and the cursor
            cursor.close()
            connection.close()
            print("PostgresSQL connection is closed")
        res["user_deleted_from_workspace"] = user_deleted
        return res


def encrypt_file(f):
    f.save(secure_filename(f.filename))

    try:

        key = 'rfCFW5NYIJq5qWBLW_bXwHeg4z0PwVM9MDssLtQ-T4o='
        print(key)

        connection = psycopg2.connect(
            database='ssc'
        )
        cursor = connection.cursor()
        filename = secure_filename(f.filename)

        print(filename)
        with open(filename, 'rb') as f:
            file = f.read()

            print(file)

            fernet = Fernet(key)
            encrypted = fernet.encrypt(file)
            print(encrypted)

        with open('S3/new_encrypted_file', 'wb') as f:
            f.write(encrypted)

        # save encrypted_file to S3

    except (Exception, psycopg2.Error) as error:
        print('Error while conecting to PostgresQL', error)

    finally:

        if (connection):
            # close the connection and the cursor
            cursor.close()
            connection.close()
            print("PostgresSQL connection is closed")

    return 'encrypted'


def decrypt_file(data):
    filename = data['filename']
    print(filename)

    try:

        key = 'rfCFW5NYIJq5qWBLW_bXwHeg4z0PwVM9MDssLtQ-T4o='
        print(key)

        connection = psycopg2.connect(
            database='ssc'
        )
        cursor = connection.cursor()
        # filename = secure_filename(f.filename)

        with open('S3/downloads/' + filename, 'rb') as f:
            file = f.read()

            print(file)

            fernet = Fernet(key)
            decrypted = fernet.decrypt(file)
            print(decrypted)

        with open('new_decrypted_file', 'wb') as f:
            f.write(decrypted)

        # with open('new_decrypted_file', 'rb') as f:
        #     decrypted_file = f.read()

    except (Exception, psycopg2.Error) as error:
        print('Error while conecting to PostgresQL', error)

    finally:

        if (connection):
            # close the connection and the cursor
            cursor.close()
            connection.close()
            print("PostgresSQL connection is closed")

    return send_file('new_decrypted_file')


def fetch_workspace_files(name):

    list_of_files = []
    res = {}
    connection = None

    try:
        connection = psycopg2.connect(
            database="ssc")

        cursor = connection.cursor()
        if (name == None):
            res["error"] = "Workspace name is invalid"
        else:
            loop = asyncio.new_event_loop()
            workspace_id = loop.run_until_complete(get_workspace_id(name))
            if (workspace_id == -1):
                res["error"] = "Workspace name is invalid"
            else:
                cursor.execute("""SELECT file_name FROM workspace_files
                       INNER JOIN workspaces ON workspaces.workspace_id = workspace_files.workspace_id
                       WHERE workspaces.workspace_id = %s
                       """, (workspace_id,))

                workspace_files = cursor.fetchall()

                for row in workspace_files:
                    list_of_files.append(
                        {'file_name': row[0]})

    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgreSQL", error)
        res["error"] = error
    finally:
        # closing database connection.
        if (connection):
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")
        if ((len(list_of_files) == 0) & ("error" not in res)):
            res["error"] = "There are no files in this workspace"
        res["files"] = list_of_files
        return res

