#!/usr/bin/env python3

import os
import sys
import argparse
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.spacelift.main import Spacelift
from gql import gql

TARGET_STACK = "glbdev-use2-eks-delhi-airflow-01"

def get_stack_dependencies(sl: Spacelift, stack_id: str) -> list:
    """Get dependencies for a specific stack."""
    query = gql("""
    query GetStackDependencies($id: ID!) {
        stack(id: $id) {
            dependenciesFullGraph {
                stack {
                    id
                }
            }
        }
    }
    """)
    result = sl._execute(query, {"id": stack_id})
    if result["stack"]["dependenciesFullGraph"]:
        # Use a set to deduplicate dependencies and remove self-references
        deps = {dep["stack"]["id"] for dep in result["stack"]["dependenciesFullGraph"]}
        # Remove self-reference if present
        deps.discard(stack_id)
        return sorted(list(deps))  # Convert back to sorted list for consistent output
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