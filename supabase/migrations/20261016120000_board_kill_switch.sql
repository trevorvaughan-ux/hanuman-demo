-- T-WB-HANI-MVP-BOARD-20261016: demo board kill switch. PROPOSED, NOT APPLIED. Grok Bot verifies first.
create table public.board_links (
  id uuid primary key default gen_random_uuid(),
  link_token text not null unique check (length(link_token) >= 24),
  school_name text not null,
  enabled boolean not null default true,
  expires_at timestamptz not null default '2027-01-01 00:00:00-05',
  created_at timestamptz not null default now(),
  notes text
);

create table public.board_global (
  id smallint primary key default 1 check (id = 1),
  enabled boolean not null default true,
  ended_message_en text default 'This demo has ended. Thank you for trying Hani!',
  ended_message_es text default 'Esta demostración ha terminado. ¡Gracias por probar Hani!',
  updated_at timestamptz not null default now()
);
insert into public.board_global (id) values (1);

alter table public.board_links enable row level security;
alter table public.board_global enable row level security;
-- No anon/authenticated policies on either table: direct REST reads return nothing.

create or replace function public.board_link_status(p_token text)
returns json
language sql
stable
security definer
set search_path = public
as $$
  select json_build_object(
    'active', coalesce((select g.enabled from board_global g where g.id = 1), false)
              and coalesce(l.enabled, false)
              and coalesce(l.expires_at > now(), false),
    'school_name', case when l.id is not null then l.school_name end,
    'msg_en', (select ended_message_en from board_global where id = 1),
    'msg_es', (select ended_message_es from board_global where id = 1))
  from (select 1) x
  left join board_links l on l.link_token = p_token;
$$;

revoke all on function public.board_link_status(text) from public;
grant execute on function public.board_link_status(text) to anon, authenticated;
