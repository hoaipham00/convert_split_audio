from tinydb import TinyDB, Query, where
from tinydb.middlewares import CachingMiddleware
from tinydb.storages import JSONStorage
from termcolor import colored


# database_connection_string = '/home/lenovo/Desktop/convert_audio_2/audio_metadata/audio_info.json'
# database = ''
# table = ''
class AudioMetadata():
    def __init__(self, database, table, database_connection_string):
        self.database = database
        self.table = table
        self.database_connection_string = database_connection_string
        self.db_connection = TinyDB(self.database_connection_string)
        self.audio_query = Query()

    def get_all(self, page):
        try:
            offset = page*10 -1 
            limit = 10
            if(page == 0):
                offset = 0
            result = self.db_connection.search(self.audio_query.is_visible == True)
            total_record = len(self.db_connection)
            return result[offset:offset + limit], total_record
        except Exception as error:
            print('Cannot get docs cause ' + repr(error))
        
    def get_by_id(self, id):
        try:
            result = self.db_connection.search(self.audio_query.id == id)
            return result
        except Exception as error:
            print('Cannot get docs by id cause ' + repr(error))
        
    def get_by_multiple_fields(self, fields_dict):
        try:
            result = []
            page = fields_dict['page']
            offset = page*10 - 1
            limit = 10
            if(page == 0):
                offset = 0
            if(fields_dict['name'] is not None and fields_dict['owner'] is None):
                result = self.db_connection.search(self.audio_query.name == fields_dict['name'])
                result = [x for x in result if x['is_visible'] == True]

            if(fields_dict['owner'] is not None and fields_dict['name'] is None):
                result = self.db_connection.search(self.audio_query.owner == fields_dict['owner'])
                result = [x for x in result if x['is_visible'] == True]

            if (fields_dict['owner'] is None and fields_dict['name'] is None):
                result = self.db_connection.all()
                result = [x for x in result if x['is_visible'] == True]

            if (fields_dict['owner'] is not None and fields_dict['name'] is not None):
                result = self.db_connection.search(self.audio_query.name == fields_dict['name'])
                result = [x for x in result if x['owner'] == fields_dict['owner'] and x['is_visible'] == True]

            total_record = len(result)
            return result[offset:offset+ limit], total_record
        except Exception as error:
            print('Cannot search by fields cause ' + repr(error))

    def insert_to_db(self, data):
        try:
            self.db_connection.insert(data)
        except Exception as error:
            print('Cannot insert to db cause ' + repr(error))

    def update_to_db(self, data):
        try:
            id = data.get('id')
            self.db_connection.update(data, self.audio_query.id == id)
        except Exception as error:
            print('Cannot update to db cause ' + repr(error)) 

    def delete_to_db(self, id):
        try:
            list_search = self.db_connection.search(self.audio_query.id == id)
            # for audio in list_search:
            #     audio['is_visible'] = False
            self.db_connection.update({'is_visible': False},  self.audio_query.id == id)

        except Exception as error:
            print('Cannot delete cause ' + repr(error)) 

    
