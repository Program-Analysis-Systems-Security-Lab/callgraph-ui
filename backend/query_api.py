import kuzu

class GraphQuery:
    def __init__(self, db_path="../callgraph_db"):
        self.db = kuzu.Database(db_path)
        self.conn = kuzu.Connection(self.db)

    def search_function(self, name_pattern):
        """
        Finds a function ID by name using a WHERE clause.
        """
        query = "MATCH (f:Function) WHERE f.name CONTAINS $name RETURN f.id, f.name, f.file, f.line"
        return self.conn.execute(query, {"name": name_pattern})

    def get_call_tree(self, root_id, depth=2):
        """
        Finds the hierarchical chain of calls:
        Root -> Parent -> Child
        This preserves the structure (A calls B, B calls C).
        """
        # This query finds the root, hops 0..depth times to find a 'parent',
        # and then finds who that 'parent' calls ('child').
        query = f"""
        MATCH (root:Function)-[:Calls*0..{depth}]->(parent:Function)-[:Calls]->(child:Function)
        WHERE root.id = $root_id
        RETURN parent.name, child.name
        """
        return self.conn.execute(query, {"root_id": root_id})


if __name__ == "__main__":
    print("Testing Query API...")
    api = GraphQuery()
    
    # 1. Test Search
    print("\n--- Searching for 'task' ---")
    results = api.search_function("task")
    while results.has_next():
        print(results.get_next())

    # 2. Test Call Tree 
    
    main_results = api.search_function("main")
    if main_results.has_next():
        main_id = main_results.get_next()[0] # Get the ID of main
        print(f"\n--- Getting Call Tree for main (ID: {main_id}) ---")
        
        tree_results = api.get_call_tree(main_id, depth=2)
        while tree_results.has_next():
            row = tree_results.get_next()
            print(f"{row[0]} calls -> {row[2]}")