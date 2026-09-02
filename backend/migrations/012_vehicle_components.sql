ALTER TABLE vehicles
    ADD COLUMN IF NOT EXISTS components JSONB NOT NULL DEFAULT '{"engine":{"condition":100,"max_condition":100,"armor":10},"hull":{"condition":100,"max_condition":100,"armor":25},"wheels":{"condition":100,"max_condition":100,"armor":5},"fuel_system":{"condition":100,"max_condition":100,"armor":15}}'::jsonb;
