# Operational Constraints

## Directory Constraints
- Working Directory: Must operate from '/Users/npayne81/projects/work/spacelift'
- No directory navigation (`cd`) allowed during operations
- All paths must be relative to working directory
- Home directory references must use full path

## Tool Usage Constraints
- One tool operation per interaction
- Must wait for confirmation after each tool use
- Cannot assume success of operations without confirmation
- Must provide complete file content when writing files

## Documentation Constraints
- Must follow tag handling rules for special tags
- Cannot modify immutable content
- Must append/prepend according to tag properties
- Must ignore content within ignore tags

## Process Constraints
- Must analyze task requirements before proceeding
- Must think through steps within thinking tags
- Must verify completion criteria are met
- Must use attempt_completion tool for final results

## Communication Constraints
- Must use English language
- Must be direct and technical (no conversational language)
- Must not start responses with "Great", "Certainly", "Okay", "Sure"
- Must not end responses with open-ended questions

## Environment Awareness
- Must consider active terminal processes
- Must verify environment compatibility for commands
- Must handle file paths consistently
- Must respect current mode restrictions (architect/code)