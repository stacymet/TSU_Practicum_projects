--1. В данных наблюдается падение выручки от пользователей из Индии.
--Выручка
select 
event_date,
sum(revenue) as revenue
from mobile_game.transactions t 
group by event_date 

--Выручка по странам
select 
t.event_date,
ui.country,
sum(t.revenue) as revenue
from mobile_game.transactions t 
left join mobile_game.user_info ui 
on t.user_id = ui.user_id
group by t.event_date, ui.country

--DAU
select
date(s.session_start_time) as event_date,
ui.country,
count(distinct s.user_id) as dau
from mobile_game.sessions s 
left join mobile_game.user_info ui
on s.user_id = ui.user_id
group by event_date, ui.country

--ARPDAU
select 
start_s_date.event_date,
start_s_date.country,
sum(t.revenue) / nullif(count(distinct start_s_date.user_id), 0) as arpdau
from(
select
s.user_id,
date(session_start_time) as event_date,
ui.country
from mobile_game.sessions s 
left join mobile_game.user_info ui 
on s.user_id = ui.user_id) start_s_date
left join mobile_game.transactions t 
on start_s_date.user_id = t.user_id 
and start_s_date.event_date = t.event_date
group by start_s_date.event_date, start_s_date.country

--ARPPU
select 
t.event_date,
ui.country,
sum(t.revenue) / nullif(count(distinct t.user_id), 0) as arppu
from mobile_game.transactions t 
left join mobile_game.user_info ui on
t.user_id = ui.user_id
group by t.event_date, ui.country

--Daily Conversion
with dau as(
select
date(s.session_start_time) as event_date,
ui.country,
count(distinct s.user_id) as dau
from mobile_game.sessions s 
left join mobile_game.user_info ui
on s.user_id = ui.user_id
group by event_date, ui.country
),
p_users as(
select
t.event_date,
ui.country,
count(distinct t.user_id) as paying_users
from mobile_game.transactions t 
left join mobile_game.user_info ui
on t.user_id = ui.user_id
group by t.event_date, ui.country
)

select 
dau.event_date,
dau.country,
case 
	when dau.dau = 0 then 0
	else coalesce(p_users.paying_users, 0)::float /dau.dau
end as daily_conversion
from dau
left join p_users
on dau.event_date = p_users.event_date
and dau.country = p_users.country

--New installs с Last Click атрибуцией
with touches as(
select
ut.user_id,
ut.touch_date,
ut.channel,
ui.user_start_date,
ui.country
from mobile_game.users_touches ut 
join mobile_game.user_info ui 
on ut.user_id = ui.user_id
where ut.touch_date <= ui.user_start_date
),

last_click as (
select 
user_id,
max(touch_date) as last_click_date
from touches
group by user_id
),

attributed_installs as (
select 
touches.user_id,
touches.user_start_date as install_date,
touches.country,
touches.channel
from touches 
join last_click lc
on touches.user_id = lc.user_id 
and touches.touch_date = lc.last_click_date
)

select 
install_date,
country,
channel,
count(*) as installs
from attributed_installs
where country = 'India'
group by install_date, country, channel

--Returning users
select 
date(s.session_start_time) as event_date,
ui.country,
count(distinct s.user_id) as returning_users
from mobile_game.sessions s
left join mobile_game.user_info ui 
on s.user_id = ui.user_id
where date(s.session_start_time) > ui.user_start_date
group by event_date, ui.country

--Выручка от Returning Users
with returning_users as (
select distinct
s.user_id,
date(s.session_start_time) as event_date,
ui.country
from mobile_game.sessions s
left join mobile_game.user_info ui 
on s.user_id = ui.user_id
where date(s.session_start_time) > ui.user_start_date
),

returning_revenue as (
select
ru.event_date,
ru.country,
sum(t.revenue) as revenue_from_returning
from returning_users ru
join mobile_game.transactions t
on ru.user_id = t.user_id
and ru.event_date = t.event_date
group by ru.event_date, ru.country
)
select *
from returning_revenue
where country = 'India'

--2.После 23 октября 2023 года пропадает выручка по скидкам
--Выручка по продуктам
select 
event_date,
product_name,
sum(revenue) as revenue
from mobile_game.transactions t 
group by event_date, product_name  
order by event_date 

--Выручка по product_name = 'sale' у разных ценовых сегментов
select 
t.event_date,
t.product_name,
ui.payer_segment,
sum(t.revenue) as revenue
from mobile_game.transactions t
left join mobile_game.user_info ui
on t.user_id = ui.user_id
where product_name = 'sale'
group by t.event_date, t.product_name, ui.payer_segment
order by t.event_date

--3. Снижение притока новых пользователей по каналу Applovin с октября 2023 года.
--Выручка по каналам
select 
t.event_date,
ut.channel,
sum(t.revenue) as revenue
from mobile_game.transactions t 
left join mobile_game.users_touches ut 
on t.user_id = ut.user_id 
group by t.event_date, ut.channel 

--DAU по каналам
with touches as (
select 
ut.user_id,
ut.touch_date,
ut.channel,
ui.user_start_date
from mobile_game.users_touches ut
join mobile_game.user_info ui 
on ut.user_id = ui.user_id
where ut.touch_date <= ui.user_start_date
),
last_click as (
select 
user_id,
max(touch_date) as last_click_date
from touches
group by user_id
),
attributed_users as (
select 
t.user_id,
t.channel
from touches t
join last_click lc
on t.user_id = lc.user_id 
and t.touch_date = lc.last_click_date
)
select
date(s.session_start_time) as event_date,
au.channel,
count(distinct au.user_id) as dau
from mobile_game.sessions s 
left join attributed_users au
on s.user_id = au.user_id
group by 1, 2

--new users
with touches as (
select 
ut.user_id,
ut.touch_date,
ut.channel,
ui.user_start_date
from mobile_game.users_touches ut
join mobile_game.user_info ui 
on ut.user_id = ui.user_id
where ut.touch_date <= ui.user_start_date
),
last_click as (
select 
user_id,
max(touch_date) as last_click_date
from touches
group by user_id
),
attributed_users as (
select 
t.user_id,
t.channel,
t.user_start_date as install_date
from touches t
join last_click lc
on t.user_id = lc.user_id 
and t.touch_date = lc.last_click_date
)
select 
install_date,
channel,
count(distinct user_id) as new_users
from attributed_users 
group by install_date, channel

--Daily conversion по каналу applovin
with touches_applovin as (
select 
ut.user_id,
ut.touch_date,
ut.channel,
ui.user_start_date
from mobile_game.users_touches ut
join mobile_game.user_info ui on ut.user_id = ui.user_id
where ut.touch_date <= ui.user_start_date and ut.channel = 'applovin'
),
last_click as (
select 
user_id,
max(touch_date) as last_click_date
from touches_applovin
group by user_id
),
attributed_users as (
select 
ta.user_id,
ui.user_start_date,
ta.channel
from touches_applovin ta
join last_click lc 
on ta.user_id = lc.user_id 
and ta.touch_date = lc.last_click_date
join mobile_game.user_info ui 
on ta.user_id = ui.user_id
),
dau as (
select 
date(s.session_start_time) as event_date,
au.channel,
count(distinct s.user_id) as dau
from mobile_game.sessions s
join attributed_users au 
on s.user_id = au.user_id
where au.channel = 'applovin'
group by 1, 2
),
paying_users as (
select 
date(t.event_date) as event_date,
au.channel,
count(distinct t.user_id) as paying_users
from mobile_game.transactions t
join attributed_users au on t.user_id = au.user_id
where au.channel = 'applovin'
group by 1, 2
)
select 
dau.event_date,
dau.channel,
dau.dau,
coalesce(pu.paying_users, 0) as paying_users,
case 
  when dau.dau = 0 then 0
  else coalesce(pu.paying_users, 0)::float / dau.dau
end as daily_conversion
from dau
left join paying_users pu 
on dau.event_date = pu.event_date 
and dau.channel = pu.channel
order by dau.event_date






