#!/usr/bin/env python3

import os
import sys
import argparse
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.spacelift.main import Spacelift
from gql import gql

TARGET_STACK = "glbdev-use2-eks-delhi-airflow-01"
TARGET_STACK = "global-dev"
def get_stack_dependencies(sl: Spacelift, stack_id: str) -> list:
    """
    Get upstream dependencies for a specific stack.
    
    The Spacelift GraphQL API returns dependencies in a specific order in the dependenciesFullGraph field:
    1. First, all downstream dependencies (stacks that depend on us)
    2. Then our own stack
    3. Finally, all upstream dependencies (stacks that we depend on)
    
    For example, if we have:
    - Stack A depends on Stack B
    - Stack B depends on Stack C
    Then querying Stack B's dependencies would return: [A, B, C]
    Where:
    - A is downstream (depends on B)
    - B is the current stack
    - C is upstream (B depends on C)
    
    This ordering is key to determining which stacks are upstream dependencies that we should
    add dependsOn labels for.
    
    Args:
        sl: Spacelift client instance
        stack_id: ID of the stack to get dependencies for
        
    Returns:
        List of stack IDs that are upstream dependencies (stacks that we depend on)
    """
    # Query both the stack's basic info and its full dependency graph
    query = gql("""
    query GetStackDependencies($id: ID!) {
        stack(id: $id) {
            id
            name
            dependenciesFullGraph {
                stack {
                    id
                    name
                }
            }
        }
    }
    """)
    result = sl._execute(query, {"id": stack_id})
    
    if result["stack"]["dependenciesFullGraph"]:
        # Print the full response in debug mode
        print(f"\nFull dependency response: {result}")
        
        # Get our stack name and ID for reference
        our_stack_name = result["stack"]["name"]
        our_stack_id = result["stack"]["id"]
        
        # The dependenciesFullGraph field returns dependencies in a specific order:
        # 1. Downstream dependencies (stacks that depend on us) come first
        # 2. Our own stack appears in the middle
        # 3. Upstream dependencies (stacks we depend on) come last
        
        # Find our position in the dependency list - this is the pivot point
        # Everything before this is downstream, everything after is upstream
        deps = result["stack"]["dependenciesFullGraph"]
        our_index = next(i for i, dep in enumerate(deps) if dep["stack"]["id"] == our_stack_id)
        
        # Get all dependencies that come after our position in the list
        # These are our upstream dependencies (the stacks we depend on)
        # Skip our own stack ID since we might appear multiple times
        upstream_deps = {
            dep["stack"]["id"]
            for dep in deps[our_index:]  # Take all deps from our position onwards
            if dep["stack"]["id"] != our_stack_id  # Skip ourselves
        }
                
        return sorted(list(upstream_deps))  # Sort for consistent output
    return []

def main():
    """Add dependency labels to target stack based on its dependencies."""
    parser = argparse.ArgumentParser(description='Add dependency labels to Spacelift stacks')
    parser.add_argument('--apply', action='store_true', help='Actually apply the changes (default is dry run)')
    parser.add_argument('--debug', action='store_true', help='Show debug information')
    args = parser.parse_args()

    sl = Spacelift()
    
    # First get basic stack info
    print("Fetching stacks...")
    stacks = sl.get_stacks(query_fields=[
        "id",
        "name",
        "labels"
    ])
    
    print(f"\nFound {len(stacks)} total stacks")
    
    # Find our target stack
    target_stacks = [s for s in stacks if s["name"] == TARGET_STACK]
    if not target_stacks:
        print(f"Stack '{TARGET_STACK}' not found!")
        return
    
    target = target_stacks[0]
    target_id = target["id"]
    current_labels = target.get("labels", [])
    
    print(f"\nAnalyzing stack {TARGET_STACK} ({target_id})")
    print(f"Current labels: {current_labels}")
    
    # Get actual dependencies from Spacelift
    print("\nFetching dependencies...")
    try:
        dependencies = get_stack_dependencies(sl, target_id)
        if args.debug:
            print("Raw dependencies response:", dependencies)
    except Exception as e:
        print(f"Error fetching dependencies: {e}")
        if args.debug:
            raise
        return
    
    if not dependencies:
        print("No dependencies found")
        return
    
    print(f"\nFound {len(dependencies)} dependencies:")
    for dep_id in dependencies:
        # Find stack name for this ID
        dep_stack = next((s for s in stacks if s["id"] == dep_id), None)
        if dep_stack:
            print(f"  {dep_stack['name']} ({dep_id})")
        else:
            print(f"  Unknown stack ({dep_id})")
    
    # Create dependency labels
    new_dependency_labels = [f"dependsOn:{dep_id}" for dep_id in dependencies]
    
    # Filter out existing dependency labels
    existing_dep_labels = [l for l in current_labels if l.startswith("dependsOn:")]
    new_labels = [l for l in current_labels if not l.startswith("dependsOn:")] + new_dependency_labels
    
    if set(existing_dep_labels) != set(new_dependency_labels):
        print("\nChanges needed:")
        print(f"  Current dependency labels: {existing_dep_labels}")
        print(f"  New dependency labels: {new_dependency_labels}")
        print(f"  Final labels would be: {new_labels}")
        
        if args.apply:
            try:
                result = sl.update_stack_labels(target_id, new_labels)
                print(f"  ✓ Successfully updated labels")
            except Exception as e:
                print(f"  ✗ Failed to update labels: {e}")
    else:
        print("\nNo changes needed - dependency labels are already correct")
    
    if not args.apply:
        print("\nThis was a dry run. To apply these changes, run with --apply")

if __name__ == "__main__":
    main()