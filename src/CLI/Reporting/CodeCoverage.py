import ast
import json

class FunctionVisitor(ast.NodeVisitor):
    def __init__(self):
        self.functions = []
    
    def visit_FunctionDef(self, node):
        if node.body:
            end_line = max(getattr(n, 'end_lineno', n.lineno) for n in node.body)
            self.functions.append((node.name, node.lineno + 1, end_line))
        self.generic_visit(node)

def get_functions_from_source(source_path):
    with open(source_path, "r") as source_file:
        source_code = source_file.read()
    tree = ast.parse(source_code)
    visitor = FunctionVisitor()
    visitor.visit(tree)
    return visitor.functions

def parse_coverage_json(coverage_json_path):
    with open(coverage_json_path) as f:
        coverage_data = json.load(f)
    return coverage_data

def calculate_coverage(functions , executed_lines):
    covered_functions = []
    uncovered_functions = []
    for func_name, start_line, end_line in functions:
        if any(line in range(start_line, end_line + 1) for line in executed_lines):
            covered_functions.append(func_name)
        else:
            uncovered_functions.append(func_name)
    return covered_functions, uncovered_functions

def process_coverage_results(file):
    coverage_data = parse_coverage_json('coverage.json')
    coverage_report = {}

    for filename, file_data in coverage_data['files'].items():
        executed_lines = file_data['executed_lines']
        executed_branches = file_data.get('executed_branches', [])
        source_path = filename
        functions = get_functions_from_source(source_path)
        covered_funcs, uncovered_funcs = calculate_coverage(functions, executed_lines)
        total_functions = len(functions)
        covered_count = len(covered_funcs)

        num_statements = file_data['summary'].get('num_statements', 0)
        num_branches = file_data['summary'].get('num_branches', 0)

        line_coverage = (len(executed_lines) / num_statements * 100) if num_statements > 0 else 100
        branch_coverage = (len(executed_branches) / num_branches * 100) if num_branches > 0 else 100

        coverage_report[filename] = {
            "function_coverage": (covered_count / total_functions) * 100 if total_functions > 0 else 100,
            "line_coverage": line_coverage,
            "branch_coverage": branch_coverage,
            "covered_functions": covered_funcs,
            "uncovered_functions": uncovered_funcs
        }
    return coverage_report




