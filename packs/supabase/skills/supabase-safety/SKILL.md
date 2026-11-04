---
name: supabase-safety
description: Rules for Supabase grants, row-level security, keys and migrations. Use when writing a migration, a grant or policy, or code that creates a Supabase client.
---

# Supabase safety

First find out how the app reaches the database. Check how Supabase clients are created and which key each one uses.

## Server-only access

The app talks to Postgres only from the server (a direct connection or the service-role key on the server).

- Never grant `anon` or `authenticated` anything. Revoke what Supabase grants by default on new tables.
- A grant here makes the table readable or writable from the browser through the REST API, whatever the app's own code does.

## Client access

The browser calls Supabase with the anon key.

- Every exposed table has RLS enabled and a policy for each operation the client needs. No policy means no access, so add policies on purpose.
- A policy decides access from `auth.uid()` or a membership lookup, never from a column the client can write.
- Test each policy by signing in as a second user and proving their rows stay hidden and unwritable.

## Always

- The service-role key stays on the server. Never put it in client code or a `NEXT_PUBLIC_` / `EXPO_PUBLIC_` variable.
- Schema changes go in migration files in the repo, never as dashboard edits.
- Check the project's security advisors after a schema change when the Supabase tools are available.
