insert into public.activities (user_uuid, message, expires_at) 
values (
(select uuid from public.users where users.handle=%(handle)s limit 1), 
%(message)s, %(expires_at)s) returning uuid;