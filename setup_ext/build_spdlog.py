import os
import re
import subprocess
import sys
import setuptools
from setuptools.command.build_clib import build_clib
from distutils.command.build import build
from distutils import log
from setuptools.command.develop import develop


def construct_cmdclass_build():
    class CustomBuild(build):
        def has_c_libraries(self):
            return True

        sub_commands = [
            ("build_py", build.has_pure_modules),
            ("build_clib", has_c_libraries),
            ("build_ext", build.has_ext_modules),
            ("build_scripts", build.has_scripts),
        ]

    return CustomBuild


def construct_cmdclass_develop():
    class CustomDevelop(develop):
        def install_for_development(self):
            self.run_command("egg_info")

            # Build clib
            self.run_command("build_clib")

            # Build extensions in-place
            self.reinitialize_command("build_ext", inplace=1)
            self.run_command("build_ext")

            if setuptools.bootstrap_install_from:
                self.easy_install(setuptools.bootstrap_install_from)
                setuptools.bootstrap_install_from = None

            self.install_namespaces()

            # create an .egg-link in the installation dir, pointing to our egg
            log.info("Creating %s (link to %s)", self.egg_link, self.egg_base)
            if not self.dry_run:
                with open(self.egg_link, "w") as f:
                    f.write(self.egg_path + "\n" + self.setup_path)
            # postprocess the installed distro, fixing up .pth, installing scripts,
            # and handling requirements
            self.process_distribution(None, self.dist, not self.no_deps)

    return CustomDevelop


# TODO
def construct_cmdclass_build_clib(src_dir, build_dir, install_dir, linkback_hook=None):
    class BuildClib(build_clib):
        def __init__(self, dist, *arg, **kwarg) -> None:
            super().__init__(dist, *arg, **kwarg)
            self.cmake_src_dir = src_dir
            self.cmake_build_dir = build_dir
            self.cmake_install_dir = install_dir

        def run(self):
            super().run()

            cmake_configure(self.cmake_src_dir, self.cmake_build_dir, self.cmake_install_dir)
            cmake_build(self.cmake_build_dir, os.cpu_count())
            cmake_install(self.cmake_build_dir)

            if linkback_hook is not None:
                linkback_hook()

    return BuildClib


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
        spdlog_src_dir = os.path.join(build_dir, "spdlog-prefix", "src")
        spdlog_include_dir = os.path.join(install_dir, "include")
        spdlog_lib64_dir = os.path.join(install_dir, "lib64")
        package_src_dir = os.path.join(package_dir, "src")
        package_include_dir = os.path.join(package_dir, "include")
        package_lib64_dir = os.path.join(package_dir, "lib64")
        # symlink
        if not os.path.exists(package_src_dir):
            os.symlink(spdlog_src_dir, package_src_dir)
        if not os.path.exists(package_include_dir):
            os.symlink(spdlog_include_dir, package_include_dir)
        if not os.path.exists(package_lib64_dir):
            os.symlink(spdlog_lib64_dir, package_lib64_dir)

    return spdlog_linkback
