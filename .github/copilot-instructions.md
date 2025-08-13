# LinkedIn Post Generator Project

## Project Overview

This is an AI-powered LinkedIn post generator that analyzes a user's writing style from their LinkedIn data export and generates new posts in their voice. The project uses GitHub Models API via the Strands Agents library for AI processing.

## Architecture and Structure

- **main.py**: Entry point script for running the post generator
- **linkedin_export_processor.py**: Processes LinkedIn data export files to extract post content
- **linkedin_style_analyzer.py**: Comprehensive AI-powered analysis of writing style patterns
- **linkedin_post_generator.py**: Generates new posts using learned style patterns
- **posts/**: Directory containing processed posts and generated content
- **pyproject.toml**: uv-compatible project configuration with dependencies

## Package Management

**IMPORTANT**: This project uses **uv** as the package manager, NOT pip.

### Development Commands

Always use `uv` for package management:
- **Install dependencies**: `uv sync`
- **Add new packages**: `uv add package-name`
- **Remove packages**: `uv remove package-name`
- **Run scripts**: `uv run python script.py`
- **Activate environment**: `uv shell`

### Key Dependencies

- `strands-agents[openai]>=1.4.0`: AI agent framework for GitHub Models integration
- `python-dotenv>=1.0.0`: Environment variable management

## Configuration

### Environment Variables (.env file required)

```bash
GITHUB_TOKEN=your_github_models_token
```

### GitHub Models API

- Uses GitHub Models API via Strands Agents
- Model: `gpt-4o` (not `gpt-4`)
- Requires GitHub personal access token with appropriate permissions

## Running the Application

```bash
# Install dependencies
uv sync

# Run the post generator
uv run python main.py
```

## Code Patterns

### AI Integration

- All AI interactions use the Strands Agents framework
- Import pattern: `from strands_agents.integrations.openai import OpenAIModel`
- GitHub Models endpoint: `https://models.inference.ai.azure.com`
- Always handle `AgentResult` objects returned by agents

### Error Handling

- Token limit management with fallback prompt generation
- Graceful handling of API failures
- File processing with proper error reporting

## Testing and Validation

When making changes:
1. Ensure uv sync runs without errors
2. Test with sample LinkedIn export data
3. Verify AI model responses are properly parsed
4. Check that generated posts maintain style consistency

## Common Issues

- **Token Limits**: Style analyzer includes fallback prompt generation for large datasets
- **Model Names**: Use `gpt-4o`, not `gpt-4` for GitHub Models
- **Import Errors**: Ensure `strands-agents[openai]` is installed, not just `strands-agents`
- **Environment**: Always run Python commands through `uv run`

## Development Notes

- LinkedIn API access is restricted, so the project uses data export processing instead
- Style analysis is performed in multiple stages: structural, tone, and engagement patterns
- Post generation includes interactive refinement capabilities
- All file operations assume the working directory is the project root
