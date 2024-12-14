from sqlalchemy import create_engine, text
import os

# Get database URL from environment variable with a default fallback
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://hackatum:hackatum2024@localhost:5433/hackatum')

# Create engine
engine = create_engine(DATABASE_URL)

def update_scenario_id_type():
    with engine.connect() as conn:
        # First backup the scenarios table
        conn.execute(text("""
            CREATE TABLE scenarios_backup AS 
            SELECT * FROM scenarios;
        """))
        
        # Drop foreign key constraints that reference scenarios.scenario_id
        conn.execute(text("""
            ALTER TABLE customers DROP CONSTRAINT IF EXISTS customers_scenario_id_fkey;
            ALTER TABLE vehicles DROP CONSTRAINT IF EXISTS vehicles_scenario_id_fkey;
            ALTER TABLE assignments DROP CONSTRAINT IF EXISTS assignments_scenario_id_fkey;
        """))
        
        # Update the column type
        conn.execute(text("""
            ALTER TABLE scenarios 
            ALTER COLUMN scenario_id TYPE uuid USING scenario_id::uuid;
        """))
        
        # Recreate the foreign key constraints
        conn.execute(text("""
            ALTER TABLE customers 
            ADD CONSTRAINT customers_scenario_id_fkey 
            FOREIGN KEY (scenario_id) REFERENCES scenarios(scenario_id);
            
            ALTER TABLE vehicles 
            ADD CONSTRAINT vehicles_scenario_id_fkey 
            FOREIGN KEY (scenario_id) REFERENCES scenarios(scenario_id);
            
            ALTER TABLE assignments 
            ADD CONSTRAINT assignments_scenario_id_fkey 
            FOREIGN KEY (scenario_id) REFERENCES scenarios(scenario_id);
        """))
        
        conn.commit()

if __name__ == "__main__":
    update_scenario_id_type()
    print("Successfully updated scenario_id column type to UUID")
