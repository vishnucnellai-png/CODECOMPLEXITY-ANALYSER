import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from pymongo import MongoClient
from .engine import analyze_python_code

# Setup MongoDB
try:
    client = MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=2000)
    # Check if server is actually available
    client.server_info()
    db = client['code_complexity_analyzer']
    history_collection = db['analysis_history']
except Exception as e:
    client = None

@csrf_exempt
def analyze_code(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            code = data.get('code', '')
            save = data.get('save', False)
            file_name = data.get('fileName', 'Untitled Snippet')
            from datetime import datetime
            
            # Run engine
            result = analyze_python_code(code)
            
            # Save to MongoDB
            if save and client:
                try:
                    history_collection.insert_one({
                        "fileName": file_name,
                        "createdAt": datetime.now().isoformat(),
                        "code": code,
                        "loc": result["loc"],
                        "timeComplexity": result["timeComplexity"],
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
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            code1 = data.get('code1', '')
            code2 = data.get('code2', '')
            
            res1 = analyze_python_code(code1)
            res2 = analyze_python_code(code2)
            
            return JsonResponse({
                "code1": res1,
                "code2": res2
            })
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)
    return JsonResponse({"error": "Method not allowed"}, status=405)

@csrf_exempt
def explain_code(request):
    import urllib.request as urllib_req
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            code = data.get('code', '')
            time_complexity = data.get('timeComplexity', 'Unknown')

            api_key = "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"
            url = "https://integrate.api.nvidia.com/v1/chat/completions"

            system_prompt = (
                "You are an expert Python code analyst. Given a Python code snippet and its detected time complexity, "
                "respond with a JSON object with exactly these 3 keys:\n"
                "1. 'suggestions': a list of 2-4 short, specific AI suggestions (e.g. 'Reduce nested loop → use a set for O(1) lookups')\n"
                "2. 'explanation': a 2-4 sentence plain English explanation of what the code does and why it has the detected complexity (e.g. 'This outer loop runs n times...')\n"
                "3. 'refactors': a list of 2-3 specific auto-refactor tips (e.g. 'Extract inner loop into a helper function', 'Replace list with set for faster membership checks')\n"
                "ONLY return valid JSON. No markdown, no explanation text outside the JSON."
            )

            user_prompt = f"Code:\n{code}\n\nDetected complexity: {time_complexity}"

            payload = {
                "model": "meta/llama-3.1-70b-instruct",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "temperature": 0.2
            }
            req_data = json.dumps(payload).encode('utf-8')
            req = urllib_req.Request(url, data=req_data, headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            })

            try:
                with urllib_req.urlopen(req, timeout=20) as response:
                    res_data = json.loads(response.read().decode('utf-8'))
                    raw = res_data['choices'][0]['message']['content']
                    # Parse the JSON from Groq response
                    import re
                    json_match = re.search(r'\{.*\}', raw, re.DOTALL)
                    if json_match:
                        parsed = json.loads(json_match.group())
                        return JsonResponse(parsed)
                    else:
                        return JsonResponse({"error": "Could not parse AI response"}, status=500)
            except urllib_req.HTTPError as http_err:
                body = http_err.read().decode('utf-8', errors='ignore')
                return JsonResponse({"error": f"NVIDIA HTTP {http_err.code}: {body[:300]}"}, status=500)
            except Exception as api_err:
                return JsonResponse({"error": "AI Explain Error: " + str(api_err)}, status=500)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)
    return JsonResponse({"error": "Method not allowed"}, status=405)

@csrf_exempt
def fix_code(request):
    import urllib.request as urllib_req
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            code = data.get('code', '')
            issue = data.get('issue', 'unknown issue')  # e.g. "Syntax Error" or "O(n²) nested loops"

            api_key = "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"
            url = "https://integrate.api.nvidia.com/v1/chat/completions"
            
            system_prompt = (
                "You are an expert Python code fixer and optimizer. "
                "The user has a Python program with an issue. "
                "Fix ONLY the problem in their code while keeping their exact logic, variable names, and structure intact. "
                "If it's a syntax error, fix the syntax. "
                "If it's a complexity issue like O(n²), optimize just that section to a better algorithm. "
                "Return ONLY the complete fixed Python code. No explanations, no markdown, no code fences."
            )
            
            user_prompt = f"Issue detected: {issue}\n\nCode to fix:\n{code}"
            
            payload = {
                "model": "meta/llama-3.1-70b-instruct",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "temperature": 0.1
            }
            req_data = json.dumps(payload).encode('utf-8')
            req = urllib_req.Request(url, data=req_data, headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            })
            
            try:
                with urllib_req.urlopen(req, timeout=20) as response:
                    res_data = json.loads(response.read().decode('utf-8'))
                    fixed = res_data['choices'][0]['message']['content']
                    fixed = fixed.replace('```python', '').replace('```', '').strip()
                    return JsonResponse({"fixedCode": fixed})
            except urllib_req.HTTPError as http_err:
                body = http_err.read().decode('utf-8', errors='ignore')
                return JsonResponse({"error": f"NVIDIA HTTP {http_err.code}: {body[:300]}"}, status=500)
            except Exception as api_err:
                return JsonResponse({"error": "AI Fix Error: " + str(api_err)}, status=500)
                
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)
    return JsonResponse({"error": "Method not allowed"}, status=405)

@csrf_exempt
def learn_code(request):
    import urllib.request as urllib_req
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            code = data.get('code', '')
            time_complexity = data.get('timeComplexity', 'Unknown')

            api_key = "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"
            url = "https://integrate.api.nvidia.com/v1/chat/completions"

            system_prompt = (
                "You are an expert Computer Science Professor and Code Instructor. "
                "Provided with a Python code snippet and its detected time complexity, respond with a JSON object with exactly these 2 keys:\n"
                "1. 'steps': A list of objects, each with 'line' (string, the code line) and 'explanation' (string, what happens here, variable state simulated).\n"
                "2. 'deepDive': A detailed (2-3 paragraphs) technical 'Masterclass' explanation of how the time complexity was derived (e.g., recursive tree, nested summations).\n"
                "Structure the 'steps' chronologically by logical flow. "
                "ONLY return valid JSON. No markdown, no explanation outside the JSON."
            )

            user_prompt = f"Code:\n{code}\n\nDetected complexity: {time_complexity}"

            payload = {
                "model": "meta/llama-3.1-70b-instruct",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "temperature": 0.2
            }
            req_data = json.dumps(payload).encode('utf-8')
            req = urllib_req.Request(url, data=req_data, headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            })

            try:
                with urllib_req.urlopen(req, timeout=30) as response:
                    res_data = json.loads(response.read().decode('utf-8'))
                    raw = res_data['choices'][0]['message']['content']
                    import re
                    json_match = re.search(r'\{.*\}', raw, re.DOTALL)
                    if json_match:
                        parsed = json.loads(json_match.group())
                        return JsonResponse(parsed)
                    else:
                        return JsonResponse({"error": "Could not parse AI response"}, status=500)
            except urllib_req.HTTPError as http_err:
                body = http_err.read().decode('utf-8', errors='ignore')
                return JsonResponse({"error": f"NVIDIA HTTP {http_err.code}: {body[:300]}"}, status=500)
            except Exception as api_err:
                return JsonResponse({"error": "AI Learning Error: " + str(api_err)}, status=500)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)
    return JsonResponse({"error": "Method not allowed"}, status=405)

@csrf_exempt
def login_code(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            code = data.get('code', '')
            
            # The official challenge: Write a function unlock(a, b) that returns a + b
            # We'll test it with a few cases
            test_cases = [(10, 20, 30), (5, -5, 0), (100, 200, 300)]
            
            namespace = {}
            try:
                # Execute the user's code in a isolated namespace
                exec(code, namespace)
                
                if 'unlock' not in namespace:
                    return JsonResponse({"success": False, "error": "Function 'unlock' not found in your code."})
                
                unlock_func = namespace['unlock']
                
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
    if request.method == 'GET':
        if client:
            try:
                # Fetch recent 15 records
                records = list(history_collection.find({}, {'_id': 0}).sort('_id', -1).limit(15))
                return JsonResponse({"history": records})
            except Exception as e:
                return JsonResponse({"error": str(e)}, status=500)
        else:
            return JsonResponse({"error": "MongoDB not connected. Ensure mongod is running natively on port 27017."}, status=500)
    return JsonResponse({"error": "Method not allowed"}, status=405)
