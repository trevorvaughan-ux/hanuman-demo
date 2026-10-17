-- PROPOSED, NOT APPLIED. T-SEC-SUPABASE-RLS-LOCKDOWN-20261016. Prepared by Claude 2026-10-17.
-- Kept in supabase/proposed/ (NOT supabase/migrations/) so no CI/GitHub integration auto-applies it.
-- Apply only after Grok Bot verification AND Trevor's own "GO T-SEC-SUPABASE-RLS-LOCKDOWN-20261016".
-- Scope: public schema. trevor_debts and credentials_vault are deliberately excluded everywhere.
-- ai_messages is excluded here (claude_grok_bridge edge functions use it with the anon key): see part2 file.
-- hani_events is excluded (anon INSERT-only with column checks is already narrow and the Hani boards need it).
-- BEFORE APPLYING: replace the all-zero placeholder uuid (marked REPLACE_WITH_TREVOR_AUTH_UID) in is_trevor() with Trevor's auth.users id (NOT confirmed read-only;
-- auth.users has 1 row and its email did not match trevorvaughan@hudsonseed.com).
BEGIN;

-- 0. Single place that decides who "Trevor" is for authenticated sessions.
CREATE OR REPLACE FUNCTION public.is_trevor() RETURNS boolean
LANGUAGE sql STABLE SET search_path = public, pg_temp
AS $f$ SELECT auth.uid() = '00000000-0000-0000-0000-000000000000'::uuid /* REPLACE_WITH_TREVOR_AUTH_UID */ $f$;
DO $$ BEGIN
  IF position('00000000-0000-0000-0000-000000000000' in pg_get_functiondef('public.is_trevor()'::regprocedure)) > 0 THEN
    RAISE EXCEPTION 'is_trevor() still has the placeholder uid. Aborting.';
  END IF;
END $$;

-- 1. approval_log: RLS on, service-role-only, no anon/authenticated privileges.
ALTER TABLE public.approval_log ENABLE ROW LEVEL SECURITY;
CREATE POLICY service_role_all_approval_log ON public.approval_log FOR ALL TO service_role USING (true) WITH CHECK (true);

-- 2. Revoke anon everything, and authenticated TRUNCATE/REFERENCES/TRIGGER, on every public relation
--    except the protected two, hani_events, ai_messages and board_links/board_global (owned by the MVP board migration).
DO $$ DECLARE r record; BEGIN
  FOR r IN SELECT c.relname FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace
           WHERE n.nspname='public' AND c.relkind IN ('r','p','v','m')
             AND c.relname NOT IN ('trevor_debts','credentials_vault','hani_events','ai_messages','board_links','board_global') LOOP
    EXECUTE format('REVOKE ALL ON public.%I FROM anon', r.relname);
    EXECUTE format('REVOKE TRUNCATE, REFERENCES, TRIGGER ON public.%I FROM authenticated', r.relname);
  END LOOP;
END $$;
REVOKE ALL ON public.approval_log FROM authenticated;

-- 3. Narrow anon grants that live pages need (each already has a matching narrow policy).
GRANT INSERT ON public.crm_contacts TO anon;             -- policy anon_insert_website_leads (column/length checks)
GRANT INSERT ON public.waitlist TO anon;                 -- policy anon_insert_waitlist (WITH CHECK true: tighten later)
GRANT SELECT ON public.hudsonseed_website_assets TO anon; -- policy anon_read_website_assets
GRANT SELECT ON public.menu_cards TO anon;               -- hanuman-menu.html, policy "read free cards"
GRANT SELECT ON public.menu_profiles TO anon;            -- needed only because menu_cards policies subquery it; RLS returns 0 rows

-- 4. Replace the wide-open "true" policies with service-role-only policies.
DROP POLICY "Service role full access" ON public.ai_yoga_teacher_curriculum;
DROP POLICY allow_all ON public.claude_grok_messages;
DROP POLICY trevor_all_email ON public.email_queue;
DROP POLICY trevor_all_responses ON public.responses;
DROP POLICY trevor_all_comms ON public.school_communications;
DROP POLICY trevor_all ON public.schools_crm;
DROP POLICY trevor_all_sent ON public.sent_emails;
DROP POLICY trevor_all_teachers ON public.teacher_enrollments;
CREATE POLICY service_role_all_ai_yoga_teacher_curriculum ON public.ai_yoga_teacher_curriculum FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY service_role_all_claude_grok_messages ON public.claude_grok_messages FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY service_role_all_email_queue ON public.email_queue FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY service_role_all_responses ON public.responses FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY service_role_all_school_communications ON public.school_communications FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY service_role_all_schools_crm ON public.schools_crm FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY service_role_all_sent_emails ON public.sent_emails FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY service_role_all_teacher_enrollments ON public.teacher_enrollments FOR ALL TO service_role USING (true) WITH CHECK (true);

-- 5. Drop anon read/update policies on contact data and notes.
DROP POLICY anon_read_blockers ON public.blockers;
DROP POLICY anon_read_diary ON public.diary;
DROP POLICY anon_read_leads ON public.leads;
DROP POLICY anon_read_teachers ON public.teachers;
DROP POLICY anon_read_lexicon ON public.shared_lexicon;
DROP POLICY allow_anon_read ON public.jc_schools_contacts_backup_20260521;
DROP POLICY allow_anon_update ON public.jc_schools_contacts_backup_20260521;

-- 6. Every blanket "any signed-in user" policy now requires Trevor (task_register, leads, system_config, districts,
--    do_not_contact and all others with qual auth.role() = 'authenticated').
DO $$ DECLARE r record; BEGIN
  FOR r IN SELECT tablename, policyname, cmd, with_check FROM pg_policies
           WHERE schemaname='public' AND qual = '(auth.role() = ''authenticated''::text)'
             AND tablename NOT IN ('trevor_debts','credentials_vault') LOOP
    IF r.cmd IN ('SELECT','DELETE') OR r.with_check IS NULL THEN
      EXECUTE format('ALTER POLICY %I ON public.%I USING (public.is_trevor())', r.policyname, r.tablename);
    ELSE
      EXECUTE format('ALTER POLICY %I ON public.%I USING (public.is_trevor()) WITH CHECK (public.is_trevor())', r.policyname, r.tablename);
    END IF;
  END LOOP;
END $$;

-- 7. In-transaction checks (abort the whole migration if anything is off).
DO $$ DECLARE bad int; BEGIN
  SELECT count(*) INTO bad FROM information_schema.role_table_grants
   WHERE table_schema='public' AND grantee='anon'
     AND table_name NOT IN ('trevor_debts','credentials_vault','hani_events','ai_messages','board_links','board_global','crm_contacts','waitlist','hudsonseed_website_assets','menu_cards','menu_profiles');
  IF bad > 0 THEN RAISE EXCEPTION 'anon grants remain on % relation privileges', bad; END IF;
  SELECT count(*) INTO bad FROM pg_policies WHERE schemaname='public' AND qual = '(auth.role() = ''authenticated''::text)'
     AND tablename NOT IN ('trevor_debts','credentials_vault');
  IF bad > 0 THEN RAISE EXCEPTION '% blanket authenticated policies remain', bad; END IF;
  IF NOT (SELECT relrowsecurity FROM pg_class WHERE oid='public.approval_log'::regclass) THEN RAISE EXCEPTION 'approval_log RLS off'; END IF;
END $$;

COMMIT;
