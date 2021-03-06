import os

import moderngl_window as mglw


class Example(mglw.WindowConfig):
    gl_version = (3, 3)
    title = "ModernGL Example"
    window_size = (512, 512)
    aspect_ratio = 1#16 / 9
    resizable = True

    resource_dir = os.path.normpath(os.path.join(__file__, '../../data'))

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @classmethod
    def run(cls, window_size):
        Example.windows_size = window_size
        Example.aspect_ratio = window_size[0] / window_size[1] 
        mglw.run_window_config(cls)
