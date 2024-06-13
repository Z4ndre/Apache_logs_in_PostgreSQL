from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import and_, func
from sqlalchemy.dialects.postgresql import INET, TIMESTAMP
from datetime import datetime
import configparser

app = Flask(__name__)
config = configparser.ConfigParser()
config.read('config.ini')

db_name = config['DataBase']['dbname']
user = config['DataBase']['user']
password = config['DataBase']['password']
host = config['DataBase']['host']
port = config['DataBase']['port']


app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{user}:{password}@{host}:{port}/{db_name}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Data(db.Model):
    __tablename__ = 'apache_logs'
    id_apache_logs = db.Column(db.BigInteger, primary_key=True)
    ip_address = db.Column(INET, nullable=False)
    logname = db.Column(db.String)
    time_log = db.Column(TIMESTAMP(timezone=True), nullable=False)
    first_line = db.Column(db.String)
    status_code = db.Column(db.SmallInteger)
    response_size = db.Column(db.String)


@app.route('/get_all_info', methods=['GET'])
def get_all_info():
    ip_address = request.args.get('ip_address')
    status_code = request.args.get('status_code')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    group_by_ip = request.args.get('group_by_ip', 'false').lower() == 'true'

    filters = []

    if ip_address:
        filters.append(Data.ip_address == ip_address)

    if status_code:
        filters.append(Data.status_code == status_code)

    if start_date:
        try:
            start_date = datetime.strptime(start_date, '%d/%b/%Y')
            filters.append(Data.time_log >= start_date)
        except ValueError:
            return jsonify({'Ошибка': 'Неверный формат начальной даты. Используйте dd/MMM/yyyy.'}), 400

    if end_date:
        try:
            end_date = datetime.strptime(end_date, '%d/%b/%Y')
            filters.append(Data.time_log <= end_date)
        except ValueError:
            return jsonify({'Ошибка': 'Неверный формат конечной даты. Используйте dd/MMM/yyyy.'}), 400

    query = db.session.query(Data)
    if group_by_ip:
        query = query.with_entities(
            Data.ip_address,
            func.count(Data.id_apache_logs).label('count'),
            func.min(Data.time_log).label('first_seen'),
            func.max(Data.time_log).label('last_seen')
        ).group_by(Data.ip_address)

    if filters:
        query = query.filter(and_(*filters))
    try:
        results = query.all()
    except Exception as e:
        return jsonify({'Ошибка': 'Ошибка связана с базой данных: ' + str(e)}), 500
    return jsonify([{'id': log.id_apache_logs, 'ip_address': log.ip_address, 'log_name': log.logname,
                         'timestamp': log.time_log, 'request': log.first_line, 'status_code': log.status_code,
                         'response_size': log.response_size} for log in results]) if not group_by_ip else jsonify(
        [{'ip_address': result.ip_address, 'count': result.count, 'first_seen': result.first_seen,
          'last_seen': result.last_seen} for result in results])


if __name__ == '__main__':
    host = config['Api']['host']
    port = int(config['Api']['port'])
    app.run(host=host, port=port, debug=True)

