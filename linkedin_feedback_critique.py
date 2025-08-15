#!/usr/bin/env python3
"""
LinkedIn Feedback & Critique Script

Independent script for analyzing and critiquing generated LinkedIn posts.
Provides comprehensive feedback on content alignment, style compliance,
readability, and structural quality.

Usage:
    uv run python linkedin_feedback_critique.py
"""

import os
import json
import sys
from datetime import datetime
from agents.feedback_agent import FeedbackAgent


def format_feedback_output(feedback: dict) -> str:
    """Format feedback data into readable report"""
    
    output = []
    output.append("LINKEDIN POST FEEDBACK & CRITIQUE")
    output.append("=" * 80)
    output.append(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    output.append("")
    
    # Overall Assessment
    overall = feedback.get('overall_assessment', {})
    output.append("📊 OVERALL ASSESSMENT")
    output.append("-" * 40)
    output.append(f"Score: {overall.get('overall_score', 'N/A')}/10 (Grade: {overall.get('grade', 'N/A')})")
    output.append(f"Summary: {overall.get('summary', 'No summary available')}")
    output.append("")
    
    # Post Metrics
    metrics = feedback.get('post_metrics', {})
    output.append("📏 POST METRICS")
    output.append("-" * 40)
    output.append(f"Character Count: {metrics.get('character_count', 'N/A')}")
    output.append(f"Word Count: {metrics.get('word_count', 'N/A')}")
    output.append(f"Paragraph Count: {metrics.get('paragraph_count', 'N/A')}")
    output.append(f"Estimated Reading Time: {metrics.get('reading_time_minutes', 'N/A')} minute(s)")
    output.append("")
    
    # Instruction Alignment
    inst_analysis = feedback.get('instruction_alignment', {})
    if inst_analysis:
        output.append("🎯 INSTRUCTION ALIGNMENT")
        output.append("-" * 40)
        output.append(f"Score: {inst_analysis.get('alignment_score', 'N/A')}/10")
        
        topic_coverage = inst_analysis.get('topic_coverage', {})
        if topic_coverage:
            output.append(f"Topic Coverage: {topic_coverage.get('coverage_percentage', 'N/A')}%")
            
            themes_addressed = topic_coverage.get('main_themes_addressed', [])
            if themes_addressed:
                output.append(f"Themes Addressed: {', '.join(themes_addressed)}")
            
            missing_themes = topic_coverage.get('missing_themes', [])
            if missing_themes:
                output.append(f"Missing Themes: {', '.join(missing_themes)}")
        
        argument_coherence = inst_analysis.get('argument_coherence', {})
        if argument_coherence:
            output.append(f"Argument Clarity: {argument_coherence.get('main_argument_clarity', 'N/A')}")
            output.append(f"Logical Flow: {argument_coherence.get('logical_flow', 'N/A')}")
            output.append(f"Evidence Support: {argument_coherence.get('evidence_support', 'N/A')}")
        
        strengths = inst_analysis.get('key_strengths', [])
        if strengths:
            output.append("Strengths:")
            for strength in strengths[:3]:
                output.append(f"  • {strength}")
        output.append("")
    
    # Style Compliance
    style_analysis = feedback.get('style_compliance', {})
    if style_analysis:
        output.append("📝 STYLE COMPLIANCE")
        output.append("-" * 40)
        output.append(f"Score: {style_analysis.get('style_score', 'N/A')}/10")
        
        tone_analysis = style_analysis.get('tone_analysis', {})
        if tone_analysis:
            output.append(f"Tone Match: {tone_analysis.get('tone_match', 'N/A')}")
            output.append(f"Professionalism: {tone_analysis.get('professionalism', 'N/A')}")
            output.append(f"Conversational Quality: {tone_analysis.get('conversational_quality', 'N/A')}")
        
        sentence_structure = style_analysis.get('sentence_structure', {})
        if sentence_structure:
            output.append(f"Average Sentence Length: {sentence_structure.get('average_sentence_length', 'N/A')} words")
            output.append(f"Complexity Level: {sentence_structure.get('complexity_level', 'N/A')}")
        
        engagement = style_analysis.get('engagement_elements', {})
        if engagement:
            output.append(f"Rhetorical Questions: {engagement.get('rhetorical_questions', 'N/A')}")
            output.append(f"Engagement Effectiveness: {engagement.get('engagement_effectiveness', 'N/A')}")
        
        formatting = style_analysis.get('formatting', {})
        if formatting:
            output.append(f"Paragraph Structure: {formatting.get('paragraph_structure', 'N/A')}")
            output.append(f"Hashtag Usage: {formatting.get('hashtag_usage', 'N/A')}")
        output.append("")
    
    # Readability & Accessibility
    read_analysis = feedback.get('readability_accessibility', {})
    if read_analysis:
        output.append("🔍 READABILITY & ACCESSIBILITY")
        output.append("-" * 40)
        output.append(f"Score: {read_analysis.get('readability_score', 'N/A')}/10")
        
        language_clarity = read_analysis.get('language_clarity', {})
        if language_clarity:
            output.append(f"Sentence Clarity: {language_clarity.get('sentence_clarity', 'N/A')}")
            output.append(f"Word Choice: {language_clarity.get('word_choice', 'N/A')}")
            output.append(f"Jargon Balance: {language_clarity.get('jargon_balance', 'N/A')}")
        
        non_native = read_analysis.get('non_native_accessibility', {})
        if non_native:
            output.append(f"Non-native Accessibility: {non_native.get('vocabulary_complexity', 'N/A')}")
        
        flow = read_analysis.get('flow_and_coherence', {})
        if flow:
            output.append(f"Logical Progression: {flow.get('logical_progression', 'N/A')}")
            output.append(f"Transition Quality: {flow.get('transition_quality', 'N/A')}")
        output.append("")
    
    # Structural Analysis
    struct_analysis = feedback.get('structural_analysis', {})
    if struct_analysis:
        output.append("📋 STRUCTURAL ANALYSIS")
        output.append("-" * 40)
        output.append(f"Score: {struct_analysis.get('structure_score', 'N/A')}/10")
        
        length_analysis = struct_analysis.get('length_analysis', {})
        if length_analysis:
            output.append(f"Length Assessment: {length_analysis.get('length_assessment', 'N/A')}")
            output.append(f"LinkedIn Optimal: {'Yes' if length_analysis.get('optimal_for_linkedin', False) else 'No'}")
        
        paragraph_analysis = struct_analysis.get('paragraph_analysis', {})
        if paragraph_analysis:
            output.append(f"Paragraph Balance: {paragraph_analysis.get('balance_assessment', 'N/A')}")
            output.append(f"Paragraph Variety: {paragraph_analysis.get('paragraph_variety', 'N/A')}")
        
        repetition = struct_analysis.get('repetition_check', {})
        if repetition:
            output.append(f"Content Repetition: {repetition.get('content_repetition', 'N/A')}")
            output.append(f"Idea Repetition: {repetition.get('idea_repetition', 'N/A')}")
        
        flow = struct_analysis.get('structural_flow', {})
        if flow:
            output.append(f"Opening Strength: {flow.get('opening_strength', 'N/A')}")
            output.append(f"Conclusion Effectiveness: {flow.get('conclusion_effectiveness', 'N/A')}")
        output.append("")
    
    # Recommendations
    recommendations = feedback.get('recommendations', [])
    if recommendations:
        output.append("💡 RECOMMENDATIONS")
        output.append("-" * 40)
        for i, rec in enumerate(recommendations[:8], 1):
            output.append(f"{i}. {rec}")
        output.append("")
    
    # Summary
    output.append("🎯 SUMMARY")
    output.append("-" * 40)
    summary_parts = []
    
    if overall.get('overall_score'):
        summary_parts.append(f"Overall quality score of {overall['overall_score']}/10")
    
    if inst_analysis.get('alignment_score'):
        summary_parts.append(f"instruction alignment at {inst_analysis['alignment_score']}/10")
    
    if style_analysis.get('style_score'):
        summary_parts.append(f"style compliance at {style_analysis['style_score']}/10")
    
    if read_analysis.get('readability_score'):
        summary_parts.append(f"readability at {read_analysis['readability_score']}/10")
    
    if summary_parts:
        output.append(f"The post achieved {', '.join(summary_parts)}.")
    
    if recommendations:
        output.append(f"Focus on the {len(recommendations)} key recommendations above for improvement.")
    
    output.append("")
    output.append("✅ Feedback analysis completed")
    output.append("=" * 80)
    
    return "\n".join(output)


def save_feedback_to_file(feedback_text: str, filename: str = "output/result-feedback.txt"):
    """Save formatted feedback to file"""
    try:
        # Ensure output directory exists
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(feedback_text)
        
        print(f"💾 Feedback saved to: {filename}")
        return True
        
    except Exception as e:
        print(f"⚠️ Warning: Could not save feedback to file: {e}")
        return False


def main():
    """Main execution function"""
    print("LinkedIn Post Feedback & Critique Analysis")
    print("=" * 50)
    print("🔍 Analyzing generated LinkedIn post...")
    print()
    
    try:
        # Initialize feedback agent
        agent = FeedbackAgent()
        
        # Load all content files
        print("📂 Loading content files...")
        content = agent.load_content_files()
        
        # Validate required files
        if not content['generated_post']:
            print("❌ Error: No generated post found at output/result.txt")
            print("   Run the main generator first: uv run python linkedin_multi_agent_generator.py")
            sys.exit(1)
        
        if not content['instructions']:
            print("⚠️ Warning: No instructions found at input/instructions.txt")
        
        if not content['style_guide']:
            print("⚠️ Warning: No style guide found at input/linkedin_style_prompt.txt")
        
        print()
        
        # Generate comprehensive feedback
        feedback = agent.generate_comprehensive_feedback(content)
        
        # Format output
        formatted_feedback = format_feedback_output(feedback)
        
        # Display results
        print("\n" + formatted_feedback)
        
        # Save to file
        save_feedback_to_file(formatted_feedback)
        
        # Also save raw JSON for programmatic access
        json_filename = "output/result-feedback.json"
        try:
            with open(json_filename, 'w', encoding='utf-8') as f:
                json.dump(feedback, f, indent=2, ensure_ascii=False)
            print(f"📊 Raw feedback data saved to: {json_filename}")
        except Exception as e:
            print(f"⚠️ Could not save JSON feedback: {e}")
        
        # Final summary
        overall_score = feedback.get('overall_assessment', {}).get('overall_score', 0)
        grade = feedback.get('overall_assessment', {}).get('grade', 'N/A')
        
        print(f"\n🏆 Final Assessment: {overall_score}/10 (Grade: {grade})")
        
        if overall_score >= 8:
            print("🎉 Excellent post! Ready for publication with minor tweaks if needed.")
        elif overall_score >= 6:
            print("👍 Good post. Consider implementing the recommendations above.")
        elif overall_score >= 4:
            print("⚠️ Post needs improvement. Focus on the key recommendations.")
        else:
            print("❌ Post requires significant revision before publication.")
    
    except KeyboardInterrupt:
        print("\n⚠️ Analysis interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        print("\n🔧 Troubleshooting:")
        print("   - Ensure OPENAI_API_KEY is set in .env file")
        print("   - Check that output/result.txt exists (run main generator first)")
        print("   - Verify input files are accessible")
        sys.exit(1)


if __name__ == "__main__":
    main()
