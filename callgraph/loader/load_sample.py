"""
Load sample call graph data into KuzuDB for testing.

This script loads sample data from JSON file into the database.
"""

import json
from pathlib import Path
from callgraph.loader.db import DB

def load_sample_data(db_path: str = "test_callgraph_db"):
    """
    Load sample call graph data into database.
    
    Args:
        db_path: Path to database file
    """
    # Sample data file - go up two levels from loader directory
    current_dir = Path(__file__).parent
    project_root = current_dir.parent.parent
    sample_file = project_root / "data" / "sample_callgraph.json"
    
    if not sample_file.exists():
        print(f"Sample file not found: {sample_file}")
        return
    
    # Load JSON data
    with open(sample_file, 'r') as f:
        data = json.load(f)
    
    # Connect to database
    db = DB(db_path)
    
    # Initialize schema
    print("Initializing schema...")
    db.init_schema()
    
    # Insert functions
    print(f"Inserting {len(data['functions'])} functions...")
    for func in data['functions']:
        query = """
        CREATE (f:Function {
            id: $id,
            name: $name,
            file: $file,
            signature: $signature
        })
        """
        params = {
            'id': func['id'],
            'name': func['name'],
            'file': func.get('file', ''),
            'signature': func.get('return_type', 'void')
        }
        try:
            db.execute_write(query, params)
        except Exception as e:
            print(f"Error inserting function {func['name']}: {e}")
    
    # Insert calls with depth
    print(f"Inserting {len(data['calls'])} call relationships...")
    for call in data['calls']:
        query = """
        MATCH (caller:Function {id: $caller_id})
        MATCH (callee:Function {id: $callee_id})
        CREATE (caller)-[r:CALLS {depth: $depth}]->(callee)
        """
        # Get depth from attributes if it exists
        depth = 0
        if 'attributes' in call and 'depth' in call['attributes']:
            depth = call['attributes']['depth']
        elif 'depth' in call:
            depth = call['depth']
        
        params = {
            'caller_id': call['caller'],
            'callee_id': call['callee'],
            'depth': depth
        }
        try:
            db.execute_write(query, params)
        except Exception as e:
            print(f"Error inserting call: {e}")
    
    db.close()
    print(f"\n✓ Sample data loaded successfully to {db_path}")


if __name__ == "__main__":
    load_sample_data()
