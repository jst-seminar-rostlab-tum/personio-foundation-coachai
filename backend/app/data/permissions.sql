ALTER TABLE hr_information ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Allow anon read access to hr_information" ON hr_information;
CREATE POLICY "Allow anon read access to hr_information"
    ON hr_information FOR SELECT TO anon USING (true);

DROP POLICY IF EXISTS "Allow anon insert access to hr_information" ON hr_information;
CREATE POLICY "Allow anon insert access to hr_information"
    ON hr_information FOR INSERT TO anon WITH CHECK (true);

DROP POLICY IF EXISTS "Allow anon update access to hr_information" ON hr_information;
CREATE POLICY "Allow anon update access to hr_information"
    ON hr_information FOR UPDATE TO anon USING (true) WITH CHECK (true);

GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE hr_information TO anon;
