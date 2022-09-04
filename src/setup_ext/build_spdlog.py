import os
import shutil
import subprocess
import setuptools
from setuptools.command.build_clib import build_clib
from setuptools.extension import Extension
from setuptools.command.build_ext import build_ext
import re


def construct_cmdclass_build_clib(package_name, src_dir, build_dir, install_dir, linkback_hook=None):
    class BuildClib(build_clib):
        def __init__(self, dist, *arg, **kwarg) -> None:
            super().__init__(dist, *arg, **kwarg)

            self.package_name = package_name

            self.cmake_src_dir = src_dir
            self.cmake_build_dir = build_dir
            self.cmake_install_dir = install_dir

            self.linkback_hook = linkback_hook

        def check_library_list(self, libraries):
            if libraries is None:
                return
            return super().check_library_list(libraries)

        def get_source_files(self):
            if self.libraries is None:
                return []
            return super().get_source_files()

        def run(self):
            res = super().run()

            cmake_configure(self.cmake_src_dir, self.cmake_build_dir, self.cmake_install_dir)
            cmake_build(self.cmake_build_dir, os.cpu_count())
            cmake_install(self.cmake_build_dir)

            build_ext = self.get_finalized_command("build_ext")
            inplace = build_ext.inplace
            if not inplace:
                package_dir = os.path.join(build_ext.build_lib, self.package_name)
                self.linkback_hook(self.cmake_build_dir, self.cmake_install_dir, package_dir)
            else:
                build_py = self.get_finalized_command("build_py")
                package_dir = os.path.abspath(build_py.get_package_dir(self.package_name))
                self.linkback_hook(self.cmake_build_dir, self.cmake_install_dir, package_dir)

            return res

    return BuildClib


class DummyExtension(Extension):
    pass


def construct_cmdclass_build_ext():
    class BuildExt(build_ext):
        def __init__(self, dist, *arg, **kwarg) -> None:
            super().__init__(dist, *arg, **kwarg)

        def run(self):
            if self.inplace:
                self.run_command("build_clib")
            return super().run()

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


def spdlog_linkback(build_dir, install_dir, package_dir):
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
    shutil.rmtree(os.path.join(package_src_dir, ".git"))
    if os.path.exists(package_include_dir):
        shutil.rmtree(package_include_dir)
    shutil.copytree(spdlog_include_dir, package_include_dir)
    if os.path.exists(package_lib64_dir):
        shutil.rmtree(package_lib64_dir)
    shutil.copytree(spdlog_lib64_dir, package_lib64_dir, symlinks=True)
    # instead of rmtree, replace prefix with "${pcfiledir}/../.."
    pkgconfig_dir = os.path.join(package_lib64_dir, "pkgconfig")
    pkgconfig_file = os.path.join(pkgconfig_dir, "spdlog.pc")
    with open(pkgconfig_file, "r") as f:
        pkgconfig_content = f.read()
    pkgconfig_content = re.sub(r"^prefix=.*", r"prefix=${pcfiledir}/../..", pkgconfig_content)
    with open(pkgconfig_file, "w") as f:
        f.write(pkgconfig_content)
