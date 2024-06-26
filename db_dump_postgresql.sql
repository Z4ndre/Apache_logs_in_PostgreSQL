PGDMP                      |            practice_spring    16.2    16.2     �           0    0    ENCODING    ENCODING        SET client_encoding = 'UTF8';
                      false            �           0    0 
   STDSTRINGS 
   STDSTRINGS     (   SET standard_conforming_strings = 'on';
                      false            �           0    0 
   SEARCHPATH 
   SEARCHPATH     8   SELECT pg_catalog.set_config('search_path', '', false);
                      false            �           1262    51969    practice_spring    DATABASE     �   CREATE DATABASE practice_spring WITH TEMPLATE = template0 ENCODING = 'UTF8' LOCALE_PROVIDER = libc LOCALE = 'Russian_Russia.1251';
    DROP DATABASE practice_spring;
                postgres    false            �            1255    52014 6   apache_logs_insert(text, text, text, text, text, text) 	   PROCEDURE     �  CREATE PROCEDURE public.apache_logs_insert(IN p_ip_address text, IN p_logname text, IN p_time_log text, IN p_first_line text, IN p_status_code text, IN p_response_size text)
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
 �   DROP PROCEDURE public.apache_logs_insert(IN p_ip_address text, IN p_logname text, IN p_time_log text, IN p_first_line text, IN p_status_code text, IN p_response_size text);
       public          postgres    false            �           0    0 �   PROCEDURE apache_logs_insert(IN p_ip_address text, IN p_logname text, IN p_time_log text, IN p_first_line text, IN p_status_code text, IN p_response_size text)    ACL     �   GRANT ALL ON PROCEDURE public.apache_logs_insert(IN p_ip_address text, IN p_logname text, IN p_time_log text, IN p_first_line text, IN p_status_code text, IN p_response_size text) TO log_adder;
          public          postgres    false    217            �            1255    52015    format_log_date(text)    FUNCTION     l  CREATE FUNCTION public.format_log_date(p_log_date text) RETURNS text
    LANGUAGE plpgsql
    AS $$
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
$$;
 7   DROP FUNCTION public.format_log_date(p_log_date text);
       public          postgres    false            �            1259    51994    apache_logs    TABLE       CREATE TABLE public.apache_logs (
    id_apache_logs bigint NOT NULL,
    ip_address inet NOT NULL,
    logname text NOT NULL,
    time_log timestamp with time zone NOT NULL,
    first_line text NOT NULL,
    status_code smallint NOT NULL,
    response_size text NOT NULL
);
    DROP TABLE public.apache_logs;
       public         heap    postgres    false            �           0    0    TABLE apache_logs    ACL     }   GRANT INSERT,DELETE,UPDATE ON TABLE public.apache_logs TO log_adder;
GRANT SELECT ON TABLE public.apache_logs TO api_getter;
          public          postgres    false    216            �            1259    51993    apache_logs_id_apache_logs_seq    SEQUENCE     �   CREATE SEQUENCE public.apache_logs_id_apache_logs_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 5   DROP SEQUENCE public.apache_logs_id_apache_logs_seq;
       public          postgres    false    216            �           0    0    apache_logs_id_apache_logs_seq    SEQUENCE OWNED BY     a   ALTER SEQUENCE public.apache_logs_id_apache_logs_seq OWNED BY public.apache_logs.id_apache_logs;
          public          postgres    false    215            �           0    0 '   SEQUENCE apache_logs_id_apache_logs_seq    ACL     S   GRANT SELECT,USAGE ON SEQUENCE public.apache_logs_id_apache_logs_seq TO log_adder;
          public          postgres    false    215                       2604    51997    apache_logs id_apache_logs    DEFAULT     �   ALTER TABLE ONLY public.apache_logs ALTER COLUMN id_apache_logs SET DEFAULT nextval('public.apache_logs_id_apache_logs_seq'::regclass);
 I   ALTER TABLE public.apache_logs ALTER COLUMN id_apache_logs DROP DEFAULT;
       public          postgres    false    215    216    216            �          0    51994    apache_logs 
   TABLE DATA           |   COPY public.apache_logs (id_apache_logs, ip_address, logname, time_log, first_line, status_code, response_size) FROM stdin;
    public          postgres    false    216   .       �           0    0    apache_logs_id_apache_logs_seq    SEQUENCE SET     M   SELECT pg_catalog.setval('public.apache_logs_id_apache_logs_seq', 1, false);
          public          postgres    false    215                       2606    52001    apache_logs pk_apache_logs 
   CONSTRAINT     d   ALTER TABLE ONLY public.apache_logs
    ADD CONSTRAINT pk_apache_logs PRIMARY KEY (id_apache_logs);
 D   ALTER TABLE ONLY public.apache_logs DROP CONSTRAINT pk_apache_logs;
       public            postgres    false    216            �      x������ � �     