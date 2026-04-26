import ast

class AdvancedComplexityVisitor(ast.NodeVisitor):
    def __init__(self):
        self.cyclomatic_complexity = 1
        self.max_loop_depth = 0
        self.current_loop_depth = 0
        self.has_recursion = False
        self.has_sort = False
        self.has_binary_search = False
        self.has_large_allocation = False
        self.max_nesting_allocation = 0
        self.functions = []
        self.current_function = None
        
        # Variable tracking
        self.assignments = set()
        self.usages = set()
        self.undefined_warnings = []
    
    def visit_FunctionDef(self, node):
        self.functions.append(node.name)
        prev_func = self.current_function
        self.current_function = node.name
        
        # Add args to assignments
        for arg in node.args.args:
            self.assignments.add(arg.arg)
            
        self.generic_visit(node)
        self.current_function = prev_func
        
    def visit_Call(self, node):
        if isinstance(node.func, ast.Name):
            if node.func.id == self.current_function or node.func.id in self.functions:
                self.has_recursion = True
            if node.func.id == 'sorted':
                self.has_sort = True
            if node.func.id in ('list', 'dict', 'set', 'setattr', 'append', 'extend', 'update'):
                self.has_large_allocation = True
                self.max_nesting_allocation = max(self.max_nesting_allocation, self.current_loop_depth)
        elif isinstance(node.func, ast.Attribute):
            if node.func.attr == 'sort':
                self.has_sort = True
            if node.func.attr in ('append', 'extend', 'update', 'add', 'insert'):
                self.has_large_allocation = True
                self.max_nesting_allocation = max(self.max_nesting_allocation, self.current_loop_depth)
        self.generic_visit(node)
        
    def visit_List(self, node):
        self.has_large_allocation = True
        self.max_nesting_allocation = max(self.max_nesting_allocation, self.current_loop_depth)
        self.generic_visit(node)

    def visit_Dict(self, node):
        self.has_large_allocation = True
        self.max_nesting_allocation = max(self.max_nesting_allocation, self.current_loop_depth)
        self.generic_visit(node)

    def visit_Set(self, node):
        self.has_large_allocation = True
        self.max_nesting_allocation = max(self.max_nesting_allocation, self.current_loop_depth)
        self.generic_visit(node)

    def visit_ListComp(self, node):
        self.has_large_allocation = True
        self.max_nesting_allocation = max(self.max_nesting_allocation, self.current_loop_depth + 1)
        self.generic_visit(node)

    def visit_DictComp(self, node):
        self.has_large_allocation = True
        self.max_nesting_allocation = max(self.max_nesting_allocation, self.current_loop_depth + 1)
        self.generic_visit(node)

    def visit_SetComp(self, node):
        self.has_large_allocation = True
        self.max_nesting_allocation = max(self.max_nesting_allocation, self.current_loop_depth + 1)
        self.generic_visit(node)
        
    def visit_BinOp(self, node):
        # check for division by 2 in a loop (O(log n) heuristic)
        if self.current_loop_depth > 0:
            if isinstance(node.op, (ast.FloorDiv, ast.Div)):
                if isinstance(node.right, ast.Constant) and node.right.value == 2:
                    self.has_binary_search = True
        self.generic_visit(node)
        
    def visit_Assign(self, node):
        for target in node.targets:
            if isinstance(target, ast.Name):
                self.assignments.add(target.id)
        self.generic_visit(node)
        
    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Load):
            self.usages.add(node.id)
            # Exclude builtins conceptually
            builtins = {'print', 'len', 'range', 'int', 'str', 'float', 'list', 'dict', 'set', 'True', 'False', 'None', 'self'}
            if node.id not in self.assignments and node.id not in builtins and node.id not in self.functions:
                # Potential undefined variable
                self.undefined_warnings.append(f"Line {node.lineno}: Variable '{node.id}' might be undefined.")
        self.generic_visit(node)

    def visit_If(self, node):
        self.cyclomatic_complexity += 1
        self.generic_visit(node)
        
    def visit_For(self, node):
        self.cyclomatic_complexity += 1
        self.current_loop_depth += 1
        if self.current_loop_depth > self.max_loop_depth:
            self.max_loop_depth = self.current_loop_depth
        self.generic_visit(node)
        self.current_loop_depth -= 1
        
    def visit_While(self, node):
        self.cyclomatic_complexity += 1
        self.current_loop_depth += 1
        if self.current_loop_depth > self.max_loop_depth:
            self.max_loop_depth = self.current_loop_depth
        self.generic_visit(node)
        self.current_loop_depth -= 1
        
    def visit_AsyncFor(self, node):
        self.cyclomatic_complexity += 1
        self.current_loop_depth += 1
        if self.current_loop_depth > self.max_loop_depth:
            self.max_loop_depth = self.current_loop_depth
        self.generic_visit(node)
        self.current_loop_depth -= 1

    def visit_BoolOp(self, node):
        self.cyclomatic_complexity += len(node.values) - 1
        self.generic_visit(node)
        
    def visit_Match(self, node):
        self.cyclomatic_complexity += len(node.cases)
        self.generic_visit(node)
        
    def visit_IfExp(self, node):
        self.cyclomatic_complexity += 1
        self.generic_visit(node)


def analyze_python_code(code: str):
    loc = len([line for line in code.split('\n') if line.strip()])
    alerts = []
    
    try:
        tree = ast.parse(code)
        visitor = AdvancedComplexityVisitor()
        visitor.visit(tree)
        
        # Add linter alerts
        for warning in visitor.undefined_warnings:
            alerts.append({"type": "warning", "title": "Linter Warning", "text": warning})
            
        unused = visitor.assignments - visitor.usages
        if unused:
            alerts.append({"type": "info", "title": "Unused Variables", "text": "Variables assigned but never used: " + ", ".join(unused)})
        
        # Determine time complexity rigorously
        time_complexity = 'O(1)'
        if visitor.has_recursion:
            time_complexity = 'O(2^n) or O(log n)'
            alerts.append({
                "type": "warning", "title": "Recursion Detected",
                "text": "Recursive calls detected. Time complexity can be exponential."
            })
        elif visitor.max_loop_depth == 0:
            if visitor.has_sort:
                time_complexity = 'O(n log n)'
            else:
                time_complexity = 'O(1)'
        elif visitor.max_loop_depth == 1:
            if visitor.has_binary_search:
                time_complexity = 'O(log n)'
            elif visitor.has_sort:
                time_complexity = 'O(n log n)'
            else:
                time_complexity = 'O(n)'
        elif visitor.max_loop_depth == 2:
            time_complexity = 'O(n²)'
        elif visitor.max_loop_depth == 3:
            time_complexity = 'O(n³)'
        else:
            time_complexity = f'O(n^{visitor.max_loop_depth})'

        # Determine space complexity
        space_complexity = 'O(1)'
        if visitor.has_recursion:
            space_complexity = 'O(depth)'
            alerts.append({"type": "info", "title": "Stack Space", "text": "Recursion uses O(depth) stack space."})
        elif visitor.has_large_allocation:
            if visitor.max_nesting_allocation == 0:
                space_complexity = 'O(n)'
            elif visitor.max_nesting_allocation == 1:
                space_complexity = 'O(n²)'
            else:
                space_complexity = f'O(n^{visitor.max_nesting_allocation + 1})'
            
        if space_complexity != 'O(1)':
            alerts.append({"type": "info", "title": "Memory Usage", "text": f"Detected dynamic memory allocation. Space complexity is around {space_complexity}."})
            
        if visitor.has_sort:
            alerts.append({"type": "info", "title": "Sorting Operation", "text": "A sort operation was detected, adding O(n log n) complexity."})
        if visitor.has_binary_search:
            alerts.append({"type": "info", "title": "Logarithmic Operation", "text": "A division operation inside a loop was detected. This might be an O(log n) step."})

        if visitor.max_loop_depth > 1:
            alerts.append({
                "type": "warning", "title": "Nested Loops",
                "text": f"Detected {visitor.max_loop_depth}-level deep loops."
            })
            
        if visitor.cyclomatic_complexity > 10:
            alerts.append({"type": "warning", "title": "High Complexity", "text": "Cyclomatic complexity is above 10. Consider refactoring."})
            
        if not alerts:
            alerts.append({"type": "info", "title": "Clean Code", "text": "No major performance or logic issues detected."})

        suggested_code = None
        if visitor.has_recursion and "fibonacci" in code:
            suggested_code = "def fibonacci(n):\n    if n <= 1:\n        return n\n    a, b = 0, 1\n    for _ in range(2, n + 1):\n        a, b = b, a + b\n    return b"
        elif visitor.max_loop_depth > 1:
            suggested_code = "# Optimized using Hash Set for O(1) lookups\ndef process_optimized(items):\n    seen = set()\n    result = []\n    for item in items:\n        if item not in seen:\n            result.append(item)\n            seen.add(item)\n    return result"

        return {
            "loc": loc,
            "timeComplexity": time_complexity,
            "spaceComplexity": space_complexity,
            "cyclomaticComplexity": visitor.cyclomatic_complexity,
            "maxNestingDepth": visitor.max_loop_depth,
            "alerts": alerts,
            "suggestedCode": suggested_code
        }
            
    except SyntaxError as e:
        default_fix = "# Syntax Error Fixed Format\ndef function_name():\n    # ensure proper indentation and use colons (:)\n    pass"
        
        # Build precise error message
        error_text = f"Invalid Syntax on Line {e.lineno}, Offset {e.offset}: {e.msg}"
        if e.text:
            error_text += f"\nSnippet: {str(e.text).strip()}"
            
        return {
            "loc": loc,
            "timeComplexity": "-",
            "cyclomaticComplexity": "-",
            "maxNestingDepth": "-",
            "alerts": [{"type": "danger", "title": "Syntax Error", "text": error_text}],
            "suggestedCode": default_fix if "def " in code else None
        }
    except Exception as e:
        return {
            "loc": loc,
            "timeComplexity": "-",
            "cyclomaticComplexity": "-",
            "maxNestingDepth": "-",
            "alerts": [{"type": "danger", "title": "Analysis Error", "text": str(e)}],
            "suggestedCode": None
        }
