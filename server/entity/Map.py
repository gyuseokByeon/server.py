""" Game map entity
"""
import sqlite3
from .Line import Line
from .Point import Point
from .Serializable import Serializable
import json
import os
PATH_MAP_DB = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'db', 'map.db')

class Map(Serializable):
    """ Map of game space
    """
    def __init__(self, name=None):
        self.okey = False
        if name is None:
            return # empty map
        try:
            connection = sqlite3.connect(PATH_MAP_DB)
            cur = connection.cursor()
            cur.execute('select id from map where name=?', (name, ))
            self.idx = cur.fetchone()[0]
            self.name = name
            self.line = []
            cur.execute('select id, len, p0, p1'
                        ' from line'
                        ' where map_id=?'
                        ' order by id', (self.idx,))
            for row in cur.fetchall():
                self.line.append(Line(row[0], row[1], row[2], row[3]))
            self.point = []
            cur.execute('select id, post_id'
                        ' from point'
                        ' where map_id=?'
                        ' order by id', (self.idx,))
            for row in cur.fetchall():
                post_id = row[1]
                if post_id == 0:
                    self.point.append(Point(row[0]))
                else:
                    self.point.append(Point(row[0], post_id=post_id))
            connection.close()
            self.okey = True
        except sqlite3.Error as e:
            print("An error occurred:", e.args[0])


    def from_json_str(self, string_data):
        data = json.loads(string_data)
        self.idx = data[u"idx"]
        self.name = data[u"name"]
        lines = data[u"line"]
        self.line = []
        for line in lines:
            self.line.append(Line(line[u"idx"],
                                  line[u"length"],
                                  line[u"point"][0],
                                  line[u"point"][1]))
        self.point = []
        points = data[u"point"]
        for p in points:
            if u"post_id" in p.keys():
                self.point.append(Point(p[u"idx"],
                                        post_id=p[u"post_id"]))
            else:
                self.point.append(Point(p[u"idx"]))
        self.okey = True