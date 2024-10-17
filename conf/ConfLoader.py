import toml
import os
from utils.logger import log
from .MenuConf import MenuConf
from .DynamicMenuConf import DynamicMenuConf

class ConfLoader:

    def __init__(self, conf_root_dir: str):
        if os.path.isfile(conf_root_dir):
            self.conf_root_dir = os.path.dirname(conf_root_dir)
        else:
            self.conf_root_dir = conf_root_dir
        self.conf_root_dir = self.ensure_path_is_absolute(self.conf_root_dir)

    def get_conf_root_dir(self):
        return self.conf_root_dir

    def get_default_conf_filename(self):
        return "conf.toml"

    def get_conf_root_path(self):
        return os.path.join(self.get_conf_root_dir(), self.get_default_conf_filename())


    async def load_parent_conf(self, conf_path: str):
        parent_conf_path = self.get_parent_path(conf_path)
        if parent_conf_path is not None:
            parent_conf = await self.load_conf(parent_conf_path)
        else:
            parent_conf = None
        return parent_conf

    async def load_conf(self, conf_path: str):
        if os.path.isdir(conf_path):
            conf_path = os.path.join(conf_path, self.get_default_conf_filename())

        if not os.path.exists(conf_path):
            raise FileNotFoundError(f"Configuration file not found: {conf_path}")

        with open(conf_path, "r") as f:
            conf = toml.load(f)
        if "type" not in conf:
            raise ValueError("Configuration must include a 'type' field")
        conf_type = conf.get("type")

        parent_conf = await self.load_parent_conf(conf_path)

        retConf = None
        if conf_type == "menu":
            retConf = MenuConf(conf,conf_path,parent_conf)
        elif conf_type == "dynamicmenu":
              retConf = DynamicMenuConf(conf,conf_path,parent_conf)
        else:
            raise ValueError(f"Unknown configuration type: {conf_type}")

        await retConf.async_init()
        return retConf

    def get_goin_path(self, current_conf_path: str, next_id: str):
        dir = os.path.dirname(current_conf_path)
        next_path = os.path.join(dir, next_id, self.get_default_conf_filename())
        return next_path

    def ensure_path_is_absolute(self, path: str):
        if not os.path.isabs(path):
            path = os.path.abspath(path)
        return path

    def is_root_path(self, current_conf_path: str):
        path = self.ensure_path_is_absolute(current_conf_path)
        ret = path == self.get_conf_root_path()
        return ret

    def get_parent_path(self, current_conf_path: str):
        if self.is_root_path(current_conf_path):
            return None
        dir = os.path.dirname(current_conf_path)
        parent_path = os.path.dirname(dir)
        return parent_path

    def get_goout_path(self, current_conf_path: str):
        if self.is_root_path(current_conf_path):
            return None
        parent_path = self.get_parent_path(current_conf_path)
        conf_file_name = self.get_default_conf_filename()
        previous_path = os.path.join(parent_path, conf_file_name)
        return previous_path

