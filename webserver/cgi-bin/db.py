
import sqlite3
import time
import calendar

class Entry:
	'''A class to be entered into a database, subclass and use the
	Database function save to add a record of that object to a table.'''
	
	_subclass_map = {}
	
	def __init__(self):
		self._id = -1
		self._created_at = 0
		self._updated_at = 0
	
	def _key(self):
		return self.__class__.__name__ + " " + str(self._id)
	
	def _variables(self):
		def viable(n):
			return len(n) and n[0] != '_'
		return filter( viable, dir(self) )
	
	def _is_pointer(self, value):
		return value == None or isinstance(value, Entry)
		
	def _evaluate(self, n):
		value = getattr(self, n)
		if value == None:
			value = ''
		if self._is_pointer(value):
			if isinstance(value, Entry):
				value = value._key()
			else:
				value = ''
		return value
	
	def _values(self):
		variables = self._variables()
		return map(self._evaluate, variables)
	
	def _value_dict(self):
		variables = self._variables()
		values = self._values()
		D = dict(zip(variables, values))
		D['id'] = self._id
		return D
	
	def _elements(self):
		l = []
		for n in self._variables():
			value = getattr(self, n)
			tp = type(value)
			if tp==int:
				l.append(n + ' integer')
			if tp==long:
				l.append(n + ' bigint')
			elif tp == str:
				l.append(n + ' text')
			elif tp == float:
				l.append(n + ' real')
			elif self._is_pointer(value):
				l.append(n + ' text')
		return l


def add_entry_subclass(new_class):
	Entry._subclass_map[new_class.__name__] = new_class



class Database:
	'''Represents a .db database file.  Has Functions for opening
	and closing the file and for saving, loading and deleting objects.'''
	
	_debug_mode = False
	
	def open(self, path):
		self.connection = sqlite3.connect(path)
		self.cursor = self.connection.cursor()
		self.object_map = {}
		if self._debug_mode:
			print 'open\n'
	
	
	def execute(self, command, parameters=()):
		try:
			result = None
			if parameters == ():
				if self._debug_mode:
					print command
				result = self.cursor.execute(command)
			else:
				if self._debug_mode:
					print command, parameters
				result = self.cursor.execute(command, parameters)
			
			if self._debug_mode:
				print ''
			return result
		except:
			if self._debug_mode:
				print 'FAILED'
	
	
	def _rebuild_table(self, entry):
		# To be implemented
		pass
	
	
	def _elements_in_table(self, entry):
		# read in the variables table
		self.execute('select * from ' + entry._table_name + '_variables')
		
		# make a list of elements in the table (already in the database) and in the entry.
		elements = []
		for vname, vtype in self.cursor:
			elements.append( vname + ' ' + vtype )
		return elements
	
	
	def _update_elements(self, entry):
		self.execute('create table if not exists ' + entry._table_name + '_variables (name text, type text)')
		self.execute('create table if not exists ' + entry._table_name + ' (id integer, created_at integer, updated_at integer)')
		
		elements_in_table = self._elements_in_table(entry)
		elements_in_entry = entry._elements()
		
		if elements_in_table == elements_in_entry:
			return
		
		self.execute('delete from ' + entry._table_name + '_variables')
		for e in entry._elements():
			self.execute('insert into ' + entry._table_name + '_variables' + ' values ("' + '","'.join(e.split()) + '")')
		
		# determine variables that need to be created or deleted (new/trash)
		def brand_new(e):
			return e not in elements_in_table
		
		def trash(e):
			return e not in elements_in_entry
		
		elements_trash = filter(trash, elements_in_table)
		elements_new = filter(brand_new, elements_in_entry)
		
		# delete the ones that are trash
		# (or maybe not, actually)
		if elements_trash:
			self._rebuild_table(entry);
		
		# add missing elements
		for e in elements_new:
			self.execute('alter table ' + entry._table_name + ' add ' + e)
	
	
	def save(self, entry_list):
		if isinstance(entry_list, Entry):
			entry_list = [entry_list]
		
		for entry in entry_list:
			self._update_elements(entry)
			
			variables = entry._variables()
			values = entry._values()
			
			# check that all members are either primitive or have ids
			bail = False
			for v in variables:
				value = getattr(entry, v)
				if entry._is_pointer(value) and value and value._id <= 0:
					if self._debug_mode:
						print "ERROR: entry saved, but not all its entry members have valid ids"
					bail = True
			if bail:
				continue
			
			# if id is non-positive, this is a new entry, and we insert, else we update.
			if entry._id <= 0:
				# get an id one more than the maximum id or 1.
				entry._id = 0
				self.execute("select max(id) from " + entry._table_name)
				for i in self.cursor:
					entry._id = i[0] or 0
					break
				entry._id += 1
				entry._created_at = calendar.timegm(time.gmtime())
				entry._updated_at = entry._created_at
				
				variables_tuple = ('id', 'created_at', 'updated_at') + tuple(variables)
				values_tuple = (entry._id, entry._created_at, entry._updated_at) + tuple(values)
				command = 'insert into ' + entry._table_name
				command += ' (' + ','.join(variables_tuple) + ')'
				command += ' values (' + ','.join(len(values_tuple) * ['?']) + ')'
				
				self.execute(command, values_tuple)
			else:
				command = 'update ' + entry._table_name + ' set '
				i = 0
				entry._updated_at = calendar.timegm(time.gmtime())
				setlines = ['updated_at = ' + str(entry._updated_at)]
				for v in variables:
					setlines.append(v + '=?')
					i+=1
				command += ', '.join(setlines) + ' where id = ' + str(entry._id)
				self.execute(command, values)
			
			self.object_map[entry._key()] = entry
	
	
	def load(self, entry_class, criteria=''):
		entry = entry_class()
		
		self._update_elements(entry)
		
		found = []
		if criteria:
			criteria = ' where ' + criteria
		
		self.execute('select ' + ', '.join(['id', 'created_at', 'updated_at'] + entry._variables()) + ' from ' + entry_class._table_name + criteria)
		
		tuples = []
		for t in self.cursor:
			tuples.append(t)
		
		for t in tuples:
			entry = entry_class()
			entry._id = t[0]
			entry._created_at = t[1]
			entry._updated_at = t[2]
			
			key = entry._key()
			if self.object_map.has_key(key):
				entry = self.object_map[key]
			else:
				i = 3
				for v in entry._variables():
					if entry._is_pointer(getattr(entry, v)):
						p = t[i].split()
						if len(p) > 1:
							for x in self.load(Entry._subclass_map[p[0]], 'id = ' + p[1]):
								setattr(entry, v, x)
					else:
						setattr(entry, v, type(getattr(entry, v))(t[i]))
					i += 1
				self.object_map[key] = entry
			found.append(entry)
		return found
	
	
	def delete(self, entry):
		self.execute('delete from ' + entry._table_name + ' where id = ' + str(entry._id))
	
	
	def close(self):
		self.cursor.close()
		self.connection.commit()
		if self._debug_mode:
			print 'close'

