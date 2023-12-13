生徒テーブル
CREATE TABLE jobreport_students1(
  id serial primary key,
  name varchar(32) not null unique,
  mail varchar(32) not null unique,
  pass varchar(256) not null,
  course varchar(32) not null, 
  salt varchar(32) not null, 
  status boolean,  
  delflag boolean  
);

select * from jobreport_students1;

報告書テーブル
CREATE TABLE job_report(
  id serial primary key,
  student_name varchar (256) not null,
  fail_pass varchar(256) not null,
  campany_name varchar(256) not null,
  region varchar(256) not null,
  address varchar(256) not null,
  category varchar(256) not null,
  test_day Date not null,
  result varchar(256) not null,
  post_day Date  not null default now(),
  status boolean,
  delflag boolean  
);

select * from job_report;

求人情報テーブル
CREATE TABLE job_info(
  id serial primary key,
  fail_pass varchar(256) not null,
  campany_name varchar(256) not null,
  region varchar(256) not null,
  address varchar(256) not null,
  category varchar(256) not null,
  post_day Date  not null default now(),
  status boolean,
  delflag boolean  
);

select * from job_info;



  id serial primary key,
  fail_pass varchar(256) not null,
  Contributor varchar(256) not null,
  title varchar(256) not null,
  contents varchar(256) not null

