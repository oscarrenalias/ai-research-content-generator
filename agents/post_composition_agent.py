#!/usr/bin/env python3
"""
Post Composition Agent

Specialized agent for generating final LinkedIn posts by combining all context:
- Original instructions
- Link analysis results
- Research findings  
- User's writing style analysis
- Few-shot examples from existing posts
"""

import json
import random
import re
from pathlib import Path
from typing import Dict, List, Any
from strands import Agent


class PostCompositionAgent:
    def __init__(self, openai_api_key: str = None, model: str = None):
        """Initialize the Post Composition Agent"""
        self.input_dir = Path("input")
        self.posts_dir = Path("posts")
        
        # Use provided API key or get from environment
        if openai_api_key:
            self.openai_api_key = openai_api_key
        else:
            import os
            from dotenv import load_dotenv
            load_dotenv()
            self.openai_api_key = os.getenv("OPENAI_API_KEY")
        
        # Use provided model or get from environment
        if model:
            self.model = model
        else:
            import os
            from dotenv import load_dotenv
            load_dotenv()
            self.model = os.getenv("COMPOSITION_MODEL", "gpt-4o")
        
        if not self.openai_api_key:
            raise Exception("OPENAI_API_KEY not found. Please set it in .env file or pass it directly.")
        
        # Initialize agent with OpenAI model
        try:
            from strands.models.openai import OpenAIModel
            
            openai_model = OpenAIModel(
                client_args={"api_key": self.openai_api_key},
                model_id=self.model,
                params={"temperature": 0.7, "max_tokens": 2000}
            )
            
            self.agent = Agent(
                system_prompt="""You are an expert LinkedIn content creator specializing in generating authentic, engaging posts that perfectly match a user's writing style and voice.

Your job is to:
1. Synthesize information from multiple sources (instructions, link analysis, research, style guide)
2. Create LinkedIn posts that sound authentic and personal, not AI-generated
3. Maintain the user's specific writing style, tone, and voice patterns
4. Incorporate research findings and link insights naturally
5. Follow LinkedIn best practices for engagement
6. Create compelling, professional content that drives meaningful discussion

Key principles:
- Always match the user's established writing style exactly
- Integrate research and link content seamlessly
- Focus on professional value and insights
- Avoid obvious AI-generated language patterns
- Create content that sparks genuine professional discussion""",
                model=openai_model,
                tools=[]  # No external tools needed for composition
            )
            
            print("✅ Post Composition Agent initialized with OpenAI API")
            print(f"✍️ Using model: {self.model}")
            
        except Exception as e:
            raise Exception(f"Failed to initialize Post Composition Agent: {e}")
    
    def load_style_analysis(self) -> str:
        """Load the user's writing style analysis"""
        style_file = self.input_dir / "linkedin_style_prompt.txt"
        
        if not style_file.exists():
            print("⚠️ Style analysis not found, using generic guidelines")
            return "Write in a professional, engaging LinkedIn style."
        
        try:
            with open(style_file, 'r', encoding='utf-8') as f:
                style_analysis = f.read().strip()
            print(f"✅ Loaded style analysis ({len(style_analysis)} characters)")
            return style_analysis
        except Exception as e:
            print(f"❌ Error loading style analysis: {e}")
            return "Write in a professional, engaging LinkedIn style."
    
    def load_base_prompt(self) -> str:
        """Load the base prompt guidelines"""
        prompt_file = self.input_dir / "prompt.txt"
        
        if not prompt_file.exists():
            print("⚠️ Base prompt not found, using default")
            return "Generate an engaging LinkedIn post based on the provided instructions."
        
        try:
            with open(prompt_file, 'r', encoding='utf-8') as f:
                base_prompt = f.read().strip()
            print(f"✅ Loaded base prompt ({len(base_prompt)} characters)")
            return base_prompt
        except Exception as e:
            print(f"❌ Error loading base prompt: {e}")
            return "Generate an engaging LinkedIn post based on the provided instructions."
    
    def load_example_posts(self, count: int = 4) -> List[Dict[str, str]]:
        """Load random example posts for few-shot learning"""
        if not self.posts_dir.exists():
            print("⚠️ Posts directory not found")
            return []
        
        posts = []
        for post_file in self.posts_dir.glob("*.txt"):
            try:
                with open(post_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Extract the actual post content
                content_match = re.search(r'CONTENT:\s*\n-+\s*\n(.*?)(?:\n\nRAW DATA|$)', content, re.DOTALL)
                if content_match:
                    post_content = content_match.group(1).strip()
                else:
                    post_content = content.strip()
                    post_content = re.sub(r'\n\s*\n\s*\n+', '\n\n', post_content)
                
                # Filter suitable posts
                if len(post_content) > 50 and not post_content.startswith("Error extracting"):
                    posts.append({
                        'filename': post_file.name,
                        'content': post_content
                    })
                    
            except Exception as e:
                print(f"⚠️ Error reading post {post_file.name}: {e}")
                continue
        
        # Select random posts
        if posts:
            selected_count = min(count, len(posts))
            selected_count = max(3, min(selected_count, 4))  # 3-4 posts
            selected_posts = random.sample(posts, selected_count)
            
            print(f"📚 Selected {len(selected_posts)} example posts for style reference")
            for post in selected_posts:
                preview = post['content'][:80] + "..." if len(post['content']) > 80 else post['content']
                print(f"   - {post['filename']}: {preview}")
                
            return selected_posts
        else:
            print("⚠️ No suitable example posts found")
            return []
    
    def build_comprehensive_context(self, instructions: str, link_analysis: Dict[str, Any], research_findings: Dict[str, Any]) -> str:
        """
        Build comprehensive context from all available sources
        
        Args:
            instructions: Original user instructions
            link_analysis: Results from LinkAnalysisAgent
            research_findings: Results from ResearchAgent
            
        Returns:
            Formatted context string for the composition agent
        """
        context_parts = []
        
        # Original instructions
        context_parts.append(f"ORIGINAL INSTRUCTIONS:\n{instructions}")
        
        # Link analysis insights
        if link_analysis and link_analysis.get('successful_analyses', 0) > 0:
            context_parts.append(f"\nLINK ANALYSIS INSIGHTS:")
            context_parts.append(f"- URLs analyzed: {link_analysis.get('total_urls', 0)}")
            context_parts.append(f"- Main themes: {', '.join(link_analysis.get('aggregated_themes', []))}")
            
            # Key points from links
            key_points = link_analysis.get('all_key_points', [])
            if key_points:
                context_parts.append("- Key points from linked content:")
                for point in key_points[:5]:  # Limit to top 5 points
                    context_parts.append(f"  • {point}")
            
            # Relevant quotes
            quotes = link_analysis.get('all_quotes', [])
            if quotes:
                context_parts.append("- Relevant quotes:")
                for quote in quotes[:3]:  # Limit to top 3 quotes
                    context_parts.append(f"  • \"{quote}\"")
        
        # Research findings
        if research_findings and research_findings.get('topics_researched'):
            context_parts.append(f"\nRESEARCH INSIGHTS:")
            context_parts.append(f"- Topics researched: {', '.join(research_findings.get('topics_researched', []))}")
            
            aggregated = research_findings.get('aggregated_insights', {})
            
            # Current trends
            trends = aggregated.get('all_trends', [])
            if trends:
                context_parts.append("- Current trends:")
                for trend in trends[:4]:  # Limit to top 4 trends
                    context_parts.append(f"  • {trend}")
            
            # Key statistics
            statistics = aggregated.get('all_statistics', [])
            if statistics:
                context_parts.append("- Supporting statistics:")
                for stat in statistics[:3]:  # Limit to top 3 stats
                    context_parts.append(f"  • {stat}")
            
            # LinkedIn angles
            angles = aggregated.get('all_angles', [])
            if angles:
                context_parts.append("- Professional angles:")
                for angle in angles[:3]:  # Limit to top 3 angles
                    context_parts.append(f"  • {angle}")
            
            # Actionable insights
            insights = aggregated.get('all_actionable_insights', [])
            if insights:
                context_parts.append("- Actionable insights:")
                for insight in insights[:3]:  # Limit to top 3 insights
                    context_parts.append(f"  • {insight}")
        
        return "\n".join(context_parts)
    
    def compose_linkedin_post(self, context: Dict[str, Any], debug: bool = False) -> str:
        """
        Generate the final LinkedIn post using all available context
        
        Args:
            context: Dictionary containing all context information
            debug: If True, prints the full prompt being sent to the model
            
        Returns:
            Generated LinkedIn post
        """
        print("✍️ Composing LinkedIn post...")
        
        # Load all supporting materials
        style_analysis = self.load_style_analysis()
        base_prompt = self.load_base_prompt()
        example_posts = self.load_example_posts()
        
        # Build comprehensive context
        comprehensive_context = self.build_comprehensive_context(
            context['instructions'],
            context['link_analysis'], 
            context['research_findings']
        )
        
        # Build the complete prompt
        full_prompt = f"""{base_prompt}

WRITING STYLE GUIDE:
{style_analysis}

COMPREHENSIVE CONTEXT:
{comprehensive_context}

EXAMPLE POSTS (for style reference):
"""
        
        # Add example posts
        for i, post in enumerate(example_posts, 1):
            full_prompt += f"\nExample {i}:\n{post['content']}\n"
        
        # Add final instruction
        full_prompt += f"""
Based on all the information above, generate a LinkedIn post that:
1. Addresses the original instructions completely
2. Incorporates insights from the link analysis naturally
3. Weaves in research findings and trends seamlessly  
4. Maintains the exact writing style demonstrated in the examples
5. Creates engaging, authentic content that doesn't sound AI-generated
6. Follows LinkedIn best practices for professional engagement

Generate the LinkedIn post now:"""

        # Debug: Print the full prompt if requested
        if debug:
            print("\n" + "="*80)
            print("🐛 DEBUG: FULL PROMPT BEING SENT TO MODEL")
            print("="*80)
            print(full_prompt)
            print("="*80)
            print()

        try:
            # Generate the post
            response = self.agent(full_prompt)
            
            # Extract the generated content
            if hasattr(response, 'content'):
                generated_post = response.content.strip()
            elif hasattr(response, 'text'):
                generated_post = response.text.strip()
            else:
                generated_post = str(response).strip()
            
            print("✅ LinkedIn post composed successfully")
            return generated_post
            
        except Exception as e:
            print(f"❌ Error composing LinkedIn post: {e}")
            return f"Error generating LinkedIn post: {e}"


def main():
    """Test the PostCompositionAgent"""
    try:
        agent = PostCompositionAgent()
        
        # Test with sample context
        test_context = {
            'instructions': """Write an article about how AI is transforming industries but we can't control it properly. Focus on security risks and the concentration of AI power in few companies.""",
            'link_analysis': {
                'total_urls': 2,
                'successful_analyses': 2,
                'aggregated_themes': ['AI safety', 'Corporate control', 'Security risks'],
                'all_key_points': [
                    'AI systems are becoming more powerful but less controllable',
                    'Few companies control the AI infrastructure',
                    'Security vulnerabilities are increasing',
                    'Regulatory frameworks are lagging behind'
                ],
                'all_quotes': [
                    'The concentration of AI power in a few hands poses systemic risks',
                    'We are building systems we cannot fully understand or control'
                ]
            },
            'research_findings': {
                'topics_researched': ['AI governance', 'Corporate concentration', 'Security risks'],
                'aggregated_insights': {
                    'all_trends': [
                        'Increasing consolidation of AI capabilities in big tech',
                        'Growing regulatory scrutiny of AI systems'
                    ],
                    'all_statistics': [
                        'Top 5 companies control 80% of AI computing infrastructure',
                        'AI security incidents increased 300% in the past year'
                    ],
                    'all_angles': [
                        'Professionals need to understand AI governance implications',
                        'Business leaders must consider AI concentration risks'
                    ],
                    'all_actionable_insights': [
                        'Diversify AI vendors to reduce dependency',
                        'Invest in AI literacy and governance frameworks'
                    ]
                }
            }
        }
        
        # Test with debug enabled to see the prompt
        post = agent.compose_linkedin_post(test_context, debug=True)
        
        print("\n" + "="*60)
        print("GENERATED LINKEDIN POST")
        print("="*60)
        print(post)
        print("="*60)
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        print("Make sure OPENAI_API_KEY is set in your .env file")


if __name__ == "__main__":
    main()
