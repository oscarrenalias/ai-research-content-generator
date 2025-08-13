# LinkedIn Post Generator

## 🌟 Overview

Generate compelling LinkedIn posts that match your unique writing style using AI. This tool analyzes your existing posts and creates new content that sounds authentically like you.

### Features

- **Style Analysis**: Advanced AI-powered analysis of your writing patterns and voice
- **AI-Powered Generation**: Uses GitHub Models (OpenAI-compatible) for high-quality content creation
- **Interactive Refinement**: Get feedback and refine posts until they're perfect
- **Export Processing**: Process LinkedIn data exports to extract your posts
- **Comprehensive Style Prompts**: Generate reusable style guides for any LLM
- **Customizable**: Easy configuration for different models, temperatures, and generation settings

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- GitHub Models API access (or compatible OpenAI API)
- Your existing LinkedIn posts (via data export or manual collection)

### Setup

1. **Install dependencies**:
   ```bash
   uv add 'strands-agents[openai]' python-dotenv
   ```

2. **Configure environment**:
   Add your GitHub Models token to `.env`:
   ```bash
   GITHUB_TOKEN=your_github_models_token_here
   ```

3. **Get your LinkedIn posts**:
   - **Option A**: Use LinkedIn data export (recommended)
     - Request your data from LinkedIn Settings > Privacy > Get a copy of your data
     - Place the ZIP file in `input/` folder
     - Run: `python linkedin_export_processor.py`
   
   - **Option B**: Manually add posts
     - Create text files in the `posts/` folder
     - Each file should contain one post's content

4. **Create your instructions**:
   Edit `input/instructions.txt` with what you want your post to be about.

### Usage

**Option A: AI-Powered Post Generation**
```bash
python linkedin_post_generator.py
```

**Option B: Advanced Style Analysis (Recommended)**
```bash
python linkedin_style_analyzer.py
```

The **Style Analyzer** will:
1. 🔍 Perform deep analysis of all your posts
2. 📊 Extract detailed writing patterns and characteristics  
3. 🎯 Generate a comprehensive style prompt for any LLM
4. 💡 Provide quantified insights into your unique voice

The **Post Generator** will:
1. 📊 Analyze your writing style from existing posts
2. 🤖 Generate a new post based on your instructions
3. 🔄 Allow you to refine and improve the post
4. 💾 Save the final result

## 📁 Folder Structure
```
linkedin-post-generator/
├── input/                    # Input files
│   ├── instructions.txt      # Your post instructions  
│   └── [data_export.zip]     # LinkedIn export (optional)
├── posts/                    # Your existing posts (one file per post)
│   ├── post_1.txt
│   └── ...
├── templates/                # AI prompt templates
│   └── linkedin_system_prompt.txt
├── linkedin_style_analyzer.py   # Advanced style analysis tool
├── linkedin_post_generator.py   # Main AI post generator
├── linkedin_export_processor.py # Process LinkedIn exports
├── test_style_analyzer.py      # Test analyzer functionality
├── config.py                 # Configuration settings
├── .env                      # Environment variables
├── STYLE_ANALYZER_GUIDE.md   # Detailed analyzer guide
└── README.md                 # This file
```

## ⚙️ Configuration

Edit `config.py` to customize:

- **Model Settings**: Change AI model, temperature, max tokens
- **Style Learning**: Adjust number of reference posts, filtering criteria  
- **Generation Options**: Refinement iterations, auto-save, display options

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

### Export Processor Issues  
- **"Export file not found"**: Make sure your ZIP file is in the `input/` folder
- **"No posts found"**: Check that you selected "Posts" when requesting your data export
- **Processing errors**: The script handles various export formats automatically

## 🤝 Contributing

Contributions welcome! Areas for improvement:
- Additional AI model providers
- Better style analysis algorithms
- Enhanced post formatting options
- LinkedIn API integration (when available)

## 📄 License

MIT License - feel free to use this for your LinkedIn content creation!

## Supported Export Formats
The script automatically detects and processes:
- CSV files with posts data
- JSON files with posts data
- Various LinkedIn export naming conventions
- Multiple file structures within exports
