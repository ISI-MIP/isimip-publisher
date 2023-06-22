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
-- Data for Name: datasets; Type: TABLE DATA; Schema: public; Owner: jochen
--

INSERT INTO public.datasets VALUES ('7616097a-aa86-4595-b298-bf3823618fa6', NULL, 'model_ipsum_dolor_sit_amet_var_global_monthly', 'round/product/sector/model/model_ipsum_dolor_sit_amet_var_global_monthly', '20230622', 29019, '{"beta": "dolor", "alpha": "ipsum", "delta": "amet", "gamma": "sit", "model": "model", "round": "round", "region": "global", "sector": "sector", "product": "product", "timestep": "monthly", "variable": "var", "modelname": "model"}', '{round,product,sector,model,modelname,alpha,beta,gamma,delta,variable,region,timestep}', true, false, NULL, NULL, '2023-06-22 11:43:04.867463', NULL, NULL, NULL);
INSERT INTO public.datasets VALUES ('716783a5-0709-4aba-a44d-652e31197004', NULL, 'model_lorem_dolor_sit_amet_var_global_monthly', 'round/product/sector/model/model_lorem_dolor_sit_amet_var_global_monthly', '20230622', 29019, '{"beta": "dolor", "alpha": "lorem", "delta": "amet", "gamma": "sit", "model": "model", "round": "round", "region": "global", "sector": "sector", "product": "product", "timestep": "monthly", "variable": "var", "modelname": "model"}', '{round,product,sector,model,modelname,alpha,beta,gamma,delta,variable,region,timestep}', true, false, NULL, NULL, '2023-06-22 11:43:04.901081', NULL, NULL, NULL);
INSERT INTO public.datasets VALUES ('9eec459d-2d20-432f-9b2c-73814be2e5ba', NULL, 'model2_ipsum_dolor_sit_amet_var_global_monthly', 'round/product/sector/model2/model2_ipsum_dolor_sit_amet_var_global_monthly', '20230622', 29019, '{"beta": "dolor", "alpha": "ipsum", "delta": "amet", "gamma": "sit", "model": "model2", "round": "round", "region": "global", "sector": "sector", "product": "product", "timestep": "monthly", "variable": "var", "modelname": "model2"}', '{round,product,sector,model,modelname,alpha,beta,gamma,delta,variable,region,timestep}', true, false, NULL, NULL, '2023-06-22 11:43:04.91435', NULL, NULL, NULL);
INSERT INTO public.datasets VALUES ('aaa35622-ebb6-4d4a-a0cb-1e05087cde9c', NULL, 'model2_lorem_dolor_sit_amet_var_global_monthly', 'round/product/sector/model2/model2_lorem_dolor_sit_amet_var_global_monthly', '20230622', 29019, '{"beta": "dolor", "alpha": "lorem", "delta": "amet", "gamma": "sit", "model": "model2", "round": "round", "region": "global", "sector": "sector", "product": "product", "timestep": "monthly", "variable": "var", "modelname": "model2"}', '{round,product,sector,model,modelname,alpha,beta,gamma,delta,variable,region,timestep}', true, false, NULL, NULL, '2023-06-22 11:43:04.927349', NULL, NULL, NULL);


--
-- PostgreSQL database dump complete
--

