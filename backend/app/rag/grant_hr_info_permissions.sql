CREATE OR REPLACE FUNCTION grant_hr_info_permissions() RETURNS TEXT AS $$
BEGIN
    GRANT SELECT, INSERT, UPDATE ON public.hr_information TO anon;
    RETURN 'Privileges granted to role anon on public.hr_information.';
END;
$$ LANGUAGE sql;