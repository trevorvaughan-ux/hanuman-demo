-- PROPOSED, NOT APPLIED. Part 2 of T-SEC-SUPABASE-RLS-LOCKDOWN-20261016. Do NOT apply before part 1 and before the
-- claude_grok_bridge and claude_grok_bridge_v2 edge functions are changed (they POST/GET /rest/v1/ai_messages with a
-- hardcoded anon key; both have verify_jwt=false, i.e. a public unauthenticated relay into ai_messages).
-- Fix to ship first: make those functions use Deno.env SUPABASE_SERVICE_ROLE_KEY (as card-signup does), add a shared
-- secret check, remove the hardcoded key from source, then rotate the anon key if Trevor wants it treated as exposed.
BEGIN;
DROP POLICY "Enable insert for authenticated users" ON public.ai_messages;
DROP POLICY "Enable read access for all users" ON public.ai_messages;
DROP POLICY anon_read_ai_messages ON public.ai_messages;
REVOKE ALL ON public.ai_messages FROM anon;
REVOKE TRUNCATE, REFERENCES, TRIGGER ON public.ai_messages FROM authenticated;
COMMIT;
