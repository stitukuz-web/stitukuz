#!/usr/bin/env python3
"""扫描代码库中的 TODO/FIXME/XXX/HACK，强制要求 deadline + owner"""
import os, re, sys, subprocess
from datetime import datetime

ROOT = '/home/stitukuz/sti'
PATTERNS = [
    (r'(?i)(TODO|FIXME|XXX|HACK)\s*[:\(]?\s*(.+)', '标准'),
    (r'(?i)@todo\s+(.+)', '注解'),
]

DEADLINE_RE = re.compile(r'(?i)(deadline|due|by)\s*[:\(]?\s*(\d{4}-\d{2}-\d{2})')
OWNER_RE = re.compile(r'(?i)(owner|assignee|@)(\w+)')

def scan_file(filepath):
    issues = []
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
    except Exception:
        return issues
    
    for i, line in enumerate(lines, 1):
        for pattern, ptype in PATTERNS:
            m = re.search(pattern, line)
            if m:
                full = line.strip()
                msg = m.group(2) if m.lastindex and m.lastindex >= 2 else m.group(1)
                
                # 检查 deadline
                dl_match = DEADLINE_RE.search(full)
                deadline = dl_match.group(2) if dl_match else None
                
                # 检查 owner
                owner_match = OWNER_RE.search(full)
                owner = owner_match.group(2) if owner_match else None
                
                issues.append({
                    'file': filepath,
                    'line': i,
                    'type': ptype,
                    'full': full[:120],
                    'msg': msg[:100],
                    'deadline': deadline,
                    'owner': owner,
                    'has_deadline': deadline is not None,
                    'has_owner': owner is not None,
                })
    return issues

def main():
    all_issues = []
    for root, dirs, files in os.walk(ROOT):
        # 跳过 vendor、node_modules、.git、logs、data
        dirs[:] = [d for d in dirs if d not in ('vendor', 'node_modules', '.git', 'logs', 'data', '__pycache__')]
        for f in files:
            if f.endswith(('.php', '.js', '.ts', '.html', '.py', '.sh', '.md', '.yml', '.yaml')):
                fp = os.path.join(root, f)
                all_issues.extend(scan_file(fp))
    
    # 分类统计
    total = len(all_issues)
    no_deadline = [x for x in all_issues if not x['has_deadline']]
    no_owner = [x for x in all_issues if not x['has_owner']]
    no_both = [x for x in all_issues if not x['has_deadline'] and not x['has_owner']]
    
    print(f"=== TODO 扫描报告 ===")
    print(f"总计: {total} 处")
    print(f"无 deadline: {len(no_deadline)} 处")
    print(f"无 owner: {len(no_owner)} 处")
    print(f"两者皆无: {len(no_both)} 处")
    print()
    
    if no_deadline:
        print("=== 缺 deadline 的 TOP 20 ===")
        for x in no_deadline[:20]:
            print(f"  {x['file']}:{x['line']} [{x['type']}] {x['msg'][:80]}")
        print()
    
    if no_owner:
        print("=== 缺 owner 的 TOP 20 ===")
        for x in no_owner[:20]:
            print(f"  {x['file']}:{x['line']} [{x['type']}] {x['msg'][:80]}")
        print()
    
    # 生成修复建议
    if no_deadline:
        print("=== 修复建议 ===")
        print("请为每个 TODO 添加标准注解：")
        print("  // TODO(deadline: 2026-11-15, owner: @username) 具体描述")
        print("  # TODO(deadline: 2026-11-15, owner: @username) 具体描述")
        print()
        print("CI 将在 PR 中拦截无 deadline/owner 的 TODO。")
    
    # 返回非零码以便 CI 拦截
    sys.exit(1 if no_deadline or no_owner else 0)

if __name__ == '__main__':
    main()
