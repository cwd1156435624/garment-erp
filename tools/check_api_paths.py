#!/usr/bin/env python
"""
API路径检查工具

此工具用于检测Django项目中的重复API路径配置，并提供修复建议。
它通过分析项目的urls.py文件，识别重复的路径模式，并生成报告。

用法:
    python check_api_paths.py [--fix] [--verbose]

选项:
    --fix       自动修复检测到的重复路径问题
    --verbose   显示详细的检查过程
"""

import os
import re
import sys
import argparse
import importlib.util
from collections import defaultdict
from pathlib import Path

# 颜色代码，用于终端输出
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def load_module_from_path(module_path):
    """从文件路径加载Python模块"""
    module_name = os.path.basename(module_path).replace('.py', '')
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def extract_path_patterns(urlpatterns, prefix='', verbose=False):
    """从urlpatterns中提取路径模式"""
    patterns = []
    
    for pattern in urlpatterns:
        if hasattr(pattern, 'pattern'):
            # 获取当前模式的路径
            pattern_str = str(pattern.pattern)
            # 移除正则表达式语法，只保留路径
            clean_pattern = re.sub(r'\(\?P<[^>]+>[^)]+\)', ':param', pattern_str)
            full_path = prefix + clean_pattern
            
            if hasattr(pattern, 'callback') and pattern.callback:
                # 这是一个视图函数
                patterns.append((full_path, pattern.callback.__name__))
                if verbose:
                    print(f"  Found path: {full_path} -> {pattern.callback.__name__}")
            
            if hasattr(pattern, 'url_patterns'):
                # 这是一个include()，递归处理
                if verbose:
                    print(f"  Exploring included patterns at {full_path}")
                included_patterns = extract_path_patterns(pattern.url_patterns, full_path, verbose)
                patterns.extend(included_patterns)
    
    return patterns

def find_duplicate_paths(patterns):
    """查找重复的路径模式"""
    path_dict = defaultdict(list)
    
    for path, view in patterns:
        path_dict[path].append(view)
    
    duplicates = {path: views for path, views in path_dict.items() if len(views) > 1}
    return duplicates

def find_urls_files(project_dir, verbose=False):
    """查找项目中的所有urls.py文件"""
    urls_files = []
    
    for root, dirs, files in os.walk(project_dir):
        if 'urls.py' in files:
            urls_path = os.path.join(root, 'urls.py')
            urls_files.append(urls_path)
            if verbose:
                print(f"Found urls.py: {urls_path}")
    
    return urls_files

def analyze_urls_file(file_path, verbose=False):
    """分析单个urls.py文件，提取路径模式"""
    if verbose:
        print(f"\nAnalyzing {file_path}...")
    
    try:
        module = load_module_from_path(file_path)
        if hasattr(module, 'urlpatterns'):
            return extract_path_patterns(module.urlpatterns, '', verbose)
        else:
            if verbose:
                print(f"  {Colors.WARNING}No urlpatterns found in {file_path}{Colors.ENDC}")
            return []
    except Exception as e:
        print(f"{Colors.FAIL}Error analyzing {file_path}: {str(e)}{Colors.ENDC}")
        return []

def generate_fix_suggestions(duplicates, project_dir):
    """生成修复建议"""
    suggestions = []
    
    for path, views in duplicates.items():
        suggestion = f"重复路径 '{path}' 映射到多个视图: {', '.join(views)}\n"
        suggestion += "建议修复:\n"
        
        # 查找定义这些路径的urls.py文件
        path_pattern = path.replace('/', r'\/').replace(':param', r'\(\?P<[^>]+>[^)]+\)')
        grep_cmd = f"grep -r --include='*.py' '{path_pattern}' {project_dir}"
        
        try:
            import subprocess
            result = subprocess.run(grep_cmd, shell=True, capture_output=True, text=True)
            if result.stdout:
                suggestion += "以下文件可能需要修改:\n"
                for line in result.stdout.splitlines():
                    suggestion += f"  - {line}\n"
            else:
                suggestion += "无法找到定义此路径的文件，请手动检查。\n"
        except Exception:
            suggestion += "无法执行grep命令，请手动查找定义此路径的文件。\n"
        
        suggestions.append(suggestion)
    
    return suggestions

def attempt_fix(duplicates, project_dir, verbose=False):
    """尝试自动修复重复路径问题"""
    fixed_count = 0
    
    # 查找主urls.py文件
    main_urls_file = os.path.join(project_dir, 'project', 'urls.py')
    if not os.path.exists(main_urls_file):
        print(f"{Colors.FAIL}无法找到主urls.py文件，无法自动修复。{Colors.ENDC}")
        return 0
    
    with open(main_urls_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 查找并注释重复的include语句
    for path, _ in duplicates.items():
        # 将API路径转换为可能的include模式
        api_path = path.strip('/')
        if api_path.startswith('api/'):
            app_path = api_path[4:]  # 移除'api/'前缀
            
            # 查找可能的include模式
            include_patterns = [
                f"path\\('api/{app_path}/', include\\('.*?'\\)\\)",
                f"path\\('api/{app_path}', include\\('.*?'\\)\\)",
                f"re_path\\(r'\\^api/{app_path}/\\?', include\\('.*?'\\)\\)"
            ]
            
            for pattern in include_patterns:
                matches = re.findall(pattern, content)
                if matches and len(matches) > 1:
                    # 保留第一个匹配项，注释其余的
                    for match in matches[1:]:
                        replacement = f"# 以下行被API路径检查工具注释，因为它导致了重复的API路径\n    # {match}"
                        content = content.replace(match, replacement)
                        fixed_count += 1
                        if verbose:
                            print(f"{Colors.OKGREEN}已注释重复路径: {match}{Colors.ENDC}")
    
    # 写回文件
    if fixed_count > 0:
        with open(main_urls_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"{Colors.OKGREEN}已自动修复 {fixed_count} 个重复路径问题。{Colors.ENDC}")
    else:
        print(f"{Colors.WARNING}未找到可自动修复的重复路径问题。{Colors.ENDC}")
    
    return fixed_count

def main():
    parser = argparse.ArgumentParser(description='检查Django项目中的重复API路径')
    parser.add_argument('--fix', action='store_true', help='自动修复检测到的重复路径问题')
    parser.add_argument('--verbose', action='store_true', help='显示详细的检查过程')
    args = parser.parse_args()
    
    # 确定项目根目录
    project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    print(f"{Colors.HEADER}正在检查项目: {project_dir}{Colors.ENDC}")
    
    # 查找所有urls.py文件
    urls_files = find_urls_files(project_dir, args.verbose)
    print(f"找到 {len(urls_files)} 个urls.py文件")
    
    # 分析所有urls.py文件
    all_patterns = []
    for file_path in urls_files:
        patterns = analyze_urls_file(file_path, args.verbose)
        all_patterns.extend(patterns)
    
    print(f"共提取 {len(all_patterns)} 个URL模式")
    
    # 查找重复路径
    duplicates = find_duplicate_paths(all_patterns)
    
    if duplicates:
        print(f"\n{Colors.FAIL}发现 {len(duplicates)} 个重复的API路径:{Colors.ENDC}")
        for path, views in duplicates.items():
            print(f"{Colors.WARNING}  - '{path}' 映射到: {', '.join(views)}{Colors.ENDC}")
        
        # 生成修复建议
        suggestions = generate_fix_suggestions(duplicates, project_dir)
        
        print(f"\n{Colors.HEADER}修复建议:{Colors.ENDC}")
        for suggestion in suggestions:
            print(suggestion)
        
        # 尝试自动修复
        if args.fix:
            print(f"\n{Colors.HEADER}尝试自动修复...{Colors.ENDC}")
            fixed_count = attempt_fix(duplicates, project_dir, args.verbose)
            if fixed_count > 0:
                print(f"{Colors.OKGREEN}自动修复完成，请重新运行检查工具验证修复效果。{Colors.ENDC}")
            else:
                print(f"{Colors.WARNING}无法自动修复，请按照上述建议手动修复。{Colors.ENDC}")
        else:
            print(f"\n{Colors.HEADER}要自动修复问题，请使用 --fix 参数运行此工具。{Colors.ENDC}")
    else:
        print(f"\n{Colors.OKGREEN}未发现重复的API路径，配置正确！{Colors.ENDC}")
    
    return 0 if not duplicates else 1

if __name__ == '__main__':
    sys.exit(main())
