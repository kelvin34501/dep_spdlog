import os
import shutil
import subprocess
import setuptools
from setuptools.command.build_clib import build_clib
from setuptools.extension import Extension
from setuptools.command.build_ext import build_ext


def construct_cmdclass_build_clib():
    class BuildClib(build_clib):
        def __init__(self, dist, *arg, **kwarg) -> None:
            super().__init__(dist, *arg, **kwarg)

        def run(self):
            super().run()

        def build_libraries(self, libraries):
            pass

    return BuildClib


class DummyExtension(Extension):
    pass


def construct_cmdclass_build_ext():
    class BuildExt(build_ext):
        def __init__(self, dist, *arg, **kwarg) -> None:
            super().__init__(dist, *arg, **kwarg)

        def run(self):
            super().run()

        def build_extension(self, ext):
            if not isinstance(ext, DummyExtension):
                super().build_extension(ext)

    return BuildExt


def upkeep_library(cmake_src_dir, cmake_build_dir, cmake_install_dir, linkback_hook=None):
    cmake_configure(cmake_src_dir, cmake_build_dir, cmake_install_dir)
    cmake_build(cmake_build_dir, os.cpu_count())
    cmake_install(cmake_build_dir)

    if linkback_hook is not None:
        linkback_hook()


def cmake_configure(src_dir, build_dir, install_dir):
    cmake_arg = [
        "-DCMAKE_BUILD_TYPE=Release",
        f"-DCMAKE_INSTALL_PREFIX={install_dir}",
    ]
    subprocess.check_call(["cmake", src_dir] + cmake_arg, cwd=build_dir)


def cmake_build(build_dir, parallel_level=None):
    build_arg = [
        "--config Release",
    ]
    if parallel_level is not None:
        build_arg.append(f"-j{parallel_level}")
    subprocess.check_call(["cmake", "--build", "."] + build_arg, cwd=build_dir)


def cmake_install(build_dir):
    install_arg = [
        "--config Release",
    ]
    subprocess.check_call(["cmake", "--install", "."] + install_arg, cwd=build_dir)


def construct_spdlog_linkback(build_dir, install_dir, package_dir):
    def spdlog_linkback():
        # * spdlog specific
        # link the src, include, lib path
        spdlog_src_dir = os.path.join(build_dir, "spdlog-prefix", "src", "spdlog")
        spdlog_include_dir = os.path.join(install_dir, "include")
        spdlog_lib64_dir = os.path.join(install_dir, "lib64")
        package_src_dir = os.path.join(package_dir, "src")
        package_include_dir = os.path.join(package_dir, "include")
        package_lib64_dir = os.path.join(package_dir, "lib64")
        # symlink
        if os.path.exists(package_src_dir):
            shutil.rmtree(package_src_dir)
        shutil.copytree(spdlog_src_dir, package_src_dir)
        if os.path.exists(package_include_dir):
            shutil.rmtree(package_include_dir)
        shutil.copytree(spdlog_include_dir, package_include_dir)
        if os.path.exists(package_lib64_dir):
            shutil.rmtree(package_lib64_dir)
        shutil.copytree(spdlog_lib64_dir, package_lib64_dir, symlinks=True)
        shutil.rmtree(os.path.join(package_lib64_dir, "pkgconfig"))

    return spdlog_linkback
