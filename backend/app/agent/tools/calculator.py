from .base import BaseTool

class CalculatorTool(BaseTool):
    name = "calculator"
    description = (
        "Evaluate a basic math expression. "
        "Example: '0.18 * 450' or '15% of 340' → write it as 0.15 * 340"
    )

    def run(self, expression: str = "") -> str:
        try:
            # Very restrictive for safety in Week 1
            allowed_chars = set("0123456789+-*/().% ")
            if not expression or not all(c in allowed_chars for c in expression):
                return "Error: invalid expression"

            # Support simple percentage writing
            expression = expression.replace("%", "/100")
            result = eval(expression, {"__builtins__": {}})
            return str(result)
        except Exception as e:
            return f"Error: {str(e)}"