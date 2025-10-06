import logging

logging.basicConfig(level=logging.INFO)

def test_tools_registry():
    """Test tools registry initialization within Flask app context"""
    from app import app
    
    with app.app_context():
        from tools_registry import ToolsRegistry
        
        print("\nInitializing Tools Registry...")
        registry = ToolsRegistry()
        
        print("\n" + "="*60)
        print("TOOLS REGISTRY INITIALIZED")
        print("="*60)
        
        info = registry.get_tool_info()
        print(f"\nTotal tools: {info['count']}")
        print("\nAvailable tools:")
        for tool_name in info['tools']:
            metadata = info['metadata'][tool_name]
            approval = " [REQUIRES APPROVAL]" if metadata['requires_approval'] else ""
            print(f"  - {tool_name}{approval}")
            print(f"    {metadata['description']}")
            print(f"    Parameters: {', '.join(metadata['parameters'])}")
            print()
        
        return registry

if __name__ == "__main__":
    test_tools_registry()
