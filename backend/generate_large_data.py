import json
import random
import hashlib


NUM_LAYERS = 5           # Deeper recursion (Exponential growth)
BRANCH_FACTOR = 6        # Up to 6 children per node
CHAOS_FACTOR = 0.5       # 50% chance of random cross-linking 


UTILS = [
    "log_error", "malloc_safe", "free_safe", "spin_lock", "spin_unlock",
    "check_permission", "flush_buffer", "audit_event", "mutex_acquire", 
    "mutex_release", "irq_disable", "irq_enable", "panic_handler"
]


ROOT_MODULES = [
    "sys", "net", "gui", "fs", "mem", "drv", "crypto", "sched", "ipc"
]


unique_counter = 0

def get_hash(name):
    # Deterministic SHA-256 ID
    return str(int(hashlib.sha256(name.encode()).hexdigest()[:16], 16))

def generate_dataset():
    global unique_counter
    print(f"🏗️ MEGA-ARCHITECT MODE: Generating massive scale graph...")
    print(f"   - Layers: {NUM_LAYERS}")
    print(f"   - Roots: {len(ROOT_MODULES)}")
    
    functions = []
    calls = []
    func_ids = []
    util_map = {}

    # 1. CREATE UTILITY HUBS (The "Dense Centers")
    for u in UTILS:
        fid = get_hash(u)
        if fid not in func_ids:
            functions.append({
                "id": fid, 
                "name": u, 
                "file": "utils/common_core.c", 
                "line": random.randint(10, 100), 
                "params": ["void*"]
            })
            util_map[u] = fid
            func_ids.append(fid)

    # 2. RECURSIVE BRANCHING GENERATOR
    def create_branch(parent_id, current_depth, prefix):
        global unique_counter
        
        
        if current_depth > NUM_LAYERS:
            return

        
        num_children = random.randint(2, BRANCH_FACTOR)
        
        for i in range(num_children):
            unique_counter += 1
            
            
            action = random.choice(['proc', 'calc', 'parse', 'load', 'init', 'sync', 'handle', 'fetch'])
            name = f"{prefix}_{action}_{unique_counter}"
            fid = get_hash(name)
            
            
            functions.append({
                "id": fid, 
                "name": name, 
                "file": f"modules/{prefix}/layer_{current_depth}.c", 
                "line": random.randint(100, 20000), 
                "params": ["ctx_t*", "int", "char*"]
            })
            func_ids.append(fid)

            
            calls.append({
                "caller": parent_id, 
                "callee": fid, 
                "attributes": {"direct": True, "line": random.randint(100, 900)}
            })

            
            if random.random() > 0.65:
                u_target = util_map[random.choice(UTILS)]
                calls.append({
                    "caller": fid, 
                    "callee": u_target, 
                    "attributes": {"direct": True, "line": 105}
                })

            
            if random.random() < CHAOS_FACTOR and len(func_ids) > 50:
                
                random_target = random.choice(func_ids)
                if random_target != fid:
                    calls.append({
                        "caller": fid, 
                        "callee": random_target, 
                        "attributes": {"direct": False, "line": random.randint(1000, 5000)}
                    })

            
            create_branch(fid, current_depth + 1, prefix)

    
    main_id = get_hash("main")
    functions.append({"id": main_id, "name": "main", "file": "main.c", "line": 10, "params": []})
    func_ids.append(main_id)
    
    
    for root_mod in ROOT_MODULES:
        # Connect main -> module_init
        root_name = f"{root_mod}_entry"
        root_id = get_hash(root_name)
        
        functions.append({"id": root_id, "name": root_name, "file": "main.c", "line": 20, "params": []})
        func_ids.append(root_id)
        calls.append({"caller": main_id, "callee": root_id, "attributes": {"direct": True, "line": 25}})
        
        # Start the recursive growth for this module
        create_branch(root_id, 1, root_mod)

    
    data = {"functions": functions, "calls": calls}
    output_path = "../data/final_hashed_graph.json"
    
    with open(output_path, "w") as f:
        json.dump(data, f, indent=2)
        
    print(f"✅ DONE. Built {len(functions)} unique nodes and {len(calls)} connections.")
    print(f"📊 Stats: {len(functions)/len(ROOT_MODULES):.1f} nodes per module avg.")

if __name__ == "__main__":
    generate_dataset()