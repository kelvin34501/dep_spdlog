import os
import sys


def src_dir():
    here = os.path.dirname(os.path.normpath(__file__))
    return os.path.join(here, "src")


def include_dir():
    here = os.path.dirname(os.path.normpath(__file__))
    return os.path.join(here, "include")


def lib64_dir():
    if sys.platform == "linux":
        here = os.path.dirname(os.path.normpath(__file__))
        return os.path.join(here, "lib64")
    else:
        raise NotImplementedError("unsupported platform")


def lib_dir():
    return lib64_dir()


def cmake_dir():
    return os.path.join(lib64_dir(), "cmake")


def setup_env():
    if sys.platform == "linux":
        lib64_path = lib64_dir()
        if "LD_LIBRARY_PATH" not in os.environ:
            os.environ["LD_LIBRARY_PATH"] = lib64_path
        elif lib64_path not in os.environ["LD_LIBRARY_PATH"]:
            os.environ["LD_LIBRARY_PATH"] = lib64_path + os.pathsep + os.environ["LD_LIBRARY_PATH"]
    else:
        raise NotImplementedError("unsupported platform")


__all__ = (
    "__version__",
    "src_dir",
    "include_dir",
    "lib64_dir",
    "lib_dir",
    "cmake_dir",
    "setup_env",
)
