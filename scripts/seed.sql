-- Demo data for the agile board: 3 engineers and a mix of tasks.
-- Run with: psql <db_url> -f scripts/seed.sql
-- Does nothing if the person table already has rows, so it is safe to re-run.

CREATE TABLE IF NOT EXISTS person (
    person_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name VARCHAR(50) NOT NULL
);

CREATE TABLE IF NOT EXISTS task (
    task_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    task_info TEXT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'Unassigned' CHECK (status IN ('Unassigned', 'In Progress', 'Done')),
    person_id INT REFERENCES person(person_id) ON DELETE SET NULL
);

DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM person) THEN
        RAISE NOTICE 'Database already has people; skipping seed.';
        RETURN;
    END IF;

    INSERT INTO person (name) VALUES
        ('Jordan Ellis'),
        ('Priya Shah'),
        ('Noah Park');

    -- NULL engineer = unassigned backlog for the manager to hand out
    INSERT INTO task (task_info, status, person_id)
    SELECT t.task_info, t.status, p.person_id
    FROM (VALUES
        ('Design database schema',             'Done',        'Jordan Ellis'),
        ('Implement summary API endpoint',     'In Progress', 'Jordan Ellis'),
        ('Add task assignment endpoint',       'Unassigned',  'Jordan Ellis'),
        ('Build manager board layout',         'Done',        'Priya Shah'),
        ('Style engineer view cards',          'In Progress', 'Priya Shah'),
        ('Make board responsive on mobile',    'Unassigned',  'Priya Shah'),
        ('Set up CI pipeline',                 'Done',        'Noah Park'),
        ('Configure EC2 deployment',           'Done',        'Noah Park'),
        ('Write pytest coverage for db layer', 'In Progress', 'Noah Park'),
        ('Write API documentation',            'Unassigned',  NULL),
        ('Add task due dates',                 'Unassigned',  NULL),
        ('Plan sprint 3 demo',                 'Unassigned',  NULL)
    ) AS t(task_info, status, engineer)
    LEFT JOIN person p ON p.name = t.engineer;

    RAISE NOTICE 'Seeded 3 engineers and 12 tasks.';
END $$;
