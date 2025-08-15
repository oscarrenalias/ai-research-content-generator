#!/usr/bin/env python3
"""
Research Agent

Specialized agent for conducting topic research based on LinkedIn post instructions
and link analysis. Generates comprehensive insights and supporting information.
"""

import json
import re
from typing import List, Dict, Any
from strands import Agent
from tavily import TavilyClient


class ResearchAgent:
    def __init__(self, openai_api_key: str = None, model: str = None):
        """Initialize the Research Agent with topic analysis capabilities"""
        
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
            self.model = os.getenv("RESEARCH_MODEL", "gpt-4o-mini")
        
        if not self.openai_api_key:
            raise Exception("OPENAI_API_KEY not found. Please set it in .env file or pass it directly.")
        
        # Check if Tavily API key is available
        import os
        from dotenv import load_dotenv
        load_dotenv()
        self.tavily_api_key = os.getenv("TAVILY_API_KEY")
        self.has_web_search = bool(self.tavily_api_key and self.tavily_api_key != "your_tavily_api_key_here")
        
        if self.has_web_search:
            self.tavily_client = TavilyClient(api_key=self.tavily_api_key)
            print("✅ Tavily web search enabled")
        else:
            self.tavily_client = None
            print("⚠️ Tavily API key not configured. Research will use knowledge-based analysis only.")
            print("   To enable web search, get an API key from https://www.tavily.com/ and set TAVILY_API_KEY in .env")
        
        # Initialize agent with OpenAI model
        try:
            from strands.models.openai import OpenAIModel
            
            openai_model = OpenAIModel(
                client_args={"api_key": self.openai_api_key},
                model_id=self.model,
                params={"temperature": 0.3, "max_tokens": 2000}
            )
            
            # Configure system prompt based on web search availability
            if self.has_web_search:
                system_prompt = """You are a research specialist focused on generating comprehensive topic insights for LinkedIn content creation. Your job is to:

1. Extract key topics and themes from instructions and existing analysis
2. Analyze web search results provided to you to gather current information and trends
3. Provide industry context and current trends for each topic based on search results
4. Generate supporting statistics, expert opinions, and data points from reliable sources
5. Identify angles and perspectives that would resonate on LinkedIn
6. Create actionable insights for content creation
7. Focus on professional, business-relevant information

You will be provided with web search results for each topic. Use this information to provide comprehensive, current insights. Always structure your research in a clear, organized format that can be easily used for content creation."""
            else:
                system_prompt = """You are a research specialist focused on generating comprehensive topic insights for LinkedIn content creation. Your job is to:

1. Extract key topics and themes from instructions and existing analysis
2. Provide industry context and current trends for each topic based on your knowledge
3. Generate supporting statistics, expert opinions, and data points from reliable sources
4. Identify angles and perspectives that would resonate on LinkedIn
5. Create actionable insights for content creation
6. Focus on professional, business-relevant information

Use your extensive knowledge to provide comprehensive insights. Always structure your research in a clear, organized format that can be easily used for content creation."""
            
            self.agent = Agent(
                system_prompt=system_prompt,
                model=openai_model
            )
            
            print("✅ Research Agent initialized with OpenAI API")
            print(f"🔍 Using model: {self.model}")
            
        except Exception as e:
            raise Exception(f"Failed to initialize Research Agent: {e}")
    
    def extract_topics(self, instructions: str, link_analysis: Dict[str, Any]) -> List[str]:
        """
        Extract key topics and themes from instructions and link analysis
        
        Args:
            instructions: Original post instructions
            link_analysis: Analysis results from LinkAnalysisAgent
            
        Returns:
            List of key topics to research
        """
        # Extract topics from instructions using AI
        topic_extraction_prompt = f"""Analyze the following content and extract the key topics and themes that should be researched for a LinkedIn post:

ORIGINAL INSTRUCTIONS:
{instructions}

LINK ANALYSIS THEMES:
{link_analysis.get('aggregated_themes', [])}

LINK ANALYSIS KEY POINTS:  
{link_analysis.get('all_key_points', [])[:10]}  # Limit to avoid token overflow

Please identify 3-5 key topics that would benefit from additional research and context. Focus on:
- Main subject areas
- Industry trends mentioned
- Technical concepts that need explanation
- Business implications
- Professional development angles

Return the topics as a simple JSON list: ["topic1", "topic2", "topic3"]"""

        try:
            response = self.agent(topic_extraction_prompt)
            
            # Extract response content
            if hasattr(response, 'content'):
                response_text = response.content
            else:
                response_text = str(response)
            
            # Try to parse JSON
            json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
            if json_match:
                topics = json.loads(json_match.group())
            else:
                # Fallback: extract topics from text
                topics = []
                lines = response_text.split('\n')
                for line in lines:
                    if any(char in line for char in ['-', '•', '1.', '2.', '3.']):
                        topic = re.sub(r'^[-•\d.\s]+', '', line).strip()
                        if topic and len(topic) > 3:
                            topics.append(topic[:100])  # Limit length
                
                # Ensure we have at least some topics
                if not topics:
                    topics = ['AI technology', 'Industry trends', 'Professional development']
            
            print(f"🎯 Extracted {len(topics)} topics for research:")
            for i, topic in enumerate(topics, 1):
                print(f"   {i}. {topic}")
            
            return topics[:5]  # Limit to 5 topics maximum
            
        except Exception as e:
            print(f"⚠️ Error extracting topics: {e}")
            # Fallback topics based on common LinkedIn themes
            return ['Industry trends', 'Technology developments', 'Professional insights']
    
    def research_topic(self, topic: str, context: str) -> Dict[str, Any]:
        """
        Conduct research on a specific topic
        
        Args:
            topic: The topic to research
            context: Additional context from instructions and link analysis
            
        Returns:
            Dictionary containing research findings for the topic
        """
        print(f"🔍 Researching topic: {topic}")
        
        # Perform web search if available
        search_results = ""
        if self.has_web_search:
            try:
                print(f"🌐 Conducting web search for: {topic}")
                # Search for current information about the topic
                search_response = self.tavily_client.search(
                    query=f"{topic} recent developments trends 2024 2025",
                    search_depth="advanced",
                    max_results=5,
                    include_raw_content=True
                )
                
                # Format search results for the AI agent
                if search_response and 'results' in search_response:
                    search_results = "\n\nWEB SEARCH RESULTS:\n"
                    for i, result in enumerate(search_response['results'][:5], 1):
                        search_results += f"\n{i}. {result.get('title', 'No title')}\n"
                        search_results += f"   URL: {result.get('url', 'No URL')}\n"
                        search_results += f"   Content: {result.get('content', 'No content')[:500]}...\n"
                        
                    print(f"✅ Found {len(search_response['results'])} search results")
                else:
                    print("⚠️ No search results found")
                    
            except Exception as e:
                print(f"⚠️ Web search failed: {e}")
                search_results = ""
        
        if self.has_web_search and search_results:
            research_prompt = f"""Conduct comprehensive research on the following topic for LinkedIn content creation using the provided web search results:

TOPIC: {topic}

CONTEXT: {context[:1000]}  # Additional context for better understanding

{search_results}

Based on the web search results above, provide comprehensive research insights in the following JSON format:

{{
    "topic": "{topic}",
    "current_trends": [
        "Current trend 1 with recent evidence from search results",
        "Current trend 2 with recent evidence from search results"
    ],
    "key_statistics": [
        "Recent statistic 1 with source from search results",
        "Recent statistic 2 with source from search results"
    ],
    "industry_implications": [
        "Business implication 1 based on current information",
        "Business implication 2 based on current information"
    ],
    "expert_perspectives": [
        "Recent expert viewpoint 1 from search results",
        "Recent expert viewpoint 2 from search results"
    ],
    "linkedin_angles": [
        "Angle 1: Why this matters to professionals right now",
        "Angle 2: How this affects business strategy today",
        "Angle 3: Current career development implications"
    ],
    "supporting_arguments": [
        "Argument 1 supported by recent developments",
        "Argument 2 supported by recent developments"
    ],
    "potential_controversies": [
        "Current debate point 1 from recent discussions",
        "Current debate point 2 from recent discussions"
    ],
    "actionable_insights": [
        "Actionable insight 1 based on current information",
        "Actionable insight 2 based on current information"
    ]
}}

Focus on the most recent information from the search results."""
        else:
            research_prompt = f"""Based on your existing knowledge, conduct comprehensive research on the following topic for LinkedIn content creation:

TOPIC: {topic}

CONTEXT: {context[:1000]}  # Additional context for better understanding

Using your training data and knowledge base, please provide comprehensive research insights in the following JSON format:

{{
    "topic": "{topic}",
    "current_trends": [
        "Current trend 1 related to this topic based on your knowledge",
        "Current trend 2 related to this topic based on your knowledge"
    ],
    "key_statistics": [
        "Relevant statistic 1 (with approximate source if known)",
        "Relevant statistic 2 (with approximate source if known)"
    ],
    "industry_implications": [
        "Business implication 1",
        "Business implication 2"
    ],
    "expert_perspectives": [
        "Expert viewpoint 1 based on known industry opinions",
        "Expert viewpoint 2 based on known industry opinions"
    ],
    "linkedin_angles": [
        "Angle 1: Why this matters to professionals",
        "Angle 2: How this affects business strategy",
        "Angle 3: Career development implications"
    ],
    "supporting_arguments": [
        "Argument 1 supporting main thesis",
        "Argument 2 supporting main thesis"
    ],
    "potential_controversies": [
        "Debate point 1",
        "Debate point 2"
    ],
    "actionable_insights": [
        "Actionable insight 1 for readers",
        "Actionable insight 2 for readers"
    ]
}}

Focus on information from your training data that would be valuable for LinkedIn content creation and professional discussion."""
            research_prompt = f"""Based on your existing knowledge, conduct comprehensive research on the following topic for LinkedIn content creation:

TOPIC: {topic}

CONTEXT: {context[:1000]}  # Additional context for better understanding

Using your training data and knowledge base, please provide comprehensive research insights in the following JSON format:

{{
    "topic": "{topic}",
    "current_trends": [
        "Current trend 1 related to this topic based on your knowledge",
        "Current trend 2 related to this topic based on your knowledge"
    ],
    "key_statistics": [
        "Relevant statistic 1 (with approximate source if known)",
        "Relevant statistic 2 (with approximate source if known)"
    ],
    "industry_implications": [
        "Business implication 1",
        "Business implication 2"
    ],
    "expert_perspectives": [
        "Expert viewpoint 1 based on known industry opinions",
        "Expert viewpoint 2 based on known industry opinions"
    ],
    "linkedin_angles": [
        "Angle 1: Why this matters to professionals",
        "Angle 2: How this affects business strategy",
        "Angle 3: Career development implications"
    ],
    "supporting_arguments": [
        "Argument 1 supporting main thesis",
        "Argument 2 supporting main thesis"
    ],
    "potential_controversies": [
        "Debate point 1",
        "Debate point 2"
    ],
    "actionable_insights": [
        "Actionable insight 1 for readers",
        "Actionable insight 2 for readers"
    ]
}}

Focus on information from your training data that would be valuable for LinkedIn content creation and professional discussion."""

        try:
            response = self.agent(research_prompt)
            
            # Extract response content
            if hasattr(response, 'content'):
                response_text = response.content
            else:
                response_text = str(response)
            
            # Try to parse JSON
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                research_data = json.loads(json_match.group())
            else:
                # Fallback structure
                research_data = {
                    'topic': topic,
                    'current_trends': [f"Current developments in {topic}"],
                    'key_statistics': [f"Growing importance of {topic} in industry"],
                    'industry_implications': [f"{topic} is reshaping business practices"],
                    'expert_perspectives': [f"Experts emphasize the significance of {topic}"],
                    'linkedin_angles': [f"Professionals should understand {topic}"],
                    'supporting_arguments': [f"{topic} drives innovation"],
                    'potential_controversies': [f"Debates around {topic} implementation"],
                    'actionable_insights': [f"Stay informed about {topic} developments"]
                }
            
            print(f"✅ Research completed for: {topic}")
            return research_data
            
        except Exception as e:
            print(f"❌ Error researching topic '{topic}': {e}")
            return {
                'topic': topic,
                'current_trends': [],
                'key_statistics': [],
                'industry_implications': [],
                'expert_perspectives': [],
                'linkedin_angles': [],
                'supporting_arguments': [],
                'potential_controversies': [],
                'actionable_insights': [],
                'error': str(e)
            }
    
    def conduct_comprehensive_research(self, instructions: str, link_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Conduct comprehensive research on all topics extracted from instructions and link analysis
        
        Args:
            instructions: Original post instructions  
            link_analysis: Analysis results from LinkAnalysisAgent
            
        Returns:
            Comprehensive research findings for all topics
        """
        print("🔍 Starting comprehensive topic research...")
        
        # Step 1: Extract topics
        topics = self.extract_topics(instructions, link_analysis)
        
        if not topics:
            print("ℹ️ No topics identified for research")
            return {
                'topics_researched': [],
                'research_results': {},
                'aggregated_insights': {
                    'all_trends': [],
                    'all_statistics': [],
                    'all_implications': [],
                    'all_angles': [],
                    'all_actionable_insights': []
                },
                'summary': 'No specific topics identified for additional research.'
            }
        
        # Step 2: Research each topic
        research_results = {}
        context = f"Instructions: {instructions[:500]}... Link Analysis: {link_analysis.get('summary', '')}"
        
        for topic in topics:
            research_results[topic] = self.research_topic(topic, context)
        
        # Step 3: Aggregate insights across all topics
        aggregated_insights = {
            'all_trends': [],
            'all_statistics': [],
            'all_implications': [],
            'all_angles': [],
            'all_actionable_insights': []
        }
        
        for topic, research in research_results.items():
            if 'error' not in research:
                aggregated_insights['all_trends'].extend(research.get('current_trends', []))
                aggregated_insights['all_statistics'].extend(research.get('key_statistics', []))
                aggregated_insights['all_implications'].extend(research.get('industry_implications', []))
                aggregated_insights['all_angles'].extend(research.get('linkedin_angles', []))
                aggregated_insights['all_actionable_insights'].extend(research.get('actionable_insights', []))
        
        # Create final research output
        final_research = {
            'topics_researched': topics,
            'research_results': research_results,
            'aggregated_insights': aggregated_insights,
            'summary': f'Conducted research on {len(topics)} topics: {", ".join(topics)}. Generated {len(aggregated_insights["all_trends"])} trends, {len(aggregated_insights["all_statistics"])} statistics, and {len(aggregated_insights["all_angles"])} LinkedIn angles.'
        }
        
        print(f"🔍 Research complete:")
        print(f"   - Topics researched: {len(topics)}")
        print(f"   - Trends identified: {len(aggregated_insights['all_trends'])}")
        print(f"   - Statistics gathered: {len(aggregated_insights['all_statistics'])}")
        print(f"   - LinkedIn angles: {len(aggregated_insights['all_angles'])}")
        print(f"   - Actionable insights: {len(aggregated_insights['all_actionable_insights'])}")
        
        return final_research


def main():
    """Test the ResearchAgent"""
    try:
        agent = ResearchAgent()
        
        # Test with sample data
        test_instructions = """
        Write an article about how AI is transforming industries but we can't control it properly.
        Focus on security risks and the concentration of AI power in few companies.
        """
        
        test_link_analysis = {
            'aggregated_themes': ['AI safety', 'Industry transformation', 'Corporate control'],
            'all_key_points': [
                'AI systems are becoming more powerful',
                'Security vulnerabilities in AI models', 
                'Few companies control AI infrastructure',
                'Regulatory challenges with AI oversight'
            ],
            'summary': 'Analysis of AI industry concerns and control issues'
        }
        
        research = agent.conduct_comprehensive_research(test_instructions, test_link_analysis)
        
        print("\n" + "="*60)
        print("RESEARCH RESULTS")
        print("="*60)
        print(json.dumps(research, indent=2))
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        print("Make sure OPENAI_API_KEY is set in your .env file")


if __name__ == "__main__":
    main()
