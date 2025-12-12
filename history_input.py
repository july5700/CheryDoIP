# --- 新增：HistoryManager 类 ---
from PySide6.QtCore import QSettings
from PySide6.QtWidgets import QComboBox


class HistoryManager:
    def __init__(self, combo: QComboBox, history_key: str = "signal_history", max_history: int = 20):
        self.combo = combo
        self.history_key = history_key
        self.max_history = max_history
        self.company = "VST"
        self.app_name = "CherryDoIP"

        # 禁止 combo 编辑（确保只读）
        self.combo.setEditable(False)

        # 加载历史
        self.load_history()

    def load_history(self):
        """从 QSettings 加载历史并填充到 combo"""
        settings = QSettings(self.company, self.app_name)
        history = settings.value(self.history_key, [])
        if isinstance(history, list):
            history = [s for s in history if isinstance(s, str)]
            self.combo.clear()
            self.combo.addItems(history)

    def save_history(self):
        """将当前 combo 内容保存到磁盘"""
        history = [self.combo.itemText(i) for i in range(self.combo.count())]
        settings = QSettings(self.company, self.app_name)
        settings.setValue(self.history_key, history)

    def add_to_history(self, text: str):
        if not text or not isinstance(text, str):
            return
        text = text.strip()
        if not text:
            return

        was_blocked = self.combo.signalsBlocked()
        self.combo.blockSignals(True)
        try:
            # 去重
            for i in range(self.combo.count() - 1, -1, -1):
                if self.combo.itemText(i) == text:
                    self.combo.removeItem(i)
            # 插入到顶部
            self.combo.insertItem(0, text)
            # 限长
            if self.combo.count() > self.max_history:
                self.combo.removeItem(self.max_history)
            # 保存
            self.save_history()
        finally:
            self.combo.blockSignals(was_blocked)

    def get_selected_text(self) -> str:
        """获取当前 combo 选中的文本"""
        return self.combo.currentText()