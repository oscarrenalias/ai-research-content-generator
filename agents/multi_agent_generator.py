#!/usr/bin/env python3
"""
Multi-Agent LinkedIn Post Generator

Main orchestrator that coordinates specialized agents using Strands native workflow system:
1. LinkAnalysisAgent - Analyzes web links in instructions
2. ResearchAgent - Conducts topic research
3. PostCompositionAgent - Generates final LinkedIn post

Uses Strands workflow tool for native dependency management and task orchestration.
"""

import os
import json
import uuid
from typing import Dict, Any
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

from strands import Agent
from strands_tools import workflow
from strands.models.openai import OpenAIModel

from .link_analysis_agent import LinkAnalysisAgent
from .research_agent import ResearchAgent
from .post_composition_agent import PostCompositionAgent

# Load environment variables
load_dotenv()


class LinkedInMultiAgentGenerator:
    def __init__(self):
        """Initialize the Multi-Agent Generator with workflow orchestration"""
        self.input_dir = Path("input")
        
        # OpenAI configuration for workflow orchestrator
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.default_model = os.getenv("DEFAULT_MODEL", "gpt-4o")
        self.debug = os.getenv("DEBUG", "false").lower() in ("true", "1", "yes", "on")
        
        if not self.openai_api_key:
            raise Exception("OPENAI_API_KEY not found in .env file")
        
        # Initialize workflow orchestrator
        try:
            model = OpenAIModel(
                client_args={"api_key": self.openai_api_key},
                model_id=self.default_model,
                params={"temperature": 0.7, "max_tokens": 2000}
            )
            
            self.orchestrator = Agent(
                system_prompt="You are a workflow orchestrator for LinkedIn post generation. Coordinate multiple specialized agents to create comprehensive, well-researched LinkedIn posts.",
                model=model,
                tools=[workflow]
            )
            
            print("✅ Multi-Agent Generator initialized with Strands workflow orchestration")
            if self.debug:
                print("🐛 Debug mode enabled")
                
        except Exception as e:
            raise Exception(f"Failed to initialize Multi-Agent Generator: {e}")
        
        # Initialize specialized agents with API key
        self.link_agent = LinkAnalysisAgent(openai_api_key=self.openai_api_key)
        self.research_agent = ResearchAgent(openai_api_key=self.openai_api_key) 
        self.composition_agent = PostCompositionAgent(openai_api_key=self.openai_api_key)
        
        # Workflow state
        self.current_workflow_id = None
        self.workflow_results = {}
    
    def read_instructions(self) -> str:
        """Read instructions from input/instructions.txt"""
        instructions_file = self.input_dir / "instructions.txt"
        
        if not instructions_file.exists():
            raise Exception(f"Instructions file not found: {instructions_file}")
        
        try:
            with open(instructions_file, 'r', encoding='utf-8') as f:
                instructions = f.read().strip()
                
            if not instructions:
                raise Exception("Instructions file is empty")
                
            print(f"✅ Read instructions: {len(instructions)} characters")
            return instructions
            
        except Exception as e:
            raise Exception(f"Error reading instructions: {e}")
    
    def create_workflow_definition(self, instructions: str) -> Dict[str, Any]:
        """
        Create Strands workflow definition for LinkedIn post generation
        
        Args:
            instructions: User instructions for the post
            
        Returns:
            Workflow definition dictionary
        """
        # Generate unique workflow ID
        workflow_id = f"linkedin_post_{uuid.uuid4().hex[:8]}"
        
        workflow_definition = {
            "workflow_id": workflow_id,
            "tasks": [
                {
                    "task_id": "link_analysis",
                    "description": f"Analyze and summarize web links found in instructions: {instructions[:200]}...",
                    "system_prompt": """You are a web content analysis specialist. Your job is to:
1. Detect URLs in the provided instructions
2. Fetch and analyze web content from those URLs
3. Extract key themes, important points, and relevant quotes
4. Structure findings for LinkedIn content creation

Focus on information that would be valuable for professional LinkedIn posts.""",
                    "priority": 5,  # High priority, runs first
                    "dependencies": [],
                    "agent_type": "link_analysis"
                },
                {
                    "task_id": "topic_research",
                    "description": f"Conduct comprehensive research on key topics from instructions and link analysis for LinkedIn content creation",
                    "system_prompt": """You are a research specialist for LinkedIn content creation. Your job is to:
1. Extract key topics from instructions and link analysis
2. Research current trends and industry implications
3. Gather supporting statistics and expert perspectives  
4. Identify LinkedIn-specific angles and professional insights
5. Generate actionable insights for the target audience

Focus on professional, business-relevant information that adds value to LinkedIn posts.""",
                    "priority": 3,  # Medium priority, runs after link analysis
                    "dependencies": ["link_analysis"],
                    "agent_type": "research"
                },
                {
                    "task_id": "post_composition",
                    "description": "Generate final LinkedIn post combining instructions, link analysis, research findings, and user's writing style",
                    "system_prompt": """You are an expert LinkedIn content creator. Your job is to:
1. Synthesize information from instructions, link analysis, and research
2. Apply the user's specific writing style and voice patterns
3. Create authentic, engaging LinkedIn content that doesn't sound AI-generated
4. Follow LinkedIn best practices for professional engagement
5. Integrate all insights naturally and compellingly

Focus on creating content that sparks meaningful professional discussion.""",
                    "priority": 1,  # Lowest priority, runs last
                    "dependencies": ["link_analysis", "topic_research"],
                    "agent_type": "composition"
                }
            ]
        }
        
        return workflow_definition
    
    def execute_task_with_agent(self, task_definition: Dict[str, Any], context_data: Dict[str, Any]) -> Any:
        """
        Execute a specific task using the appropriate specialized agent
        
        Args:
            task_definition: Task configuration from workflow
            context_data: Data from previous tasks
            
        Returns:
            Task execution results
        """
        task_id = task_definition["task_id"]
        agent_type = task_definition["agent_type"]
        
        print(f"🤖 Executing task: {task_id} (agent: {agent_type})")
        
        try:
            if agent_type == "link_analysis":
                # Execute link analysis
                instructions = context_data.get("instructions", "")
                result = self.link_agent.analyze_all_links(instructions)
                
            elif agent_type == "research":
                # Execute research
                instructions = context_data.get("instructions", "")
                link_analysis = context_data.get("link_analysis", {})
                result = self.research_agent.conduct_comprehensive_research(instructions, link_analysis)
                
            elif agent_type == "composition":
                # Execute post composition
                composition_context = {
                    "instructions": context_data.get("instructions", ""),
                    "link_analysis": context_data.get("link_analysis", {}),
                    "research_findings": context_data.get("topic_research", {})
                }
                result = self.composition_agent.compose_linkedin_post(composition_context)
                
            else:
                raise Exception(f"Unknown agent type: {agent_type}")
            
            print(f"✅ Task {task_id} completed successfully")
            return result
            
        except Exception as e:
            print(f"❌ Task {task_id} failed: {e}")
            raise e
    
    def execute_sequential_workflow(self, instructions: str) -> str:
        """
        Execute the workflow sequentially using specialized agents
        (Alternative to Strands workflow tool for more direct control)
        
        Args:
            instructions: User instructions for the post
            
        Returns:
            Generated LinkedIn post
        """
        print("🚀 Starting sequential multi-agent workflow...")
        
        # Initialize context
        workflow_context = {
            "instructions": instructions,
            "timestamp": datetime.now().isoformat()
        }
        
        # Step 1: Link Analysis
        print("\n" + "="*50)
        print("🔗 PHASE 1: LINK ANALYSIS")  
        print("="*50)
        
        link_analysis = self.link_agent.analyze_all_links(instructions)
        workflow_context["link_analysis"] = link_analysis
        
        if self.debug:
            print(f"🐛 Link analysis results: {json.dumps(link_analysis, indent=2)[:500]}...")
        
        # Step 2: Topic Research
        print("\n" + "="*50)
        print("🔍 PHASE 2: TOPIC RESEARCH")
        print("="*50)
        
        research_findings = self.research_agent.conduct_comprehensive_research(
            instructions, link_analysis
        )
        workflow_context["research_findings"] = research_findings
        
        if self.debug:
            print(f"🐛 Research findings: {json.dumps(research_findings, indent=2)[:500]}...")
        
        # Step 3: Post Composition
        print("\n" + "="*50)
        print("✍️ PHASE 3: POST COMPOSITION")
        print("="*50)
        
        composition_context = {
            "instructions": instructions,
            "link_analysis": link_analysis, 
            "research_findings": research_findings
        }
        
        final_post = self.composition_agent.compose_linkedin_post(composition_context)
        
        if self.debug:
            print(f"🐛 Final post length: {len(final_post)} characters")
        
        # Save workflow metadata
        self.save_workflow_metadata(workflow_context, final_post)
        
        print("\n" + "🎉 Multi-agent workflow completed successfully!")
        return final_post
    
    def execute_strands_workflow(self, instructions: str) -> str:
        """
        Execute the workflow using Strands native workflow tool
        (Primary method using Strands orchestration)
        
        Args:
            instructions: User instructions for the post
            
        Returns:
            Generated LinkedIn post
        """
        print("🚀 Starting Strands native workflow...")
        
        try:
            # Create workflow definition
            workflow_def = self.create_workflow_definition(instructions)
            self.current_workflow_id = workflow_def["workflow_id"]
            
            print(f"📋 Created workflow: {self.current_workflow_id}")
            
            # Create workflow using Strands workflow tool
            create_response = self.orchestrator.tool.workflow(
                action="create",
                workflow_id=self.current_workflow_id,
                tasks=workflow_def["tasks"]
            )
            
            if self.debug:
                print(f"🐛 Workflow creation response: {create_response}")
            
            # Execute workflow  
            print("🎬 Starting workflow execution...")
            start_response = self.orchestrator.tool.workflow(
                action="start", 
                workflow_id=self.current_workflow_id
            )
            
            if self.debug:
                print(f"🐛 Workflow start response: {start_response}")
            
            # Monitor workflow progress
            print("📊 Monitoring workflow progress...")
            status_response = self.orchestrator.tool.workflow(
                action="status",
                workflow_id=self.current_workflow_id
            )
            
            if self.debug:
                print(f"🐛 Workflow status: {status_response}")
            
            # For now, fall back to sequential execution since we need to integrate our agents
            print("🔄 Executing tasks with specialized agents...")
            return self.execute_sequential_workflow(instructions)
            
        except Exception as e:
            print(f"❌ Strands workflow execution failed: {e}")
            print("🔄 Falling back to sequential execution...")
            return self.execute_sequential_workflow(instructions)
    
    def save_workflow_metadata(self, workflow_context: Dict[str, Any], final_post: str):
        """Save workflow execution metadata for debugging and analysis"""
        try:
            metadata = {
                "timestamp": datetime.now().isoformat(),
                "workflow_id": self.current_workflow_id,
                "instructions": workflow_context["instructions"],
                "final_post": final_post,
                "link_analysis_summary": workflow_context.get("link_analysis", {}).get("summary", ""),
                "research_summary": workflow_context.get("research_findings", {}).get("summary", ""),
                "post_length": len(final_post),
                "links_analyzed": workflow_context.get("link_analysis", {}).get("total_urls", 0),
                "topics_researched": len(workflow_context.get("research_findings", {}).get("topics_researched", []))
            }
            
            # Save to workflow history
            workflow_history_file = Path("workflow_history.json")
            history = []
            
            if workflow_history_file.exists():
                with open(workflow_history_file, 'r', encoding='utf-8') as f:
                    history = json.load(f)
            
            history.append(metadata)
            
            with open(workflow_history_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, indent=2, ensure_ascii=False)
                
            print(f"💾 Workflow metadata saved to {workflow_history_file}")
            
        except Exception as e:
            print(f"⚠️ Could not save workflow metadata: {e}")
    
    def generate_post(self, use_strands_workflow: bool = False) -> str:
        """
        Main entry point for generating LinkedIn posts
        
        Args:
            use_strands_workflow: Whether to use Strands native workflow (True) or sequential (False)
            
        Returns:
            Generated LinkedIn post
        """
        try:
            # Read instructions
            instructions = self.read_instructions()
            
            # Execute workflow - use sequential by default for better reliability
            if use_strands_workflow:
                print("🔄 Attempting Strands native workflow...")
                try:
                    final_post = self.execute_strands_workflow(instructions)
                except Exception as workflow_error:
                    print(f"⚠️ Strands workflow failed: {workflow_error}")
                    print("🔄 Falling back to sequential execution...")
                    final_post = self.execute_sequential_workflow(instructions)
            else:
                final_post = self.execute_sequential_workflow(instructions)
            
            return final_post
            
        except Exception as e:
            print(f"❌ Multi-agent generation failed: {e}")
            raise e


def main():
    """Main entry point for the multi-agent LinkedIn post generator"""
    try:
        generator = LinkedInMultiAgentGenerator()
        
        # Generate post using Strands workflow orchestration
        final_post = generator.generate_post(use_strands_workflow=True)
        
        # Display results
        print("\n" + "="*80)
        print("🎯 GENERATED LINKEDIN POST:")
        print("="*80)
        print(final_post)
        print("="*80)
        print(f"📊 Character count: {len(final_post)}")
        print("="*80)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nMake sure you have:")
        print("1. OPENAI_API_KEY in your .env file")
        print("2. input/instructions.txt with your post instructions")  
        print("3. input/prompt.txt with the base prompt")
        print("4. input/linkedin_style_prompt.txt with style analysis")
        print("5. Posts in posts/ folder for few-shot examples")
        print("\nTip: Set DEBUG=true in .env to see detailed workflow execution")


if __name__ == "__main__":
    main()
