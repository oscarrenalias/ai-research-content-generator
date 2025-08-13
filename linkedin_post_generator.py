#!/usr/bin/env python3
"""
LinkedIn Post Generator with AI
Generates LinkedIn posts based on instructions and mimics user's writing style
"""

import os
import json
import random
import re
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
from strands import Agent
from strands.models.openai import OpenAIModel

# Load environment variables
load_dotenv()

class LinkedInPostGenerator:
    def __init__(self):
        self.input_dir = Path("input")
        self.posts_dir = Path("posts")
        self.templates_dir = Path("templates")
        
        # Create directories if they don't exist
        self.input_dir.mkdir(exist_ok=True)
        self.templates_dir.mkdir(exist_ok=True)
        
        # OpenAI configuration
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.default_model = os.getenv("DEFAULT_MODEL", "gpt-4o")
        self.default_temperature = float(os.getenv("DEFAULT_TEMPERATURE", "0.7"))
        self.default_max_tokens = int(os.getenv("DEFAULT_MAX_TOKENS", "1000"))
        
        # Debug flag - can be set via environment variable
        self.debug = os.getenv("DEBUG", "false").lower() in ("true", "1", "yes", "on")
        
        if not self.openai_api_key:
            raise Exception("OPENAI_API_KEY not found in .env file")
            raise Exception("OPENAI_API_KEY not found in .env file")
        
        # Initialize Strands OpenAI model and agent
        try:
            model = OpenAIModel(
                client_args={
                    "api_key": self.openai_api_key,
                    # No base_url needed for direct OpenAI endpoints
                },
                model_id=self.default_model,
                params={
                    "temperature": self.default_temperature,
                    "max_tokens": self.default_max_tokens
                }
            )
            
            self.agent = Agent(model=model)
            print("✅ Connected to OpenAI API")
            if self.debug:
                print("🐛 Debug mode enabled - will log full prompts")
        except Exception as e:
            raise Exception(f"Failed to initialize OpenAI client: {e}")
        
        # Conversation history for iterative refinement
        self.conversation_history = []
        self.selected_posts = []
        
    def read_instructions(self):
        """Read instructions from input/instructions.txt"""
        instructions_file = self.input_dir / "instructions.txt"
        
        if not instructions_file.exists():
            print(f"❌ Instructions file not found: {instructions_file}")
            print("Please create input/instructions.txt with your post instructions")
            return None
        
        try:
            with open(instructions_file, 'r', encoding='utf-8') as f:
                instructions = f.read().strip()
                
            if not instructions:
                print("⚠️ Instructions file is empty")
                return None
                
            print(f"✅ Read instructions: {len(instructions)} characters")
            return instructions
            
        except Exception as e:
            print(f"❌ Error reading instructions: {e}")
            return None
    
    def read_base_prompt(self):
        """Read base prompt from input/prompt.txt"""
        prompt_file = self.input_dir / "prompt.txt"
        
        if not prompt_file.exists():
            print(f"❌ Base prompt file not found: {prompt_file}")
            print("Please create input/prompt.txt with the base prompt")
            return None
        
        try:
            with open(prompt_file, 'r', encoding='utf-8') as f:
                prompt = f.read().strip()
                
            if not prompt:
                print("⚠️ Base prompt file is empty")
                return None
                
            print(f"✅ Read base prompt: {len(prompt)} characters")
            return prompt
            
        except Exception as e:
            print(f"❌ Error reading base prompt: {e}")
            return None
    
    def read_style_analysis(self):
        """Read style analysis from input/linkedin_style_prompt.txt"""
        style_file = self.input_dir / "linkedin_style_prompt.txt"
        
        if not style_file.exists():
            print(f"❌ Style analysis file not found: {style_file}")
            print("Please run linkedin_style_analyzer.py first to generate the style analysis")
            return None
        
        try:
            with open(style_file, 'r', encoding='utf-8') as f:
                style_analysis = f.read().strip()
                
            if not style_analysis:
                print("⚠️ Style analysis file is empty")
                return None
                
            print(f"✅ Read style analysis: {len(style_analysis)} characters")
            return style_analysis
            
        except Exception as e:
            print(f"❌ Error reading style analysis: {e}")
            return None
    
    def get_available_posts(self):
        """Get all available posts from posts/ folder"""
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
                        'full_text': content
                    })
                        
            except Exception as e:
                print(f"⚠️ Error reading post {post_file.name}: {e}")
                continue
        
        print(f"✅ Found {len(posts)} suitable posts for style reference")
        return posts
    
    def select_random_posts(self, available_posts, count=4):
        """Randomly select posts for few-shot examples"""
        if len(available_posts) == 0:
            print("❌ No posts available for few-shot examples")
            return []
        
        # Select random posts (3-4 posts for few-shot learning)
        selected_count = min(count, len(available_posts))
        selected_count = max(3, min(selected_count, 4))  # Ensure 3-4 posts
        selected = random.sample(available_posts, selected_count)
        
        print(f"🎲 Randomly selected {len(selected)} posts for few-shot examples:")
        for post in selected:
            preview = post['content'][:100] + "..." if len(post['content']) > 100 else post['content']
            print(f"   - {post['filename']}: {preview}")
        
        return selected
    
    def build_system_prompt(self, base_prompt, style_analysis, selected_posts):
        """Build the comprehensive system prompt using all input sources"""
        
        # Start with the base prompt
        system_prompt = base_prompt + "\n\n"
        
        # Add style analysis
        system_prompt += "WRITING STYLE ANALYSIS:\n"
        system_prompt += style_analysis + "\n\n"
        
        # Add example posts for few-shot learning
        system_prompt += "EXAMPLE POSTS (for few-shot learning):\n"
        system_prompt += "Study these examples to understand the user's writing patterns:\n\n"
        
        for i, post in enumerate(selected_posts, 1):
            system_prompt += f"Example {i}:\n{post['content']}\n\n"
        
        system_prompt += "Now generate a LinkedIn post following the user's instructions while matching their established style patterns."
        
        return system_prompt
    
    def generate_post(self, instructions, system_prompt, temperature=None, max_tokens=None):
        """Generate LinkedIn post using OpenAI API"""
        if temperature is None:
            temperature = self.default_temperature
        if max_tokens is None:
            max_tokens = self.default_max_tokens
            
        try:
            print(f"🤖 Generating post with temperature={temperature}, max_tokens={max_tokens}")
            
            # Create a new agent with updated parameters if they differ from defaults
            if temperature != self.default_temperature or max_tokens != self.default_max_tokens:
                model = OpenAIModel(
                    client_args={
                        "api_key": self.openai_api_key,
                    },
                    model_id=self.default_model,
                    params={
                        "temperature": temperature,
                        "max_tokens": max_tokens
                    }
                )
                agent = Agent(model=model)
            else:
                agent = self.agent
            
            # Build the full prompt
            full_prompt = f"{system_prompt}\n\nUSER INSTRUCTIONS:\n{instructions}\n\nGenerate the LinkedIn post now:"
            
            # Debug logging
            if self.debug:
                print("\n" + "="*80)
                print("🐛 DEBUG: Full prompt sent to LLM:")
                print("="*80)
                print(full_prompt)
                print("="*80)
                print(f"Model: {self.default_model}")
                print(f"Temperature: {temperature}")
                print(f"Max tokens: {max_tokens}")
                print("="*80)
            
            response = agent(full_prompt)
            
            # Handle AgentResult object properly
            if hasattr(response, 'content'):
                generated_post = response.content.strip()
            elif hasattr(response, 'text'):
                generated_post = response.text.strip()
            else:
                generated_post = str(response).strip()
            
            print("✅ Post generated successfully")
            return generated_post
            
        except Exception as e:
            print(f"❌ Error generating post: {e}")
            return None
    
    def display_post(self, post_content):
        """Display the generated post in a clear format"""
        print("\n" + "="*60)
        print("🎯 GENERATED LINKEDIN POST:")
        print("="*60)
        print(post_content)
        print("="*60)
        print(f"📊 Character count: {len(post_content)}")
        print("="*60)
    
    def get_user_feedback(self):
        """Get feedback from user about the generated post"""
        print("\n💬 What would you like to change about this post?")
        print("   Examples:")
        print("   - 'Make it shorter'")
        print("   - 'More professional tone'")  
        print("   - 'Add more hashtags'")
        print("   - 'Change the opening line'")
        print("   - 'Regenerate' (try with different style examples)")
        print("   - 'Perfect' or 'done' (if satisfied)")
        print()
        
        feedback = input("👤 Your feedback: ").strip()
        return feedback
    
    def process_feedback(self, feedback, original_instructions):
        """Process user feedback and create refinement prompt"""
        feedback_lower = feedback.lower()
        
        if feedback_lower in ['perfect', 'done', 'good', 'ok', 'looks good']:
            return None  # User is satisfied
        
        if feedback_lower == 'regenerate':
            return 'REGENERATE'  # Signal to pick new style examples
        
        # Create refinement prompt
        refinement_prompt = f"Please revise the previous post based on this feedback: {feedback}\n\nMaintain the same writing style but incorporate the requested changes."
        
        return refinement_prompt
    
    def run_interactive_session(self):
        """Run the main interactive post generation session"""
        print("LinkedIn Post Generator with AI")
        print("="*50)
        
        # Step 1: Read instructions
        instructions = self.read_instructions()
        if not instructions:
            return
        
        # Step 2: Get available posts and select random ones
        available_posts = self.get_available_posts()
        if not available_posts:
            print("❌ No posts available for style reference. Please add some posts to the posts/ folder.")
            return
        
        self.selected_posts = self.select_random_posts(available_posts)
        if not self.selected_posts:
            return
        
        # Step 3: Build system prompt with style examples
        system_prompt = self.build_system_prompt(self.selected_posts)
        
        # Step 4: Generate initial post
        current_post = self.generate_post(instructions, system_prompt)
        if not current_post:
            return
        
        # Step 5: Interactive refinement loop
        iteration = 1
        while True:
            print(f"\n🔄 Iteration {iteration}")
            self.display_post(current_post)
            
            feedback = self.get_user_feedback()
            if not feedback:
                break
                
            refinement_prompt = self.process_feedback(feedback, instructions)
            if refinement_prompt is None:
                # User is satisfied
                break
            elif refinement_prompt == 'REGENERATE':
                # Pick new style examples and regenerate
                print("🎲 Selecting new style examples...")
                self.selected_posts = self.select_random_posts(available_posts)
                system_prompt = self.build_system_prompt(self.selected_posts)
                self.conversation_history = []  # Reset conversation
                current_post = self.generate_post(instructions, system_prompt)
            else:
                # Apply refinement
                self.conversation_history.extend([
                    {"role": "assistant", "content": current_post},
                    {"role": "user", "content": refinement_prompt}
                ])
                
                current_post = self.generate_post(instructions, system_prompt)
            
            if not current_post:
                print("❌ Failed to generate refined post")
                break
                
            iteration += 1
            
            # Prevent infinite loops
            if iteration > 10:
                print("⚠️ Maximum iterations reached. Showing current version.")
                break
        
        # Step 6: Final output
        print("\n" + "🎉 FINAL LINKEDIN POST:" + "\n")
        print(current_post)
        
        # Optional: Save metadata
        self.save_session_metadata(instructions, current_post, iteration)
    
    def save_session_metadata(self, instructions, final_post, iterations):
        """Save session metadata for reference"""
        try:
            metadata = {
                'timestamp': datetime.now().isoformat(),
                'instructions': instructions,
                'final_post': final_post,
                'iterations': iterations,
                'selected_posts': [post['filename'] for post in self.selected_posts],
                'model_settings': {
                    'model': self.default_model,
                    'temperature': self.default_temperature,
                    'max_tokens': self.default_max_tokens
                }
            }
            
            # Save to a sessions file (optional)
            sessions_file = Path("generated_sessions.json")
            sessions = []
            
            if sessions_file.exists():
                with open(sessions_file, 'r', encoding='utf-8') as f:
                    sessions = json.load(f)
            
            sessions.append(metadata)
            
            with open(sessions_file, 'w', encoding='utf-8') as f:
                json.dump(sessions, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"⚠️ Could not save session metadata: {e}")

    def run_simple_generation(self):
        """Run simple post generation using all input files"""
        print("LinkedIn Post Generator with AI")
        print("="*50)
        
        # Step 1: Read all input files
        instructions = self.read_instructions()
        if not instructions:
            return
        
        base_prompt = self.read_base_prompt()
        if not base_prompt:
            return
            
        style_analysis = self.read_style_analysis()
        if not style_analysis:
            return
        
        # Step 2: Get available posts and select 3-4 random ones
        available_posts = self.get_available_posts()
        if not available_posts:
            print("❌ No posts available for few-shot examples. Please add some posts to the posts/ folder.")
            return
        
        selected_posts = self.select_random_posts(available_posts, count=4)
        if not selected_posts:
            return
        
        # Step 3: Build comprehensive system prompt
        system_prompt = self.build_system_prompt(base_prompt, style_analysis, selected_posts)
        
        # Step 4: Generate post
        generated_post = self.generate_post(instructions, system_prompt)
        
        if generated_post:
            # Step 5: Output to stdout
            print("\n" + "="*80)
            print("🎯 GENERATED LINKEDIN POST:")
            print("="*80)
            print(generated_post)
            print("="*80)
            print(f"📊 Character count: {len(generated_post)}")
            print("="*80)
        else:
            print("❌ Failed to generate post")

def main():
    try:
        generator = LinkedInPostGenerator()
        generator.run_simple_generation()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nMake sure you have:")
        print("1. OPENAI_API_KEY in your .env file")
        print("2. input/instructions.txt with your post instructions")
        print("3. input/prompt.txt with the base prompt")
        print("4. input/linkedin_style_prompt.txt with style analysis")
        print("5. Posts in posts/ folder for few-shot examples")
        print("\nTip: Set DEBUG=true in .env or run with DEBUG=true to see full prompts")

if __name__ == "__main__":
    main()
