#!/usr/bin/env python3
"""
Langie Agent Demo Script
Comprehensive demonstration of the LangGraph Customer Support Agent
"""

import asyncio
import json
import time
from langie_agent import LangieAgent

class DemoRunner:
    """Demo runner for Langie Agent"""
    
    def __init__(self):
        self.agent = LangieAgent()
    
    def print_header(self, title: str):
        """Print formatted section header"""
        print("\n" + "="*80)
        print(f"🎯 {title}")
        print("="*80)
    
    def print_subheader(self, title: str):
        """Print formatted subsection header"""
        print(f"\n🔸 {title}")
        print("-" * 60)
    
    async def demo_basic_workflow(self):
        """Demonstrate basic workflow execution"""
        self.print_header("BASIC WORKFLOW DEMONSTRATION")
        
        # Sample customer request
        sample_input = {
            "customer_name": "Jane Smith",
            "email": "jane.smith@email.com",
            "query": "My premium subscription renewal failed but I was still charged. Please help me resolve this billing issue.",
            "priority": "high",
            "ticket_id": "TKT-DEMO001"
        }
        
        print("📋 Input Payload:")
        print(json.dumps(sample_input, indent=2))
        
        # Execute workflow
        start_time = time.time()
        result = await self.agent.execute_workflow(sample_input)
        execution_time = time.time() - start_time
        
        self.print_subheader("EXECUTION RESULTS")
        print(f"⏱️  Total Execution Time: {execution_time:.2f} seconds")
        print(f"🎫 Ticket ID: {result['ticket_id']}")
        print(f"👤 Customer: {result['customer']['name']}")
        print(f"📊 Stages Completed: {result['processing']['stages_completed']}")
        print(f"✅ Status: {result['processing']['status']}")
        
        return result
    
    async def demo_escalation_scenario(self):
        """Demonstrate escalation scenario with low confidence score"""
        self.print_header("ESCALATION SCENARIO DEMONSTRATION")
        
        # Sample request that would trigger escalation
        escalation_input = {
            "customer_name": "Robert Wilson",
            "email": "robert.wilson@email.com",
            "query": "I have a very complex billing issue involving multiple accounts and international transactions that occurred over several months.",
            "priority": "critical",
            "ticket_id": "TKT-ESCL001"
        }
        
        print("📋 Complex Input Payload (Expected to Escalate):")
        print(json.dumps(escalation_input, indent=2))
        
        # Note: In a real scenario, this would trigger escalation based on solution scoring
        print("\n💡 Note: This scenario would typically result in escalation to human agent")
        print("    when solution confidence score < 90")
        
        result = await self.agent.execute_workflow(escalation_input)
        
        # Check if escalation logic was triggered
        decide_stage = result['results'].get('DECIDE', {})
        escalation_result = decide_stage.get('escalation_decision', {})
        
        self.print_subheader("ESCALATION ANALYSIS")
        if escalation_result.get('escalate', False):
            print("🚨 ESCALATED: Ticket assigned to human agent")
            print(f"   Reason: {escalation_result.get('reason', 'Score below threshold')}")
        else:
            print("✅ AUTOMATED: Sufficient confidence for automated resolution")
        
        return result
    
    def analyze_execution_log(self, result: dict):
        """Analyze and display execution log statistics"""
        self.print_header("EXECUTION LOG ANALYSIS")
        
        execution_log = result.get('execution_log', [])
        
        # Server usage statistics
        server_stats = {}
        stage_stats = {}
        
        for log_entry in execution_log:
            server = log_entry.get('server', 'unknown')
            stage = log_entry.get('stage', 'unknown')
            
            server_stats[server] = server_stats.get(server, 0) + 1
            stage_stats[stage] = stage_stats.get(stage, 0) + 1
        
        self.print_subheader("SERVER USAGE STATISTICS")
        for server, count in server_stats.items():
            print(f"  {server.upper()} Server: {count} abilities executed")
        
        self.print_subheader("STAGE EXECUTION SUMMARY")
        for stage, count in stage_stats.items():
            print(f"  {stage}: {count} abilities")
        
        self.print_subheader("DETAILED EXECUTION LOG")
        for i, log_entry in enumerate(execution_log, 1):
            timestamp = log_entry.get('timestamp', '')
            stage = log_entry.get('stage', '')
            ability = log_entry.get('ability', '')
            server = log_entry.get('server', '')
            
            print(f"  {i:2d}. {timestamp[-8:]} | {stage:10s} | {ability:20s} | {server:8s}")
    
    def display_stage_results(self, result: dict):
        """Display detailed stage results"""
        self.print_header("DETAILED STAGE RESULTS")
        
        stage_results = result.get('results', {})
        
        for stage_name, abilities in stage_results.items():
            self.print_subheader(f"STAGE: {stage_name}")
            
            for ability_name, ability_result in abilities.items():
                print(f"  📝 {ability_name}:")
                
                # Display key results (truncated for readability)
                if isinstance(ability_result, dict):
                    for key, value in list(ability_result.items())[:3]:  # Show first 3 items
                        if isinstance(value, str) and len(value) > 50:
                            value = value[:50] + "..."
                        print(f"     • {key}: {value}")
                    
                    if len(ability_result) > 3:
                        print(f"     • ... ({len(ability_result) - 3} more items)")
                else:
                    print(f"     • Result: {ability_result}")
                print()
    
    async def run_comprehensive_demo(self):
        """Run comprehensive demonstration"""
        print("🤖 LANGIE - LANGGRAPH CUSTOMER SUPPORT AGENT")
        print("🎯 Comprehensive Demo Execution")
        print("="*80)
        
        try:
            # Demo 1: Basic workflow
            result1 = await self.demo_basic_workflow()
            
            # Demo 2: Escalation scenario
            result2 = await self.demo_escalation_scenario()
            
            # Analysis
            self.analyze_execution_log(result1)
            self.display_stage_results(result1)
            
            # Final summary
            self.print_header("DEMO COMPLETION SUMMARY")
            print("✅ Basic Workflow: Completed successfully")
            print("✅ Escalation Scenario: Demonstrated decision logic")
            print("✅ Log Analysis: Server usage and timing analyzed")
            print("✅ Stage Results: Detailed output reviewed")
            print("\n🎉 Langie Agent demonstration completed successfully!")
            print("\n📊 Key Features Demonstrated:")
            print("   • 11-stage graph workflow execution")
            print("   • State persistence across stages")
            print("   • MCP server integration (Common/Atlas)")
            print("   • Non-deterministic decision making")
            print("   • Comprehensive logging and monitoring")
            print("   • Structured payload output")
            
        except Exception as e:
            print(f"❌ Demo execution failed: {e}")
            raise

async def main():
    """Main demo execution function"""
    demo = DemoRunner()
    await demo.run_comprehensive_demo()

if __name__ == "__main__":
    asyncio.run(main())
