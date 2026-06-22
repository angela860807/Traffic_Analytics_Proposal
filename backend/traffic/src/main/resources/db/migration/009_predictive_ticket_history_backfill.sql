-- ============================================================
-- 009_predictive_ticket_history_backfill.sql
-- Existing maintenance ticket history backfill.
--
-- Purpose:
-- - Tickets created before append-only history support may have no
--   maintenance_ticket_histories rows.
-- - Add one initial row per ticket so the operations UI can show a
--   server-backed timeline for existing demo data.
--
-- Safe to re-run:
-- - NOT EXISTS guard keeps this idempotent per ticket.
-- ============================================================

INSERT INTO maintenance_ticket_histories (
    maintenance_ticket_id,
    from_status,
    to_status,
    changed_by,
    note,
    changed_at
)
SELECT
    mt.id,
    NULL,
    mt.status,
    COALESCE(mt.created_by, mt.assignee_id),
    COALESCE(NULLIF(mt.action_note, ''), 'Initial maintenance ticket history backfill'),
    COALESCE(mt.created_at, CURRENT_TIMESTAMP)
FROM maintenance_tickets mt
WHERE NOT EXISTS (
    SELECT 1
    FROM maintenance_ticket_histories h
    WHERE h.maintenance_ticket_id = mt.id
);
