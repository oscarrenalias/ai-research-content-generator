#!/usr/bin/env python3
"""
LinkedIn Multi-Agent Post Generator

Main entry point for the multi-agent LinkedIn post generation system.

This system uses specialized agents working in coordination:
1. LinkAnalysisAgent - Analyzes web links in instructions  
2. ResearchAgent - Conducts topic research
3. PostCompositionAgent - Generates final posts with style matching

Orchestrated using Strands native workflow system for optimal performance.
"""

from agents import LinkedInMultiAgentGenerator


def main():
    """Run the multi-agent LinkedIn post generator"""
    print("LinkedIn Multi-Agent Post Generator")
    print("="*50)
    print("🤖 Initializing specialized agents...")
    print("🔗 Link Analysis Agent - Web content analysis")  
    print("🔍 Research Agent - Topic research and insights")
    print("✍️ Post Composition Agent - Style-matched content generation")
    print("🎼 Multi-Agent Orchestrator - Workflow coordination")
    print()
    
    try:
        # Initialize the multi-agent generator
        generator = LinkedInMultiAgentGenerator()
        
        # Generate post using coordinated agents
        print("🚀 Starting multi-agent workflow...")
        final_post = generator.generate_post(use_strands_workflow=False)  # Use sequential by default
        
        # Display final results
        print("\n" + "="*80)
        print("🎯 FINAL LINKEDIN POST:")
        print("="*80)
        print(final_post)
        print("="*80)
        print(f"📊 Character count: {len(final_post)}")
        
        # Calculate reading time (average 200 words per minute)
        word_count = len(final_post.split())
        reading_time = max(1, round(word_count / 200))
        print(f"📖 Word count: {word_count} words (~{reading_time} min read)")
        print("="*80)
        
        print("\n✅ Multi-agent post generation completed successfully!")
        print("\n💡 Tips:")
        print("   - Review the post for accuracy and tone")
        print("   - Consider adding relevant hashtags if needed")
        print("   - Check that linked content is properly referenced")
        print("   - Ensure the post matches your professional voice")
        
    except Exception as e:
        print(f"❌ Generation failed: {e}")
        print("\n🔧 Troubleshooting:")
        print("1. Check that OPENAI_API_KEY is set in .env file")
        print("2. Ensure input/instructions.txt contains your post requirements")
        print("3. Verify input/prompt.txt and input/linkedin_style_prompt.txt exist")
        print("4. Make sure posts/ folder contains example posts for style reference")
        print("5. Run 'uv sync' to ensure all dependencies are installed")
        print("\n🐛 Debug mode:")
        print("   Set DEBUG=true in .env or run with DEBUG=true for detailed logs")


if __name__ == "__main__":
    main()
