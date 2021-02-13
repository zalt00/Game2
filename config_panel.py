# -*- coding:Utf-8 -*-

import sys
try:
    from utils.advanced_configuration_panel import App
except ImportError:
    sys.path.append('./sources/')
    from utils.advanced_configuration_panel import App


if __name__ == '__main__':
    app = App()
    app.run()
