import psycopg2
from messages_for_user import show_notification


class DataBase:
    def __init__(self, config):
        self.conn = None
        self.config = config
        self.load_last_char()

    def load_last_char(self):
        try:
            self.last_char = int(self.config['db_files']['last_char'])
        except:
            self.last_char = 0

    def save_last_char(self):
        self.config.set('db_files', 'last_char', str(self.last_char))
        with open('config.ini', 'w') as configfile:
            self.config.write(configfile)

    def connect_to_Db(self, dbname, user, password, host, port):
        try:
            self.conn = psycopg2.connect(
                dbname=dbname,
                user=user,
                password=password,
                host=host,
                port=port
            )
        except psycopg2.Error as e:
            show_notification(f"EROR: {e}")
        return self.conn

    def call_procedure_insert(self, procedure_name, ip_address, log_name, timestamp, request, status_code,
                              response_size):
        if self.conn is None:
            show_notification("Соединение с базой данных не установлено.")
            return
        with self.conn.cursor() as cur:
            try:
                cur.execute(
                    f"CALL {procedure_name}(%s, %s, %s, %s, %s, %s)",
                    (ip_address, log_name, timestamp, request, status_code, response_size)
                )
                self.conn.commit()
            except psycopg2.Error as e:
                show_notification(f"Ошибка при выполнении процедуры: {e}")

    def insert_to_log_table(self, path_to_log_file, procedure_name, pattern):
        try:
            with open(path_to_log_file, 'r', encoding="utf-8") as file:
                file.seek(self.last_char)
                lines = file.readlines()
                self.last_char = file.tell()
                self.save_last_char()
                for line in lines:
                    match = pattern.match(line)
                    if match:
                        log_data = match.groupdict()
                        ip = log_data['ip']
                        remLogName = log_data['remote_logname']
                        dateTime = log_data['datetime']
                        request = log_data['request']
                        status = log_data['status']
                        size = log_data['size']
                        self.call_procedure_insert(procedure_name, ip, remLogName,
                                                   dateTime, request, status, size)
                    else:
                        show_notification("Файл логов пуст!")
        except (psycopg2.Error, IndexError, FileNotFoundError) as e:
            show_notification(f"EROR: {e}")
