from setuptools import setup
import pathlib
import importlib.util


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

# collect, build & install dll
# TODO

# current packages
packages = [
    "dep_spdlog",
]

setup(
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
    # cmdclass
)
