#!/usr/bin/env python3
"""
LangGraph Customer Support Agent - Langie
A structured workflow agent for handling customer support tickets through 11 stages.
"""

import json
import logging
import asyncio
from typing import Dict, List, Any, Optional, TypedDict
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import uuid

# Mock MCP Client Implementation (replace with actual MCP clients)
class MCPServerType(Enum):
    COMMON = "common"
    ATLAS = "atlas"

class MockMCPClient:
    """Mock MCP Client for demonstration purposes"""
    
    def __init__(self, server_type: MCPServerType):
        self.server_type = server_type
        self.logger = logging.getLogger(f"MCP-{server_type.value.upper()}")
    
    async def call_ability(self, ability_name: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Mock ability execution"""
        self.logger.info(f"Executing {ability_name} on {self.server_type.value} server")
        
        # Mock responses for different abilities
        mock_responses = {
            "parse_request_text": {
                "structured_data": {
                    "issue_type": "billing",
                    "urgency": "high",
                    "keywords": ["refund", "charge", "error"]
                }
            },
            "extract_entities": {
                "entities": {
                    "product": "Premium Subscription",
                    "account_id": "ACC-12345",
                    "dates": ["2024-01-15"]
                }
            },
            "normalize_fields": {
                "normalized": {
                    "date_format": "ISO-8601",
                    "priority_code": "P1",
                    "ticket_id": payload.get("ticket_id", "").upper()
                }
            },
            "enrich_records": {
                "enriched": {
                    "sla_deadline": "2024-01-17T10:00:00Z",
                    "customer_tier": "Premium",
                    "previous_tickets": 2
                }
            },
            "add_flags_calculations": {
                "flags": {
                    "sla_risk": "medium",
                    "priority_score": 85,
                    "auto_escalate": False
                }
            },
            "clarify_question": {
                "clarification": "Could you please provide your transaction ID for the billing issue?"
            },
            "extract_answer": {
                "customer_response": "Transaction ID: TXN-789456"
            },
            "knowledge_base_search": {
                "kb_results": [
                    {"article": "Billing FAQ", "relevance": 95},
                    {"article": "Refund Process", "relevance": 88}
                ]
            },
            "solution_evaluation": {
                "solutions": [
                    {"solution": "Process refund", "score": 95},
                    {"solution": "Apply credit", "score": 78}
                ],
                "best_score": 95
            },
            "escalation_decision": {
                "escalate": False,
                "reason": "Score above threshold"
            },
            "update_ticket": {
                "status": "In Progress",
                "updated_fields": ["priority", "assignee"]
            },
            "close_ticket": {
                "status": "Resolved",
                "resolution_time": "2 hours"
            },
            "response_generation": {
                "response": "We've processed your refund request. You should see the credit within 3-5 business days."
            },
            "execute_api_calls": {
                "api_calls": ["CRM Update", "Billing System"],
                "success": True
            },
            "trigger_notifications": {
                "notifications": ["Email sent", "SMS sent"],
                "delivery_status": "Success"
            }
        }
        
        # Simulate processing time
        await asyncio.sleep(0.1)
        
        return mock_responses.get(ability_name, {"result": "Mock response"})

# State Management
class WorkflowState(TypedDict):
    """Type definition for workflow state"""
    customer_name: str
    email: str
    query: str
    priority: str
    ticket_id: str
    current_stage: str
    stage_results: Dict[str, Any]
    final_payload: Dict[str, Any]
    execution_log: List[Dict[str, Any]]

# Stage Definitions
@dataclass
class StageConfig:
    """Configuration for each workflow stage"""
    name: str
    mode: str  # "deterministic" or "non-deterministic"
    abilities: List[Dict[str, Any]]  # List of abilities with server mapping
    description: str

class LangieAgent:
    """
    Langie - A structured and logical Lang Graph Agent for Customer Support
    """
    
    def __init__(self):
        self.logger = logging.getLogger("Langie")
        self.common_client = MockMCPClient(MCPServerType.COMMON)
        self.atlas_client = MockMCPClient(MCPServerType.ATLAS)
        
        # Initialize stage configurations
        self.stages = self._initialize_stages()
        
        self.logger.info("🧩 Langie Agent initialized with 11 workflow stages")
    
    def _initialize_stages(self) -> List[StageConfig]:
        """Initialize all 11 workflow stages"""
        return [
            StageConfig(
                name="INTAKE",
                mode="deterministic",
                abilities=[{"name": "accept_payload", "server": "internal"}],
                description="📥 Accept incoming customer request payload"
            ),
            StageConfig(
                name="UNDERSTAND",
                mode="deterministic",
                abilities=[
                    {"name": "parse_request_text", "server": "common"},
                    {"name": "extract_entities", "server": "atlas"}
                ],
                description="🧠 Parse and understand customer request"
            ),
            StageConfig(
                name="PREPARE",
                mode="deterministic",
                abilities=[
                    {"name": "normalize_fields", "server": "common"},
                    {"name": "enrich_records", "server": "atlas"},
                    {"name": "add_flags_calculations", "server": "common"}
                ],
                description="🛠️ Prepare and enrich customer data"
            ),
            StageConfig(
                name="ASK",
                mode="deterministic",
                abilities=[{"name": "clarify_question", "server": "atlas"}],
                description="❓ Ask for clarification if needed"
            ),
            StageConfig(
                name="WAIT",
                mode="deterministic",
                abilities=[
                    {"name": "extract_answer", "server": "atlas"},
                    {"name": "store_answer", "server": "internal"}
                ],
                description="⏳ Wait for and process customer response"
            ),
            StageConfig(
                name="RETRIEVE",
                mode="deterministic",
                abilities=[
                    {"name": "knowledge_base_search", "server": "atlas"},
                    {"name": "store_data", "server": "internal"}
                ],
                description="📚 Retrieve relevant knowledge base information"
            ),
            StageConfig(
                name="DECIDE",
                mode="non-deterministic",
                abilities=[
                    {"name": "solution_evaluation", "server": "common"},
                    {"name": "escalation_decision", "server": "atlas"},
                    {"name": "update_payload", "server": "internal"}
                ],
                description="⚖️ Evaluate solutions and make decisions"
            ),
            StageConfig(
                name="UPDATE",
                mode="deterministic",
                abilities=[
                    {"name": "update_ticket", "server": "atlas"},
                    {"name": "close_ticket", "server": "atlas"}
                ],
                description="🔄 Update ticket status and information"
            ),
            StageConfig(
                name="CREATE",
                mode="deterministic",
                abilities=[{"name": "response_generation", "server": "common"}],
                description="✍️ Generate customer response"
            ),
            StageConfig(
                name="DO",
                mode="deterministic",
                abilities=[
                    {"name": "execute_api_calls", "server": "atlas"},
                    {"name": "trigger_notifications", "server": "atlas"}
                ],
                description="🏃 Execute actions and notifications"
            ),
            StageConfig(
                name="COMPLETE",
                mode="deterministic",
                abilities=[{"name": "output_payload", "server": "internal"}],
                description="✅ Output final structured payload"
            )
        ]
    
    async def _execute_ability(self, ability: Dict[str, Any], state: WorkflowState) -> Dict[str, Any]:
        """Execute a single ability using appropriate MCP client"""
        ability_name = ability["name"]
        server = ability["server"]
        
        self.logger.info(f"🎯 Executing ability: {ability_name} on {server} server")
        
        if server == "common":
            return await self.common_client.call_ability(ability_name, state)
        elif server == "atlas":
            return await self.atlas_client.call_ability(ability_name, state)
        else:
            # Internal abilities (state management)
            return await self._handle_internal_ability(ability_name, state)
    
    async def _handle_internal_ability(self, ability_name: str, state: WorkflowState) -> Dict[str, Any]:
        """Handle internal abilities for state management"""
        if ability_name == "accept_payload":
            return {"status": "payload_accepted", "timestamp": datetime.now().isoformat()}
        elif ability_name == "store_answer":
            return {"status": "answer_stored", "timestamp": datetime.now().isoformat()}
        elif ability_name == "store_data":
            return {"status": "data_stored", "timestamp": datetime.now().isoformat()}
        elif ability_name == "update_payload":
            return {"status": "payload_updated", "timestamp": datetime.now().isoformat()}
        elif ability_name == "output_payload":
            return {"status": "payload_output", "final": True}
        else:
            return {"status": "unknown_internal_ability"}
    
    async def _execute_deterministic_stage(self, stage: StageConfig, state: WorkflowState) -> Dict[str, Any]:
        """Execute abilities in deterministic sequence"""
        self.logger.info(f"📋 Executing deterministic stage: {stage.name}")
        
        stage_results = {}
        for ability in stage.abilities:
            result = await self._execute_ability(ability, state)
            stage_results[ability["name"]] = result
            
            # Log execution
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "stage": stage.name,
                "ability": ability["name"],
                "server": ability["server"],
                "result": result
            }
            state["execution_log"].append(log_entry)
        
        return stage_results
    
    async def _execute_non_deterministic_stage(self, stage: StageConfig, state: WorkflowState) -> Dict[str, Any]:
        """Execute abilities with dynamic orchestration"""
        self.logger.info(f"🎲 Executing non-deterministic stage: {stage.name}")
        
        stage_results = {}
        
        # For DECIDE stage, implement scoring logic
        if stage.name == "DECIDE":
            # First evaluate solutions
            solution_ability = next(a for a in stage.abilities if a["name"] == "solution_evaluation")
            solution_result = await self._execute_ability(solution_ability, state)
            stage_results["solution_evaluation"] = solution_result
            
            # Log solution evaluation
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "stage": stage.name,
                "ability": "solution_evaluation",
                "server": "common",
                "result": solution_result
            }
            state["execution_log"].append(log_entry)
            
            # Dynamic decision: escalate if score < 90
            best_score = solution_result.get("best_score", 0)
            self.logger.info(f"🔍 Best solution score: {best_score}")
            
            if best_score < 90:
                self.logger.info("⬆️ Score below threshold, executing escalation decision")
                escalation_ability = next(a for a in stage.abilities if a["name"] == "escalation_decision")
                escalation_result = await self._execute_ability(escalation_ability, state)
                stage_results["escalation_decision"] = escalation_result
                
                # Log escalation
                log_entry = {
                    "timestamp": datetime.now().isoformat(),
                    "stage": stage.name,
                    "ability": "escalation_decision",
                    "server": "atlas",
                    "result": escalation_result
                }
                state["execution_log"].append(log_entry)
            else:
                self.logger.info("✅ Score above threshold, no escalation needed")
                stage_results["escalation_decision"] = {"escalate": False, "reason": "Score above threshold"}
            
            # Always update payload
            update_ability = next(a for a in stage.abilities if a["name"] == "update_payload")
            update_result = await self._execute_ability(update_ability, state)
            stage_results["update_payload"] = update_result
            
            # Log payload update
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "stage": stage.name,
                "ability": "update_payload",
                "server": "internal",
                "result": update_result
            }
            state["execution_log"].append(log_entry)
        
        return stage_results
    
    async def execute_workflow(self, initial_payload: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the complete customer support workflow"""
        self.logger.info("🚀 Starting customer support workflow execution")
        
        # Initialize state
        state: WorkflowState = {
            "customer_name": initial_payload.get("customer_name", ""),
            "email": initial_payload.get("email", ""),
            "query": initial_payload.get("query", ""),
            "priority": initial_payload.get("priority", "medium"),
            "ticket_id": initial_payload.get("ticket_id", f"TKT-{uuid.uuid4().hex[:8].upper()}"),
            "current_stage": "",
            "stage_results": {},
            "final_payload": {},
            "execution_log": []
        }
        
        self.logger.info(f"📋 Processing ticket: {state['ticket_id']}")
        
        # Execute all stages
        for stage in self.stages:
            self.logger.info(f"\n{'='*50}")
            self.logger.info(f"🎯 Stage: {stage.name} - {stage.description}")
            self.logger.info(f"Mode: {stage.mode}")
            
            state["current_stage"] = stage.name
            
            if stage.mode == "deterministic":
                stage_results = await self._execute_deterministic_stage(stage, state)
            else:
                stage_results = await self._execute_non_deterministic_stage(stage, state)
            
            # Store stage results in state
            state["stage_results"][stage.name] = stage_results
            
            self.logger.info(f"✅ Completed stage: {stage.name}")
        
        # Prepare final payload
        final_payload = {
            "ticket_id": state["ticket_id"],
            "customer": {
                "name": state["customer_name"],
                "email": state["email"]
            },
            "request": {
                "query": state["query"],
                "priority": state["priority"]
            },
            "processing": {
                "stages_completed": len(self.stages),
                "execution_time": datetime.now().isoformat(),
                "status": "completed"
            },
            "results": state["stage_results"],
            "execution_log": state["execution_log"]
        }
        
        state["final_payload"] = final_payload
        
        self.logger.info("\n" + "="*50)
        self.logger.info("🎉 Workflow completed successfully!")
        self.logger.info(f"📊 Total stages executed: {len(self.stages)}")
        self.logger.info(f"📝 Total abilities executed: {len(state['execution_log'])}")
        
        return final_payload

async def main():
    """Demo execution of the LangGraph Customer Support Agent"""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Sample customer query
    sample_input = {
        "customer_name": "John Doe",
        "email": "john.doe@email.com",
        "query": "I was charged twice for my subscription this month. I need a refund for the duplicate charge.",
        "priority": "high",
        "ticket_id": "TKT-2024001"
    }
    
    print("🤖 Langie - LangGraph Customer Support Agent")
    print("=" * 60)
    print("Sample Input:")
    print(json.dumps(sample_input, indent=2))
    print("\n" + "=" * 60)
    
    # Initialize and run agent
    agent = LangieAgent()
    
    try:
        final_result = await agent.execute_workflow(sample_input)
        
        print("\n" + "=" * 60)
        print("🎯 FINAL PAYLOAD OUTPUT:")
        print("=" * 60)
        print(json.dumps(final_result, indent=2))
        
        # Summary statistics
        print("\n" + "=" * 60)
        print("📊 EXECUTION SUMMARY:")
        print("=" * 60)
        print(f"Ticket ID: {final_result['ticket_id']}")
        print(f"Customer: {final_result['customer']['name']}")
        print(f"Stages Completed: {final_result['processing']['stages_completed']}")
        print(f"Total Abilities Executed: {len(final_result['execution_log'])}")
        print(f"Status: {final_result['processing']['status']}")
        
        # Show execution log summary
        print("\n📋 EXECUTION LOG SUMMARY:")
        for log_entry in final_result['execution_log']:
            print(f"  {log_entry['stage']}: {log_entry['ability']} -> {log_entry['server']} server")
        
    except Exception as e:
        print(f"❌ Error during workflow execution: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
