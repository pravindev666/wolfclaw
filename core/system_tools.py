import logging
from core.tools import run_terminal_command, run_remote_ssh_command, web_search, read_document, simulate_gui, web_browser

logger = logging.getLogger(__name__)

class SystemTools:
    """
    Bridge class for ProactiveAgent to access system tools. 
    This provides a consistent interface for non-human agent interactions.
    """
    def __init__(self):
        self.available_tools = {
            "run_terminal_command": run_terminal_command,
            "run_remote_ssh_command": run_remote_ssh_command,
            "web_search": web_search,
            "read_document": read_document,
            "simulate_gui": simulate_gui,
            "web_browser": web_browser
        }

    def execute(self, tool_name, **kwargs):
        if tool_name not in self.available_tools:
            logger.error(f"Tool {tool_name} not found in SystemTools")
            return None
        
        try:
            return self.available_tools[tool_name](**kwargs)
        except Exception as e:
            logger.error(f"Error executing tool {tool_name}: {e}")
            return None
