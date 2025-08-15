# LinkedIn Post Generator

## 🌟 Overview

Generate compelling posts backed with automated research based on guidance provided, written in a style that matches someone's unique writing style using AI. This tool analyzes your existing posts and creates new content that sounds authentically like you.

## Disclaimer

Yes, this was vibe coded.

### Features

- **Style Analysis**: Advanced AI-powered analysis of your writing patterns and voice
- **AI-Powered Generation**: Uses GitHub Models (OpenAI-compatible) for high-quality content creation
- **Interactive Refinement**: Get feedback and refine posts until they're perfect
- **Export Processing**: Process LinkedIn data exports to extract your posts
- **Comprehensive Style Prompts**: Generate reusable style guides for any LLM
- **Customizable**: Easy configuration for different models, temperatures, and generation settings

## 🚀 Quick Start

### Prerequisites

- Python 3.13
- Existing content (e.g., LinkedIn posts) to be analyzed for style
- An OpenAI API key
- A Tavily API key

### Setup

1. **Install dependencies**:
   ```bash
   uv sync
   ```

2. **Configure environment**:

Copy ```.env.sample``` to ```.env``` and update as needed:

These are used for post generation (writing). Use a different model or temperature if you'd like the model to get
more creative:

```
# Model configuration
DEFAULT_MODEL=gpt-4o
DEFAULT_TEMPERATURE=0.7
DEFAULT_MAX_TOKENS=8000
```

These models are used for style analysis; the first one is the model used for analyzing content provided in the posts/ folder, whereas the second is for aggregating analysis insights from batches and generating the style guide. It is recommended to use two separate models to avoid hitting token per minute quotas in the OpenAI APIs:

```
# Model for batch processing (structural, tone, engagement analysis)
ANALYZER_BATCH_MODEL=gpt-4o-mini
# Model for final synthesis and style prompt generation
ANALYZER_SYNTHESIS_MODEL=gpt-4o
```

API keys, required to connect to the OpenAI API endpoints, as well as to Tavily to perform searches:

```
# OpenAI endpoint configuration
OPENAI_API_KEY=sk-proj-xxx

# Tavily API Configuration
TAVILY_API_KEY=tvly-dev-xxx
```

3. **Enable Web Search (Optional)**:
   For real-time web search capabilities in the multi-agent system, set up Tavily API:
   
   - Visit [https://www.tavily.com/](https://www.tavily.com/)
   - Sign up for a free account
   - Navigate to the API section of your dashboard
   - Copy your API key
   - Add it to your `.env` file:
   
   ```bash
   TAVILY_API_KEY=tvly-your-actual-api-key-here
   ```

   **Features enabled with Tavily API:**
   - ✅ Real-time web searches for current trends
   - ✅ Recent statistics and data points  
   - ✅ Expert opinions from recent articles
   - ✅ Current business implications
   - ✅ LinkedIn-relevant discussion points
   - ✅ Information from the last 6 months
   
   **Note**: If not configured, the system automatically falls back to knowledge-based research using the AI model's training data.

4. **Get your LinkedIn posts**:
   - **Option A**: Use LinkedIn data export (recommended)
     - Request your data from LinkedIn Settings > Privacy > Get a copy of your data
     - Place the ZIP file in `input/` folder
     - Run: `python linkedin_export_processor.py`
   
   - **Option B**: Manually add posts
     - Create text files in the `posts/` folder
     - Each file should contain one post's content

5. **Create your instructions**:
   Edit `input/instructions.txt` with what you want your post to be about.

### Usage

**Multi-Agent Content Generation**
```bash
python linkedin_multi_agent_generator.py
```

**Post Feedback & Critique**
```bash
python linkedin_feedback_critique.py
```

**Style Analysis**

This is required to instruct the model how to write:

```bash
python linkedin_style_analyzer.py
```

The **Multi-Agent Generator** will:
1. 🔗 Analyze any URLs in your instructions for context
2. 🔍 Conduct real-time web research on your topics (with Tavily API)
3. 📝 Generate posts using specialized agents for link analysis, research, and composition
4. 🎯 Combine current web data with your personal writing style

The **Feedback & Critique Agent** will:
1. 🎯 Analyze instruction alignment and topic coverage
2. 📝 Evaluate style guide compliance and voice consistency
3. 🔍 Assess readability and accessibility for diverse audiences  
4. 📋 Review structure, length, and formatting
5. 💡 Provide specific, actionable recommendations

The **Style Analyzer** will:
1. 🔍 Perform deep analysis of all your posts
2. 📊 Extract detailed writing patterns and characteristics  
3. 🎯 Generate a comprehensive style prompt for any LLM
4. 💡 Provide quantified insights into your unique voice

## 📁 Folder Structure
```
linkedin-post-generator/
├── input/                         # Input files
│   ├── instructions.txt           # Your post instructions  
│   └── [data_export.zip]          # LinkedIn export (optional)
├── output/                        # Generated content and analysis
│   ├── result.txt                 # Generated LinkedIn post
│   ├── result-feedback.txt        # Feedback and critique analysis
│   └── result-feedback.json       # Raw feedback data (JSON)
├── posts/                         # Your existing posts (one file per post)
│   ├── post_1.txt
│   └── ...
├── agents/                        # Multi-agent system components
│   ├── __init__.py
│   ├── link_analysis_agent.py     # URL analysis and content extraction
│   ├── research_agent.py          # Real-time web research with Tavily
│   ├── post_composition_agent.py  # Final post generation
│   └── feedback_agent.py          # Post analysis and critique
├── linkedin_multi_agent_generator.py  # Multi-agent post generator (recommended)
├── linkedin_feedback_critique.py      # Independent feedback analysis tool
├── linkedin_style_analyzer.py        # Advanced style analysis tool
├── linkedin_export_processor.py      # Process LinkedIn exportss
├── .env                             # Environment variables
└── README.md                        # This file
```

## ⚙️ Model Configuration

The system supports different AI models for different tasks to optimize cost and performance:

### **Multi-Agent System Models**
Configure in your `.env` file:

```bash
# Link Analysis (web content processing, URL analysis)
LINK_ANALYSIS_MODEL=gpt-4o-mini

# Research Tasks (topic research, trend analysis, statistics gathering)  
RESEARCH_MODEL=gpt-4o-mini

# Post Composition (final content generation with style matching)
COMPOSITION_MODEL=gpt-4o
```

### **Style Analyzer Models**
```bash
# Batch Processing (structural, tone, engagement analysis)
ANALYZER_BATCH_MODEL=gpt-4o-mini

# Final Synthesis (style prompt generation)
ANALYZER_SYNTHESIS_MODEL=gpt-4o
```

### **Feedback & Critique Agent**
```bash
# Feedback Analysis (post critique, quality assessment)
FEEDBACK_MODEL=gpt-4o-mini
```

### **Model Selection Guidelines**
- **GPT-4o-mini**: Faster, cheaper, higher rate limits - ideal for bulk processing
- **GPT-4o**: Higher quality, better reasoning - use for final synthesis and style-critical tasks
- **Custom Models**: Any OpenAI-compatible model can be specified

## 📝 Tips for Better Posts

1. **Quality Reference Posts**: Ensure your existing posts in `posts/` are high-quality examples of your writing
2. **Clear Instructions**: Be specific about the topic, tone, and key points you want to cover
3. **Iterative Refinement**: Use the refinement feature to polish your posts
4. **LinkedIn Best Practices**: 
   - Keep posts between 100-1300 characters (600 is optimal)
   - Use 2-5 relevant hashtags
   - Include a call-to-action or question
   - Start with an engaging hook

## 🔧 Data Export Processing (Alternative to API)

### Step 1: Request LinkedIn Data Export
1. Go to [LinkedIn Privacy Settings - Data Export](https://www.linkedin.com/psettings/privacy/export)
2. Select the data you want to export (make sure to include "Posts")
3. Submit your request
4. Wait for LinkedIn to prepare your export (usually takes a few hours to a day)
5. Download the ZIP file when LinkedIn emails you

### Step 2: Process Your Export
1. Place the downloaded ZIP file in the `input/` folder
2. Run the processor:
   ```bash
   python linkedin_export_processor.py
   ```
3. Check the `posts/` folder for your processed posts

### Export Features
- ✅ Processes both CSV and JSON export formats
- ✅ Handles different LinkedIn export structures
- ✅ Preserves metadata (dates, engagement stats, URLs)
- ✅ Robust error handling and sanitized filenames
- ✅ Complete historical data (not just recent posts)

### Why Use Data Export Instead of API?
LinkedIn has restricted access to the `r_member_social` permission. The data export method:
- Uses LinkedIn's official export feature
- Is completely legal and compliant
- Has no rate limits or API restrictions
- Includes all metadata and engagement statistics

## 🚨 Troubleshooting

### AI Generator Issues
- **"GITHUB_TOKEN not found"**: Add your GitHub Models token to `.env` file
- **"No posts available"**: Make sure you have posts in the `posts/` folder
- **"API connection error"**: Check your GitHub Models token and internet connection
- **"Generation failed"**: Try simpler instructions or check the model configuration
- **"Package not found"**: Run `uv add <package-name>` to install missing dependencies

### Multi-Agent System Issues
- **"TAVILY_API_KEY not found"**: Add your Tavily API key to `.env` file (optional - system will fallback to knowledge-based research)
- **Web search not working**: Verify your Tavily API key at [https://www.tavily.com/](https://www.tavily.com/)
- **Multi-agent generation slow**: This is normal - the system analyzes links, conducts research, and generates posts sequentially

### Export Processor Issues  
- **"Export file not found"**: Make sure your ZIP file is in the `input/` folder
- **"No posts found"**: Check that you selected "Posts" when requesting your data export
- **Processing errors**: The script handles various export formats automatically