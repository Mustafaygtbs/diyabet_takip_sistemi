# database/connection.py
import psycopg2
import psycopg2.extras
from psycopg2 import pool

class DatabaseConnection:
   __instance = None
   __connection_pool = None
   
   @staticmethod
   def get_instance():
       if DatabaseConnection.__instance is None:
           DatabaseConnection()
       return DatabaseConnection.__instance
   
   def __init__(self):
       if DatabaseConnection.__instance is not None:
           raise Exception("Bu bir Singleton sınıftır, get_instance() metodunu kullanın!")
       else:
           DatabaseConnection.__instance = self
           self.db_config = {
               'host': 'localhost',
               'database': 'diabetes_monitoring',
               'user': 'postgres',
               'password': 'mustafa',
               'port': 5432,
               'client_encoding': 'UTF8' 
           }
           self.init_connection_pool()
   
   def init_connection_pool(self, min_connections=1, max_connections=10):
       try:
           self.__connection_pool = pool.ThreadedConnectionPool(
               min_connections,
               max_connections,
               **self.db_config
           )
           print("Veritabanı bağlantı havuzu başlatıldı")
           return True
       except (Exception, psycopg2.Error) as error:
           print("Veritabanı bağlantı havuzu oluşturulurken hata:", error)
           return False    
   
   def get_connection(self):
       try:
           connection = self.__connection_pool.getconn()
           if connection:
               return connection
       except (Exception, psycopg2.Error) as error:
           print("Veritabanı bağlantısı alınırken hata:", error)
       return None
   
   def release_connection(self, connection):
       try:
           self.__connection_pool.putconn(connection)
       except (Exception, psycopg2.Error) as error:
           print("Veritabanı bağlantısı serbest bırakılırken hata:", error)
   
   def close_all_connections(self):
       try:
           if self.__connection_pool:
               self.__connection_pool.closeall()
               print("Tüm veritabanı bağlantıları kapatıldı")
       except (Exception, psycopg2.Error) as error:
           print("Veritabanı bağlantıları kapatılırken hata:", error)
   
   def execute_query(self, query, params=None, fetch=True):
       """
       SQL sorgusu çalıştırır ve sonuçları döndürür.
       
       :param query: Çalıştırılacak SQL sorgusu
       :param params: Sorgu parametreleri (tuple, dict veya list)
       :param fetch: Sonuçları çekme (True) veya sadece çalıştırma (False)
       :return: Sorgu sonuçları veya etkilenen satır sayısı
       """
       connection = None
       cursor = None
       try:
           connection = self.get_connection()
           cursor = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
           cursor.execute(query, params)
           
           if fetch:
               result = cursor.fetchall()
               return result
           else:
               connection.commit()
               return cursor.rowcount
       except (Exception, psycopg2.Error) as error:
           if connection:
               connection.rollback()
           print("Sorgu çalıştırılırken hata:", error)
           raise
       finally:
           if cursor:
               cursor.close()
           if connection:
               self.release_connection(connection)
   
   def execute_batch(self, query, params_list):
       """
       Toplu SQL sorgusu çalıştırır.
       
       :param query: Çalıştırılacak SQL sorgusu şablonu
       :param params_list: Her sorgu için parametreler listesi
       :return: Etkilenen satır sayısı
       """
       connection = None
       cursor = None
       try:
           connection = self.get_connection()
           cursor = connection.cursor()
           psycopg2.extras.execute_batch(cursor, query, params_list)
           connection.commit()
           return cursor.rowcount
       except (Exception, psycopg2.Error) as error:
           if connection:
               connection.rollback()
           print("Toplu sorgu çalıştırılırken hata:", error)
           raise
       finally:
           if cursor:
               cursor.close()
           if connection:
               self.release_connection(connection)
   
   def execute_values(self, query, params_list):
       """
       Çoklu değer ekleme SQL sorgusu çalıştırır.
       
       :param query: Çalıştırılacak SQL sorgusu şablonu
       :param params_list: Eklenecek değerler listesi
       :return: Etkilenen satır sayısı
       """
       connection = None
       cursor = None
       try:
           connection = self.get_connection()
           cursor = connection.cursor()
           psycopg2.extras.execute_values(cursor, query, params_list)
           connection.commit()
           return cursor.rowcount
       except (Exception, psycopg2.Error) as error:
           if connection:
               connection.rollback()
           print("Çoklu değer eklenirken hata:", error)
           raise
       finally:
           if cursor:
               cursor.close()
           if connection:
               self.release_connection(connection)
   
   def test_connection(self):
       """
       Veritabanı bağlantısını test eder.
       
       :return: Bağlantı başarılı ise True, değilse False
       """
       connection = None
       cursor = None
       try:
           connection = self.get_connection()
           cursor = connection.cursor()
           cursor.execute("SELECT version();")
           version = cursor.fetchone()
           print("PostgreSQL versiyonu:", version)
           return True
       except (Exception, psycopg2.Error) as error:
           print("Veritabanı bağlantısı test edilirken hata:", error)
           return False
       finally:
           if cursor:
               cursor.close()
           if connection:
               self.release_connection(connection)