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
                limit = limit - 1
            result = sorted(self.db_connection.all()[offset:offset + limit], key=lambda k: k['id'])
            return result
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
                limit = limit - 1
                
            if(fields_dict['name'] is not None or fields_dict['owner'] is not None):
                for name in fields_dict['name']:
                    result_names = self.db_connection.search(self.audio_query.name == name)
                    result = result + result_names
                for owner in fields_dict['owner']:
                    result_owner = self.db_connection.search(self.audio_query.owner== owner)
                    result = result + result_owner
            else:
                result = self.db_connection.all()
            return result[offset:offset+ limit]
        except Exception as error:
            print('Cannot search by fields cause ' + repr(error))

    def insert_to_db(self, data):
        try:
            self.db_connection.insert(data)
        except Exception as error:
            print('Cannot insert to db cause ' + repr(error))

    def update_to_db(self, data):
        try:
            self.db_connection.update(data)
        except Exception as error:
            print('Cannot update to db cause ' + repr(error)) 

    def delete_to_db(self, data):
        try:
            id = data.get('id')
            self.db_connection.remove(where('id') == id)
        except Exception as error:
            print('Cannot delete cause ' + repr(error)) 

# if __name__ == '__main__':

#     db_metadata_audio = AudioMetadata(database, table, database_connection_string)
#     print(colored("..............................................................", "white"))
#     print(colored("Please wait.....", "green"))
#     print(colored("..............................................................", "green"))
#     data = {'int': 6, 'char': 'd'}


#     fields_dict = {'name': ['a'], 'owner': ['suonghoang', 'haodo']}
#     result = db_metadata_audio.get_by_id('bc3ae13d-8c3f-4614-a26b-4c4fb8b9128a')
#     print(result)
    # for i in result:
    #     print(i)

#     print(colored("..............................................................", "green"))
#     print(colored('Completed','green'))
#     print(colored("..............................................................", "white"))

    
