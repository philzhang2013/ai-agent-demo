"""
工具系统测试
"""
import pytest

from app.agent.tools import calculator_tool, weather_tool, find_tool


class TestCalculatorTool:
    """测试计算器工具"""

    def test_should_have_correct_metadata(self):
        """测试应该有正确的元数据"""
        assert calculator_tool.name == "calculator"
        assert "计算" in calculator_tool.description
        assert calculator_tool.parameters["type"] == "object"
        assert "expression" in calculator_tool.parameters["properties"]
        assert "expression" in calculator_tool.parameters["required"]

    def test_should_execute_addition(self):
        """测试应该执行加法"""
        result = calculator_tool.execute({"expression": "18 + 25"})
        assert "43" in result

    def test_should_execute_subtraction(self):
        """测试应该执行减法"""
        result = calculator_tool.execute({"expression": "50 - 15"})
        assert "35" in result

    def test_should_execute_multiplication(self):
        """测试应该执行乘法"""
        result = calculator_tool.execute({"expression": "6 * 7"})
        assert "42" in result

    def test_should_execute_division(self):
        """测试应该执行除法"""
        result = calculator_tool.execute({"expression": "100 / 4"})
        assert "25" in result

    def test_should_handle_complex_expression(self):
        """测试应该处理复杂表达式"""
        result = calculator_tool.execute({"expression": "(10 + 5) * 2 - 8"})
        assert "22" in result

    def test_should_return_error_on_invalid_expression(self):
        """测试无效表达式应该返回错误"""
        result = calculator_tool.execute({"expression": "invalid"})
        assert "错误" in result.lower()

    def test_should_handle_division_by_zero(self):
        """测试应该处理除以零"""
        result = calculator_tool.execute({"expression": "10 / 0"})
        # 返回 Infinity 或错误
        assert "错误" in result.lower() or "infinity" in result.lower()


class TestWeatherTool:
    """测试天气查询工具"""

    def test_should_have_correct_metadata(self):
        """测试应该有正确的元数据"""
        assert weather_tool.name == "get_weather"
        assert "天气" in weather_tool.description
        assert weather_tool.parameters["type"] == "object"
        assert "city" in weather_tool.parameters["properties"]
        assert "city" in weather_tool.parameters["required"]

    def test_should_query_beijing_weather(self):
        """测试应该查询北京天气"""
        result = weather_tool.execute({"city": "北京"})
        assert "北京" in result
        assert "晴天" in result
        assert "18" in result  # 温度

    def test_should_query_shanghai_weather(self):
        """测试应该查询上海天气"""
        result = weather_tool.execute({"city": "上海"})
        assert "上海" in result
        assert "多云" in result

    def test_should_return_unknown_for_unsupported_city(self):
        """测试不支持的 city 应该返回未知"""
        result = weather_tool.execute({"city": "火星"})
        assert "火星" in result
        assert "未知" in result


class TestFindTool:
    """测试查找工具"""

    def test_should_find_calculator(self):
        """测试应该找到计算器"""
        tool = find_tool("calculator")
        assert tool is not None
        assert tool.name == "calculator"

    def test_should_find_weather_tool(self):
        """测试应该找到天气工具"""
        tool = find_tool("get_weather")
        assert tool is not None
        assert tool.name == "get_weather"

    def test_should_return_none_for_unknown_tool(self):
        """测试未知工具应该返回 None"""
        tool = find_tool("unknown_tool")
        assert tool is None
