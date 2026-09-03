-- B1 hardening: Phase 6 simulation must have an initial pressure row for
-- every supported resource, not only scrap. Existing rows are preserved.
INSERT INTO regional_resource_pressure(region_id, resource_type, target_quantity, available_quantity)
SELECT r.id, resource_type, 1000, 1000
FROM world_regions r
CROSS JOIN (VALUES ('scrap'), ('fuel'), ('water')) AS resources(resource_type)
ON CONFLICT (region_id, resource_type) DO NOTHING;
