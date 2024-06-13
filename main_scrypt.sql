-- Создание главной таблицы куда будут сохраняться логи из файла
create table apache_logs (
	id_apache_logs bigserial not null constraint pk_apache_logs PRIMARY KEY,
	ip_address inet not null,
	logname text not null,
	time_log timestamptz not null,
	first_line text not null,
	status_code smallint not null,
	response_size text not null
);

-- Функция для изменения формата даты полученной из файла логов Apache
CREATE OR REPLACE FUNCTION format_log_date(p_log_date text)
RETURNS text AS $$
DECLARE
  v_date_part text;
  v_time_part text;
  v_tz_part text;
BEGIN
  v_date_part := substring(p_log_date, 2, 20);
  v_time_part := substring(v_date_part, 1, 17);
  v_tz_part := substring(v_date_part, 19, 6);
  RETURN v_date_part || ' ' || v_tz_part;
END;
$$ LANGUAGE plpgsql;


-- Процедура на добавление данных в таблицу
CREATE OR REPLACE PROCEDURE apache_logs_insert(
  p_ip_address text, 
  p_logname text, 
  p_time_log text, 
  p_first_line text, 
  p_status_code text, 
  p_response_size text
)
LANGUAGE plpgsql
AS $$
DECLARE
  v_formatted_time_log text;
BEGIN
  v_formatted_time_log := format_log_date(p_time_log);
  INSERT INTO apache_logs(
    ip_address, 
    logname, 
    time_log, 
    first_line, 
    status_code, 
    response_size
  )
  VALUES (
    p_ip_address::inet, 
    p_logname, 
    to_timestamp(v_formatted_time_log, 'DD/Mon/YYYY:HH24:MI:SS TZH')::timestamptz, 
    p_first_line, 
    p_status_code::smallint, 
    p_response_size
  );
END;
$$;

-- Просмотр данных в таблице логов Apache
select * from apache_logs;
-- Полная очистка таблицы
DELETE FROM apache_logs;
-- "Сброс счётчика id_apache_logs", дабы счёт вёлся с 1 
ALTER SEQUENCE apache_logs_id_apache_logs_seq RESTART WITH 1;

-- Создание роли в базе данных с доступом к таблице и к процедуре добавления данных в таблицу
create role log_adder with login password 'Pa$$w0Rd';
grant insert, update, delete on table apache_logs to log_adder;
grant usage, select on sequence apache_logs_id_apache_logs_seq to log_adder;
grant execute on procedure apache_logs_insert to log_adder;

-- Создание роли в базе данных с доступом только на просмотр данных
create role api_getter with login password 'Pa$$w0Rd';
grant select on table apache_logs to api_getter;

