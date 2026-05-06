/**
 * Supabase client helpers.
 *
 * createBrowserClient — safe to call from Client Components and lib/api.ts
 * createServerClient  — ONLY call from Server Components / Server Actions
 *                       (imports next/headers which is server-only)
 */
import { createBrowserClient as createSupabaseBrowserClient } from "@supabase/ssr";

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!;
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!;

/**
 * Browser (client-side) Supabase client.
 * Safe to call from any context — does NOT import next/headers.
 */
export function createBrowserClient() {
  return createSupabaseBrowserClient(supabaseUrl, supabaseAnonKey);
}
