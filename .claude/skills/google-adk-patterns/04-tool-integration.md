# Module 04: Tool Integration & Function Calling

Complete guide to adding function calling capabilities to ADK agents.

---

## Simple Python Function Tools

**Google ADK automatically converts Python functions to tools using:**
- Type hints for parameter types
- Docstrings for descriptions
- Return type hints

```python
def get_current_weather(city: str, unit: str = "celsius") -> dict:
    """Get the current weather for a specified city.

    Args:
        city: The name of the city to get weather for.
        unit: Temperature unit (celsius or fahrenheit). Defaults to celsius.

    Returns:
        A dictionary containing weather information including temperature and conditions.
    """
    # Simulated weather data
    return {
        "city": city,
        "temperature": 22,
        "unit": unit,
        "conditions": "Partly cloudy",
    }

def calculate_sum(numbers: list[float]) -> float:
    """Calculate the sum of a list of numbers.

    Args:
        numbers: List of numbers to sum.

    Returns:
        The total sum of all numbers.
    """
    return sum(numbers)

# Create agent with tools
agent = LlmAgent(
    model="gemini-2.0-flash",
    name="weather_agent",
    tools=[get_current_weather, calculate_sum],  # Just pass functions
    instruction="You can check weather and do calculations.",
)
```

---

## Tool Best Practices

### 1. Type Hints Required

All parameters must have type hints:

```python
# ✅ Good
def get_user(user_id: int) -> dict:
    """Fetch user profile."""
    return {"id": user_id, "name": "Alice"}

# ❌ Bad - no type hints
def get_user(user_id):
    return {"id": user_id, "name": "Alice"}
```

### 2. Clear Docstrings

ADK parses docstrings to generate tool schemas:

```python
# ✅ Good
def search_products(query: str, max_results: int = 10) -> list[dict]:
    """Search for products in the catalog.

    Args:
        query: Search query string.
        max_results: Maximum number of results to return.

    Returns:
        List of product dictionaries with name, price, and description.
    """
    pass

# ❌ Bad - no docstring
def search_products(query: str, max_results: int = 10) -> list[dict]:
    return []
```

### 3. Specific Types

Use specific types (list[str], dict, int) not generic (any, object):

```python
# ✅ Good - specific types
def process_items(items: list[str], config: dict) -> dict:
    """Process a list of items with configuration."""
    return {"processed": len(items)}

# ❌ Bad - generic types
def process_items(items: list, config: dict) -> object:
    return {"processed": len(items)}
```

### 4. Return Structured Data

Always return structured data (dict, list, str, int), not None:

```python
# ✅ Good - returns dict
def create_order(items: list[str]) -> dict:
    """Create a new order."""
    return {"order_id": "12345", "status": "created"}

# ❌ Bad - returns None
def create_order(items: list[str]) -> None:
    """Create a new order."""
    # Side effect only, no return value
    pass
```

---

## Using @adk_tool Decorator

The `@adk_tool` decorator standardizes responses and provides additional metadata:

```python
from google.adk.tools import adk_tool

@adk_tool
def fetch_user_profile(user_id: int) -> dict:
    """Fetch user profile information from database.

    Args:
        user_id: The unique user identifier.

    Returns:
        User profile dictionary with id, name, email, and preferences.
    """
    # Database lookup (simulated)
    return {
        "id": user_id,
        "name": "Alice Smith",
        "email": "alice@example.com",
        "preferences": {"theme": "dark", "notifications": True}
    }
```

---

## Complete Example: Data Analysis Agent

```python
"""
Complete example: Data Analysis Agent with tools using Google ADK
"""
import asyncio
from typing import List, Dict
from google.adk.agents import LlmAgent
from google.adk.runners import InMemoryRunner
from google.genai import types
import statistics

# Define tools as Python functions

def query_sales_data(product: str, days: int = 30) -> List[Dict]:
    """Query sales data for a specific product.

    Args:
        product: Product name to query.
        days: Number of days of historical data. Defaults to 30.

    Returns:
        List of daily sales records with date, units, and revenue.
    """
    # Simulated database query
    return [
        {"date": "2025-01-20", "units": 42, "revenue": 4200.00},
        {"date": "2025-01-21", "units": 38, "revenue": 3800.00},
        {"date": "2025-01-22", "units": 55, "revenue": 5500.00},
    ]

def calculate_statistics(values: List[float]) -> Dict:
    """Calculate statistical metrics for a dataset.

    Args:
        values: List of numerical values.

    Returns:
        Dictionary with mean, median, min, max, and standard deviation.
    """
    if not values:
        return {"error": "No data provided"}

    return {
        "mean": statistics.mean(values),
        "median": statistics.median(values),
        "min": min(values),
        "max": max(values),
        "std_dev": statistics.stdev(values) if len(values) > 1 else 0,
    }

def create_recommendation(analysis: str) -> str:
    """Generate actionable recommendations based on analysis.

    Args:
        analysis: Text description of the analysis findings.

    Returns:
        Formatted recommendations string.
    """
    # In production, this might use another LLM call or business logic
    return f"Based on the analysis: {analysis}\n\nRecommendations:\n- Monitor trends closely\n- Adjust inventory accordingly"

# Create agent with tools
data_agent = LlmAgent(
    model="gemini-2.0-flash",
    name="data_analyst",
    description="Analyzes sales data and provides insights",
    tools=[query_sales_data, calculate_statistics, create_recommendation],
    instruction="""You are a data analysis assistant.

    Your capabilities:
    - Query sales data using query_sales_data()
    - Calculate statistics using calculate_statistics()
    - Generate recommendations using create_recommendation()

    Always:
    1. Query relevant data first
    2. Calculate meaningful statistics
    3. Provide clear, actionable insights
    4. Support recommendations with data
    """,
)

# Run the agent
async def main():
    runner = InMemoryRunner(agent=data_agent, app_name="analytics_app")

    # Create session
    session_service = runner.session_service
    await session_service.create_session(
        app_name="analytics_app",
        user_id="analyst_001",
        session_id="session_001",
    )

    # Analyze product
    async for event in runner.run_async(
        user_id="analyst_001",
        session_id="session_001",
        new_message=types.Content(
            role="user",
            parts=[types.Part(text="Analyze sales performance for ProductX")]
        ),
    ):
        if event.is_final_response() and event.content:
            print("\n=== Analysis Result ===")
            print(event.content.parts[0].text)

asyncio.run(main())
```

---

## Tool Error Handling

### Graceful Error Handling in Tools

```python
def fetch_user(user_id: int) -> dict:
    """Fetch user information by ID.
    
    Args:
        user_id: The unique user identifier.
        
    Returns:
        User information dictionary or error message.
    """
    try:
        # Database lookup
        user = database.get_user(user_id)
        if not user:
            return {"error": f"User {user_id} not found"}
        
        return {
            "id": user.id,
            "name": user.name,
            "email": user.email
        }
    except Exception as e:
        return {"error": f"Failed to fetch user: {str(e)}"}
```

### Tool Validation

```python
def create_order(
    user_id: int,
    items: list[str],
    total: float
) -> dict:
    """Create a new customer order.
    
    Args:
        user_id: Customer ID.
        items: List of product IDs.
        total: Order total amount.
        
    Returns:
        Order confirmation with order_id and status.
    """
    # Validation
    if not items:
        return {"error": "Cannot create order with no items"}
    
    if total <= 0:
        return {"error": "Order total must be positive"}
    
    if user_id <= 0:
        return {"error": "Invalid user ID"}
    
    # Create order
    order_id = generate_order_id()
    save_order(order_id, user_id, items, total)
    
    return {
        "order_id": order_id,
        "status": "created",
        "total": total,
        "items_count": len(items)
    }
```

---

## Troubleshooting

### Issue: Agent not calling tools

**Possible Causes:**
1. Missing type hints on parameters
2. Unclear or missing docstrings
3. Agent instruction doesn't mention tool availability
4. Tool descriptions too similar (agent confused)

**Solution**:
```python
# ✅ Good - clear type hints and docstring
def search_database(query: str, limit: int = 10) -> list[dict]:
    """Search the product database for matching items.
    
    Args:
        query: Search query string to match against product names.
        limit: Maximum number of results to return (default 10).
        
    Returns:
        List of product dictionaries with id, name, and price.
    """
    pass

# ✅ Good - instruction mentions tools
agent = LlmAgent(
    model="gemini-2.0-flash",
    name="search_agent",
    tools=[search_database],
    instruction="You can search the database using search_database(). Always search before answering product questions."
)
```

### Issue: Tool returns unexpected results

**Solution**: Add input validation and clear error messages:
```python
def divide_numbers(a: float, b: float) -> dict:
    """Divide two numbers.
    
    Args:
        a: Numerator.
        b: Denominator.
        
    Returns:
        Result dictionary with quotient or error message.
    """
    if b == 0:
        return {"error": "Cannot divide by zero"}
    
    return {"result": a / b}
```

---

## Minimal Tools Per Agent

**Best Practice**: Give each agent only the tools it needs.

```python
# ✅ Good - focused set of related tools
agent = LlmAgent(
    name="weather_agent",
    model="gemini-2.0-flash",
    tools=[get_current_weather, get_forecast, get_air_quality],
    description="Handles weather-related queries"
)

# ❌ Bad - too many unrelated tools
agent = LlmAgent(
    name="assistant",
    model="gemini-2.0-flash",
    tools=[tool1, tool2, tool3, ... tool25],  # Confuses agent
)
```

**Why**: Too many tools:
- Confuses the LLM
- Increases latency (tool schema processing)
- Reduces accuracy (agent picks wrong tool)

**Solution**: Use multi-agent hierarchy:
```python
weather_specialist = LlmAgent(
    name="weather_specialist",
    tools=[get_weather, get_forecast],
    description="Weather specialist"
)

restaurant_specialist = LlmAgent(
    name="restaurant_specialist", 
    tools=[search_restaurants, get_reviews],
    description="Restaurant specialist"
)

coordinator = LlmAgent(
    name="coordinator",
    sub_agents=[weather_specialist, restaurant_specialist],
    description="Routes to specialists"
)
```

---

## Testing Tools

### Unit Test Example

```python
import pytest

def test_calculate_statistics():
    """Test statistics calculation tool."""
    values = [10, 20, 30, 40, 50]
    result = calculate_statistics(values)
    
    assert result["mean"] == 30
    assert result["median"] == 30
    assert result["min"] == 10
    assert result["max"] == 50
    assert result["std_dev"] > 0

def test_calculate_statistics_empty():
    """Test statistics with empty list."""
    result = calculate_statistics([])
    assert "error" in result

def test_calculate_statistics_single():
    """Test statistics with single value."""
    result = calculate_statistics([42])
    assert result["mean"] == 42
    assert result["std_dev"] == 0  # Single value has no deviation
```

### Integration Test with Agent

```python
@pytest.mark.asyncio
async def test_agent_calls_tool():
    """Verify agent calls tool correctly."""
    def mock_weather(city: str) -> dict:
        """Get weather for city."""
        return {"city": city, "temp": 72, "conditions": "Sunny"}
    
    agent = LlmAgent(
        model="gemini-2.0-flash",
        name="test_agent",
        tools=[mock_weather],
        instruction="Use mock_weather to get weather info."
    )
    
    runner = InMemoryRunner(agent=agent, app_name="test")
    response = await runner.run_debug("What's the weather in Paris?")
    
    # Verify response mentions Paris and weather data
    assert "Paris" in str(response) or "72" in str(response)
```

---

## Summary

**Key Takeaways**:
1. **Type hints required** on all parameters and return values
2. **Clear docstrings** with Args and Returns sections
3. **Return structured data** (dict, list), not None
4. **Error handling** inside tools (return error dict)
5. **Minimal tools** per agent (focused toolset)
6. **Tool validation** (check inputs, return clear errors)

**Common Errors**:
- ❌ Missing type hints → agent can't call tool
- ❌ Vague docstrings → agent uses tool incorrectly
- ❌ Too many tools → agent confused, picks wrong tool
- ❌ Returning None → agent has no information

**Correct Workflow**:
1. Write function with type hints
2. Add clear docstring (Args, Returns)
3. Validate inputs
4. Return structured data (dict/list)
5. Test tool independently
6. Add to agent tools list
7. Mention tool in agent instruction

---

**Next Module**: [05-fastapi-integration.md](05-fastapi-integration.md) - Production API integration

**See Also**:
- [01-agent-setup.md](01-agent-setup.md) - Agent creation
- [06-multi-agent-deployment.md](06-multi-agent-deployment.md) - Multi-agent hierarchies
