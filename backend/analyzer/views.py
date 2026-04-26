import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .engine import analyze_python_code
import urllib.request as urllib_req
import re

NVIDIA_API_KEY = "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"
NVIDIA_URL = "https://integrate.api.nvidia.com/v1/chat/completions"
NVIDIA_MODEL = "meta/llama-3.1-8b-instruct"

def _call_nvidia(system_prompt, user_prompt, timeout=8):
    """Call NVIDIA API. Returns (text, error_string)."""
    payload = json.dumps({
        "model": NVIDIA_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.2,
        "top_p": 0.7,
        "max_tokens": 1024
    }).encode("utf-8")
    req = urllib_req.Request(NVIDIA_URL, data=payload, headers={
        "Authorization": f"Bearer {NVIDIA_API_KEY}",
        "Content-Type": "application/json"
    })
    try:
        with urllib_req.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            content = data["choices"][0]["message"]["content"]
            return content, None
    except Exception as e:
        print(f"NVIDIA API Error: {str(e)}")
        return None, str(e)

def _parse_ai_json(raw_text):
    """Robustly parse JSON from AI response, handling markdown blocks."""
    if not raw_text:
        return None
    
    # Standard non-recursive brace finding
    try:
        start = raw_text.find('{')
        end = raw_text.rfind('}')
        if start != -1 and end != -1:
            json_str = raw_text[start:end+1]
            return json.loads(json_str)
    except Exception:
        pass
    return None

# MongoDB — optional
try:
    from pymongo import MongoClient
    _client = MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=2000)
    _client.server_info()
    db = _client["code_complexity_analyzer"]
    history_collection = db["analysis_history"]
    MONGO_OK = True
except Exception:
    MONGO_OK = False


@csrf_exempt
def analyze_code(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            code = data.get("code", "")
            save = data.get("save", False)
            file_name = data.get("fileName", "Untitled Snippet")
            result = analyze_python_code(code)
            if save and MONGO_OK:
                from datetime import datetime
                try:
                    history_collection.insert_one({
                        "fileName": file_name,
                        "createdAt": datetime.now().isoformat(),
                        "code": code,
                        "loc": result["loc"],
                        "timeComplexity": result["timeComplexity"],
                        "spaceComplexity": result.get("spaceComplexity", "O(1)"),
                        "cyclomaticComplexity": result["cyclomaticComplexity"]
                    })
                except Exception:
                    pass
            return JsonResponse(result)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)
    return JsonResponse({"error": "Method not allowed"}, status=405)


@csrf_exempt
def compare_code(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            res1 = analyze_python_code(data.get("code1", ""))
            res2 = analyze_python_code(data.get("code2", ""))
            return JsonResponse({"code1": res1, "code2": res2})
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)
    return JsonResponse({"error": "Method not allowed"}, status=405)


@csrf_exempt
def explain_code(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            code = data.get("code", "")
            time_complexity = data.get("timeComplexity", "Unknown")
            space_complexity = data.get("spaceComplexity", "Unknown")
            system_prompt = (
                "You are an expert Python code analyst. Given a Python code snippet and its detected complexities, "
                "respond with a JSON object with exactly these 3 keys:\n"
                "1. 'suggestions': a list of 2-4 short, specific AI suggestions\n"
                "2. 'explanation': a 2-4 sentence plain English explanation covering both TIME and SPACE complexity\n"
                "3. 'refactors': a list of 2-3 specific auto-refactor tips\n"
                "ONLY return valid JSON. Do not include markdown code fences or any other text."
            )
            raw, err = _call_nvidia(system_prompt, f"Code:\n{code}\n\nTime complexity: {time_complexity}\nSpace complexity: {space_complexity}")
            parsed = _parse_ai_json(raw)
            if parsed:
                return JsonResponse(parsed)
            
            # Offline fallback
            result = analyze_python_code(code)
            suggestions = ["Consider reducing nested loops." if result.get('maxNestingDepth', 0) > 1 else "Code looks clean!"]
            return JsonResponse({
                "suggestions": suggestions,
                "explanation": f"Time: {time_complexity}, Space: {result.get('spaceComplexity', 'O(1)')}. (Offline Fallback)",
                "refactors": ["Extract repeated logic into helper functions.", "Use list comprehensions where possible."]
            })
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)
    return JsonResponse({"error": "Method not allowed"}, status=405)


@csrf_exempt
def fix_code(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            code = data.get("code", "")
            issue = data.get("issue", "unknown issue")
            system_prompt = (
                "You are an expert Python code fixer. Fix ONLY the problem in the user's code while keeping their logic intact. "
                "Return ONLY the complete fixed Python code. No explanations, no markdown, no code fences."
            )
            raw, err = _call_nvidia(system_prompt, f"Issue: {issue}\n\nCode:\n{code}")
            if raw:
                fixed = re.sub(r'```python|```', '', raw).strip()
                return JsonResponse({"fixedCode": fixed})
            # Offline fallback
            result = analyze_python_code(code)
            return JsonResponse({"fixedCode": result.get("suggestedCode") or code})
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)
    return JsonResponse({"error": "Method not allowed"}, status=405)


@csrf_exempt
def learn_code(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            code = data.get("code", "")
            time_complexity = data.get("timeComplexity", "Unknown")
            space_complexity = data.get("spaceComplexity", "Unknown")
            system_prompt = (
                "You are an expert CS Professor. Given Python code and its complexities, respond with a JSON object with:\n"
                "1. 'steps': list of {line, explanation} objects\n"
                "2. 'deepDive': 2-3 paragraph technical masterclass explanation covering BOTH time and space complexity\n"
                "ONLY return valid JSON. No markdown outside the JSON."
            )
            raw, err = _call_nvidia(system_prompt, f"Code:\n{code}\n\nTime: {time_complexity}\nSpace: {space_complexity}", timeout=8)
            parsed = _parse_ai_json(raw)
            if parsed:
                return JsonResponse(parsed)
            # Offline fallback
            result = analyze_python_code(code)
            lines = [l for l in code.split("\n") if l.strip()]
            steps = [{"line": l.strip(), "explanation": "Python executes this statement sequentially."} for l in lines[:20]]
            return JsonResponse({"steps": steps, "deepDive": f"<strong>Complexity: Time {time_complexity}, Space {result.get('spaceComplexity', 'O(1)')}</strong><br>AI explanation unavailable at this moment."})
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)
    return JsonResponse({"error": "Method not allowed"}, status=405)


@csrf_exempt
def login_code(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            code = data.get("code", "")
            test_cases = [(10, 20, 30), (5, -5, 0), (100, 200, 300)]
            namespace = {}
            try:
                exec(code, namespace)
                if "unlock" not in namespace:
                    return JsonResponse({"success": False, "error": "Function 'unlock' not found in your code."})
                unlock_func = namespace["unlock"]
                for a, b, expected in test_cases:
                    if unlock_func(a, b) != expected:
                        return JsonResponse({"success": False, "error": f"Test failed: unlock({a}, {b}) did not return {expected}"})
                return JsonResponse({"success": True, "message": "Code Login Successful! Dashboard Unlocked."})
            except Exception as e:
                return JsonResponse({"success": False, "error": f"Execution Error: {str(e)}"})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": "Method not allowed"}, status=405)


@csrf_exempt
def get_history(request):
    if request.method == "GET":
        if MONGO_OK:
            try:
                records = list(history_collection.find({}, {"_id": 0}).sort("_id", -1).limit(15))
                return JsonResponse({"history": records})
            except Exception as e:
                return JsonResponse({"error": str(e)}, status=500)
        else:
            return JsonResponse({"error": "MongoDB not connected. Start mongod to enable history."}, status=500)
    return JsonResponse({"error": "Method not allowed"}, status=405)
