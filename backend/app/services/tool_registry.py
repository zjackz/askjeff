from typing import Callable, Dict, Any, List

class ToolRegistry:
    _tools: Dict[str, Callable] = {}
    _schemas: List[Dict[str, Any]] = []

    @classmethod
    def register(cls, name: str, description: str, parameters: Dict[str, Any]):
        """
        Register a tool using a decorator.
        
        :param name: Unique name of the tool
        :param description: Description for LLM
        :param parameters: JSON schema parameters for LLM
        """
        def decorator(func: Callable):
            cls._tools[name] = func
            cls._schemas.append({
                "name": name,
                "description": description,
                "parameters": parameters
            })
            return func
        return decorator

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
