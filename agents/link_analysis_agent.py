#!/usr/bin/env python3
"""
Link Analysis Agent

Specialized agent for detecting and analyzing web links in LinkedIn post instructions.
Uses Strands http_request tool to fetch and summarize web content.
"""

import re
import json
from typing import List, Dict, Any
from strands import Agent
from strands_tools import http_request


class LinkAnalysisAgent:
    def __init__(self, openai_api_key: str = None, model: str = "gpt-4o"):
        """Initialize the Link Analysis Agent with web browsing capabilities"""
        
        # Use provided API key or get from environment
        if openai_api_key:
            self.openai_api_key = openai_api_key
        else:
            import os
            from dotenv import load_dotenv
            load_dotenv()
            self.openai_api_key = os.getenv("OPENAI_API_KEY")
        
        if not self.openai_api_key:
            raise Exception("OPENAI_API_KEY not found. Please set it in .env file or pass it directly.")
        
        # Initialize agent with OpenAI model
        try:
            from strands.models.openai import OpenAIModel
            
            openai_model = OpenAIModel(
                client_args={"api_key": self.openai_api_key},
                model_id=model,
                params={"temperature": 0.3, "max_tokens": 2000}
            )
            
            self.agent = Agent(
                system_prompt="""You are a web content analysis specialist. Your job is to:
1. Extract and analyze key information from web pages
2. Identify main themes and important points
3. Find relevant quotes that support LinkedIn post arguments  
4. Summarize content in a structured, actionable format
5. Focus on information that would be valuable for LinkedIn content creation

Always provide structured analysis with key points, themes, and relevant quotes.""",
                model=openai_model,
                tools=[http_request]
            )
            
            print("✅ Link Analysis Agent initialized with OpenAI API")
            
        except Exception as e:
            raise Exception(f"Failed to initialize Link Analysis Agent: {e}")
    
    def detect_links(self, instructions: str) -> List[str]:
        """
        Detect all URLs in the instructions text using regex patterns
        
        Args:
            instructions: The instruction text to analyze
            
        Returns:
            List of URLs found in the instructions
        """
        # Common URL patterns
        url_patterns = [
            r'https?://[^\s]+',  # Standard HTTP/HTTPS URLs
            r'www\.[^\s]+',      # www URLs without protocol
            r'[a-zA-Z0-9-]+\.[a-zA-Z]{2,}[^\s]*'  # Domain-like patterns
        ]
        
        urls = []
        for pattern in url_patterns:
            matches = re.findall(pattern, instructions)
            urls.extend(matches)
        
        # Clean and validate URLs
        cleaned_urls = []
        for url in urls:
            # Add protocol if missing
            if not url.startswith(('http://', 'https://')):
                if url.startswith('www.'):
                    url = 'https://' + url
                elif '.' in url:
                    url = 'https://' + url
            
            # Remove trailing punctuation
            url = re.sub(r'[.,;!?]+$', '', url)
            
            # Basic validation
            if '.' in url and len(url) > 10:
                cleaned_urls.append(url)
        
        # Remove duplicates while preserving order
        unique_urls = list(dict.fromkeys(cleaned_urls))
        
        print(f"🔗 Found {len(unique_urls)} URLs in instructions:")
        for url in unique_urls:
            print(f"   - {url}")
            
        return unique_urls
    
    def fetch_and_analyze_content(self, url: str) -> Dict[str, Any]:
        """
        Fetch web content and analyze it for key information
        
        Args:
            url: The URL to fetch and analyze
            
        Returns:
            Dictionary containing analysis results
        """
        try:
            print(f"🌐 Fetching content from: {url}")
            
            # Use the agent to fetch content with http_request tool
            fetch_prompt = f"""I need you to fetch content from this URL: {url}

Please use the http_request tool to get the webpage content. If the fetch is successful, analyze the content and provide this structured JSON response:

{{
    "title": "Page title or main heading",
    "main_theme": "Primary topic or theme",
    "key_points": ["Key point 1", "Key point 2", "Key point 3"],
    "relevant_quotes": ["Quote 1", "Quote 2"],
    "supporting_data": ["Data point 1", "Data point 2"],
    "linkedin_relevance": "How this could be used in LinkedIn posts",
    "summary": "2-3 sentence summary"
}}

If the URL cannot be accessed (blocked, requires login, etc.), please provide an analysis based on what you can infer from the URL itself, including the domain and any visible path information."""
            
            response = self.agent(fetch_prompt)
            
            # Check if we got a response
            if not response:
                print(f"⚠️ Failed to fetch content from {url}")
                return self._create_fallback_analysis(url, "No response from agent")
            
            # Extract content from response
            if hasattr(response, 'content'):
                content = response.content
            else:
                content = str(response)
            
            # Check if the content contains actual analysis or error messages
            if not content or len(content) < 50:
                print(f"⚠️ Failed to fetch content from {url}")
                return self._create_fallback_analysis(url, "Minimal content received")
            
            # Look for JSON in the response
            try:
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    analysis_data = json.loads(json_match.group())
                    analysis_data.update({
                        'url': url,
                        'status': 'success',
                        'content_length': len(content)
                    })
                    print(f"✅ Successfully analyzed content from {url}")
                    return analysis_data
                else:
                    # No JSON found, but we got content - create structured response
                    print(f"⚠️ Partial analysis completed for {url}")
                    return self._extract_analysis_from_text(content, url)
                    
            except json.JSONDecodeError:
                # JSON parsing failed, extract what we can
                print(f"⚠️ Partial analysis completed for {url}")
                return self._extract_analysis_from_text(content, url)
            
            
        except Exception as e:
            print(f"❌ Error analyzing content from {url}: {e}")
            return self._create_fallback_analysis(url, str(e))
    
    def _extract_analysis_from_text(self, content: str, url: str) -> Dict[str, Any]:
        """Extract analysis from unstructured text response"""
        
        # Look for common patterns in the response
        lines = content.split('\n')
        key_points = []
        quotes = []
        
        for line in lines:
            line = line.strip()
            if line.startswith('-') or line.startswith('•') or line.startswith('*'):
                key_points.append(line[1:].strip())
            elif '"' in line and len(line) > 20:
                quotes.append(line.strip('"'))
        
        # If we got substantial content, mark as partial success
        status = 'partial_success' if len(content) > 200 else 'failed'
        
        return {
            'url': url,
            'status': status,
            'title': self._extract_title_from_url(url),
            'main_theme': self._infer_theme_from_url(url),
            'key_points': key_points[:5] if key_points else [content[:200] + "..."],
            'relevant_quotes': quotes[:3],
            'supporting_data': [],
            'linkedin_relevance': 'Supporting content for LinkedIn post',
            'summary': content[:300] + "..." if len(content) > 300 else content,
            'content_length': len(content)
        }
    
    def _create_fallback_analysis(self, url: str, error: str) -> Dict[str, Any]:
        """Create fallback analysis when URL cannot be accessed"""
        
        # Try to infer content from URL structure
        title = self._extract_title_from_url(url)
        theme = self._infer_theme_from_url(url)
        
        # Create analysis based on URL alone
        key_points = []
        if 'twitter.com' in url or 'x.com' in url:
            key_points = [
                "Social media post from Twitter/X platform",
                "May contain opinions or breaking news",
                "Could include viral content or trending topics"
            ]
        elif 'nytimes.com' in url:
            key_points = [
                "News article from The New York Times",
                "Professional journalism and reporting", 
                "Likely contains in-depth analysis of current events"
            ]
        elif 'linkedin.com' in url:
            key_points = [
                "Professional social media content",
                "Business or career-related information",
                "Professional networking context"
            ]
        else:
            key_points = [f"Web content from {url}"]
        
        return {
            'url': url,
            'status': 'fallback',
            'error': error,
            'title': title,
            'main_theme': theme,
            'key_points': key_points,
            'relevant_quotes': [],
            'supporting_data': [],
            'linkedin_relevance': f'Reference material from {title}',
            'summary': f'Content from {title}. Based on URL structure, this appears to be {theme.lower()} content. The specific details could not be retrieved due to access restrictions.'
        }
    
    def _extract_title_from_url(self, url: str) -> str:
        """Extract a meaningful title from URL"""
        if 'twitter.com' in url or 'x.com' in url:
            return "Twitter/X Post"
        elif 'nytimes.com' in url:
            return "New York Times Article"
        elif 'linkedin.com' in url:
            return "LinkedIn Content"
        else:
            # Extract domain name
            try:
                import urllib.parse
                parsed = urllib.parse.urlparse(url)
                domain = parsed.netloc.replace('www.', '')
                return f"Content from {domain}"
            except:
                return "Web Content"
    
    def _infer_theme_from_url(self, url: str) -> str:
        """Infer content theme from URL"""
        url_lower = url.lower()
        
        if any(keyword in url_lower for keyword in ['ai', 'artificial-intelligence', 'machine-learning', 'chatbot']):
            return "Artificial Intelligence"
        elif any(keyword in url_lower for keyword in ['tech', 'technology', 'innovation']):
            return "Technology"
        elif any(keyword in url_lower for keyword in ['business', 'finance', 'economy']):
            return "Business"
        elif any(keyword in url_lower for keyword in ['health', 'mental-health', 'psychology']):
            return "Health & Wellness"
        elif 'twitter.com' in url_lower or 'x.com' in url_lower:
            return "Social Media Discussion"
        elif 'news' in url_lower:
            return "News & Current Events"
        else:
            return "Web Content"
    
    def analyze_all_links(self, instructions: str) -> Dict[str, Any]:
        """
        Complete link analysis workflow: detect links and analyze all content
        
        Args:
            instructions: The instruction text containing potential URLs
            
        Returns:
            Comprehensive analysis of all links found
        """
        print("🔗 Starting link analysis...")
        
        # Step 1: Detect all URLs
        urls = self.detect_links(instructions)
        
        if not urls:
            print("ℹ️ No URLs found in instructions")
            return {
                'urls_found': [],
                'total_urls': 0,
                'successful_analyses': 0,
                'failed_analyses': 0,
                'content_summaries': [],
                'aggregated_themes': [],
                'all_key_points': [],
                'all_quotes': [],
                'summary': 'No links found in instructions to analyze.'
            }
        
        # Step 2: Analyze each URL
        content_summaries = []
        successful_analyses = 0
        partial_analyses = 0
        failed_analyses = 0
        
        for url in urls:
            analysis = self.fetch_and_analyze_content(url)
            content_summaries.append(analysis)
            
            if analysis['status'] == 'success':
                successful_analyses += 1
            elif analysis['status'] in ['partial_success', 'fallback']:
                partial_analyses += 1
            else:
                failed_analyses += 1
        
        # Step 3: Aggregate insights (include partial and fallback analyses)
        all_themes = []
        all_key_points = []
        all_quotes = []
        
        for summary in content_summaries:
            # Include all analyses that have useful information
            if summary['status'] in ['success', 'partial_success', 'fallback']:
                if 'main_theme' in summary and summary['main_theme']:
                    all_themes.append(summary['main_theme'])
                if 'key_points' in summary and summary['key_points']:
                    all_key_points.extend(summary['key_points'])
                if 'relevant_quotes' in summary and summary['relevant_quotes']:
                    all_quotes.extend(summary['relevant_quotes'])
        
        # Create final analysis
        total_useful_analyses = successful_analyses + partial_analyses
        final_analysis = {
            'urls_found': urls,
            'total_urls': len(urls),
            'successful_analyses': successful_analyses,
            'partial_analyses': partial_analyses,
            'failed_analyses': failed_analyses,
            'content_summaries': content_summaries,
            'aggregated_themes': list(set(all_themes)),  # Remove duplicates
            'all_key_points': all_key_points,
            'all_quotes': all_quotes,
            'summary': f'Analyzed {len(urls)} URLs with {successful_analyses} successful and {partial_analyses} partial analyses. Found {len(set(all_themes))} unique themes and {len(all_key_points)} key points.'
        }
        
        print(f"🔗 Link analysis complete:")
        print(f"   - URLs found: {len(urls)}")
        print(f"   - Successful analyses: {successful_analyses}")
        print(f"   - Partial analyses: {partial_analyses}")
        print(f"   - Failed analyses: {failed_analyses}")
        print(f"   - Themes identified: {len(set(all_themes))}")
        print(f"   - Key points extracted: {len(all_key_points)}")
        
        return final_analysis


def main():
    """Test the LinkAnalysisAgent"""
    try:
        agent = LinkAnalysisAgent()
        
        # Test with sample instructions
        test_instructions = """
        Write an article about AI safety issues. Here are some relevant links:
        https://www.example.com/ai-safety-article
        Check out this research: https://arxiv.org/abs/1234.5678
        Also see: www.ai-news.com/latest-developments
        """
        
        analysis = agent.analyze_all_links(test_instructions)
        
        print("\n" + "="*60)
        print("LINK ANALYSIS RESULTS")
        print("="*60)
        print(json.dumps(analysis, indent=2))
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        print("Make sure OPENAI_API_KEY is set in your .env file")


if __name__ == "__main__":
    main()
