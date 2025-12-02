from typing import Callable, Dict, Any, List

class ToolRegistry:
    _tools: Dict[str, Callable] = {}
    _schemas: List[Dict[str, Any]] = []

    @classmethod
    def register(cls, name: str, func: Callable, schema: Dict[str, Any]):
        """
        Register a tool with its function and schema.
        
        :param name: Unique name of the tool (e.g., 'query_products')
        :param func: The callable function to execute
        :param schema: JSON schema describing the tool (for LLM context)
        """
        cls._tools[name] = func
        cls._schemas.append({
            "name": name,
            "schema": schema
        })

    @classmethod
    def get_tool(cls, name: str) -> Callable | None:
        """Get a tool function by name."""
        return cls._tools.get(name)

    @classmethod
    def get_schemas(cls) -> List[Dict[str, Any]]:
        """Get all registered tool schemas."""
        return cls._schemas

    @classmethod
    def execute(cls, name: str, **kwargs) -> Any:
        """Execute a tool by name with arguments."""
        tool = cls.get_tool(name)
        if not tool:
            raise ValueError(f"Tool '{name}' not found")
        return tool(**kwargs)
