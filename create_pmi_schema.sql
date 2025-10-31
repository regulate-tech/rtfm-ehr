/*
-- This SQL script creates the patient_index table for the PMI database.
*/

-- We use "CREATE TABLE IF NOT EXISTS" to prevent errors if the script is run multiple times.
CREATE TABLE IF NOT EXISTS patient_index (
    -- Primary Identifier
    nhs_number VARCHAR(10) PRIMARY KEY,

    -- Patient Name
    title VARCHAR(35),
    given_name VARCHAR(100) NOT NULL,
    family_name VARCHAR(100) NOT NULL,

    -- Demographics
    date_of_birth DATE NOT NULL,
    gender VARCHAR(20),

    -- UK Address
    address_line_1 VARCHAR(255),
    address_line_2 VARCHAR(255),
    town_or_city VARCHAR(100),
    county VARCHAR(100),
    postcode VARCHAR(8),

    -- Contact Details
    phone_mobile VARCHAR(20),
    phone_home VARCHAR(20),
    email_address VARCHAR(254),

    -- Record Keeping
    -- 'TIMESTAMPTZ' stores the timestamp with time zone information (highly recommended).
    -- 'CURRENT_TIMESTAMP' automatically sets the time when the record is created.
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

/*
-- Optional: We can create a function to automatically update the 'updated_at' column
-- whenever a record is changed. This is a common and very useful pattern.
*/
CREATE OR REPLACE FUNCTION trigger_set_timestamp()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = CURRENT_TIMESTAMP;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

/*
-- And here we create the "trigger" that uses the function.
-- It fires "BEFORE UPDATE" on the patient_index table for each row.
*/
-- Drop trigger if it exists before creating (makes script re-runnable)
DROP TRIGGER IF EXISTS set_timestamp ON patient_index;

CREATE TRIGGER set_timestamp
BEFORE UPDATE ON patient_index
FOR EACH ROW
EXECUTE FUNCTION trigger_set_timestamp();
