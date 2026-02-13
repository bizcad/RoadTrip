"""
base_agent.py - Base Class for Registry Agents

Provides common interface for all workstream agents (WS0-4).
Enables inter-agent communication and state tracking.
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from datetime import datetime

from .registry_models import AgentState, AgentStatus, AgentQuery


class BaseAgent(ABC):
    """Base class for all registry workstream agents."""
    
    def __init__(self, agent_id: str, use_mock: bool = True):
        """
        Initialize agent.
        
        Args:
            agent_id: Identifier like "WS0", "WS1", etc.
            use_mock: If True, use mock data; if False, use real implementation
        """
        self.agent_id = agent_id
        self.use_mock = use_mock
        self.state = AgentState.INIT
        self.last_action = ""
        self.error: Optional[str] = None
        self.query_log: List[AgentQuery] = []
        
        # Set up logging
        self.logger = logging.getLogger(agent_id)
        handler = logging.StreamHandler()
        formatter = logging.Formatter(f'[{agent_id}] %(levelname)s: %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
    
    def transition_state(self, new_state: AgentState, action: str = ""):
        """Transition agent to new state."""
        self.logger.info(f"{self.state.value} → {new_state.value}")
        self.state = new_state
        self.last_action = action
    
    def query_agent(self, target_agent: "BaseAgent", query: str) -> Any:
        """
        Query another agent. Enables inter-agent communication.
        
        Args:
            target_agent: The agent to query
            query: The query string
            
        Returns:
            Response from target agent
        """
        self.transition_state(AgentState.QUERYING, f"Querying {target_agent.agent_id}")
        
        try:
            # Call target agent's handler
            response = target_agent.handle_query(query)
            
            # Log the interaction
            self.log_query(target_agent.agent_id, query, response)
            
            return response
        except Exception as e:
            self.error = str(e)
            self.transition_state(AgentState.ERROR, f"Query failed: {e}")
            raise
    
    @abstractmethod
    def handle_query(self, query: str) -> Any:
        """
        Handle a query from another agent.
        
        Must be implemented by subclass.
        """
        pass
    
    def log_query(self, to_agent: str, query: str, response: Any):
        """Log inter-agent query."""
        log_entry = AgentQuery(
            from_agent=self.agent_id,
            to_agent=to_agent,
            query=query,
            response=str(response)[:200]  # Truncate for logging
        )
        self.query_log.append(log_entry)
        
        # Also log to file for debugging
        self.logger.debug(f"→ {to_agent}: {query[:50]}...")
        self.logger.debug(f"← {to_agent}: {response}")
    
    def get_status(self) -> AgentStatus:
        """Get current agent status."""
        return AgentStatus(
            agent_id=self.agent_id,
            state=self.state,
            last_action=self.last_action,
            error=self.error
        )
    
    def clarify(self, question: str) -> str:
        """
        Ask for clarification (hook for external coordination).
        
        Usage: agent.clarify("Should I register deprecated skills?")
        
        This is a placeholder - in production, this would prompt
        the external coordinator/operator.
        """
        self.logger.warning(f"⚠️ CLARIFICATION NEEDED: {question}")
        return "PENDING_RESPONSE"
    
    def validate_determinism(self, key: str, func, *args):
        """
        Verify that a function is deterministic (called twice = same result).
        
        Used during mock validation to ensure real impl will be deterministic.
        """
        result1 = func(*args)
        result2 = func(*args)
        
        if result1 != result2:
            self.logger.error(f"❌ Non-deterministic function: {key}")
            raise RuntimeError(f"Function {key} is not deterministic!")
        
        self.logger.info(f"✅ Deterministic verified: {key}")
        return result1
