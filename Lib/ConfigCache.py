import configparser
import chardet
import os
# from tkinter import messagebox
# from loguru import logger
import os
import toml
from collections import OrderedDict

class TomlConfig(object):
    _cache = {}

    def __init__(self, toml_path):
        self.dir = os.getcwd()
        self.toml_path = toml_path
        self.toml_path = os.path.join(self.dir, self.toml_path)
        # logger.debug(f"Using ini path: {self.toml_path}")

        if self.toml_path not in self._cache:
            with open(self.toml_path, 'r', encoding='utf-8') as t:
                self._cache[self.toml_path] = toml.load(t, _dict=OrderedDict)
        self.config = self._cache[self.toml_path]

    def read(self, key, default=None):
        keys = key.split('.')
        current = self.config
        for k in keys:
            if k in current:
                current = current[k]
            else:
                return default
        return current

    def write(self, key, value):
        keys = key.split('.')
        current = self.config
        for k in keys[:-1]:
            if k not in current:
                current[k] = OrderedDict()
            current = current[k]
        current[keys[-1]] = value
        self._save()

    def _save(self):
        with open(self.toml_path, 'w', encoding='utf-8') as t:
            toml.dump(self.config, t)

    def get(self, key, default=None):
        return self.read(key, default)

    def set(self, key, value):
        self.write(key, value)

    def delete(self, key):
        keys = key.split('.')
        current = self.config
        for k in keys[:-1]:
            if k in current:
                current = current[k]
            else:
                return
        if keys[-1] in current:
            del current[keys[-1]]
        self._save()

    def keys(self):
        return list(self.config.keys())

    def items(self):
        return list(self.config.items())

    def __getitem__(self, key):
        return self.read(key)

    def __setitem__(self, key, value):
        self.write(key, value)

    def __delitem__(self, key):
        self.delete(key)

    def __contains__(self, key):
        return self.read(key) is not None

    def add_version(self, version_info):
        """
        添加一个新的版本信息到 TOML 文件中。
        :param version_info: 包含版本信息的字典
        """
        new_version = OrderedDict([
            ('version', version_info['version']),
            ('date', version_info['date']),
            ('link', version_info['link']),
            ('path', version_info['path'])
        ])
        self.config.setdefault('versions', []).append(new_version)
        self._save()

# 示例用法
if __name__ == "__main__":
    config = TomlConfig(r'..\BX\cfg.toml')

    version_info = {
        'version': '5.2.6.79',
        'date': '2024.11.14_13:16:00',
        'link': 'https://hw-snc-jfrog-dmz.zeekrlife.com/artifactory/zeekr/8295_ZEEKR/daily_8155/BXCN_OS5.2/Release/V5.2.6.77/b_Package_USB.zip',
        'path': 'C:/Users/qdai4/Desktop/Integration/BX/BXCN_OS5.2/Release/V5.2.6.77/b_Package_USB.zip'
    }
    config.add_version(version_info)
    os._exit(0)
    # 读取配置
    print(config['common.api'])  # 输出: localhost
    print(config.get('common.api'))  # 输出: 5432

    # 写入配置
    config['common.qnx_port'] = 'com5'
    config.set('common.qnx_port', 'com6')

    # 删除配置
    del config['common.vip_port']  # 使用 del 关键字
    config.delete('common.port')  # 使用 delete 方法

    # 检查键是否存在
    print('common.web' in config)  # 输出: True

    # 获取所有顶级键和键值对
    print(config.keys())  # 输出: ['database', 'clients']
    print(config.items())  # 输出: [('database', {...}), ('clients', [...])]

    # 使用下标操作的详细示例
    print("使用下标操作的详细示例:")

    # 读取配置
    print(config['database.host'])  # 输出: localhost
    print(config['database.port'])  # 输出: 5432

    # 写入配置
    config['common.qnx_port'] = '123'
    print(config['database.test_key'])  # 输出: test_value
    os._exit(0)
    # 删除配置
    del config['database.test_key']  # 使用 del 关键字
    print('database.test_key' in config)  # 输出: False

    # 更新配置
    config['database.port'] = 5433
    print(config['database.port'])  # 输出: 5433

    # 检查键是否存在
    print('database.host' in config)  # 输出: True
    print('database.nonexistent_key' in config)  # 输出: False

    # 获取所有顶级键和键值对
    print(config.keys())  # 输出: ['database', 'clients']
    print(config.items())  # 输出: [('database', {...}), ('clients', [...])]


class IniConfig(object):
    _cache = {}  # Class-level cache

    def __init__(self, ini_path):
        self.dir = os.getcwd()
        self.ini_path = ini_path
        # print(f"self.ini_path: {self.ini_path}")
        self.ini_path = os.path.join(self.dir, self.ini_path)

        if self.ini_path not in self._cache:
            # If the configuration file is not in the cache, read it and cache it
            self._cache[self.ini_path] = configparser.ConfigParser()
            self._cache[self.ini_path].read(self.ini_path, encoding=self.read_encoding())
        self.config = self._cache[self.ini_path]

    def read_cfg(self, section, key):
        """
        Return a string value, located by section and key
        :param section: section name in the config file
        :param key: key within the section
        :return: string value
        """
        return self.config.get(section, key)

    def read_encoding(self):
        """
        Re-encode, chardet can be used to detect the encoding type of the file.
        :return: encoding
        """
        with open(self.ini_path, "rb") as f:
            data = f.read()
            encoding = chardet.detect(data)["encoding"]
            return encoding

    def read_cfg_with_check(self, section, key):
        value = self.read_cfg(section, key)
        if not value:
            print(f"Warning: '{key}' cannot be empty")
            # messagebox.showwarning("Error", message)
            return None
        else:
            return value

    def update_cfg(self, section, key, new_value):
        """
        Update the value of a key in a specified section of the INI file and save the changes.
        :param section: section name in the config file
        :param key: key within the section
        :param new_value: new value to set
        """
        if not self.config.has_section(section):
            self.config.add_section(section)
        self.config.set(section, key, new_value)
        with open(self.ini_path, 'w', encoding=self.read_encoding()) as configfile:
            self.config.write(configfile)
        logger.info(f"Updated {key} in section {section} to {new_value}.")
        self._clear_cache()

    def _clear_cache(self):
        if self.ini_path in self._cache:
            del self._cache[self.ini_path]

if __name__ == "__main__":
    # cfg = IniConfig('../BX/download.ini')
    # print(f"cfg value= {cfg}")
    # print(f"type of cfg = {type(cfg)}")
    # print(f"cfg._cache value = {cfg._cache}")
    # print(f"type of cfg._cache = {type(cfg._cache)}")
    # guess = cfg._cache['E:\\Integration\\PrivateLib\\../BX/download.ini']
    # print(f"guess type is {type(guess)}")
    # web = cfg.read_cfg('common', 'web')
    # print(f"web value = {web}")
    # print(f"type of web = {type(web)}")
    # assert cfg.config != guess

    cfg = TomlConfig('../BX/cfg.toml')
    v1 = cfg.read_cfg('versions')
    print(f"v1 = {v1}")
    print(f"type of v1 = {type(v1)}")
    v2 = cfg.read_cfg('parameter','is_proxies')
    print('----'*30)
    print(v2)

    # new_cfg['parameter','is_proxies'] = 'ttrue'

    v2="123aa"
    new_cfg = cfg.config
    print(f"new_cfg = {new_cfg}")
    cfg.write_cfg(new_cfg)
    v2 = cfg.read_cfg('parameter', 'is_proxies')
    print(f"v2 = {v2}")