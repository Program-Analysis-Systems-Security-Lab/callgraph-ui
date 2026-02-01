import json
import os
import sys
import tempfile
import real_ladybug as lb

INPUT_PATH = "sample_callgraph.json"
OUTPUT_PATH = os.getenv("OUTPUT_PATH", "callgraph.lbug")

def read_json_file(path):
    with open(path, 'r') as f:
        return json.load(f)

def check_json_data(data):
    if "functions" not in data or "calls" not in data:
        print("Error: JSON needs 'functions' and 'calls'")
        sys.exit(1)

def make_function_nodes(functions):
    nodes = []
    for func in functions:
        node = {
            "id": func["id"],
            "name": func["name"],
            "file": func["file"],
            "line": func["line"],
            "return_type": func["return_type"],
            "params": func["params"],
            "visibility": func["visibility"],
            "is_static": func["is_static"],
            "language": func["language"]
        }
        nodes.append(node)
    return nodes

def make_call_edges(calls):
    edges = []
    for call in calls:
        edge = {
            "from": call["caller"],
            "to": call["callee"],
            "direct": call["attributes"]["direct"],
            "indirect": call["attributes"]["indirect"],
            "via_function_pointer": call["attributes"]["via_function_pointer"],
            "resolution_method": call["attributes"]["resolution_method"],
            "file": call["attributes"]["file"],
            "line": call["attributes"]["line"],
            "depth": call["attributes"]["depth"]
        }
        edges.append(edge)
    return edges

def write_temp_json(data, filename):
    with open(filename, 'w') as f:
        json.dump(data, f)

def setup_ladybug_db(db_path):
    db = lb.Database(db_path)
    conn = lb.Connection(db)
    return conn

def run_cypher(conn, cypher):
    try:
        conn.execute(cypher)
    except:
        pass

def create_schema(conn):
    run_cypher(conn, "INSTALL json;")
    run_cypher(conn, "LOAD json;")
    run_cypher(conn, """CREATE NODE TABLE Function (
        id STRING PRIMARY KEY, name STRING, file STRING, line INT64,
        return_type STRING, params STRING[], visibility STRING,
        is_static BOOL, language STRING);""")
    run_cypher(conn, """CREATE REL TABLE CALLS FROM Function TO Function (
        direct BOOL, indirect BOOL, via_function_pointer BOOL,
        resolution_method STRING, file STRING, line INT64, depth INT64);""")

def import_data(conn, func_file, calls_file):
    run_cypher(conn, f"COPY Function FROM '{func_file}' (HEADERS = false);")
    run_cypher(conn, f"COPY CALLS FROM '{calls_file}' (HEADERS = false);")

def print_stats(conn):
    result = conn.execute("MATCH (f:Function) RETURN count(f) AS count;")
    nodes = next(result).count
    print(f"Functions loaded: {nodes}")
    
    result = conn.execute("MATCH (:Function)-[c:CALLS]->(:Function) RETURN count(c) AS count;")
    edges = next(result).count
    print(f"CALLS relationships: {edges}")
    
    print("Top 5 functions by CALLS:")
    result = conn.execute("""
        MATCH (f:Function)-[:CALLS]->()
        RETURN f.name, count(*) AS calls
        ORDER BY calls DESC LIMIT 5;
    """)
    for row in result:
        print(f"  {row['f.name']}: {row['calls']} calls")

def main():
    data = read_json_file(INPUT_PATH)
    check_json_data(data)
    
    functions = make_function_nodes(data["functions"])
    calls = make_call_edges(data["calls"])
    
    with tempfile.TemporaryDirectory() as temp_dir:
        func_file = f"{temp_dir}/functions.json"
        calls_file = f"{temp_dir}/calls.json"
        
        write_temp_json(functions, func_file)
        write_temp_json(calls, calls_file)
        
        conn = setup_ladybug_db(OUTPUT_PATH)
        create_schema(conn)
        import_data(conn, func_file, calls_file)
        
        print_stats(conn)

if __name__ == "__main__":
    main()
