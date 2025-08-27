🤖 Langie - LangGraph Customer Support Agent
A sophisticated customer support workflow agent built with LangGraph, featuring 11-stage graph-based processing with state persistence and MCP (Model Context Protocol) client integration.

📋 Project Overview
Langie is a structured and logical LangGraph Agent that processes customer support tickets through a comprehensive 11-stage workflow. Each stage represents a clear phase of the customer support process, with abilities executed through MCP clients connecting to Atlas and Common servers.

🎯 Key Features
Graph-based Workflow: 11 well-defined stages with clear transitions
State Persistence: Maintains state variables across all stages
MCP Integration: Seamless integration with Atlas and Common MCP servers
Hybrid Execution: Both deterministic and non-deterministic stage execution
Comprehensive Logging: Detailed execution logs and performance metrics
Dynamic Decision Making: Runtime orchestration based on context and scoring
🏗️ Architecture
Workflow Stages
Stage	Icon	Description	Mode	Key Abilities
INTAKE	📥	Accept incoming payload	Deterministic	accept_payload
UNDERSTAND	🧠	Parse and understand request	Deterministic	parse_request_text, extract_entities
PREPARE	🛠️	Prepare and enrich data	Deterministic	normalize_fields, enrich_records, add_flags_calculations
ASK	❓	Request clarification	Deterministic	clarify_question
WAIT	⏳	Process customer response	Deterministic	extract_answer, store_answer
RETRIEVE	📚	Knowledge base search	Deterministic	knowledge_base_search, store_data
DECIDE	⚖️	Evaluate and decide	Non-deterministic	solution_evaluation, escalation_decision, update_payload
UPDATE	🔄	Update ticket status	Deterministic	update_ticket, close_ticket
CREATE	✍️	Generate response	Deterministic	response_generation
DO	🏃	Execute actions	Deterministic	execute_api_calls, trigger_notifications
COMPLETE	✅	Output final payload	Deterministic	output_payload
MCP Server Integration
COMMON Server: Handles abilities with no external data requirements
ATLAS Server: Manages abilities requiring external system interaction
Internal: State management and workflow control
🚀 Quick Start
Prerequisites
bash
pip install asyncio logging dataclasses typing datetime uuid enum
Basic Usage
python
import asyncio
from langie_agent import LangieAgent

# Sample customer request
sample_input = {
    "customer_name": "John Doe",
    "email": "john.doe@email.com",
    "query": "I was charged twice for my subscription this month. I need a refund for the duplicate charge.",
    "priority": "high",
    "ticket_id": "TKT-2024001"
}

# Initialize and run agent
async def main():
    agent = LangieAgent()
    result = await agent.execute_workflow(sample_input)
    print(json.dumps(result, indent=2))

asyncio.run(main())
📊 Input Schema
json
{
  "customer_name": "string (required)",
  "email": "string (required, email format)",
  "query": "string (required)",
  "priority": "string (low|medium|high|critical, default: medium)",
  "ticket_id": "string (format: TKT-XXXXXXXX)"
}
🔄 Workflow Execution Flow
mermaid
graph TD
    A[📥 INTAKE] --> B[🧠 UNDERSTAND]
    B --> C[🛠️ PREPARE]
    C --> D[❓ ASK]
    D --> E[⏳ WAIT]
    E --> F[📚 RETRIEVE]
    F --> G[⚖️ DECIDE]
    G --> H[🔄 UPDATE]
    H --> I[✍️ CREATE]
    I --> J[🏃 DO]
    J --> K[✅ COMPLETE]
    
    G -.->|Score < 90| L[Escalate to Human]
    G -.->|Score ≥ 90| H
🧩 Stage Details
Non-Deterministic Stage: DECIDE ⚖️
The DECIDE stage implements dynamic orchestration:

Solution Evaluation: Scores potential solutions (1-100)
Dynamic Decision: If score < 90, escalates to human agent
Payload Update: Records decision outcomes
python
# Example decision logic
if best_score < 90:
    # Execute escalation_decision ability
    escalate_to_human_agent()
else:
    # Proceed with automated resolution
    continue_workflow()
📝 State Management
The agent maintains persistent state across all stages:

python
class WorkflowState:
    customer_name: str
    email: str
    query: str
    priority: str
    ticket_id: str
    current_stage: str
    stage_results: Dict[str, Any]
    final_payload: Dict[str, Any]
    execution_log: List[Dict[str, Any]]
🔧 Configuration
The agent uses a comprehensive YAML configuration file (agent_config.yaml) that defines:

Input schema validation
MCP server endpoints and capabilities
Stage definitions and execution modes
State management rules
Error handling policies
Logging configuration
📈 Execution Logging
Every ability execution is logged with:

json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "stage": "UNDERSTAND",
  "ability": "parse_request_text",
  "server": "common",
  "result": {...}
}
🎯 Sample Output
json
{
  "ticket_id": "TKT-2024001",
  "customer": {
    "name": "John Doe",
    "email": "john.doe@email.com"
  },
  "request": {
    "query": "I was charged twice for my subscription...",
    "priority": "high"
  },
  "processing": {
    "stages_completed": 11,
    "execution_time": "2024-01-15T10:35:00Z",
    "status": "completed"
  },
  "results": {
    "UNDERSTAND": {
      "parse_request_text": {...},
      "extract_entities": {...}
    },
    "DECIDE": {
      "solution_evaluation": {"best_score": 95},
      "escalation_decision": {"escalate": false}
    }
  },
  "execution_log": [...]
}
🧪 Testing & Demo
Run the included demo to see Langie in action:

bash
python langie_agent.py
This will execute a complete workflow with sample customer data and display:

Stage-by-stage execution logs
Ability calls to MCP servers
Final structured payload
Execution summary statistics
🔍 Monitoring & Debugging
Execution Summary
Total stages completed
Abilities executed per server
Processing time
Success/failure rates
Logs Analysis
Stage transition timing
MCP server response times
Decision points and reasoning
Error tracking and recovery
⚡ Performance Features
Async Execution: Non-blocking ability execution
Timeout Management: Configurable timeouts per ability
Retry Logic: Automatic retry on transient failures
Resource Optimization: Efficient state management
🛠️ Development & Extension
Adding New Stages
Define stage in agent_config.yaml
Implement stage logic in LangieAgent
Add abilities to appropriate MCP servers
Update state transitions
Custom Abilities
python
async def _execute_custom_ability(self, ability_name: str, state: WorkflowState):
    # Implement custom ability logic
    return {"result": "custom_response"}
🔒 Security & Compliance
Input validation and sanitization
Secure MCP client communications
Audit trail for all operations
PII handling best practices
📚 Dependencies
Python 3.8+
asyncio: Asynchronous execution
logging: Comprehensive logging
typing: Type annotations
dataclasses: Structured data
datetime: Timestamp handling
uuid: Unique identifier generation
🤝 Contributing
Fork the repository
Create a feature branch
Implement changes with tests
Submit pull request with detailed description
📄 License
This project is licensed under the MIT License - see the LICENSE file for details.

👨‍💻 Author
Langie Agent - A sophisticated customer support workflow automation system built with LangGraph and MCP integration.

Langie thinks in stages, carries forward state variables carefully, and orchestrates MCP clients to deliver exceptional customer support experiences.

