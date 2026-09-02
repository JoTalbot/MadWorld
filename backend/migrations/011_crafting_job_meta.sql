CREATE TABLE crafting_job_meta (
    job_id UUID PRIMARY KEY REFERENCES jobs(id) ON DELETE CASCADE,
    recipe_id UUID NOT NULL REFERENCES crafting_recipes(id),
    inventory_id UUID NOT NULL REFERENCES inventories(id)
);

CREATE INDEX idx_crafting_job_meta_recipe ON crafting_job_meta(recipe_id);
