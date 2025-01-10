#!/usr/bin/env python3
"""
Spacelift Stack Dependency Label Manager

This script manages dependency labels for Spacelift stacks by analyzing the dependency graph
and adding appropriate dependsOn labels. It uses the Spacelift GraphQL API to query both
direct dependencies (dependsOn) and reverse dependencies (isDependedOnBy).

The script analyzes the dependency relationships to identify which stacks are upstream
dependencies (stacks that we depend on) and adds the appropriate dependsOn labels.

Example:
    If Stack B depends on Stack C, and Stack A depends on Stack B, then:
    - Stack B's dependsOn field would show C
    - Stack B's isDependedOnBy field would show A
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
TARGET_STACK = "glbdev-use2-eks-delhi-airflow-02"

def get_stack_dependencies(sl: Spacelift, stack_id: str) -> list:
    """
    Get upstream dependencies for a specific stack.
    
    The function queries both direct dependencies (dependsOn) and reverse dependencies
    (isDependedOnBy) to build a complete picture of the dependency graph. The upstream
    dependencies are those stacks that our target stack directly depends on.
    
    For example, if we have:
    - Stack A depends on Stack B
    - Stack B depends on Stack C
    Then:
    - Stack B's dependsOn would show C
    - Stack B's isDependedOnBy would show A
    
    Args:
        sl: Spacelift client instance
        stack_id: ID of the stack to get dependencies for
        
    Returns:
        List of stack IDs that are upstream dependencies (stacks that we depend on)
    """
    # Query both the stack's basic info and its dependencies
    query = gql("""
    fragment stackVendorConfig on Stack {
  vendorConfig {
    __typename
    ... on StackConfigVendorPulumi {
      loginURL
      stackName
      __typename
    }
    ... on StackConfigVendorTerraform {
      version
      workspace
      useSmartSanitization
      externalStateAccessEnabled
      workflowTool
      __typename
    }
    ... on StackConfigVendorCloudFormation {
      stackName
      entryTemplateFile
      templateBucket
      region
      __typename
    }
    ... on StackConfigVendorKubernetes {
      namespace
      kubectlVersion
      kubernetesWorkflowTool
      __typename
    }
    ... on StackConfigVendorAnsible {
      playbook
      __typename
    }
    ... on StackConfigVendorTerragrunt {
      terraformVersion
      terragruntVersion
      tool
      effectiveVersions {
        effectiveTerragruntVersion
        effectiveTerraformVersion
        __typename
      }
      useRunAll
      useSmartSanitization
      __typename
    }
  }
  __typename
}

query GetStack($id: ID!) {
  stack(id: $id) {
    administrative
    id
    apiHost
    blocker {
      id
      state
      type
      __typename
    }
    branch
    blueprint {
      ulid
      name
      __typename
    }
    canWrite
    isDisabled
    isStateRollback
    dependsOn {
      id
      stack {
        id
        name
        space {
          id
          name
          accessLevel
          __typename
        }
        vendorConfig {
          __typename
        }
        __typename
      }
      dependsOnStack {
        id
        name
        space {
          id
          name
          accessLevel
          __typename
        }
        vendorConfig {
          __typename
        }
        __typename
      }
      referenceCount
      references {
        id
        inputName
        outputName
        triggerAlways
        __typename
      }
      __typename
    }
    description
    isDependedOnBy {
      id
      stack {
        id
        name
        space {
          id
          name
          accessLevel
          __typename
        }
        vendorConfig {
          __typename
        }
        __typename
      }
      dependsOnStack {
        id
        name
        space {
          id
          name
          accessLevel
          __typename
        }
        vendorConfig {
          __typename
        }
        __typename
      }
      referenceCount
      references {
        id
        inputName
        outputName
        triggerAlways
        __typename
      }
      __typename
    }
    effectiveTerraformVersion
    labels
    lockedAt
    lockedBy
    lockNote
    managesStateFile
    enableWellKnownSecretMasking
    enableSensitiveOutputUpload
    name
    namespace
    projectRoot
    provider
    repository
    repositoryURL
    runnerImage
    spaceDetails {
      id
      name
      accessLevel
      __typename
    }
    starred
    state
    stateSetAt
    trackedCommit {
      url
      hash
      __typename
    }
    trackedBranchHead {
      url
      hash
      __typename
    }
    trackedCommitSetBy
    ...stackVendorConfig
    vcsDetached
    vcsIntegration {
      id
      name
      provider
      __typename
    }
    workerPool {
      id
      name
      busyWorkers
      pendingRuns
      workers {
        id
        busy
        drained
        __typename
      }
      __typename
    }
    additionalProjectGlobs
    __typename
  }
  tier
  tierFeatures
}
    """)
    result = sl._execute(query, {"id": stack_id})
    
    if result["stack"]:
        # Print the full response in debug mode
        print(f"\nFull dependency response: {result}")
        
        # Extract direct dependencies from the dependsOn field
        # These are our upstream dependencies (stacks we depend on)
        upstream_deps = set()
        
        if result["stack"].get("dependsOn"):
            for dep in result["stack"]["dependsOn"]:
                if dep["dependsOnStack"]:
                    upstream_deps.add(dep["dependsOnStack"]["id"])
                
        return sorted(list(upstream_deps))  # Sort for consistent output
    return []

def main():
    """
    Add dependency labels to target stack based on its upstream dependencies.
    
    This script analyzes a stack's dependencies in Spacelift and adds appropriate
    dependsOn labels. It works by:
    
    1. Getting all stacks to build a mapping of IDs to names
    2. Finding the target stack we want to analyze
    3. Getting the stack's dependencies from Spacelift
    4. Identifying upstream dependencies from the dependsOn field
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