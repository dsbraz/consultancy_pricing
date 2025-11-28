-- Add cost_hourly_rate column to project_allocations table
-- This freezes the professional's cost at the time of allocation

ALTER TABLE project_allocations 
ADD COLUMN IF NOT EXISTS cost_hourly_rate FLOAT DEFAULT 0.0 NOT NULL;

-- Optional: Backfill existing allocations with current professional costs
-- Uncomment the following if you want to populate existing records:
-- UPDATE project_allocations pa
-- SET cost_hourly_rate = p.hourly_cost
-- FROM professionals p
-- WHERE pa.professional_id = p.id AND pa.cost_hourly_rate = 0.0;
