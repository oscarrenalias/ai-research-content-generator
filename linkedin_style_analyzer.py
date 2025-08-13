#!/usr/bin/env python3
"""LinkedIn Style Analyzer
Analyzes your LinkedIn posts to extract writing style patterns and generates 
a comprehensive style prompt for LLMs to replicate your voice.
Uses OpenAI API for analysis.
"""

import os
import json
import re
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
from strands import Agent
from strands.models.openai import OpenAIModel

# Load environment variables
load_dotenv()

class LinkedInStyleAnalyzer:
    def __init__(self):
        self.posts_dir = Path("posts")
        
        # OpenAI configuration
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.default_model = os.getenv("DEFAULT_MODEL", "gpt-4o")  # Use gpt-4o as default for OpenAI
        self.analysis_temperature = 0.3  # Lower temperature for more consistent analysis
        self.max_tokens = 2000  # Higher limits with OpenAI
        
        if not self.openai_api_key:
            raise Exception("OPENAI_API_KEY not found in .env file")
        
        # Initialize Strands OpenAI model and agent for direct OpenAI endpoints
        try:
            model = OpenAIModel(
                client_args={
                    "api_key": self.openai_api_key,
                    # No base_url needed for direct OpenAI endpoints
                },
                model_id=self.default_model,
                params={
                    "temperature": self.analysis_temperature,
                    "max_tokens": self.max_tokens
                }
            )
            
            self.agent = Agent(model=model)
            print("✅ Connected to OpenAI API for style analysis")
        except Exception as e:
            raise Exception(f"Failed to initialize OpenAI client: {e}")
        
        # Analysis results storage
        self.post_analyses = []
        self.aggregated_insights = {}
        self.style_prompt = ""
    
    def load_all_posts(self):
        """Load all posts from the posts directory"""
        if not self.posts_dir.exists():
            print(f"❌ Posts directory not found: {self.posts_dir}")
            return []
        
        posts = []
        for post_file in self.posts_dir.glob("*.txt"):
            try:
                with open(post_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Extract the actual post content (try structured format first, then fallback to entire content)
                content_match = re.search(r'CONTENT:\s*\n-+\s*\n(.*?)(?:\n\nRAW DATA|$)', content, re.DOTALL)
                if content_match:
                    # Structured format from LinkedIn export processor
                    post_content = content_match.group(1).strip()
                else:
                    # Fallback: use entire file content for plain .txt files
                    post_content = content.strip()
                    # Clean up common issues in plain text files
                    post_content = re.sub(r'\n\s*\n\s*\n+', '\n\n', post_content)  # Remove excessive line breaks
                    post_content = post_content.strip()
                    
                # Filter out very short posts or error posts
                if len(post_content) > 50 and not post_content.startswith("Error extracting"):
                    posts.append({
                        'filename': post_file.name,
                        'content': post_content,
                        'word_count': len(post_content.split()),
                        'char_count': len(post_content)
                    })
                    print(f"  ✅ Loaded post: {post_file.name} ({len(post_content.split())} words)")
                        
            except Exception as e:
                print(f"⚠️ Error reading post {post_file.name}: {e}")
                continue
        
        print(f"📚 Loaded {len(posts)} posts for analysis")
        return posts
    
    def create_structural_analysis_prompt(self):
        """Create prompt for analyzing structural patterns"""
        return """
Analyze the structural and formatting patterns in the following LinkedIn posts. Focus on:

STRUCTURAL ELEMENTS:
1. Sentence patterns (length, complexity - simple/compound/complex sentences)
2. Paragraph structure (single vs multi-paragraph, typical paragraph length)  
3. Use of formatting (bullet points, numbered lists, line breaks, spacing)
4. Opening patterns (questions, statements, personal anecdotes, hooks)
5. Closing patterns (call-to-action, questions, summary statements)

QUANTITATIVE METRICS:
- Average sentence length in words
- Average paragraph length in sentences
- Frequency of different sentence types
- Usage patterns of formatting elements

STRUCTURAL STYLE CHARACTERISTICS:
- How does this writer organize their thoughts?
- What structural patterns make their posts scannable?
- How do they use white space and formatting for readability?

Return your analysis in this JSON format:
{
  "sentence_analysis": {
    "avg_length": "X-Y words",
    "complexity": "primarily simple/compound/complex",
    "patterns": ["pattern1", "pattern2"]
  },
  "paragraph_structure": {
    "typical_length": "X sentences",
    "multi_paragraph_frequency": "X%", 
    "paragraph_patterns": ["pattern1", "pattern2"]
  },
  "formatting_usage": {
    "bullet_points": "frequency description",
    "line_breaks": "usage pattern",
    "spacing": "style description"
  },
  "opening_patterns": ["most common openings"],
  "closing_patterns": ["most common closings"]
}
"""
    
    def create_tone_analysis_prompt(self):
        """Create prompt for analyzing tone and voice characteristics"""
        return """
Analyze the tone, voice, and personality characteristics in the following LinkedIn posts. Focus on:

TONE CHARACTERISTICS:
1. Professional level (highly formal, professional but approachable, casual professional, etc.)
2. Emotional tone (optimistic, analytical, reflective, confident, humble, etc.)
3. Authority level (expert/thought leader, peer/colleague, learner/student)
4. Personal vs impersonal approach

VOICE PATTERNS:
1. Use of first-person vs third-person perspective
2. Personal anecdote frequency and style
3. Vulnerability vs authority balance
4. Humor or personality injection

LANGUAGE STYLE:
1. Vocabulary complexity (technical jargon, business language, conversational)
2. Industry-specific terminology usage
3. Metaphors, analogies, or storytelling devices
4. Energy level and enthusiasm patterns

Return your analysis in this JSON format:
{
  "tone_profile": {
    "professional_level": "description",
    "emotional_tone": "primary characteristics",
    "authority_style": "how they position themselves",
    "personality_traits": ["trait1", "trait2", "trait3"]
  },
  "voice_characteristics": {
    "perspective_usage": "first/third person patterns",
    "personal_sharing": "frequency and style of personal content",
    "vulnerability_balance": "how they balance personal/professional",
    "distinctive_expressions": ["phrases or styles unique to this writer"]
  },
  "language_patterns": {
    "vocabulary_level": "complexity description",
    "industry_language": "technical vs accessible",
    "rhetorical_devices": ["devices they commonly use"],
    "energy_signature": "their typical energy/enthusiasm level"
  }
}
"""
    
    def create_engagement_analysis_prompt(self):
        """Create prompt for analyzing LinkedIn engagement patterns"""
        return """
Analyze how this writer engages their LinkedIn audience based on these posts. Focus on:

ENGAGEMENT STRATEGIES:
1. Question usage (frequency, placement, types of questions)
2. Call-to-action patterns (explicit CTAs, implicit engagement invites)
3. Hashtag strategy (number used, types, professional vs trending)
4. Emoji usage (frequency, types, placement)

CONTENT ENGAGEMENT:
1. How they hook readers (opening strategies)
2. How they maintain interest (storytelling, data, examples)
3. How they encourage interaction (ending strategies)
4. Community building approaches

LINKEDIN-SPECIFIC PATTERNS:
1. Professional networking language
2. Industry thought leadership positioning
3. Value-sharing vs self-promotion balance
4. Audience addressing style (direct, inclusive, etc.)

Return your analysis in this JSON format:
{
  "engagement_tactics": {
    "question_strategy": "frequency and style of questions used",
    "cta_patterns": "how they encourage engagement", 
    "hook_techniques": ["methods used to grab attention"],
    "interaction_style": "how they invite responses"
  },
  "linkedin_optimization": {
    "hashtag_strategy": "number and types typically used",
    "emoji_usage": "frequency and style",
    "professional_positioning": "how they present expertise",
    "community_approach": "how they build connections"
  },
  "content_structure": {
    "value_delivery": "how they provide value to readers",
    "storytelling_style": "narrative patterns they use",
    "example_usage": "how they use concrete examples",
    "credibility_building": "how they establish authority"
  }
}
"""
    
    def analyze_posts_batch(self, posts, batch_size=5):
        """Analyze posts in batches using AI"""
        print(f"🔍 Starting analysis of {len(posts)} posts in batches of {batch_size}")
        
        # Create analysis prompts
        structural_prompt = self.create_structural_analysis_prompt()
        tone_prompt = self.create_tone_analysis_prompt() 
        engagement_prompt = self.create_engagement_analysis_prompt()
        
        all_analyses = {
            'structural': [],
            'tone': [],
            'engagement': []
        }
        
        # Process posts in batches
        for i in range(0, len(posts), batch_size):
            batch = posts[i:i+batch_size]
            batch_num = (i // batch_size) + 1
            total_batches = (len(posts) + batch_size - 1) // batch_size
            
            print(f"📊 Analyzing batch {batch_num}/{total_batches} ({len(batch)} posts)")
            
            # Combine batch posts for analysis
            batch_content = "\n\n" + "="*50 + "\n\n".join([
                f"POST {j+1} ({post['filename']}):\n{post['content']}" 
                for j, post in enumerate(batch)
            ])
            
            # Run three different analyses on this batch
            try:
                # Structural Analysis
                structural_analysis = self.run_analysis(structural_prompt + batch_content)
                if structural_analysis:
                    all_analyses['structural'].append(structural_analysis)
                
                # Tone Analysis  
                tone_analysis = self.run_analysis(tone_prompt + batch_content)
                if tone_analysis:
                    all_analyses['tone'].append(tone_analysis)
                
                # Engagement Analysis
                engagement_analysis = self.run_analysis(engagement_prompt + batch_content)
                if engagement_analysis:
                    all_analyses['engagement'].append(engagement_analysis)
                    
                print(f"  ✅ Completed analysis for batch {batch_num}")
                    
            except Exception as e:
                print(f"  ⚠️ Error analyzing batch {batch_num}: {e}")
                continue
        
        return all_analyses
    
    def run_analysis(self, prompt):
        """Run a single analysis using the AI"""
        try:
            system_message = "You are an expert writing style analyst. Analyze the provided LinkedIn posts and return detailed insights in the requested JSON format. Be specific and quantitative where possible."
            
            response = self.agent(f"{system_message}\n\n{prompt}")
            
            # Handle AgentResult object properly
            if hasattr(response, 'content'):
                analysis_text = response.content.strip()
            elif hasattr(response, 'text'):
                analysis_text = response.text.strip()
            else:
                analysis_text = str(response).strip()
            
            # Try to extract JSON from the response
            json_match = re.search(r'\{.*\}', analysis_text, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group())
                except json.JSONDecodeError:
                    # If JSON parsing fails, return the raw text
                    return {"raw_analysis": analysis_text}
            else:
                return {"raw_analysis": analysis_text}
                
        except Exception as e:
            print(f"  ❌ Analysis error: {e}")
            return None
    
    def aggregate_insights(self, all_analyses):
        """Aggregate insights from all batch analyses"""
        print("🔄 Aggregating insights from all analyses...")
        
        aggregation_prompt = f"""
Based on the following style analyses from multiple batches of LinkedIn posts, create a comprehensive summary of this writer's style characteristics.

ANALYSIS DATA:
{json.dumps(all_analyses, indent=2)}

Please synthesize these findings into a unified style profile. Look for:
1. Consistent patterns across batches
2. Most frequent characteristics
3. Distinctive style elements that make this writer unique
4. Quantifiable metrics where possible

Create a comprehensive style summary that captures the essence of how this person writes on LinkedIn.

Return your synthesis in this JSON format:
{{
  "style_summary": {{
    "primary_characteristics": ["top 5 most defining characteristics"],
    "structural_signature": "how they typically structure content",
    "tone_profile": "their consistent voice and tone",
    "engagement_approach": "how they connect with their audience"
  }},
  "writing_patterns": {{
    "sentence_style": "typical sentence patterns and length",
    "paragraph_approach": "how they organize thoughts",
    "formatting_preferences": "bullet points, spacing, etc.",
    "opening_signature": "how they typically start posts",
    "closing_signature": "how they typically end posts"
  }},
  "linkedin_optimization": {{
    "hashtag_strategy": "their hashtag approach",
    "emoji_usage": "how they use emojis",
    "engagement_tactics": "how they encourage interaction",
    "professional_positioning": "how they present their expertise"
  }},
  "unique_elements": ["what makes their writing distinctive"],
  "style_prompt_components": ["key elements for an LLM style prompt"]
}}
"""
        
        try:
            system_message = "You are an expert at synthesizing writing style analyses into comprehensive style profiles. Focus on identifying the most consistent and distinctive patterns."
            
            response = self.agent(f"{system_message}\n\n{aggregation_prompt}")
            
            # Handle AgentResult object properly
            if hasattr(response, 'content'):
                synthesis_text = response.content.strip()
            elif hasattr(response, 'text'):
                synthesis_text = response.text.strip()
            else:
                synthesis_text = str(response).strip()
            
            # Try to extract JSON
            json_match = re.search(r'\{.*\}', synthesis_text, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group())
                except json.JSONDecodeError:
                    return {"raw_synthesis": synthesis_text}
            else:
                return {"raw_synthesis": synthesis_text}
                
        except Exception as e:
            print(f"❌ Error aggregating insights: {e}")
            return None
    
    def generate_style_prompt(self, aggregated_insights):
        """Generate a comprehensive style prompt for LLMs"""
        print("✍️ Generating final style prompt...")
        
        # Create a more concise prompt generation request
        prompt_generation_request = f"""
Based on this LinkedIn writing style analysis, create a concise but comprehensive style prompt for LLMs.

STYLE ANALYSIS SUMMARY:
{json.dumps(aggregated_insights, indent=1)[:3000]}...

Create a practical style guide with these sections:
1. TONE & VOICE: Key characteristics for replicating their voice
2. STRUCTURE: How they organize posts (openings, body, closings)  
3. ENGAGEMENT: How they connect with audiences
4. LINKEDIN OPTIMIZATION: Hashtags, emojis, formatting patterns

Format as a clear, actionable prompt that starts with "LINKEDIN WRITING STYLE GUIDE:" and provides specific instructions for an LLM to follow when generating content in this person's voice.

Keep it concise but comprehensive - focus on the most distinctive and important elements."""
        
        try:
            system_message = "You are an expert at creating concise, actionable LLM prompts. Generate a comprehensive style guide that captures the essential elements of this person's writing voice."
            
            response = self.agent(f"{system_message}\n\n{prompt_generation_request}")
            
            # Handle AgentResult object properly
            if hasattr(response, 'content'):
                return response.content.strip()
            elif hasattr(response, 'text'):
                return response.text.strip()
            else:
                return str(response).strip()
            
        except Exception as e:
            print(f"❌ Error generating style prompt: {e}")
            
            # Fallback: Create a basic style prompt from the aggregated insights
            print("🔄 Creating fallback style prompt from analysis...")
            return self.create_fallback_style_prompt(aggregated_insights)
    
    def create_fallback_style_prompt(self, aggregated_insights):
        """Create a fallback style prompt when AI generation fails"""
        try:
            style_prompt = "LINKEDIN WRITING STYLE GUIDE:\n\n"
            
            if 'style_summary' in aggregated_insights:
                summary = aggregated_insights['style_summary']
                
                if 'tone_profile' in summary:
                    style_prompt += f"TONE & VOICE:\n{summary['tone_profile']}\n\n"
                
                if 'structural_signature' in summary:
                    style_prompt += f"STRUCTURE:\n{summary['structural_signature']}\n\n"
                
                if 'engagement_approach' in summary:
                    style_prompt += f"ENGAGEMENT:\n{summary['engagement_approach']}\n\n"
            
            if 'writing_patterns' in aggregated_insights:
                patterns = aggregated_insights['writing_patterns']
                style_prompt += "WRITING PATTERNS:\n"
                
                for key, value in patterns.items():
                    style_prompt += f"• {key.replace('_', ' ').title()}: {value}\n"
                style_prompt += "\n"
            
            if 'linkedin_optimization' in aggregated_insights:
                optimization = aggregated_insights['linkedin_optimization']
                style_prompt += "LINKEDIN OPTIMIZATION:\n"
                
                for key, value in optimization.items():
                    style_prompt += f"• {key.replace('_', ' ').title()}: {value}\n"
                style_prompt += "\n"
            
            if 'unique_elements' in aggregated_insights:
                style_prompt += "UNIQUE ELEMENTS:\n"
                for element in aggregated_insights['unique_elements']:
                    style_prompt += f"• {element}\n"
                style_prompt += "\n"
            
            style_prompt += "INSTRUCTIONS FOR LLM:\nWhen writing LinkedIn posts, follow the tone, structure, and engagement patterns described above. Maintain the professional yet approachable voice, use the specified formatting preferences, and always end with an engaging question to encourage interaction."
            
            return style_prompt
            
        except Exception as e:
            print(f"⚠️ Error creating fallback prompt: {e}")
            return "BASIC STYLE GUIDE: Professional but approachable tone, use bullet points for clarity, end with engaging questions, include 3-5 relevant hashtags."
    
    def display_results(self, posts, all_analyses, aggregated_insights, style_prompt):
        """Display the complete analysis results"""
        print("\n" + "="*80)
        print("🎯 LINKEDIN STYLE ANALYSIS COMPLETE")
        print("="*80)
        
        print(f"\n📊 ANALYSIS OVERVIEW:")
        print(f"   • Posts analyzed: {len(posts)}")
        print(f"   • Total word count: {sum(post['word_count'] for post in posts):,}")
        print(f"   • Average post length: {sum(post['word_count'] for post in posts) // len(posts)} words")
        print(f"   • Analysis batches processed: {len(all_analyses.get('structural', []))}")
        
        if aggregated_insights:
            print(f"\n🎨 STYLE INSIGHTS:")
            
            if 'style_summary' in aggregated_insights:
                summary = aggregated_insights['style_summary']
                if 'primary_characteristics' in summary:
                    print("   Primary Characteristics:")
                    for char in summary['primary_characteristics']:
                        print(f"   • {char}")
            
            if 'unique_elements' in aggregated_insights:
                print("\n   Unique Style Elements:")
                for element in aggregated_insights['unique_elements']:
                    print(f"   • {element}")
        
        if style_prompt:
            print(f"\n" + "="*80)
            print("📝 GENERATED STYLE PROMPT FOR LLM USE:")
            print("="*80)
            print(style_prompt)
            print("="*80)
        else:
            print(f"\n⚠️ Style prompt generation failed, but analysis data is available above.")
        
        print(f"\n💡 This style analysis can be used to create LinkedIn posts in your voice!")
        print(f"📅 Analysis completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Save the results to a file for reference
        self.save_analysis_results(posts, all_analyses, aggregated_insights, style_prompt)
    
    def save_analysis_results(self, posts, all_analyses, aggregated_insights, style_prompt):
        """Save analysis results to files for reference"""
        try:
            # Create input directory if it doesn't exist
            input_dir = Path("input")
            input_dir.mkdir(exist_ok=True)
            
            # Save complete analysis as JSON
            results = {
                'timestamp': datetime.now().isoformat(),
                'posts_analyzed': len(posts),
                'total_words': sum(post['word_count'] for post in posts),
                'individual_analyses': all_analyses,
                'aggregated_insights': aggregated_insights,
                'style_prompt': style_prompt
            }
            
            results_file = input_dir / 'linkedin_style_analysis_results.json'
            with open(results_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            
            print(f"💾 Complete analysis saved to: {results_file}")
            
            # Save just the style prompt as a text file if available
            if style_prompt:
                prompt_file = input_dir / 'linkedin_style_prompt.txt'
                with open(prompt_file, 'w', encoding='utf-8') as f:
                    f.write(style_prompt)
                print(f"📝 Style prompt saved to: {prompt_file}")
                
        except Exception as e:
            print(f"⚠️ Could not save analysis results: {e}")
    
    def run_complete_analysis(self):
        """Run the complete style analysis process"""
        print("🔍 LinkedIn Style Analyzer")
        print("="*50)
        
        # Step 1: Load all posts
        posts = self.load_all_posts()
        if not posts:
            print("❌ No posts found for analysis")
            return
        
        if len(posts) < 3:
            print(f"⚠️ Only {len(posts)} posts found. For better analysis, consider having at least 5-10 posts.")
        
        # Step 2: Analyze posts in batches
        all_analyses = self.analyze_posts_batch(posts)
        
        if not any(all_analyses.values()):
            print("❌ No successful analyses completed")
            return
        
        # Step 3: Aggregate insights across all analyses
        aggregated_insights = self.aggregate_insights(all_analyses)
        
        if not aggregated_insights:
            print("⚠️ Could not aggregate insights, but individual analyses completed")
            aggregated_insights = {}
        
        # Step 4: Generate comprehensive style prompt
        style_prompt = self.generate_style_prompt(aggregated_insights)
        
        # Step 5: Display complete results
        self.display_results(posts, all_analyses, aggregated_insights, style_prompt)
        
        # Store results for potential future use
        self.post_analyses = all_analyses
        self.aggregated_insights = aggregated_insights
        self.style_prompt = style_prompt

def main():
    try:
        analyzer = LinkedInStyleAnalyzer()
        analyzer.run_complete_analysis()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nMake sure you have:")
        print("1. OPENAI_API_KEY in your .env file")
        print("2. Posts in posts/ folder to analyze")

if __name__ == "__main__":
    main()
