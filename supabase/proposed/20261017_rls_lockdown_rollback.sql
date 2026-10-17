-- ROLLBACK for 20261017_rls_lockdown.sql. Generated from live pg_policies / role_table_grants on 2026-10-17 (read-only).
-- Before the migration: every public relation except hani_events had ALL (7) privileges for anon and authenticated.
-- hani_events (anon INSERT; authenticated DELETE,INSERT,SELECT,UPDATE) is never touched. trevor_debts/credentials_vault never touched.
-- Column-level grants were not inventoried (NOT TESTED). Run as postgres/service role.
BEGIN;

-- Restore policies first (they reference nothing new), then grants, then remove what the migration added.
CREATE POLICY "Service role full access" ON public.ai_yoga_teacher_curriculum AS PERMISSIVE FOR ALL TO public USING (true);
CREATE POLICY anon_read_blockers ON public.blockers AS PERMISSIVE FOR SELECT TO public USING (true);
CREATE POLICY allow_all ON public.claude_grok_messages AS PERMISSIVE FOR ALL TO public USING (true);
CREATE POLICY anon_read_diary ON public.diary AS PERMISSIVE FOR SELECT TO public USING (true);
CREATE POLICY trevor_all_email ON public.email_queue AS PERMISSIVE FOR ALL TO public USING (true) WITH CHECK (true);
CREATE POLICY allow_anon_read ON public.jc_schools_contacts_backup_20260521 AS PERMISSIVE FOR SELECT TO anon USING (true);
CREATE POLICY allow_anon_update ON public.jc_schools_contacts_backup_20260521 AS PERMISSIVE FOR UPDATE TO anon USING (true) WITH CHECK (true);
CREATE POLICY anon_read_leads ON public.leads AS PERMISSIVE FOR SELECT TO public USING ((auth.role() = 'anon'::text));
CREATE POLICY trevor_all_responses ON public.responses AS PERMISSIVE FOR ALL TO public USING (true) WITH CHECK (true);
CREATE POLICY trevor_all_comms ON public.school_communications AS PERMISSIVE FOR ALL TO public USING (true) WITH CHECK (true);
CREATE POLICY trevor_all ON public.schools_crm AS PERMISSIVE FOR ALL TO public USING (true) WITH CHECK (true);
CREATE POLICY trevor_all_sent ON public.sent_emails AS PERMISSIVE FOR ALL TO public USING (true) WITH CHECK (true);
CREATE POLICY anon_read_lexicon ON public.shared_lexicon AS PERMISSIVE FOR SELECT TO public USING (true);
CREATE POLICY trevor_all_teachers ON public.teacher_enrollments AS PERMISSIVE FOR ALL TO public USING (true) WITH CHECK (true);
CREATE POLICY anon_read_teachers ON public.teachers AS PERMISSIVE FOR SELECT TO public USING (true);

ALTER POLICY trevor_dashboard_all_agent_runs ON public.agent_runs USING ((auth.role() = 'authenticated'::text)) WITH CHECK ((auth.role() = 'authenticated'::text));
ALTER POLICY trevor_dashboard_all_agent_specs ON public.agent_specs USING ((auth.role() = 'authenticated'::text)) WITH CHECK ((auth.role() = 'authenticated'::text));
ALTER POLICY trevor_dashboard_all_ai_messages ON public.ai_messages USING ((auth.role() = 'authenticated'::text)) WITH CHECK ((auth.role() = 'authenticated'::text));
ALTER POLICY authenticated_all_blockers ON public.blockers USING ((auth.role() = 'authenticated'::text));
ALTER POLICY authenticated_all_diary ON public.diary USING ((auth.role() = 'authenticated'::text));
ALTER POLICY trevor_dashboard_all_districts ON public.districts USING ((auth.role() = 'authenticated'::text)) WITH CHECK ((auth.role() = 'authenticated'::text));
ALTER POLICY trevor_dashboard_all_dnc ON public.do_not_contact USING ((auth.role() = 'authenticated'::text)) WITH CHECK ((auth.role() = 'authenticated'::text));
ALTER POLICY trevor_dashboard_all_email_events ON public.email_events USING ((auth.role() = 'authenticated'::text)) WITH CHECK ((auth.role() = 'authenticated'::text));
ALTER POLICY trevor_dashboard_all_engagement ON public.engagement_pipeline USING ((auth.role() = 'authenticated'::text)) WITH CHECK ((auth.role() = 'authenticated'::text));
ALTER POLICY trevor_dashboard_all_final_test ON public.final_test_run USING ((auth.role() = 'authenticated'::text)) WITH CHECK ((auth.role() = 'authenticated'::text));
ALTER POLICY trevor_dashboard_all_grok_audit ON public.grok_audit_results USING ((auth.role() = 'authenticated'::text)) WITH CHECK ((auth.role() = 'authenticated'::text));
ALTER POLICY trevor_dashboard_all_hs_drawings ON public.hudsonseed_drawings USING ((auth.role() = 'authenticated'::text)) WITH CHECK ((auth.role() = 'authenticated'::text));
ALTER POLICY trevor_dashboard_all_hs_email_std ON public.hudsonseed_email_standards USING ((auth.role() = 'authenticated'::text)) WITH CHECK ((auth.role() = 'authenticated'::text));
ALTER POLICY trevor_dashboard_all_hs_memory ON public.hudsonseed_memory USING ((auth.role() = 'authenticated'::text)) WITH CHECK ((auth.role() = 'authenticated'::text));
ALTER POLICY trevor_dashboard_all_hs_vendors ON public.hudsonseed_vendors USING ((auth.role() = 'authenticated'::text)) WITH CHECK ((auth.role() = 'authenticated'::text));
ALTER POLICY trevor_dashboard_all_jc_schools ON public.jersey_city_schools USING ((auth.role() = 'authenticated'::text)) WITH CHECK ((auth.role() = 'authenticated'::text));
ALTER POLICY trevor_dashboard_all_leads ON public.leads USING ((auth.role() = 'authenticated'::text)) WITH CHECK ((auth.role() = 'authenticated'::text));
ALTER POLICY trevor_dashboard_all_pitches ON public.pitches USING ((auth.role() = 'authenticated'::text)) WITH CHECK ((auth.role() = 'authenticated'::text));
ALTER POLICY trevor_dashboard_read_plan15_actions ON public.plan15_actions USING ((auth.role() = 'authenticated'::text));
ALTER POLICY trevor_dashboard_read_plan15_kpis ON public.plan15_kpis USING ((auth.role() = 'authenticated'::text));
ALTER POLICY trevor_dashboard_read_plan15_months ON public.plan15_months USING ((auth.role() = 'authenticated'::text));
ALTER POLICY trevor_dashboard_read_plan15_quarters ON public.plan15_quarters USING ((auth.role() = 'authenticated'::text));
ALTER POLICY trevor_dashboard_read_plan15_weekly_quotas ON public.plan15_weekly_quotas USING ((auth.role() = 'authenticated'::text));
ALTER POLICY trevor_dashboard_all_school_crm ON public.school_crm USING ((auth.role() = 'authenticated'::text)) WITH CHECK ((auth.role() = 'authenticated'::text));
ALTER POLICY trevor_dashboard_all_school_dm ON public.school_decision_makers USING ((auth.role() = 'authenticated'::text)) WITH CHECK ((auth.role() = 'authenticated'::text));
ALTER POLICY trevor_dashboard_all_security ON public.security_incidents USING ((auth.role() = 'authenticated'::text)) WITH CHECK ((auth.role() = 'authenticated'::text));
ALTER POLICY trevor_dashboard_all_session_done ON public.session_done USING ((auth.role() = 'authenticated'::text)) WITH CHECK ((auth.role() = 'authenticated'::text));
ALTER POLICY authenticated_all_lexicon ON public.shared_lexicon USING ((auth.role() = 'authenticated'::text));
ALTER POLICY trevor_dashboard_all_system_config ON public.system_config USING ((auth.role() = 'authenticated'::text)) WITH CHECK ((auth.role() = 'authenticated'::text));
ALTER POLICY trevor_dashboard_all_task_register ON public.task_register USING ((auth.role() = 'authenticated'::text)) WITH CHECK ((auth.role() = 'authenticated'::text));
ALTER POLICY authenticated_all_teachers ON public.teachers USING ((auth.role() = 'authenticated'::text));
ALTER POLICY trevor_dashboard_all_trevor_memory ON public.trevor_memory USING ((auth.role() = 'authenticated'::text)) WITH CHECK ((auth.role() = 'authenticated'::text));
ALTER POLICY trevor_dashboard_all_vault ON public.vault_status USING ((auth.role() = 'authenticated'::text)) WITH CHECK ((auth.role() = 'authenticated'::text));

-- Remove policies the migration added.
DROP POLICY service_role_all_approval_log ON public.approval_log;
DROP POLICY service_role_all_ai_yoga_teacher_curriculum ON public.ai_yoga_teacher_curriculum;
DROP POLICY service_role_all_claude_grok_messages ON public.claude_grok_messages;
DROP POLICY service_role_all_email_queue ON public.email_queue;
DROP POLICY service_role_all_responses ON public.responses;
DROP POLICY service_role_all_school_communications ON public.school_communications;
DROP POLICY service_role_all_schools_crm ON public.schools_crm;
DROP POLICY service_role_all_sent_emails ON public.sent_emails;
DROP POLICY service_role_all_teacher_enrollments ON public.teacher_enrollments;
ALTER TABLE public.approval_log DISABLE ROW LEVEL SECURITY;

-- Restore grants exactly as they were (ALL for anon and authenticated everywhere except hani_events).
DO $$ DECLARE r record; BEGIN
  FOR r IN SELECT c.relname FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace
           WHERE n.nspname='public' AND c.relkind IN ('r','p','v','m')
             AND c.relname NOT IN ('trevor_debts','credentials_vault','hani_events') LOOP
    EXECUTE format('GRANT ALL ON public.%I TO anon, authenticated', r.relname);
  END LOOP;
END $$;

DROP FUNCTION public.is_trevor();
COMMIT;
