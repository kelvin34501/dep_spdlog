import os
from setuptools import setup
import pathlib
import importlib.util
from glob import glob


# setup util function
def module_from_file(module_name, file_location):
    spec = importlib.util.spec_from_file_location(module_name, file_location)
    assert spec is not None, f"failed to load module {module_name} at {file_location}"
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None, f"ModuleSpec.loader is None for {module_name} at {file_location}"
    spec.loader.exec_module(module)
    return module


# get setup.py location
here = pathlib.Path(__file__).parent.resolve()
long_description = (here / "README.md").read_text(encoding="utf-8")

# import from location
build_spdlog = module_from_file("cmake", here / "setup_ext" / "build_spdlog.py")
SRC_DIR = here / "src" / "buildsys"
BUILD_DIR = here / "workdir" / "build"
INSTALL_DIR = here / "workdir" / "install"
PACKAGE_DIR = here / "src" / "dep_spdlog"

# create dir
BUILD_DIR.mkdir(parents=True, exist_ok=True)
INSTALL_DIR.mkdir(parents=True, exist_ok=True)
build_spdlog.upkeep_library(
    SRC_DIR,
    BUILD_DIR,
    INSTALL_DIR,
    linkback_hook=build_spdlog.construct_spdlog_linkback(BUILD_DIR, INSTALL_DIR, PACKAGE_DIR),
)

# current packages
packages = [
    "dep_spdlog",
]


def get_package_file():
    include_list = [
        os.path.relpath(file, str(PACKAGE_DIR))
        for file in glob(str(PACKAGE_DIR / "include" / "**" / "*"), recursive=True)
    ]
    lib64_list = [
        os.path.relpath(file, str(PACKAGE_DIR))
        for file in glob(str(PACKAGE_DIR / "lib64" / "**" / "*"), recursive=True)
    ]
    src_list = [
        os.path.relpath(file, str(PACKAGE_DIR)) for file in glob(str(PACKAGE_DIR / "src" / "**" / "*"), recursive=True)
    ]
    res = include_list + lib64_list + src_list
    return res


setup(
    # attr
    name="dep_spdlog",
    version="0.0.0",
    description="pip install dependency: spdlog",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/kelvin34501/dep_spdlog",
    author="kelvin34501",
    author_email="kelvin34501@foxmail.com",
    # dep
    python_requires=">=3.9, <4",
    # pkg
    package_dir={"": "src"},
    packages=packages,
    package_data={"dep_spdlog": get_package_file()},
    # cmdclass
    cmdclass={
        "build_clib": build_spdlog.construct_cmdclass_build_clib(),
        "build_ext": build_spdlog.construct_cmdclass_build_ext(),
    },
    libraries=[("dummy", {"sources": []})],
    ext_modules=[build_spdlog.DummyExtension("dummy", [])],
)
