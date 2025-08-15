#!/usr/bin/env python3
"""
Feedback Agent

Specialized agent for analyzing and critiquing generated LinkedIn posts.
Evaluates content against original instructions, style guide compliance,
readability, structure, and overall quality.
"""

import os
import re
import json
from typing import Dict, List, Any, Optional
from strands import Agent
from dotenv import load_dotenv


class FeedbackAgent:
    def __init__(self, model: str = None):
        """Initialize the Feedback Agent for post analysis"""
        
        # Load environment variables
        load_dotenv()
        
        # Get API key
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        if not self.openai_api_key:
            raise Exception("OPENAI_API_KEY not found. Please set it in .env file.")
        
        # Use provided model or get from environment
        self.model = model or os.getenv("FEEDBACK_MODEL", "gpt-4o-mini")
        
        # Initialize agent with OpenAI model
        try:
            from strands.models.openai import OpenAIModel
            
            openai_model = OpenAIModel(
                client_args={"api_key": self.openai_api_key},
                model_id=self.model,
                params={"temperature": 0.2, "max_tokens": 3000}  # Lower temp for consistent analysis
            )
            
            self.agent = Agent(
                system_prompt="""You are an expert LinkedIn content analyst and writing critique specialist. Your job is to:

1. Analyze LinkedIn posts for alignment with original instructions and requirements
2. Evaluate style guide compliance and consistency
3. Assess readability, clarity, and accessibility for diverse audiences
4. Review structural elements like length, paragraphing, and flow
5. Identify repetition, redundancy, and areas for improvement
6. Provide specific, actionable feedback for content enhancement

Always provide structured, detailed analysis with specific examples and concrete recommendations.
Focus on professional LinkedIn content standards and user engagement potential.""",
                model=openai_model
            )
            
            print("✅ Feedback Agent initialized")
            print(f"🔍 Using model: {self.model}")
            
        except Exception as e:
            raise Exception(f"Failed to initialize Feedback Agent: {e}")
    
    def load_content_files(self) -> Dict[str, str]:
        """Load all required content files for analysis"""
        
        files = {
            'generated_post': 'output/result.txt',
            'instructions': 'input/instructions.txt', 
            'style_guide': 'input/linkedin_style_prompt.txt'
        }
        
        content = {}
        
        for key, filepath in files.items():
            try:
                if os.path.exists(filepath):
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content[key] = f.read().strip()
                    print(f"✅ Loaded {key}: {len(content[key])} characters")
                else:
                    print(f"⚠️ File not found: {filepath}")
                    content[key] = ""
            except Exception as e:
                print(f"❌ Error loading {key} from {filepath}: {e}")
                content[key] = ""
        
        return content
    
    def analyze_instruction_alignment(self, post: str, instructions: str) -> Dict[str, Any]:
        """Analyze how well the post aligns with original instructions"""
        
        analysis_prompt = f"""Analyze how well this LinkedIn post aligns with the original instructions.

ORIGINAL INSTRUCTIONS:
{instructions}

GENERATED POST:
{post}

Provide a detailed JSON analysis:

{{
    "alignment_score": [1-10],
    "topic_coverage": {{
        "main_themes_addressed": ["theme1", "theme2"],
        "missing_themes": ["missing1", "missing2"],
        "coverage_percentage": [0-100]
    }},
    "research_integration": {{
        "sources_referenced": ["source1", "source2"],
        "integration_quality": "excellent/good/fair/poor",
        "specific_examples": ["example1", "example2"]
    }},
    "argument_coherence": {{
        "main_argument_clarity": "excellent/good/fair/poor",
        "logical_flow": "excellent/good/fair/poor",
        "evidence_support": "strong/moderate/weak"
    }},
    "key_strengths": ["strength1", "strength2"],
    "areas_for_improvement": ["improvement1", "improvement2"],
    "specific_recommendations": ["rec1", "rec2"]
}}

Focus on concrete examples and specific alignment issues."""
        
        try:
            response = self.agent(analysis_prompt)
            content = response.content if hasattr(response, 'content') else str(response)
            
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                return self._create_fallback_analysis("instruction_alignment", content)
                
        except Exception as e:
            print(f"⚠️ Error in instruction alignment analysis: {e}")
            return self._create_fallback_analysis("instruction_alignment", str(e))
    
    def analyze_style_compliance(self, post: str, style_guide: str) -> Dict[str, Any]:
        """Analyze compliance with the style guide"""
        
        analysis_prompt = f"""Analyze this LinkedIn post's compliance with the provided style guide.

STYLE GUIDE:
{style_guide}

GENERATED POST:
{post}

Provide a detailed JSON analysis:

{{
    "style_score": [1-10],
    "tone_analysis": {{
        "tone_match": "excellent/good/fair/poor",
        "professionalism": "excellent/good/fair/poor", 
        "conversational_quality": "excellent/good/fair/poor",
        "critical_voice": "strong/moderate/weak"
    }},
    "sentence_structure": {{
        "average_sentence_length": [number],
        "complexity_level": "appropriate/too_simple/too_complex",
        "variety_score": [1-10]
    }},
    "engagement_elements": {{
        "rhetorical_questions": [count],
        "personal_anecdotes": [count],
        "storytelling_devices": ["device1", "device2"],
        "engagement_effectiveness": "high/medium/low"
    }},
    "formatting": {{
        "paragraph_structure": "excellent/good/fair/poor",
        "line_breaks": "appropriate/excessive/insufficient", 
        "hashtag_usage": "optimal/excessive/insufficient",
        "hashtag_relevance": "high/medium/low"
    }},
    "style_strengths": ["strength1", "strength2"],
    "style_issues": ["issue1", "issue2"],
    "style_recommendations": ["rec1", "rec2"]
}}

Analyze specific examples from the post."""
        
        try:
            response = self.agent(analysis_prompt)
            content = response.content if hasattr(response, 'content') else str(response)
            
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                return self._create_fallback_analysis("style_compliance", content)
                
        except Exception as e:
            print(f"⚠️ Error in style compliance analysis: {e}")
            return self._create_fallback_analysis("style_compliance", str(e))
    
    def analyze_readability(self, post: str) -> Dict[str, Any]:
        """Analyze readability and accessibility"""
        
        analysis_prompt = f"""Analyze the readability and accessibility of this LinkedIn post.

GENERATED POST:
{post}

Provide a detailed JSON analysis:

{{
    "readability_score": [1-10],
    "language_clarity": {{
        "sentence_clarity": "excellent/good/fair/poor",
        "word_choice": "excellent/good/fair/poor",
        "jargon_balance": "appropriate/too_technical/too_simple",
        "accessibility": "high/medium/low"
    }},
    "non_native_accessibility": {{
        "vocabulary_complexity": "appropriate/too_complex/too_simple",
        "sentence_structure_clarity": "clear/moderate/confusing",
        "cultural_references": "universal/region_specific/unclear"
    }},
    "flow_and_coherence": {{
        "logical_progression": "excellent/good/fair/poor",
        "transition_quality": "smooth/adequate/choppy",
        "idea_connectivity": "strong/moderate/weak"
    }},
    "comprehension_barriers": ["barrier1", "barrier2"],
    "readability_strengths": ["strength1", "strength2"],
    "accessibility_improvements": ["improvement1", "improvement2"]
}}

Focus on how easy it is for diverse audiences to understand and engage with the content."""
        
        try:
            response = self.agent(analysis_prompt)
            content = response.content if hasattr(response, 'content') else str(response)
            
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                return self._create_fallback_analysis("readability", content)
                
        except Exception as e:
            print(f"⚠️ Error in readability analysis: {e}")
            return self._create_fallback_analysis("readability", str(e))
    
    def analyze_structure(self, post: str) -> Dict[str, Any]:
        """Analyze structural elements and organization"""
        
        analysis_prompt = f"""Analyze the structural elements of this LinkedIn post.

GENERATED POST:
{post}

Provide a detailed JSON analysis:

{{
    "structure_score": [1-10],
    "length_analysis": {{
        "character_count": [count],
        "word_count": [count],
        "optimal_for_linkedin": true/false,
        "length_assessment": "too_short/optimal/too_long"
    }},
    "paragraph_analysis": {{
        "paragraph_count": [count],
        "average_sentences_per_paragraph": [number],
        "paragraph_variety": "excellent/good/fair/poor",
        "balance_assessment": "well_balanced/uneven/monotonous"
    }},
    "repetition_check": {{
        "content_repetition": "none/minimal/moderate/excessive",
        "word_repetition": "none/minimal/moderate/excessive",
        "idea_repetition": "none/minimal/moderate/excessive",
        "repetitive_elements": ["element1", "element2"]
    }},
    "structural_flow": {{
        "opening_strength": "strong/adequate/weak",
        "body_development": "excellent/good/fair/poor",
        "conclusion_effectiveness": "strong/adequate/weak"
    }},
    "structural_strengths": ["strength1", "strength2"],
    "structural_issues": ["issue1", "issue2"],
    "structural_recommendations": ["rec1", "rec2"]
}}

Count actual characters, words, and paragraphs accurately."""
        
        try:
            response = self.agent(analysis_prompt)
            content = response.content if hasattr(response, 'content') else str(response)
            
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                return self._create_fallback_analysis("structure", content)
                
        except Exception as e:
            print(f"⚠️ Error in structural analysis: {e}")
            return self._create_fallback_analysis("structure", str(e))
    
    def generate_comprehensive_feedback(self, content: Dict[str, str]) -> Dict[str, Any]:
        """Generate comprehensive feedback combining all analysis dimensions"""
        
        print("🔍 Starting comprehensive feedback analysis...")
        
        # Perform individual analyses
        instruction_analysis = self.analyze_instruction_alignment(
            content['generated_post'], 
            content['instructions']
        )
        print("✅ Instruction alignment analysis complete")
        
        style_analysis = self.analyze_style_compliance(
            content['generated_post'], 
            content['style_guide']
        )
        print("✅ Style compliance analysis complete")
        
        readability_analysis = self.analyze_readability(content['generated_post'])
        print("✅ Readability analysis complete")
        
        structure_analysis = self.analyze_structure(content['generated_post'])
        print("✅ Structural analysis complete")
        
        # Calculate overall assessment
        scores = [
            instruction_analysis.get('alignment_score', 5),
            style_analysis.get('style_score', 5),
            readability_analysis.get('readability_score', 5),
            structure_analysis.get('structure_score', 5)
        ]
        
        overall_score = sum(scores) / len(scores)
        
        # Compile comprehensive feedback
        feedback = {
            'overall_assessment': {
                'overall_score': round(overall_score, 1),
                'grade': self._score_to_grade(overall_score),
                'summary': self._generate_overall_summary(overall_score, instruction_analysis, style_analysis, readability_analysis, structure_analysis)
            },
            'instruction_alignment': instruction_analysis,
            'style_compliance': style_analysis,
            'readability_accessibility': readability_analysis,
            'structural_analysis': structure_analysis,
            'recommendations': self._compile_recommendations(instruction_analysis, style_analysis, readability_analysis, structure_analysis),
            'post_metrics': {
                'character_count': len(content['generated_post']),
                'word_count': len(content['generated_post'].split()),
                'paragraph_count': len([p for p in content['generated_post'].split('\n\n') if p.strip()]),
                'reading_time_minutes': max(1, round(len(content['generated_post'].split()) / 200))
            }
        }
        
        print("✅ Comprehensive feedback analysis complete")
        return feedback
    
    def _create_fallback_analysis(self, analysis_type: str, content: str) -> Dict[str, Any]:
        """Create fallback analysis when JSON parsing fails"""
        return {
            'analysis_type': analysis_type,
            'status': 'partial',
            'raw_content': content[:500] + "..." if len(content) > 500 else content,
            'note': 'Analysis completed but structured data extraction failed'
        }
    
    def _score_to_grade(self, score: float) -> str:
        """Convert numeric score to letter grade"""
        if score >= 9: return "A"
        elif score >= 8: return "B+"
        elif score >= 7: return "B"
        elif score >= 6: return "C+"
        elif score >= 5: return "C"
        else: return "D"
    
    def _generate_overall_summary(self, score: float, inst_analysis: Dict, style_analysis: Dict, read_analysis: Dict, struct_analysis: Dict) -> str:
        """Generate overall summary based on all analyses"""
        
        grade = self._score_to_grade(score)
        
        if score >= 8:
            return f"Excellent LinkedIn post (Grade {grade}). Strong alignment with instructions, good style compliance, and high readability. Minor refinements could enhance impact."
        elif score >= 6:
            return f"Good LinkedIn post (Grade {grade}). Generally meets requirements with some areas for improvement in style, structure, or alignment."
        elif score >= 4:
            return f"Fair LinkedIn post (Grade {grade}). Addresses basic requirements but needs significant improvements in multiple areas."
        else:
            return f"Poor LinkedIn post (Grade {grade}). Major revisions needed across instruction alignment, style, readability, and structure."
    
    def _compile_recommendations(self, inst_analysis: Dict, style_analysis: Dict, read_analysis: Dict, struct_analysis: Dict) -> List[str]:
        """Compile top recommendations from all analyses"""
        
        recommendations = []
        
        # Add recommendations from each analysis
        for analysis in [inst_analysis, style_analysis, read_analysis, struct_analysis]:
            if isinstance(analysis, dict):
                # Try different possible recommendation keys
                for key in ['specific_recommendations', 'style_recommendations', 'accessibility_improvements', 'structural_recommendations', 'areas_for_improvement']:
                    if key in analysis and isinstance(analysis[key], list):
                        recommendations.extend(analysis[key][:2])  # Top 2 from each category
        
        # Remove duplicates while preserving order
        seen = set()
        unique_recommendations = []
        for rec in recommendations:
            if isinstance(rec, str) and rec not in seen:
                seen.add(rec)
                unique_recommendations.append(rec)
        
        return unique_recommendations[:8]  # Return top 8 recommendations


def main():
    """Test the FeedbackAgent"""
    try:
        agent = FeedbackAgent()
        
        # Load content files
        content = agent.load_content_files()
        
        if not content['generated_post']:
            print("❌ No generated post found. Run the main generator first.")
            return
        
        # Generate comprehensive feedback
        feedback = agent.generate_comprehensive_feedback(content)
        
        print("\n" + "="*60)
        print("FEEDBACK ANALYSIS RESULTS")
        print("="*60)
        print(json.dumps(feedback, indent=2))
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        print("Make sure OPENAI_API_KEY is set in your .env file")


if __name__ == "__main__":
    main()
