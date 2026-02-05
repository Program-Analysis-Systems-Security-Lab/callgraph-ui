import kuzu
import json
import os
import shutil

def build_database(json_path, db_path="callgraph_db"):
    """
    Reads a JSON call graph and loads it into a KuzuDB database at 'db_path'.
    """
    print(f"🔨 Building DB at: {db_path}")

    
    db = kuzu.Database(db_path)
    conn = kuzu.Connection(db)

    
    try:
        conn.execute("DROP TABLE Calls")
        conn.execute("DROP TABLE Function")
    except RuntimeError:
        pass 

    try:
        
        conn.execute("CREATE NODE TABLE Function(id STRING, name STRING, file STRING, line INT64, params STRING, PRIMARY KEY (id))")
        
        conn.execute("CREATE REL TABLE Calls(FROM Function TO Function, line INT64, direct BOOLEAN)")
    except Exception as e:
        print(f"⚠️ Schema warning: {e}")

    
    try:
        with open(json_path, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"❌ Error: Could not find file at {json_path}")
        return

    print(f"   📄 Found {len(data['functions'])} functions and {len(data['calls'])} calls.")

    
    print("   ... Inserting Functions")
    for func in data['functions']:
        
        params_str = ", ".join(func.get('params', []))
        
        
        safe_name = func['name'].replace("'", "")
        safe_file = func['file'].replace("'", "")

        query = f"""
        CREATE (:Function {{
            id: '{func['id']}', 
            name: '{safe_name}', 
            file: '{safe_file}', 
            line: {func['line']},
            params: '{params_str}'
        }})
        """
        try:
            conn.execute(query)
        except Exception as e:
            
            pass

    
    print("   ... Inserting Calls")
    for call in data['calls']:
        caller = call['caller']
        callee = call['callee']
        line = call['attributes'].get('line', 0)
        
        direct = str(call['attributes'].get('direct', True)).lower()

        query = f"""
        MATCH (a:Function), (b:Function)
        WHERE a.id = '{caller}' AND b.id = '{callee}'
        CREATE (a)-[:Calls {{line: {line}, direct: {direct}}}]->(b)
        """
        try:
            conn.execute(query)
        except Exception as e:
            pass

    print(f"✅ Database built successfully at: {db_path}")

if __name__ == "__main__":
    
    default_json = "../data/final_hashed_graph.json"
    build_database(default_json)