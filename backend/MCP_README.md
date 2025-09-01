# MCP (Model Context Protocol) Implementation

## Overview

The MCP (Model Context Protocol) system provides a standardized interface for AI agents to access external tools, APIs, and services. This implementation follows best practices and provides a robust foundation for tool orchestration in the AI Dietitian system.

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   AI Agents     │    │   MCP Client    │    │   MCP Server    │
│                 │◄──►│                 │◄──►│                 │
│ • Diet Planner  │    │ • Tool Calls    │    │ • Tool Registry │
│ • Recipe Gen    │    │ • Async Support │    │ • Rate Limiting │
│ • Grocery Mgmt  │    │ • Error Handling│    │ • Session Mgmt  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                       │
                                ▼                       ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │   Tool Categories│    │   External APIs │
                       │                 │    │                 │
                       │ • Nutrition     │    │ • Nutrition DB  │
                       │ • Recipes       │    │ • Recipe APIs   │
                       │ • Grocery       │    │ • Grocery Stores│
                       │ • Health        │    │ • Health APIs   │
                       │ • Ordering      │    │ • Delivery Svc  │
                       │ • Tracking      │    │ • Analytics     │
                       └─────────────────┘    └─────────────────┘
```

## 🚀 Features

### Core Features
- **Tool Registry**: Centralized tool management with validation
- **Session Management**: User session tracking and management
- **Rate Limiting**: Per-user and per-tool rate limiting
- **Error Handling**: Comprehensive error handling with custom exceptions
- **Async Support**: Asynchronous tool execution for better performance
- **Health Monitoring**: Server health checks and performance metrics

### Tool Categories
1. **Nutrition Tools**: Food data, calorie calculations, dietary restrictions
2. **Recipe Tools**: Recipe search, generation, and adaptation
3. **Grocery Tools**: List generation, store finding, price comparison
4. **Health Tools**: Health insights, goal tracking, wellness recommendations
5. **Ordering Tools**: Grocery ordering, delivery tracking, payment processing
6. **Tracking Tools**: Progress monitoring, data analysis, goal assessment

## 📁 File Structure

```
backend/app/mcp/
├── __init__.py              # Package initialization
├── config.py                # Configuration settings
├── exceptions.py            # Custom exception classes
├── mcp_server.py            # Main MCP server
├── mcp_client.py            # Client for agents
├── tool_registry.py         # Tool management
├── schemas.py               # Pydantic data models
└── tools/                   # Tool category implementations
    ├── __init__.py
    ├── nutrition_tools.py
    ├── recipe_tools.py
    ├── grocery_tools.py
    ├── health_tools.py
    ├── ordering_tools.py
    └── tracking_tools.py
```

## 🔧 Installation

### 1. Install Dependencies
```bash
cd backend
pip install -r requirements-mcp.txt
```

### 2. Environment Variables
Add to your `.env` file:
```bash
# MCP Configuration
MCP_ENABLED=true
MCP_MAX_CONCURRENT_CALLS=100
MCP_DEFAULT_TIMEOUT=30.0
MCP_ENABLE_RATE_LIMITING=true

# External API Keys
NUTRITION_API_KEY=your_nutrition_api_key
RECIPE_API_KEY=your_recipe_api_key
GROCERY_API_KEY=your_grocery_api_key
ZEPTO_API_KEY=your_zepto_api_key
BLINKIT_API_KEY=your_blinkit_api_key
```

## 🎯 Usage

### 1. Basic Agent Integration

```python
from app.agents.base_agent import BaseAgent

class DietPlannerAgent(BaseAgent):
    async def process(self, state):
        # Initialize MCP client
        user_id = state.get("user_data", {}).get("user_id")
        if user_id:
            self.initialize_mcp_client(user_id)
        
        # Use MCP tools
        if self.mcp_client:
            # Get nutrition info
            nutrition = await self.get_nutrition_info("chicken breast", 100, "grams")
            
            # Search recipes
            recipes = await self.search_recipes(["chicken", "vegetables"])
            
            # Generate grocery list
            grocery_list = await self.generate_grocery_list(meal_plan)
        
        return state
```

### 2. Direct MCP Client Usage

```python
from app.mcp.mcp_client import MCPClient

async def main():
    # Create MCP client
    client = MCPClient("user123", "session456")
    
    # Call tools
    result = await client.call_tool("get_nutrition_info", {
        "food_name": "apple",
        "quantity": 1,
        "unit": "piece"
    })
    
    print(f"Apple nutrition: {result}")
    
    # Cleanup
    await client.cleanup()
```

### 3. Async Tool Execution

```python
async def async_example():
    client = MCPClient("user123")
    
    # Start async execution
    request_id = await client.call_tool_async("order_groceries", {
        "grocery_list": ["milk", "bread"],
        "delivery_address": "123 Main St"
    })
    
    # Do other work...
    
    # Get result when ready
    result = await client.get_async_result(request_id, timeout=60)
    print(f"Order result: {result}")
```

## 🌐 API Endpoints

### Tool Management
- `GET /api/v1/mcp/tools` - List all available tools
- `GET /api/v1/mcp/tools/{category}` - Get tools by category
- `GET /api/v1/mcp/tools/details/{tool_name}` - Get tool details
- `GET /api/v1/mcp/categories` - List tool categories

### Tool Execution
- `POST /api/v1/mcp/execute` - Execute tool synchronously
- `POST /api/v1/mcp/execute/async` - Execute tool asynchronously

### Search and Discovery
- `GET /api/v1/mcp/search` - Search tools by query
- `GET /api/v1/mcp/statistics` - Get tool usage statistics

### Server Management
- `GET /api/v1/mcp/server/status` - Get server status
- `GET /api/v1/mcp/server/health` - Get server health
- `GET /api/v1/mcp/validation` - Validate tool registration
- `GET /api/v1/mcp/export` - Export tool specifications

## 🛠️ Adding New Tools

### 1. Create Tool Definition

```python
# In app/mcp/tools/your_category_tools.py
from ..schemas import MCPTool, ToolParameter, ToolCategory, ParameterType

class YourCategoryTools:
    def get_tools(self):
        return [self._get_your_tool()]
    
    def _get_your_tool(self):
        return MCPTool(
            name="your_tool_name",
            description="Description of your tool",
            category=ToolCategory.YOUR_CATEGORY,
            parameters={
                "param1": ToolParameter(
                    name="param1",
                    type=ParameterType.STRING,
                    description="Parameter description",
                    required=True
                )
            },
            required_params=["param1"],
            version="1.0.0",
            author="Your Name",
            tags=["your", "tool", "tags"]
        )
```

### 2. Register Tool Category

```python
# In app/mcp/mcp_server.py
def _register_core_tools(self):
    from .tools import (
        NutritionTools, RecipeTools, GroceryTools, 
        HealthTools, OrderingTools, TrackingTools,
        YourCategoryTools  # Add this
    )
    
    tool_categories = [
        NutritionTools(),
        RecipeTools(),
        GroceryTools(),
        HealthTools(),
        OrderingTools(),
        TrackingTools(),
        YourCategoryTools()  # Add this
    ]
```

### 3. Add to Package Exports

```python
# In app/mcp/tools/__init__.py
from .your_category_tools import YourCategoryTools

__all__ = [
    "NutritionTools",
    "RecipeTools", 
    "GroceryTools",
    "HealthTools",
    "OrderingTools",
    "TrackingTools",
    "YourCategoryTools"  # Add this
]
```

## 🔍 Monitoring and Debugging

### 1. Health Checks
```bash
curl http://localhost:8000/api/v1/mcp/server/health
```

### 2. Tool Statistics
```bash
curl http://localhost:8000/api/v1/mcp/statistics
```

### 3. Server Status
```bash
curl http://localhost:8000/api/v1/mcp/server/status
```

### 4. Tool Validation
```bash
curl http://localhost:8000/api/v1/mcp/validation
```

## 🚨 Error Handling

The MCP system provides comprehensive error handling:

### Custom Exceptions
- `MCPError`: Base exception for all MCP errors
- `ToolNotFoundError`: Tool not found
- `InvalidParametersError`: Invalid tool parameters
- `ToolExecutionError`: Tool execution failed
- `ToolTimeoutError`: Tool execution timed out
- `ToolRateLimitError`: Rate limit exceeded

### Error Response Format
```json
{
    "success": false,
    "error": "Error message",
    "error_code": "ERROR_CODE",
    "details": {
        "tool_name": "tool_name",
        "context": "Additional context"
    }
}
```

## 📊 Performance Optimization

### 1. Rate Limiting
- Per-user rate limiting (60 requests/minute default)
- Per-tool rate limiting
- Configurable limits via environment variables

### 2. Concurrency Control
- Semaphore-based concurrent call limiting
- Configurable max concurrent calls (100 default)
- Async execution support

### 3. Caching
- Redis-based caching support
- Configurable TTL (300 seconds default)
- Tool result caching

### 4. Session Management
- Automatic session cleanup (24 hours)
- Session activity tracking
- Memory-efficient session storage

## 🔒 Security Features

### 1. Authentication
- User ID validation for all tool calls
- Session-based access control
- Configurable anonymous tool access

### 2. Input Validation
- Pydantic-based parameter validation
- Required parameter checking
- Type and format validation

### 3. Rate Limiting
- Prevents abuse and DoS attacks
- Per-user and per-tool limits
- Configurable limits

## 🧪 Testing

### 1. Unit Tests
```bash
cd backend
pytest app/mcp/ -v
```

### 2. Integration Tests
```bash
pytest tests/test_mcp_integration.py -v
```

### 3. Load Testing
```bash
# Test concurrent tool execution
python -m pytest tests/test_mcp_load.py -v
```

## 🚀 Deployment

### 1. Docker
```dockerfile
# Add to your Dockerfile
COPY app/mcp/ /app/app/mcp/
RUN pip install -r requirements-mcp.txt
```

### 2. Environment Configuration
```bash
# Production settings
MCP_ENABLED=true
MCP_MAX_CONCURRENT_CALLS=200
MCP_DEFAULT_TIMEOUT=60.0
MCP_ENABLE_RATE_LIMITING=true
MCP_ENABLE_CACHING=true
MCP_ENABLE_METRICS=true
```

### 3. Health Checks
```yaml
# Docker Compose health check
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/api/v1/mcp/server/health"]
  interval: 30s
  timeout: 10s
  retries: 3
```

## 📈 Future Enhancements

### Planned Features
1. **Plugin System**: Dynamic tool loading
2. **Webhook Support**: Real-time notifications
3. **Advanced Caching**: Multi-level caching strategy
4. **Metrics Dashboard**: Real-time performance monitoring
5. **Tool Marketplace**: Community-contributed tools
6. **AI-Powered Tool Selection**: Automatic tool recommendation

### Integration Opportunities
1. **LangChain**: Enhanced AI agent integration
2. **OpenAI Functions**: Direct function calling
3. **Vector Databases**: Semantic tool search
4. **GraphQL**: Flexible query interface
5. **WebSocket**: Real-time tool updates

## 🤝 Contributing

### 1. Code Style
- Follow PEP 8 guidelines
- Use type hints
- Add comprehensive docstrings
- Include unit tests

### 2. Tool Development
- Follow the established tool structure
- Include parameter validation
- Add error handling
- Provide usage examples

### 3. Testing
- Maintain >90% test coverage
- Include integration tests
- Test error scenarios
- Performance testing

## 📚 Additional Resources

- [MCP Specification](https://modelcontextprotocol.io/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pydantic Documentation](https://pydantic-docs.helpmanual.io/)
- [AsyncIO Documentation](https://docs.python.org/3/library/asyncio.html)

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section
2. Review error logs
3. Validate tool configurations
4. Check API endpoint responses
5. Verify environment variables

---

**Note**: This MCP implementation is designed to be production-ready with comprehensive error handling, monitoring, and security features. It follows industry best practices and provides a solid foundation for building AI agent systems.




