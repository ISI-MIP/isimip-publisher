--
-- PostgreSQL database dump
--

-- Dumped from database version 13.10 (Debian 13.10-0+deb11u1)
-- Dumped by pg_dump version 13.10 (Debian 13.10-0+deb11u1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Data for Name: files; Type: TABLE DATA; Schema: public; Owner: jochen
--

INSERT INTO public.files VALUES ('a8373223-0792-4b87-beef-8564266c914f', '7616097a-aa86-4595-b298-bf3823618fa6', NULL, 'model_ipsum_dolor_sit_amet_var_global_monthly_2000_2001.nc', 'round/product/sector/model/model_ipsum_dolor_sit_amet_var_global_monthly_2000_2001.nc', '20230622', 9673, 'd85e8bc3ba4d2f23cdf5594182d9a2f39f5fac0b8ca39d6166831b5932e7f044dd18b1f46e550b14725f794436b6452ede12801f4faa8cb2a127ec14b819968c', 'sha512', '{"variables": {"lat": {"axis": "Y", "units": "degrees_north", "long_name": "latitude", "dimensions": ["lat"], "standard_name": "latitude"}, "lon": {"axis": "X", "units": "degrees_east", "long_name": "longitude", "dimensions": ["lon"], "standard_name": "longitude"}, "var": {"units": "m", "long_name": "variable", "dimensions": ["time", "lat", "lon"], "missing_value": "1.e+20f", "standard_name": "variable"}, "time": {"axis": "T", "units": "days since 1661-1-1 00:00:00", "calendar": "proleptic_gregorian", "long_name": "time", "dimensions": ["time"], "standard_name": "time"}}, "dimensions": {"lat": 360, "lon": 720, "time": 0}, "global_attributes": {"contact": "Tony Testing <testing@example.com>", "institution": "Institute of applied testing"}}', '{"beta": "dolor", "alpha": "ipsum", "delta": "amet", "gamma": "sit", "model": "model", "round": "round", "region": "global", "sector": "sector", "product": "product", "end_year": 2001, "timestep": "monthly", "variable": "var", "modelname": "model", "start_year": 2000}', '{round,product,sector,model,modelname,alpha,beta,gamma,delta,variable,region,timestep,start_year,end_year}', '2023-06-22 11:43:04.875606', NULL);
INSERT INTO public.files VALUES ('7ddbad35-4976-4181-a3ac-5f346a1ae65c', '7616097a-aa86-4595-b298-bf3823618fa6', NULL, 'model_ipsum_dolor_sit_amet_var_global_monthly_2001_2002.nc', 'round/product/sector/model/model_ipsum_dolor_sit_amet_var_global_monthly_2001_2002.nc', '20230622', 9673, 'd85e8bc3ba4d2f23cdf5594182d9a2f39f5fac0b8ca39d6166831b5932e7f044dd18b1f46e550b14725f794436b6452ede12801f4faa8cb2a127ec14b819968c', 'sha512', '{"variables": {"lat": {"axis": "Y", "units": "degrees_north", "long_name": "latitude", "dimensions": ["lat"], "standard_name": "latitude"}, "lon": {"axis": "X", "units": "degrees_east", "long_name": "longitude", "dimensions": ["lon"], "standard_name": "longitude"}, "var": {"units": "m", "long_name": "variable", "dimensions": ["time", "lat", "lon"], "missing_value": "1.e+20f", "standard_name": "variable"}, "time": {"axis": "T", "units": "days since 1661-1-1 00:00:00", "calendar": "proleptic_gregorian", "long_name": "time", "dimensions": ["time"], "standard_name": "time"}}, "dimensions": {"lat": 360, "lon": 720, "time": 0}, "global_attributes": {"contact": "Tony Testing <testing@example.com>", "institution": "Institute of applied testing"}}', '{"beta": "dolor", "alpha": "ipsum", "delta": "amet", "gamma": "sit", "model": "model", "round": "round", "region": "global", "sector": "sector", "product": "product", "end_year": 2002, "timestep": "monthly", "variable": "var", "modelname": "model", "start_year": 2001}', '{round,product,sector,model,modelname,alpha,beta,gamma,delta,variable,region,timestep,start_year,end_year}', '2023-06-22 11:43:04.880561', NULL);
INSERT INTO public.files VALUES ('2fdbd5ba-d810-49f2-97bd-b284091d87ee', '7616097a-aa86-4595-b298-bf3823618fa6', NULL, 'model_ipsum_dolor_sit_amet_var_global_monthly_2002_2003.nc', 'round/product/sector/model/model_ipsum_dolor_sit_amet_var_global_monthly_2002_2003.nc', '20230622', 9673, 'd85e8bc3ba4d2f23cdf5594182d9a2f39f5fac0b8ca39d6166831b5932e7f044dd18b1f46e550b14725f794436b6452ede12801f4faa8cb2a127ec14b819968c', 'sha512', '{"variables": {"lat": {"axis": "Y", "units": "degrees_north", "long_name": "latitude", "dimensions": ["lat"], "standard_name": "latitude"}, "lon": {"axis": "X", "units": "degrees_east", "long_name": "longitude", "dimensions": ["lon"], "standard_name": "longitude"}, "var": {"units": "m", "long_name": "variable", "dimensions": ["time", "lat", "lon"], "missing_value": "1.e+20f", "standard_name": "variable"}, "time": {"axis": "T", "units": "days since 1661-1-1 00:00:00", "calendar": "proleptic_gregorian", "long_name": "time", "dimensions": ["time"], "standard_name": "time"}}, "dimensions": {"lat": 360, "lon": 720, "time": 0}, "global_attributes": {"contact": "Tony Testing <testing@example.com>", "institution": "Institute of applied testing"}}', '{"beta": "dolor", "alpha": "ipsum", "delta": "amet", "gamma": "sit", "model": "model", "round": "round", "region": "global", "sector": "sector", "product": "product", "end_year": 2003, "timestep": "monthly", "variable": "var", "modelname": "model", "start_year": 2002}', '{round,product,sector,model,modelname,alpha,beta,gamma,delta,variable,region,timestep,start_year,end_year}', '2023-06-22 11:43:04.884244', NULL);
INSERT INTO public.files VALUES ('f7dd6801-1b2b-46d1-811b-938ee3170307', '716783a5-0709-4aba-a44d-652e31197004', NULL, 'model_lorem_dolor_sit_amet_var_global_monthly_2000_2001.nc', 'round/product/sector/model/model_lorem_dolor_sit_amet_var_global_monthly_2000_2001.nc', '20230622', 9673, 'd85e8bc3ba4d2f23cdf5594182d9a2f39f5fac0b8ca39d6166831b5932e7f044dd18b1f46e550b14725f794436b6452ede12801f4faa8cb2a127ec14b819968c', 'sha512', '{"variables": {"lat": {"axis": "Y", "units": "degrees_north", "long_name": "latitude", "dimensions": ["lat"], "standard_name": "latitude"}, "lon": {"axis": "X", "units": "degrees_east", "long_name": "longitude", "dimensions": ["lon"], "standard_name": "longitude"}, "var": {"units": "m", "long_name": "variable", "dimensions": ["time", "lat", "lon"], "missing_value": "1.e+20f", "standard_name": "variable"}, "time": {"axis": "T", "units": "days since 1661-1-1 00:00:00", "calendar": "proleptic_gregorian", "long_name": "time", "dimensions": ["time"], "standard_name": "time"}}, "dimensions": {"lat": 360, "lon": 720, "time": 0}, "global_attributes": {"contact": "Tony Testing <testing@example.com>", "institution": "Institute of applied testing"}}', '{"beta": "dolor", "alpha": "lorem", "delta": "amet", "gamma": "sit", "model": "model", "round": "round", "region": "global", "sector": "sector", "product": "product", "end_year": 2001, "timestep": "monthly", "variable": "var", "modelname": "model", "start_year": 2000}', '{round,product,sector,model,modelname,alpha,beta,gamma,delta,variable,region,timestep,start_year,end_year}', '2023-06-22 11:43:04.904319', NULL);
INSERT INTO public.files VALUES ('094306cd-b597-45a2-959f-659123fcc5f5', '716783a5-0709-4aba-a44d-652e31197004', NULL, 'model_lorem_dolor_sit_amet_var_global_monthly_2001_2002.nc', 'round/product/sector/model/model_lorem_dolor_sit_amet_var_global_monthly_2001_2002.nc', '20230622', 9673, 'd85e8bc3ba4d2f23cdf5594182d9a2f39f5fac0b8ca39d6166831b5932e7f044dd18b1f46e550b14725f794436b6452ede12801f4faa8cb2a127ec14b819968c', 'sha512', '{"variables": {"lat": {"axis": "Y", "units": "degrees_north", "long_name": "latitude", "dimensions": ["lat"], "standard_name": "latitude"}, "lon": {"axis": "X", "units": "degrees_east", "long_name": "longitude", "dimensions": ["lon"], "standard_name": "longitude"}, "var": {"units": "m", "long_name": "variable", "dimensions": ["time", "lat", "lon"], "missing_value": "1.e+20f", "standard_name": "variable"}, "time": {"axis": "T", "units": "days since 1661-1-1 00:00:00", "calendar": "proleptic_gregorian", "long_name": "time", "dimensions": ["time"], "standard_name": "time"}}, "dimensions": {"lat": 360, "lon": 720, "time": 0}, "global_attributes": {"contact": "Tony Testing <testing@example.com>", "institution": "Institute of applied testing"}}', '{"beta": "dolor", "alpha": "lorem", "delta": "amet", "gamma": "sit", "model": "model", "round": "round", "region": "global", "sector": "sector", "product": "product", "end_year": 2002, "timestep": "monthly", "variable": "var", "modelname": "model", "start_year": 2001}', '{round,product,sector,model,modelname,alpha,beta,gamma,delta,variable,region,timestep,start_year,end_year}', '2023-06-22 11:43:04.907861', NULL);
INSERT INTO public.files VALUES ('08f2e995-e021-4b9e-871e-9aa3cb5be874', '716783a5-0709-4aba-a44d-652e31197004', NULL, 'model_lorem_dolor_sit_amet_var_global_monthly_2002_2003.nc', 'round/product/sector/model/model_lorem_dolor_sit_amet_var_global_monthly_2002_2003.nc', '20230622', 9673, 'd85e8bc3ba4d2f23cdf5594182d9a2f39f5fac0b8ca39d6166831b5932e7f044dd18b1f46e550b14725f794436b6452ede12801f4faa8cb2a127ec14b819968c', 'sha512', '{"variables": {"lat": {"axis": "Y", "units": "degrees_north", "long_name": "latitude", "dimensions": ["lat"], "standard_name": "latitude"}, "lon": {"axis": "X", "units": "degrees_east", "long_name": "longitude", "dimensions": ["lon"], "standard_name": "longitude"}, "var": {"units": "m", "long_name": "variable", "dimensions": ["time", "lat", "lon"], "missing_value": "1.e+20f", "standard_name": "variable"}, "time": {"axis": "T", "units": "days since 1661-1-1 00:00:00", "calendar": "proleptic_gregorian", "long_name": "time", "dimensions": ["time"], "standard_name": "time"}}, "dimensions": {"lat": 360, "lon": 720, "time": 0}, "global_attributes": {"contact": "Tony Testing <testing@example.com>", "institution": "Institute of applied testing"}}', '{"beta": "dolor", "alpha": "lorem", "delta": "amet", "gamma": "sit", "model": "model", "round": "round", "region": "global", "sector": "sector", "product": "product", "end_year": 2003, "timestep": "monthly", "variable": "var", "modelname": "model", "start_year": 2002}', '{round,product,sector,model,modelname,alpha,beta,gamma,delta,variable,region,timestep,start_year,end_year}', '2023-06-22 11:43:04.911495', NULL);
INSERT INTO public.files VALUES ('3d59d820-326d-4ad3-9dd1-3bc6c86120b2', '9eec459d-2d20-432f-9b2c-73814be2e5ba', NULL, 'model2_ipsum_dolor_sit_amet_var_global_monthly_2000_2001.nc', 'round/product/sector/model2/model2_ipsum_dolor_sit_amet_var_global_monthly_2000_2001.nc', '20230622', 9673, 'd85e8bc3ba4d2f23cdf5594182d9a2f39f5fac0b8ca39d6166831b5932e7f044dd18b1f46e550b14725f794436b6452ede12801f4faa8cb2a127ec14b819968c', 'sha512', '{"variables": {"lat": {"axis": "Y", "units": "degrees_north", "long_name": "latitude", "dimensions": ["lat"], "standard_name": "latitude"}, "lon": {"axis": "X", "units": "degrees_east", "long_name": "longitude", "dimensions": ["lon"], "standard_name": "longitude"}, "var": {"units": "m", "long_name": "variable", "dimensions": ["time", "lat", "lon"], "missing_value": "1.e+20f", "standard_name": "variable"}, "time": {"axis": "T", "units": "days since 1661-1-1 00:00:00", "calendar": "proleptic_gregorian", "long_name": "time", "dimensions": ["time"], "standard_name": "time"}}, "dimensions": {"lat": 360, "lon": 720, "time": 0}, "global_attributes": {"contact": "Tony Testing <testing@example.com>", "institution": "Institute of applied testing"}}', '{"beta": "dolor", "alpha": "ipsum", "delta": "amet", "gamma": "sit", "model": "model2", "round": "round", "region": "global", "sector": "sector", "product": "product", "end_year": 2001, "timestep": "monthly", "variable": "var", "modelname": "model2", "start_year": 2000}', '{round,product,sector,model,modelname,alpha,beta,gamma,delta,variable,region,timestep,start_year,end_year}', '2023-06-22 11:43:04.917559', NULL);
INSERT INTO public.files VALUES ('40bfda33-b94a-428d-a021-81d72ffbf11a', '9eec459d-2d20-432f-9b2c-73814be2e5ba', NULL, 'model2_ipsum_dolor_sit_amet_var_global_monthly_2001_2002.nc', 'round/product/sector/model2/model2_ipsum_dolor_sit_amet_var_global_monthly_2001_2002.nc', '20230622', 9673, 'd85e8bc3ba4d2f23cdf5594182d9a2f39f5fac0b8ca39d6166831b5932e7f044dd18b1f46e550b14725f794436b6452ede12801f4faa8cb2a127ec14b819968c', 'sha512', '{"variables": {"lat": {"axis": "Y", "units": "degrees_north", "long_name": "latitude", "dimensions": ["lat"], "standard_name": "latitude"}, "lon": {"axis": "X", "units": "degrees_east", "long_name": "longitude", "dimensions": ["lon"], "standard_name": "longitude"}, "var": {"units": "m", "long_name": "variable", "dimensions": ["time", "lat", "lon"], "missing_value": "1.e+20f", "standard_name": "variable"}, "time": {"axis": "T", "units": "days since 1661-1-1 00:00:00", "calendar": "proleptic_gregorian", "long_name": "time", "dimensions": ["time"], "standard_name": "time"}}, "dimensions": {"lat": 360, "lon": 720, "time": 0}, "global_attributes": {"contact": "Tony Testing <testing@example.com>", "institution": "Institute of applied testing"}}', '{"beta": "dolor", "alpha": "ipsum", "delta": "amet", "gamma": "sit", "model": "model2", "round": "round", "region": "global", "sector": "sector", "product": "product", "end_year": 2002, "timestep": "monthly", "variable": "var", "modelname": "model2", "start_year": 2001}', '{round,product,sector,model,modelname,alpha,beta,gamma,delta,variable,region,timestep,start_year,end_year}', '2023-06-22 11:43:04.921017', NULL);
INSERT INTO public.files VALUES ('2f0ebca2-ee09-4772-bfce-ccff670964b0', '9eec459d-2d20-432f-9b2c-73814be2e5ba', NULL, 'model2_ipsum_dolor_sit_amet_var_global_monthly_2002_2003.nc', 'round/product/sector/model2/model2_ipsum_dolor_sit_amet_var_global_monthly_2002_2003.nc', '20230622', 9673, 'd85e8bc3ba4d2f23cdf5594182d9a2f39f5fac0b8ca39d6166831b5932e7f044dd18b1f46e550b14725f794436b6452ede12801f4faa8cb2a127ec14b819968c', 'sha512', '{"variables": {"lat": {"axis": "Y", "units": "degrees_north", "long_name": "latitude", "dimensions": ["lat"], "standard_name": "latitude"}, "lon": {"axis": "X", "units": "degrees_east", "long_name": "longitude", "dimensions": ["lon"], "standard_name": "longitude"}, "var": {"units": "m", "long_name": "variable", "dimensions": ["time", "lat", "lon"], "missing_value": "1.e+20f", "standard_name": "variable"}, "time": {"axis": "T", "units": "days since 1661-1-1 00:00:00", "calendar": "proleptic_gregorian", "long_name": "time", "dimensions": ["time"], "standard_name": "time"}}, "dimensions": {"lat": 360, "lon": 720, "time": 0}, "global_attributes": {"contact": "Tony Testing <testing@example.com>", "institution": "Institute of applied testing"}}', '{"beta": "dolor", "alpha": "ipsum", "delta": "amet", "gamma": "sit", "model": "model2", "round": "round", "region": "global", "sector": "sector", "product": "product", "end_year": 2003, "timestep": "monthly", "variable": "var", "modelname": "model2", "start_year": 2002}', '{round,product,sector,model,modelname,alpha,beta,gamma,delta,variable,region,timestep,start_year,end_year}', '2023-06-22 11:43:04.924511', NULL);
INSERT INTO public.files VALUES ('775c81ae-1266-46c3-b04f-717a33c4109a', 'aaa35622-ebb6-4d4a-a0cb-1e05087cde9c', NULL, 'model2_lorem_dolor_sit_amet_var_global_monthly_2000_2001.nc', 'round/product/sector/model2/model2_lorem_dolor_sit_amet_var_global_monthly_2000_2001.nc', '20230622', 9673, 'd85e8bc3ba4d2f23cdf5594182d9a2f39f5fac0b8ca39d6166831b5932e7f044dd18b1f46e550b14725f794436b6452ede12801f4faa8cb2a127ec14b819968c', 'sha512', '{"variables": {"lat": {"axis": "Y", "units": "degrees_north", "long_name": "latitude", "dimensions": ["lat"], "standard_name": "latitude"}, "lon": {"axis": "X", "units": "degrees_east", "long_name": "longitude", "dimensions": ["lon"], "standard_name": "longitude"}, "var": {"units": "m", "long_name": "variable", "dimensions": ["time", "lat", "lon"], "missing_value": "1.e+20f", "standard_name": "variable"}, "time": {"axis": "T", "units": "days since 1661-1-1 00:00:00", "calendar": "proleptic_gregorian", "long_name": "time", "dimensions": ["time"], "standard_name": "time"}}, "dimensions": {"lat": 360, "lon": 720, "time": 0}, "global_attributes": {"contact": "Tony Testing <testing@example.com>", "institution": "Institute of applied testing"}}', '{"beta": "dolor", "alpha": "lorem", "delta": "amet", "gamma": "sit", "model": "model2", "round": "round", "region": "global", "sector": "sector", "product": "product", "end_year": 2001, "timestep": "monthly", "variable": "var", "modelname": "model2", "start_year": 2000}', '{round,product,sector,model,modelname,alpha,beta,gamma,delta,variable,region,timestep,start_year,end_year}', '2023-06-22 11:43:04.93053', NULL);
INSERT INTO public.files VALUES ('c5f59fed-ab18-4adf-9fd7-e6121684e76e', 'aaa35622-ebb6-4d4a-a0cb-1e05087cde9c', NULL, 'model2_lorem_dolor_sit_amet_var_global_monthly_2001_2002.nc', 'round/product/sector/model2/model2_lorem_dolor_sit_amet_var_global_monthly_2001_2002.nc', '20230622', 9673, 'd85e8bc3ba4d2f23cdf5594182d9a2f39f5fac0b8ca39d6166831b5932e7f044dd18b1f46e550b14725f794436b6452ede12801f4faa8cb2a127ec14b819968c', 'sha512', '{"variables": {"lat": {"axis": "Y", "units": "degrees_north", "long_name": "latitude", "dimensions": ["lat"], "standard_name": "latitude"}, "lon": {"axis": "X", "units": "degrees_east", "long_name": "longitude", "dimensions": ["lon"], "standard_name": "longitude"}, "var": {"units": "m", "long_name": "variable", "dimensions": ["time", "lat", "lon"], "missing_value": "1.e+20f", "standard_name": "variable"}, "time": {"axis": "T", "units": "days since 1661-1-1 00:00:00", "calendar": "proleptic_gregorian", "long_name": "time", "dimensions": ["time"], "standard_name": "time"}}, "dimensions": {"lat": 360, "lon": 720, "time": 0}, "global_attributes": {"contact": "Tony Testing <testing@example.com>", "institution": "Institute of applied testing"}}', '{"beta": "dolor", "alpha": "lorem", "delta": "amet", "gamma": "sit", "model": "model2", "round": "round", "region": "global", "sector": "sector", "product": "product", "end_year": 2002, "timestep": "monthly", "variable": "var", "modelname": "model2", "start_year": 2001}', '{round,product,sector,model,modelname,alpha,beta,gamma,delta,variable,region,timestep,start_year,end_year}', '2023-06-22 11:43:04.933967', NULL);
INSERT INTO public.files VALUES ('75c0a10b-1186-4e92-bd1b-1a5f39ea88c5', 'aaa35622-ebb6-4d4a-a0cb-1e05087cde9c', NULL, 'model2_lorem_dolor_sit_amet_var_global_monthly_2002_2003.nc', 'round/product/sector/model2/model2_lorem_dolor_sit_amet_var_global_monthly_2002_2003.nc', '20230622', 9673, 'd85e8bc3ba4d2f23cdf5594182d9a2f39f5fac0b8ca39d6166831b5932e7f044dd18b1f46e550b14725f794436b6452ede12801f4faa8cb2a127ec14b819968c', 'sha512', '{"variables": {"lat": {"axis": "Y", "units": "degrees_north", "long_name": "latitude", "dimensions": ["lat"], "standard_name": "latitude"}, "lon": {"axis": "X", "units": "degrees_east", "long_name": "longitude", "dimensions": ["lon"], "standard_name": "longitude"}, "var": {"units": "m", "long_name": "variable", "dimensions": ["time", "lat", "lon"], "missing_value": "1.e+20f", "standard_name": "variable"}, "time": {"axis": "T", "units": "days since 1661-1-1 00:00:00", "calendar": "proleptic_gregorian", "long_name": "time", "dimensions": ["time"], "standard_name": "time"}}, "dimensions": {"lat": 360, "lon": 720, "time": 0}, "global_attributes": {"contact": "Tony Testing <testing@example.com>", "institution": "Institute of applied testing"}}', '{"beta": "dolor", "alpha": "lorem", "delta": "amet", "gamma": "sit", "model": "model2", "round": "round", "region": "global", "sector": "sector", "product": "product", "end_year": 2003, "timestep": "monthly", "variable": "var", "modelname": "model2", "start_year": 2002}', '{round,product,sector,model,modelname,alpha,beta,gamma,delta,variable,region,timestep,start_year,end_year}', '2023-06-22 11:43:04.937413', NULL);


--
-- PostgreSQL database dump complete
--

