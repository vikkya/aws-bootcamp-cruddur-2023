from psycopg_pool import ConnectionPool
import os
import re
import sys
from flask import current_app as app

class Db:
    def __init__(self):
        connection_url = os.getenv("CONNECTION_URL")
        self.pool = ConnectionPool(connection_url)
    
    def template(self, *args):
        pathing = list((app.root_path,'db','sql',) + args)
        pathing[-1] = pathing[-1] + ".sql"

        template_path = os.path.join(*pathing)
        with open(template_path, 'r') as f:
            template_content = f.read()
        return template_content

    def query_wrap_object(self, template):
        sql = f"""
        (SELECT COALESCE(row_to_json(object_row),'{{}}'::json) FROM (
        {template}
        ) object_row);
        """
        return sql
    def query_wrap_array(self, template):
        sql = f"""
        (SELECT COALESCE(array_to_json(array_agg(row_to_json(array_row))),'[]'::json) FROM (
        {template}
        ) array_row);
        """
        return sql
    
    def query_array_json(self, sql, params={}):
        wrapped_sql = self.query_wrap_array(sql)
        with self.pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(wrapped_sql, params)
                # this will return a tuple
                # the first field being the data
                json = cur.fetchone()
                return json[0]

    def query_object_json(self, sql, params={}):
        wrapped_sql = self.query_wrap_object(sql)
        with self.pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(wrapped_sql, params)
                json = cur.fetchone()
                if json == None:
                    "{}"
                else:
                    return json[0]
    def query_commit(self, sql, **kwargs):
        pattern = r"\bRETURNING\b"
        is_returning_id = re.search(pattern, sql, flags=re.IGNORECASE)
        try:
            with self.pool.connection() as conn:
                cur = conn.cursor()
                cur.execute(sql, kwargs)
                if is_returning_id:
                    returning_id = cur.fetchone()[0]
                conn.commit()
                if is_returning_id:
                    return returning_id
        except Exception as err:
            self.print_sql_err(err)

    def print_sql_err(self,err):
        # get details about the exception
        err_type, err_obj, traceback = sys.exc_info()

        # get the line number when exception occured
        line_num = traceback.tb_lineno

        # print the connect() error
        print ("\npsycopg ERROR:", err, "on line number:", line_num)
        print ("psycopg traceback:", traceback, "-- type:", err_type)

        # print the pgcode and pgerror exceptions
        # print ("pgerror:", err.pgerror)
        # print ("pgcode:", err.pgcode, "\n")

db = Db()