# Contributing to Legal AI Agents for India

Thank you for your interest in contributing to Legal AI Agents for India! This project is maintained by **CynorSense Solutions Pvt. Ltd.** and we welcome contributions from the community to help improve and expand our legal AI frameworks.

## About the Maintainer

**CynorSense Solutions Pvt. Ltd.**  
Author: Arun R M  
Email: [email@cynorsense.com](mailto:email@cynorsense.com)  
Website: [www.cynorsense.com](https://cynorsense.com)

## Table of Contents
- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [How to Contribute](#how-to-contribute)
- [Development Guidelines](#development-guidelines)
- [Commit Guidelines](#commit-guidelines)
- [Pull Request Process](#pull-request-process)
- [Testing](#testing)
- [Documentation](#documentation)
- [Community](#community)

## Code of Conduct

By participating in this project, you agree to abide by our Code of Conduct:

- Use welcoming and inclusive language
- Be respectful of differing viewpoints and experiences
- Gracefully accept constructive criticism
- Focus on what is best for the community
- Show empathy towards other community members

## Getting Started

1. **Fork the Repository**
   ```bash
   git clone https://github.com/Cyarun/Legal-AI-Agents-IND.git
   cd Legal-AI-Agents-IND
   ```

2. **Set Up Development Environment**
   - Follow the installation instructions in the README
   - Install development dependencies
   - Set up pre-commit hooks

3. **Choose Your Area**
   - **Graphiti**: Knowledge graph framework
   - **Unstract**: Document processing platform
   - **Documentation**: Improve docs and examples
   - **Testing**: Add or improve tests

## How to Contribute

### Reporting Bugs

Before reporting a bug, please:
- Check existing issues to avoid duplicates
- Use the bug report template
- Provide detailed reproduction steps
- Include system information

### Suggesting Enhancements

- Use the feature request template
- Explain the problem your feature solves
- Provide use cases and examples
- Consider implementation complexity

### Code Contributions

1. **Find an Issue**
   - Look for issues labeled `good first issue` or `help wanted`
   - Comment on the issue to claim it
   - Ask questions if needed

2. **Create a Branch**
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/your-bug-fix
   ```

3. **Make Changes**
   - Follow the development guidelines
   - Write clean, documented code
   - Add tests for new features
   - Update documentation

## Development Guidelines

### Python Code Style

- Follow PEP 8 guidelines
- Use type hints for all functions
- Maximum line length: 88 characters (Black formatter)
- Use docstrings for all public functions

```python
def process_legal_document(
    document: str,
    model: str = "gpt-4",
    temperature: float = 0.7
) -> Dict[str, Any]:
    """
    Process a legal document using the specified model.
    
    Args:
        document: The legal document text to process
        model: The LLM model to use
        temperature: The temperature for generation
        
    Returns:
        A dictionary containing extracted entities and metadata
    """
    # Implementation
    pass
```

### TypeScript/JavaScript Code Style

- Use ESLint and Prettier
- Prefer functional components in React
- Use TypeScript for type safety
- Follow naming conventions

```typescript
interface LegalDocument {
  id: string;
  title: string;
  content: string;
  metadata: DocumentMetadata;
}

const DocumentViewer: React.FC<{ document: LegalDocument }> = ({ document }) => {
  // Component implementation
};
```

### Testing Requirements

#### Graphiti Testing
```bash
cd graphiti
make test  # Run all tests
make test-unit  # Unit tests only
make test-integration  # Integration tests
```

#### Unstract Testing
```bash
cd unstract
tox  # Run backend tests
cd frontend && npm test  # Run frontend tests
```

### Documentation Standards

- Update README if adding features
- Add docstrings to all functions
- Include examples in documentation
- Update CLAUDE.md for AI assistant context

## Commit Guidelines

We follow conventional commits:

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Test additions/changes
- `chore`: Maintenance tasks

### Examples
```
feat(graphiti): add support for custom entity types

- Implement CustomEntity class
- Add entity registration system
- Update documentation

Closes #123
```

```
fix(unstract): resolve memory leak in document processing

The document processor was not properly releasing memory
after processing large PDF files.

Fixes #456
```

## Pull Request Process

1. **Before Submitting**
   - Run all tests locally
   - Update documentation
   - Check code formatting
   - Rebase on latest main

2. **PR Description**
   - Use the PR template
   - Reference related issues
   - Describe changes clearly
   - Include screenshots if UI changes

3. **Review Process**
   - Address review comments
   - Keep PR focused and small
   - Be patient and respectful
   - Update as needed

4. **Merge Requirements**
   - All tests must pass
   - Code review approval required
   - No merge conflicts
   - Documentation updated

## Testing

### Writing Tests

#### Python Tests (pytest)
```python
def test_legal_entity_extraction():
    """Test extraction of legal entities from text."""
    text = "The Supreme Court in State of Punjab v. Rafiq Masih..."
    entities = extract_legal_entities(text)
    
    assert len(entities) > 0
    assert any(e.type == "CaseLaw" for e in entities)
```

#### JavaScript Tests (Jest)
```javascript
describe('DocumentProcessor', () => {
  it('should extract text from PDF', async () => {
    const result = await processor.extractText(pdfFile);
    expect(result.text).toBeDefined();
    expect(result.pages).toBeGreaterThan(0);
  });
});
```

### Test Coverage

- Aim for >80% code coverage
- Test edge cases and error handling
- Include integration tests
- Test with real legal documents

## Documentation

### Where to Document

1. **Code Documentation**
   - Inline comments for complex logic
   - Docstrings for all public APIs
   - Type hints and interfaces

2. **User Documentation**
   - README for overview
   - Wiki for detailed guides
   - Examples directory

3. **API Documentation**
   - OpenAPI/Swagger for REST APIs
   - GraphQL schema documentation
   - SDK documentation

### Documentation Style

- Use clear, simple language
- Include code examples
- Add diagrams where helpful
- Keep it up to date

## Community

### Communication Channels

- **GitHub Issues**: Bug reports and features
- **Discussions**: General questions and ideas
- **Pull Requests**: Code contributions

### Getting Help

- Check documentation first
- Search existing issues
- Ask in discussions
- Be specific and provide context

### Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md
- Mentioned in release notes
- Given credit in documentation

## Legal Considerations

### Licensing

- All contributions must be under MIT License
- You retain copyright of your contributions
- By contributing, you agree to the license terms

### Legal Domain Expertise

- Consult legal experts for domain-specific features
- Ensure accuracy in legal terminology
- Consider jurisdiction-specific requirements
- Respect privacy and confidentiality

## Resources

- [Project Documentation](https://github.com/Cyarun/Legal-AI-Agents-IND/wiki)
- [Indian Cyber Law Resources](https://www.meity.gov.in/)
- [Python Style Guide](https://www.python.org/dev/peps/pep-0008/)
- [TypeScript Style Guide](https://github.com/microsoft/TypeScript/wiki/Coding-guidelines)

Thank you for contributing to Legal AI Agents for India! Your efforts help build better legal technology for everyone.