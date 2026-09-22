# -*- coding: utf-8 -*-
"""
自动分析测试用例并添加自动化分类列
第一列：自动化等级 (A/B/C/D/E)
第二列：分类原因

分类规则:
- A 类：纯 UDS 诊断，无需外部条件，可直接自动化
- B 类：DTC 相关，但需要特定条件触发
- C 类：需要硬件设备 (电源/电阻箱等)
- D 类：需要插拔硬件或人工操作 (adb 命令/文件操作等)
- E 类：功能未实现或硬件不支持
"""

import openpyxl
import os

# Excel 文件路径
excel_path = 'D:/Code/CheryDoIP/Chery_case_V5.0.xlsx'
output_path = 'D:/Code/CheryDoIP/Chery_case_V5.0_已分类.xlsx'
print(f"使用文件：{excel_path}")

wb = openpyxl.load_workbook(excel_path)
ws = wb['诊断']

# 检查是否已有分类列，有则删除
print("检查是否已有分类列...")
if ws.cell(row=1, column=1).value == "自动化等级":
    print("发现已有分类列，正在删除...")
    ws.delete_cols(1, 2)

# 在 A 列和 B 列之前插入两列
print("正在插入两列...")
ws.insert_cols(1, 2)

# 设置表头
ws.cell(row=1, column=1, value="自动化等级")
ws.cell(row=1, column=2, value="分类原因")

print("表头已设置：A 列=自动化等级，B 列=分类原因")


def classify_test_case(row_data):
    """
    根据测试用例内容分类
    返回：(等级，原因列表)
    """
    summary = str(row_data.get('Summary', '') or '')
    description = str(row_data.get('Description', '') or '')
    action = str(row_data.get('Action', '') or '')
    result = str(row_data.get('Result', '') or '')
    test_spec = str(row_data.get('Test Specification', '') or '')
    issue_desc = str(row_data.get('问题描述', '') or '')
    
    reasons = []
    
    # ========== E 类：功能未实现 ==========
    if '未实现' in issue_desc or '依赖 BSP' in issue_desc:
        return 'E', ['功能未实现']
    elif '无法' in issue_desc or '电子回复' in issue_desc:
        return 'E', ['硬件不支持']
    
    # ========== D 类：需要人工操作/插拔硬件 ==========
    # 检查是否需要插拔硬件
    if ('不连接' in action or '连接' in action) and ('摄像头' in action or '麦克风' in action or 'USB' in action):
        return 'D', ['需要插拔硬件']
    
    # 检查是否需要 adb 命令或文件操作
    if 'adb' in action.lower() or 'mv ' in action or 'shell' in action:
        return 'D', ['需要 adb 命令']
    
    # 检查是否需要断电重启
    if '断电' in action or '重启' in action or '重新上电' in action:
        return 'D', ['需要断电重启']
    
    # 检查是否需要改配置/改时间
    if '改配置' in action or '改 ICC 时间' in action or 'carconfig' in action.lower():
        return 'D', ['需要修改配置']
    
    # 检查是否需要 2E 写入特定值
    if '2E ' in action and ('D0' in action or 'F1' in action):
        return 'D', ['需要写入特定值']
    
    # ========== C 类：需要硬件设备 ==========
    if '电压' in action or '电阻' in action or '电流' in action or '短路' in action or '开路' in action:
        reason = ['需要硬件设备']
        if '电阻箱' in action:
            reason.append('需要电阻箱')
        if '电源' in action or '电压' in action:
            reason.append('需要程控电源')
        return 'C', reason
    
    if '电阻箱' in action or '万用表' in action or '示波器' in action:
        return 'C', ['需要测试设备']
    
    # ========== B 类：DTC 相关 (需要特定条件触发) ==========
    # 检查是否有复杂的触发条件（多条条件）
    action_lines = [l.strip() for l in action.split('\n') if l.strip()]
    if len(action_lines) >= 3 and ('DTC' in summary or '故障' in summary):
        # 多条触发条件，可能是 B 类
        if any(kw in action for kw in ['无过欠压', 'Power Mode', 'Crank', 'IGN']):
            return 'B', ['DTC 触发条件']
    
    # 检查 Result 是否包含 DTC 相关
    if ('清除' in result and '读取' in result) or ('include' in result.lower() and '0x' in result):
        return 'B', ['DTC 相关']
    
    # ========== A 类：纯 UDS 诊断 ==========
    # 检查是否是标准 UDS 服务响应
    uds_patterns = [
        ('50', '会话控制'), ('62', 'DID 读取'), ('6F', 'DID 写入'),
        ('67', '安全访问'), ('71', '例程控制'), ('C5', 'DTC 设置'),
        ('7E', '心跳'), ('68', '通信控制'), ('51', 'ECU 重置')
    ]
    
    for pattern, tag in uds_patterns:
        if result.startswith(pattern):
            return 'A', [f'纯 UDS 诊断 [{tag}]']
    
    # 默认：检查响应格式
    if len(result) <= 10 and result.replace(' ', '').isalnum():
        return 'A', ['纯 UDS 诊断']
    
    # 其他情况归为 B 类
    return 'B', ['其他诊断测试']


# 遍历所有测试用例行 (从第 2 行开始)
print("\n开始分类测试用例...")
classification_stats = {'A': 0, 'B': 0, 'C': 0, 'D': 0, 'E': 0}

for row_idx in range(2, ws.max_row + 1):
    # 读取该行的所有数据 (原始列偏移了 2 列)
    row_data = {}
    
    col_mapping = {
        'Issue Id': 3, 'Issue key': 4, 'Issue type': 5, 'Summary': 6,
        'Test type': 7, 'Test Specification': 8, 'Description': 9,
        'Action': 10, 'Result': 12, '测试环境': 19, '优先级': 20,
        '测试结果': 21, '测试版本': 22, '测试日期': 23, '测试人': 24,
        '问题描述': 25, 'bugID': 26
    }
    
    for header, col_idx in col_mapping.items():
        cell_value = ws.cell(row=row_idx, column=col_idx).value
        row_data[header] = cell_value
    
    # 分类
    level, reasons = classify_test_case(row_data)
    
    # 写入 A 列：等级
    ws.cell(row=row_idx, column=1, value=level)
    
    # 写入 B 列：原因
    reason_str = ','.join(reasons)
    ws.cell(row=row_idx, column=2, value=reason_str)
    
    # 统计
    classification_stats[level] = classification_stats.get(level, 0) + 1
    
    # 每 100 行打印一次进度
    if row_idx % 100 == 0:
        print(f"  已处理 {row_idx - 1} 条用例...")

print("\n分类完成!")
print("\n统计结果:")
for level in ['A', 'B', 'C', 'D', 'E']:
    count = classification_stats.get(level, 0)
    desc = {
        'A': '纯 UDS 诊断 (易自动化)',
        'B': 'DTC 相关 (需条件触发)',
        'C': '需要硬件设备 (半自动)',
        'D': '需要人工操作 (困难)',
        'E': '功能未实现 (不可自动)'
    }
    print(f"  {level}类：{count} 条 - {desc[level]}")

# 保存文件
print(f"\n正在保存文件...")
print(f"  输出文件：{output_path}")
wb.save(output_path)

print("\n✅ 完成!")
print(f"   共处理 {ws.max_row - 1} 条测试用例")
