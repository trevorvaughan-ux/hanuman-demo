-- PROPOSED INSERT, NOT APPLIED. Run only after Grok Bot verifies the migration.
-- Token is generated at apply time (64 hex chars) and lives only in the row. Read it with:
--   select link_token from public.board_links where school_name = 'Great Oaks PreK';
insert into public.board_links (link_token, school_name, enabled, expires_at, notes)
values (replace(gen_random_uuid()::text || gen_random_uuid()::text, '-', ''),
        'Great Oaks PreK', true, '2027-01-01 00:00:00-05', 'First link (Amnah). Trevor flips enabled/expires_at in the table editor.');
