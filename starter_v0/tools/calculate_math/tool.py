# File: tools/calculate/tool.py

def calculate_math(expression: str, context: str = "") -> dict:
    """
    Thực hiện phép tính toán học cơ bản từ biểu thức chuỗi.
    Trả về kết quả (result) hoặc báo lỗi (error).
    """
    if not expression or str(expression).strip() == "":
        return {"error": "Biểu thức tính toán (expression) không được để trống."}
    
    try:
        # Tính toán an toàn (bỏ qua các hàm built-in nguy hiểm của Python)
        res = eval(expression, {"__builtins__": None}, {})
        return {"result": res, "context": context}
    except ZeroDivisionError:
        return {"error": "Lỗi toán học: Không thể chia cho 0."}
    except Exception as e:
        return {"error": f"Biểu thức không hợp lệ. Vui lòng kiểm tra lại: {str(e)}"}