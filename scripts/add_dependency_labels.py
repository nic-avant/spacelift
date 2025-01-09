#!/usr/bin/env python3
"""
Spacelift Stack Dependency Label Manager

This script manages dependency labels for Spacelift stacks by analyzing the dependency graph
and adding appropriate dependsOn labels. It uses the Spacelift GraphQL API's dependenciesFullGraph
field, which returns dependencies in a specific order:

1. First, all downstream dependencies (stacks that depend on us)
2. Then our own stack
3. Finally, all upstream dependencies (stacks that we depend on)

Using this ordering, the script can identify which stacks are upstream dependencies
(stacks that we depend on) and add the appropriate dependsOn labels.

Example:
    If Stack B depends on Stack C, and Stack A depends on Stack B, then:
    - Querying Stack B's dependencies returns: [A, B, C]
    - The script will add 'dependsOn:C' to Stack B's labels
    - Stack A would have 'dependsOn:B' (when run for Stack A)

Usage:
    python3 add_dependency_labels.py [--apply] [--debug]

Options:
    --apply    Actually apply the changes (default is dry run)
    --debug    Show debug information including API responses
"""

import os
import sys
import argparse
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.spacelift.main import Spacelift
from gql import gql

# TODO: Replace with command line argument
# For now, hardcoded to test with a specific stack
# This will be replaced with a command line argument when the script is ready
# to process multiple stacks
TARGET_STACK = "glbdev-use2-eks-delhi"
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
    """
    Add dependency labels to target stack based on its upstream dependencies.
    
    This script analyzes a stack's dependencies in Spacelift and adds appropriate
    dependsOn labels. It works by:
    
    1. Getting all stacks to build a mapping of IDs to names
    2. Finding the target stack we want to analyze
    3. Getting the stack's full dependency graph from Spacelift
    4. Using the ordering in dependenciesFullGraph to identify upstream dependencies:
       - Dependencies listed before our stack are downstream (they depend on us)
       - Dependencies listed after our stack are upstream (we depend on them)
    5. Creating dependsOn labels for each upstream dependency
    6. Updating the stack's labels if they've changed
    
    The script supports:
    - Dry run mode (default) to preview changes
    - Debug mode to see detailed API responses
    - Apply mode to actually make the changes
    """
    parser = argparse.ArgumentParser(description='Add dependency labels to Spacelift stacks')
    parser.add_argument('--apply', action='store_true', help='Actually apply the changes (default is dry run)')
    parser.add_argument('--debug', action='store_true', help='Show debug information')
    args = parser.parse_args()

    sl = Spacelift()
    
    # First get basic stack info - we need this to:
    # 1. Find our target stack
    # 2. Get its current labels
    # 3. Map dependency IDs to readable names
    print("Fetching stacks...")
    stacks = sl.get_stacks(query_fields=[
        "id",
        "name",
        "labels"
    ])
    
    print(f"\nFound {len(stacks)} total stacks")
    
    # Find our target stack by name
    target_stacks = [s for s in stacks if s["name"] == TARGET_STACK]
    if not target_stacks:
        print(f"Stack '{TARGET_STACK}' not found!")
        return
    
    target = target_stacks[0]
    target_id = target["id"]
    current_labels = target.get("labels", [])
    
    print(f"\nAnalyzing stack {TARGET_STACK} ({target_id})")
    print(f"Current labels: {current_labels}")
    
    # Get dependencies from Spacelift
    # The get_stack_dependencies function will use the ordering in dependenciesFullGraph
    # to determine which stacks are upstream dependencies
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
    
    # Print human-readable dependency information
    print(f"\nFound {len(dependencies)} dependencies:")
    for dep_id in dependencies:
        # Map dependency IDs to stack names for better readability
        dep_stack = next((s for s in stacks if s["id"] == dep_id), None)
        if dep_stack:
            print(f"  {dep_stack['name']} ({dep_id})")
        else:
            print(f"  Unknown stack ({dep_id})")
    
    # Create new dependsOn labels for each upstream dependency
    new_dependency_labels = [f"dependsOn:{dep_id}" for dep_id in dependencies]
    
    # Preserve non-dependency labels while replacing all dependency labels
    existing_dep_labels = [l for l in current_labels if l.startswith("dependsOn:")]
    new_labels = [l for l in current_labels if not l.startswith("dependsOn:")] + new_dependency_labels
    
    # Only update if the dependency labels have changed
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