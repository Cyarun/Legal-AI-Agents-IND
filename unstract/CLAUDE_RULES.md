# Claude Rules for Unstract Project

## Core Principles

1. **Understand Before Acting**
   - Never make changes without fully understanding the current state
   - Document the working features first
   - Test thoroughly before claiming something is broken

2. **Documentation First**
   - Document all findings comprehensively
   - Create clear records of what works and what doesn't
   - Include evidence for any claimed issues

3. **Conservative Approach**
   - Don't fix what isn't broken
   - Verify issues multiple times before attempting fixes
   - Always preserve working functionality

4. **User Communication**
   - Listen to user feedback about working features
   - Don't contradict user observations
   - Ask for clarification when uncertain

## Workflow Rules

### When Analyzing the Application:
1. First, document what IS working
2. Test features systematically
3. Record exact error messages and contexts
4. Distinguish between configuration issues and actual bugs

### Before Making Changes:
1. Confirm the issue exists
2. Understand why it's happening
3. Document the current state
4. Get user confirmation if uncertain
5. Make minimal necessary changes

### Documentation Requirements:
- Create detailed feature documentation
- Include screenshots/output where possible
- Note dependencies and configurations
- Track version information

## Forbidden Actions

1. **Never delete or modify files without understanding their purpose**
2. **Never assume something is broken based on partial information**
3. **Never make sweeping changes to fix perceived issues**
4. **Never ignore user feedback about working features**

## Required Actions

1. **Always document findings before making changes**
2. **Always test multiple times before declaring something broken**
3. **Always preserve working configurations**
4. **Always communicate findings clearly to the user**
5. **ALWAYS check documented findings FIRST before searching again**
6. **Maintain a knowledge base of discovered information**
7. **Reference previous findings instead of re-searching**

## Search Efficiency Rules (CRITICAL - NO TOKEN WASTE)

1. **Before ANY search**:
   - Check existing documentation files FIRST
   - Reference previous findings in conversation
   - Only search if information is genuinely NOT already known

2. **Document Everything Once**:
   - Create comprehensive documentation on first discovery
   - Update documentation when new information is found
   - Never re-search what's already documented

3. **Wasting Tokens is Forbidden**:
   - Redundant searches waste user tokens
   - Re-discovering known information is unacceptable
   - Always reference documented knowledge first
   - If caught searching for already-known information, STOP immediately