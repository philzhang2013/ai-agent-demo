"""
工具定义模块
定义 Agent 可以使用的工具
"""
from typing import Dict, Any, List, Callable, Optional


class Tool:
    """工具基类"""

    def __init__(
        self,
        name: str,
        description: str,
        parameters: Dict[str, Any],
        execute_func: Callable[[Dict[str, Any]], str]
    ):
        self.name = name
        self.description = description
        self.parameters = parameters
        self._execute_func = execute_func

    def execute(self, args: Dict[str, Any]) -> str:
        """执行工具"""
        return self._execute_func(args)


# ========== 工具定义 ==========

@staticmethod
def _execute_calculator(args: Dict[str, Any]) -> str:
    """执行计算器工具"""
    try:
        expression = args["expression"].strip()
        result = eval(expression)
        return f"计算结果: {expression} = {result}"
    except Exception as e:
        return f"计算错误: {e}"


@staticmethod
def _execute_weather(args: Dict[str, Any]) -> str:
    """执行天气查询工具（模拟数据）"""
    weather_data = {
        "北京": {"condition": "晴天", "temperature": 18, "aqi": 75},
        "上海": {"condition": "多云", "temperature": 22, "aqi": 60},
        "深圳": {"condition": "阴天", "temperature": 25, "aqi": 45},
        "广州": {"condition": "小雨", "temperature": 24, "aqi": 55},
    }

    city = args["city"]
    data = weather_data.get(city, {"condition": "未知", "temperature": "--", "aqi": "--"})
    return f"{city}今天{data['condition']}，温度 {data['temperature']}°C，空气质量 {data['aqi']}"


# 工具实例
calculator_tool = Tool(
    name="calculator",
    description="执行数学计算，支持加减乘除和括号",
    parameters={
        "type": "object",
        "properties": {
            "expression": {
                "type": "string",
                "description": "要计算的数学表达式，例如 '18 + 25' 或 '(10 * 5) / 2'"
            }
        },
        "required": ["expression"]
    },
    execute_func=_execute_calculator
)

weather_tool = Tool(
    name="get_weather",
    description="查询指定城市的天气信息",
    parameters={
        "type": "object",
        "properties": {
            "city": {
                "type": "string",
                "description": "城市名称，例如 '北京'、'上海'"
            }
        },
        "required": ["city"]
    },
    execute_func=_execute_weather
)

# 工具列表
tools: List[Tool] = [calculator_tool, weather_tool]


def find_tool(name: str) -> Tool | None:
    """根据名称查找工具"""
    for tool in tools:
        if tool.name == name:
            return tool
    return None
