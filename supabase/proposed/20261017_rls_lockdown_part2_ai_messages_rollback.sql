-- ROLLBACK for part2 (generated from live pg_policies on 2026-10-17).
BEGIN;
CREATE POLICY "Enable insert for authenticated users" ON public.ai_messages AS PERMISSIVE FOR INSERT TO public WITH CHECK (true);
CREATE POLICY "Enable read access for all users" ON public.ai_messages AS PERMISSIVE FOR SELECT TO public USING (true);
CREATE POLICY anon_read_ai_messages ON public.ai_messages AS PERMISSIVE FOR SELECT TO public USING ((auth.role() = 'anon'::text));
GRANT ALL ON public.ai_messages TO anon, authenticated;
COMMIT;
