# Development Standards for Claude 3.5

This directory contains the development standards and guidelines optimized for Claude 3.5-sonnet's capabilities. These standards ensure consistent, high-quality code generation and maintenance.

## Core Principles

1. **Systematic Approach**
   - Break down complex tasks into clear steps
   - Verify each step before proceeding
   - Maintain clear documentation of progress

2. **Code Quality**
   - Follow established coding standards
   - Implement proper error handling
   - Consider edge cases and failure modes
   - Write self-documenting code

3. **Documentation Quality**
   - Maintain clear, concise documentation
   - Update documentation with code changes
   - Follow markdown formatting standards
   - Use appropriate tags and properties

4. **Tool Usage**
   - Use appropriate tools for each task
   - Verify tool operations success
   - Handle errors gracefully
   - Document tool usage patterns

## Standards Overview

### [Coding Standards](coding.md)
- SOLID Principles
- Clean Code Practices
- Error Handling Patterns
- Testing Guidelines
- Performance Considerations
- Stack Dependency Guidelines
  - Use clear label naming (`dependsOn:stack-id`)
  - Document dependencies in stack configs
  - Avoid circular dependencies
  - Consider chain length impact

### [Documentation Standards](documentation.md)
- File Structure
- Markdown Formatting
- Tag Usage Rules
- Update Procedures

### [Workflow Standards](workflow.md)
- Temporal Best Practices
  - Keep workflows deterministic
  - Use appropriate timeouts
  - Implement proper error handling
  - Follow retry policies
- Activity Guidelines
  - Handle API rate limits
  - Implement idempotency
  - Use consistent error types
  - Log key events

## Compliance

All code generation and modifications must adhere to these standards. Review relevant documents before making changes.

## Verification

- Verify changes meet all standards
- Test modifications thoroughly
- Update documentation accordingly
- Confirm successful implementation