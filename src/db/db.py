# Copyright 2009 - 2011 Burak Sezer <purak@hadronproject.org>
# 
# This file is part of lpms
#  
# lpms is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#   
# lpms is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#   
# You should have received a copy of the GNU General Public License
# along with lpms.  If not, see <http://www.gnu.org/licenses/>.

import sqlite3
import cPickle as pickle

import lpms
from lpms.db import skel

class PackageDatabase:
    def __init__(self, db_path):
        self.db_path = db_path
        try:
            self.connection = sqlite3.connect(self.db_path)
        except sqlite3.OperationalError:
            lpms.terminate("lpms could not connected to the database(%s)" % self.db_path)

        self.cursor = self.connection.cursor()
        table = self.cursor.execute('select * from sqlite_master where type = "table"')
        if table.fetchone() is None:
            self.initialize_db()

    def initialize_db(self):
        tablelist = self.cursor.execute('select * from sqlite_master where type="table"')
        tablelist = self.cursor.fetchall()
        content = []
        for i in tablelist:
            content += list(i)

        # get list of tables and drop them
        for t in content:
            try:
                self.cursor.execute('drop table %s' % (t,))
            except sqlite3.OperationalError:
                # skip, can not drop table...
                continue
        self.cursor.executescript(skel.schema(self.db_path))

    def commit(self):
        return self.connection.commit()

    def get_repos(self):
        self.cursor.execute('''select repo from metadata''')
        return set(self.connection.fetchall())

    def add_pkg(self, data, commit=True):
        repo, category, name, version, summary, homepage, _license, src_url, options = data
        if not self.pkg_is_exists(repo, category, name):
            self.cursor.execute('''insert into metadata values (?, ?, ?, ?, ?, ?, ?, ?, ?)''', (
                repo, category, name, version, summary, homepage, _license, src_url, options))
        if commit:
            self.commit()

    def pkg_is_exists(self, rname, category, name):
        if (rname, category, name) in self.find_pkg(name):
            return True
        return False

    def find_pkg(self, name):
        self.cursor.execute('''select repo, category, name, version from metadata where name=(?)''', (name,))
        return self.cursor.fetchall()

    def get_metadata(self, keyword, repo, category, name):
        self.cursor.execute('''select %s from metadata where repo=(?) and category=(?) and name=(?)''' 
                % keyword, (repo, category, name,))
        return self.cursor.fetchone()

    def get_all_names(self, repo=None):
        if repo is not None:
            self.cursor.execute('''select repo, category, name from metadata where repo=(?)''', (repo,))
        else:
            self.cursor.execute('''select repo, category, name from metadata''')
        return self.cursor.fetchall()

    def drop(self, rname, category=None, name=None):
        if category is None and name is None:
            self.cursor.execute('''delete from metadata where %s=(?)''' % "repo", (rname,))
        else:
            self.cursor.execute('''delete from metadata where %s=(?) and %s=(?) and %s=(?)''' 
                    % ("repo", "category", "name"), (rname, category, name,))
        self.commit()

    def add_depends(self, data):
        for __data in data:
            repo_name, category, name, build, runtime = __data
            if self.get_depends(repo_name, category, name) is not None:
                continue
            self.cursor.execute('''insert into depends values (?, ?, ?, ?)''', 
                    (repo_name, category, name, 
                    sqlite3.Binary(pickle.dumps(build, 1)),
                    sqlite3.Binary(pickle.dumps(runtime, 1))
                    ))
        self.commit()

    def get_depends(self, _type, repo_name, category, name):
        for deps in self.cursor.execute('''select %s from depends where repo=(?) and category=(?) and name=(?)''' % _type,
                (repo_name, category, name,)):
            return pickle.loads(deps[0])
