import psycopg2
import aiopg


from dbconfig import dsn
from dbconnection import connection, cursor


async def get_user_id(username):
    try:
        pool = await aiopg.create_pool(dsn)
        async with pool.acquire() as connection:
            async with connection.cursor() as cursor:
                get_user_id_sql = "select user_id from users where username=%s"
                await cursor.execute(get_user_id_sql, (username,))
                user_id = await cursor.fetchone()
    except (Exception, psycopg2.Error) as error:
        print("psycopg2 error: ", error)
    finally:
        if (connection):
            cursor.close()
            connection.close()
            if (user_id is None):
                return -1
            else:
                return user_id[0]
        else:
            return -1


async def is_user_admin(user_id, workspace_id):
    try:
        pool = await aiopg.create_pool(dsn)
        async with pool.acquire() as connection:
            async with connection.cursor() as cursor:
                is_user_admin_sql = "select * from workspace_users where user_id=%s " \
                            "and workspace_id=%s and is_admin=True"
                await cursor.execute(is_user_admin_sql, (user_id, workspace_id))
                count = cursor.rowcount
                # print(count)
    except (Exception, psycopg2.Error) as error:
        print("psycopg2 error: ", error)
        count = 0
    finally:
        if (connection):
            cursor.close()
            connection.close()
            return count
        else:
            return 0


async def get_workspace_id(workspace):

    try:
        pool = await aiopg.create_pool(dsn)
        async with pool.acquire() as connection:
            async with connection.cursor() as cursor:
                get_workspace_id_sql = "select workspace_id from workspaces where name=%s"
                await cursor.execute(get_workspace_id_sql, (workspace,))
                workspace_id = await cursor.fetchone()


    except (Exception, psycopg2.Error) as error:
        print("psycopg2 error: ", error)
    finally:
        if (connection):
            cursor.close()
            connection.close()
            if (workspace_id is None):
                return -1
            else:
                return workspace_id[0]
        else:

            return -1
