# ✅ **TODO: Call Graph Schema + UI using LadybugDB + Streamlit**

---

# **1. PROJECT GOAL**

* Loads a call graph (JSON → LadybugDB)
* Stores it in a clean, efficient **Function node + CALLS edge schema**
* Provides a **Streamlit UI** for:

  * Searching functions
  * Viewing call tree with depth
  * Viewing call edges in table form
  * Exporting any subgraph to JSON

---

# **2. SCHEMA DESIGN**

## **2.1 Node Type**

### **FUNCTION Node**

Attributes:

* `id` (string/int)
* `name`
* `mangled_name` (optional)
* `file`
* `line`
* `return_type`
* `params` (list of types)
* `visibility` (public/private/static)
* `is_static` (bool)
* `language`
* `fan_in` (optional)
* `fan_out` (optional)

---

## **2.2 Edge Type**

### **CALLS Edge** (Function → Function)

All callsite info is stored here.

Attributes:

* `direct` (bool)
* `indirect` (bool)
* `via_function_pointer` (bool)
* `resolution_method` (“static” / “dynamic”)
* `file` (file where call occurs)
* `line` (line of call)
* `depth` (call-tree depth, optionally computed later)
* `callsite_id` (optional unique string)

---

# **3. JSON → GRAPHDB Layer **

### Tasks

* [ ] Define a loader function: `load_from_json(json_file)`
* [ ] Insert FUNCTION nodes
* [ ] Insert CALLS edges with attributes
* [ ] Validate graph structure after load:

  * check missing callees
  * report orphan nodes
  * handle duplicates

### Action Items

* [ ] Create a minimal example JSON
* [ ] Write a verification script printing:

  * number of functions
  * number of edges
  * top 10 functions by fan-out

---

# **4. BACKEND QUERY FUNCTIONS (DB Layer)**

Implement the following helper APIs:

---

## **4.1 Function Search**

* [ ] `search_functions(name_substring)`
* [ ] Support fuzzy search
* [ ] Return list of function nodes + file + line

---

## **4.2 Call Tree Query**

* [ ] `get_call_tree(root_function, depth)`
* [ ] Use DFS/BFS
* [ ] Stop at max depth
* [ ] Handle cycles safely (mark visited)

Returns:

```
{
  "root": "...",
  "nodes": [...],
  "edges": [...]
}
```

---

## **4.3 Direct Children Query**

* [ ] `get_callees(function_name)`
  Returns:
* list of callees
* edge attributes

---

## **4.4 Subgraph Export (Later, not now)**

* [ ] `export_subgraph(function, depth)`
* [ ] Format into JSON
* [ ] Minimize fields for portability

---

# **5. STREAMlit UI DEVELOPMENT**

## **5.1 Layout Structure**

### Left Sidebar:

* Search bar
* Depth selector
* Filter:

  * direct/indirect
  * resolution method

### Main Area:

* **Top:** Function details
* **Left:** Call Tree Viewer
* **Right:** Table View
* **Bottom:** Export JSON button

---

# **6. STREAMlit UI COMPONENT TASKS**

---

## **6.1 Search Panel**

* [ ] Add text input for function name
* [ ] Display search results in table
* [ ] Allow user to select a function → loads tree

---

## **6.2 Call Tree Viewer**

### Approach:

Tasks:

* [ ] Visualize tree up to N depth
* [ ] Expand/collapse nodes
* [ ] Show attributes on hover (direct/indirect, line number, resolution)
* [ ] Click a child → reload tree from that function

---

## **6.3 Table View (Detailed Call Info)**

Columns:

* Function name
* Caller → Callee
* Direct/Indirect
* Resolution Method
* File / Line
* Depth
---



# **8. DOCUMENTATION**

* [ ] `README.md` describing:

  * schema
  * UI workflow
  * installation steps
  * sample JSON format

## Sample Call graph JSON format 
```json

{
  "functions": [
    {
      "id": "F1",
      "name": "main",
      "file": "main.c",
      "line": 10,
      "return_type": "int",
      "params": [],
      "visibility": "public",
      "is_static": false,
      "language": "c"
    },
    {
      "id": "F2",
      "name": "init",
      "file": "init.c",
      "line": 5,
      "return_type": "void",
      "params": [],
      "visibility": "private",
      "is_static": true,
      "language": "c"
    },
    {
      "id": "F3",
      "name": "load_config",
      "file": "config.c",
      "line": 20,
      "return_type": "int",
      "params": ["const char *"],
      "visibility": "public",
      "is_static": false,
      "language": "c"
    },
    {
      "id": "F4",
      "name": "run",
      "file": "run.c",
      "line": 12,
      "return_type": "void",
      "params": [],
      "visibility": "public",
      "is_static": false,
      "language": "c"
    }
  ],
  "calls": [
    {
      "caller": "F1",
      "callee": "F2",
      "attributes": {
        "direct": true,
        "indirect": false,
        "via_function_pointer": false,
        "resolution_method": "static",
        "file": "main.c",
        "line": 12,
        "depth": 1
      }
    },
    {
      "caller": "F2",
      "callee": "F3",
      "attributes": {
        "direct": true,
        "indirect": false,
        "via_function_pointer": false,
        "resolution_method": "static",
        "file": "init.c",
        "line": 7,
        "depth": 2
      }
    },
    {
      "caller": "F1",
      "callee": "F4",
      "attributes": {
        "direct": false,
        "indirect": true,
        "via_function_pointer": true,
        "resolution_method": "static",
        "file": "main.c",
        "line": 20,
        "depth": 1
      }
    }
  ]
}
```


