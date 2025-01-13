# Documentation Standards

## File Structure

1. **Organization**
   - Use clear directory structure
   - Maintain logical file hierarchy
   - Group related documentation
   - Follow consistent naming

2. **Format**
   - Use Markdown for all documentation
   - Follow consistent formatting
   - Include table of contents for long documents
   - Use appropriate headers

## Content Guidelines

1. **Clarity**
   - Write clear, concise content
   - Use proper technical terminology
   - Avoid ambiguity
   - Provide examples when helpful

2. **Completeness**
   - Cover all necessary information
   - Include context when needed
   - Document assumptions
   - Note dependencies

## Tag Usage

1. **Immutable Tags**
   ```markdown
   <INSTRUCTION immutable>
   Content that cannot be modified
   </INSTRUCTION>
   ```
   - Never modify content within these tags
   - Preserve exact formatting

2. **Append Tags**
   ```markdown
   <LOG append>
   Existing content - new content added at end
   </LOG>
   ```
   - Only add content at the end
   - Maintain existing content

3. **Prepend Tags**
   ```markdown
   <LOG prepend>
   New content added at start - existing content
   </LOG>
   ```
   - Only add content at the beginning
   - Maintain existing content

4. **Ignore Tags**
   ```markdown
   <LOG ignore>
   Content to be ignored
   </LOG>
   ```
   - Skip content within these tags
   - Do not process or modify

## Update Procedures

1. **Documentation Updates**
   - Update with code changes
   - Maintain version consistency
   - Follow change tracking procedures
   - Update related documents

2. **Review Process**
   - Verify accuracy
   - Check formatting
   - Validate links
   - Ensure completeness

## Markdown Guidelines

1. **Formatting**
   - Use proper header hierarchy
   - Include code blocks with language
   - Use lists appropriately
   - Implement tables when needed

2. **Links**
   - Use relative paths
   - Check link validity
   - Include descriptive text
   - Document external dependencies