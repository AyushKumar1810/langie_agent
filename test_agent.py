#!/usr/bin/env python3
"""
Test Suite for Langie - LangGraph Customer Support Agent
"""

import asyncio
import pytest
import json
from langie_agent import LangieAgent, WorkflowState, StageConfig, MCPServerType, MockMCPClient

class TestLangieAgent:
    """Test suite for Langie Agent"""
    
    @pytest.fixture
    def agent(self):
        """Create agent instance for testing"""
        return LangieAgent()
    
    @pytest.fixture
    def sample_input(self):
        """Sample input payload for testing"""
        return {
            "customer_name": "Test User",
            "email": "test@example.com",
            "query": "Test support request",
            "priority": "medium",
            "ticket_id": "TKT-TEST001"
        }
    
    def test_agent_initialization(self, agent):
        """Test agent initialization"""
        assert agent is not None
        assert len(agent.stages) == 11
        assert agent.common_client is not None
        assert agent.atlas_client is not None
    
    def test_stage_configuration(self, agent):
        """Test stage configuration correctness"""
        expected_stages = [
            "INTAKE", "UNDERSTAND", "PREPARE", "ASK", "WAIT",
            "RETRIEVE", "DECIDE", "UPDATE", "CREATE", "DO", "COMPLETE"
        ]
        
        actual_stages = [stage.name for stage in agent.stages]
        assert actual_stages == expected_stages
        
        # Test deterministic vs non-deterministic modes
        decide_stage = next(s for s in agent.stages if s.name == "DECIDE")
        assert decide_stage.mode == "non-deterministic"
        
        intake_stage = next(s for s in agent.stages if s.name == "INTAKE")
        assert intake_stage.mode == "deterministic"
    
    @pytest.mark.asyncio
    async def test_mcp_client_calls(self, agent):
        """Test MCP client ability execution"""
        # Test common server call
        result = await agent.common_client.call_ability("parse_request_text", {})
        assert "structured_data" in result
        
        # Test atlas server call
        result = await agent.atlas_client.call_ability("extract_entities", {})
        assert "entities" in result
    
    @pytest.mark.asyncio
    async def test_internal_abilities(self, agent):
        """Test internal ability handling"""
        test_state = {
            "ticket_id": "TKT-TEST001",
            "customer_name": "Test User"
        }
        
        result = await agent._handle_internal_ability("accept_payload", test_state)
        assert result["status"] == "payload_accepted"
        assert "timestamp" in result
        
        result = await agent._handle_internal_ability("store_answer", test_state)
        assert result["status"] == "answer_stored"
    
    @pytest.mark.asyncio
    async def test_deterministic_stage_execution(self, agent):
        """Test deterministic stage execution"""
        # Get UNDERSTAND stage (deterministic)
        understand_stage = next(s for s in agent.stages if s.name == "UNDERSTAND")
        
        test_state = {
            "ticket_id": "TKT-TEST001",
            "customer_name": "Test User",
            "execution_log": []
        }
        
        result = await agent._execute_deterministic_stage(understand_stage, test_state)
        
        # Should have results for both abilities
        assert "parse_request_text" in result
        assert "extract_entities" in result
        
        # Should have logged both executions
        assert len(test_state["execution_log"]) == 2
    
    @pytest.mark.asyncio
    async def test_non_deterministic_stage_execution(self, agent):
        """Test non-deterministic stage execution (DECIDE stage)"""
        decide_stage = next(s for s in agent.stages if s.name == "DECIDE")
        
        test_state = {
            "ticket_id": "TKT-TEST001",
            "customer_name": "Test User",
            "execution_log": []
        }
        
        result = await agent._execute_non_deterministic_stage(decide_stage, test_state)
        
        # Should always have solution evaluation
        assert "solution_evaluation" in result
        assert "escalation_decision" in result
        assert "update_payload" in result
    
    @pytest.mark.asyncio
    async def test_complete_workflow_execution(self, agent, sample_input):
        """Test complete workflow execution"""
        result = await agent.execute_workflow(sample_input)
        
        # Validate final payload structure
        assert "ticket_id" in result
        assert "customer" in result
        assert "request" in result
        assert "processing" in result
        assert "results" in result
        assert "execution_log" in result
        
        # Validate processing information
        assert result["processing"]["stages_completed"] == 11
        assert result["processing"]["status"] == "completed"
        
        # Validate all stages were executed
        stage_names = set(result["results"].keys())
        expected_stages = {
            "INTAKE", "UNDERSTAND", "PREPARE", "ASK", "WAIT",
            "RETRIEVE", "DECIDE", "UPDATE", "CREATE", "DO", "COMPLETE"
        }
        assert stage_names == expected_stages
    
    @pytest.mark.asyncio
    async def test_state_persistence(self, agent, sample_input):
        """Test state persistence across stages"""
        result = await agent.execute_workflow(sample_input)
        
        # Check that original input data persists
        assert result["customer"]["name"] == sample_input["customer_name"]
        assert result["customer"]["email"] == sample_input["email"]
        assert result["request"]["query"] == sample_input["query"]
        assert result["request"]["priority"] == sample_input["priority"]
    
    @pytest.mark.asyncio
    async def test_execution_logging(self, agent, sample_input):
        """Test comprehensive execution logging"""
        result = await agent.execute_workflow(sample_input)
        
        execution_log = result["execution_log"]
        
        # Should have multiple log entries
        assert len(execution_log) > 0
        
        # Each log entry should have required fields
        for log_entry in execution_log:
            assert "timestamp" in log_entry
            assert "stage" in log_entry
            assert "ability" in log_entry
            assert "server" in log_entry
            assert "result" in log_entry
        
        # Should have entries for different servers
        servers = {entry["server"] for entry in execution_log}
        assert "common" in servers
        assert "atlas" in servers
        assert "internal" in servers
    
    def test_stage_config_validation(self, agent):
        """Test stage configuration validation"""
        for stage in agent.stages:
            # Each stage should have required attributes
            assert hasattr(stage, 'name')
            assert hasattr(stage, 'mode')
            assert hasattr(stage, 'abilities')
            assert hasattr(stage, 'description')
            
            # Mode should be valid
            assert stage.mode in ["deterministic", "non-deterministic"]
            
            # Should have at least one ability
            assert len(stage.abilities) > 0
            
            # Each ability should have name and server
            for ability in stage.abilities:
                assert "name" in ability
                assert "server" in ability
    
    @pytest.mark.asyncio
    async def test_error_handling(self, agent):
        """Test error handling for invalid inputs"""
        # Test with missing required fields
        invalid_input = {
            "customer_name": "Test User"
            # Missing other required fields
        }
        
        try:
            result = await agent.execute_workflow(invalid_input)
            # Should still complete but with default values
            assert result is not None
        except Exception as e:
            # Should handle gracefully
            assert isinstance(e, (KeyError, ValueError))

class TestMockMCPClient:
    """Test suite for Mock MCP Client"""
    
    def test_client_initialization(self):
        """Test MCP client initialization"""
        common_client = MockMCPClient(MCPServerType.COMMON)
        atlas_client = MockMCPClient(MCPServerType.ATLAS)
        
        assert common_client.server_type == MCPServerType.COMMON
        assert atlas_client.server_type == MCPServerType.ATLAS
    
    @pytest.mark.asyncio
    async def test_ability_execution(self):
        """Test ability execution through MCP client"""
        client = MockMCPClient(MCPServerType.COMMON)
        
        result = await client.call_ability("parse_request_text", {})
        assert result is not None
        assert isinstance(result, dict)

# Performance Tests
class TestPerformance:
    """Performance tests for Langie Agent"""
    
    @pytest.mark.asyncio
    async def test_workflow_execution_time(self):
        """Test workflow execution completes within reasonable time"""
        agent = LangieAgent()
        sample_input = {
            "customer_name": "Performance Test",
            "email": "perf@test.com",
            "query": "Performance test query",
            "priority": "low",
            "ticket_id": "TKT-PERF001"
        }
        
        import time
        start_time = time.time()
        
        result = await agent.execute_workflow(sample_input)
        
        execution_time = time.time() - start_time
        
        # Should complete within 5 seconds (generous for mock implementation)
        assert execution_time < 5.0
        assert result["processing"]["status"] == "completed"

# Integration Tests
class TestIntegration:
    """Integration tests for complete system"""
    
    @pytest.mark.asyncio
    async def test_end_to_end_customer_support_flow(self):
        """Test complete customer support flow end-to-end"""
        agent = LangieAgent()
        
        # Realistic customer support scenario
        customer_request = {
            "customer_name": "Alice Johnson",
            "email": "alice.johnson@email.com",
            "query": "I'm having trouble accessing my account after the recent update. I can't reset my password and need urgent help.",
            "priority": "high",
            "ticket_id": "TKT-REAL001"
        }
        
        result = await agent.execute_workflow(customer_request)
        
        # Comprehensive validation
        assert result["processing"]["status"] == "completed"
        assert result["customer"]["name"] == "Alice Johnson"
        assert len(result["execution_log"]) > 10  # Should have many ability executions
        
        # Check critical stages executed
        critical_stages = ["UNDERSTAND", "DECIDE", "CREATE"]
        for stage in critical_stages:
            assert stage in result["results"]

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
