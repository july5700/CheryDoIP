# -*- coding: utf-8 -*-
# 自动生成的 A 类测试用例 (纯 UDS 诊断)

from typing import List
from dataclasses import dataclass

@dataclass
class TestCase:
    """测试用例数据类"""
    issue_key: str
    request: str
    expected_response: str
    session_required: int = 0
    security_required: int = 0
    pre_command: str = ""

def get_a_class_tests() -> List[TestCase]:
    """A 类测试用例 (纯 UDS 诊断 - 易自动化)"""
    return [
