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
def construct_cmdclass_build_clib(src_dir, build_dir):
    class BuildClib(build_clib):
        def __init__(self, dist, *arg, **kwarg) -> None:
            super().__init__(dist, *arg, **kwarg)
            self.cmake_src_dir = src_dir
            self.cmake_build_dir = build_dir
            print(self.cmake_src_dir)
            print(self.cmake_build_dir)

        def run(self):
            super().run()

    return BuildClib


def cmake_configure(src_dir, build_dir):
    cmake_arg = []
    subprocess.check_call(["cmake", src_dir] + cmake_arg, cwd=build_dir)


def cmake_build():
    pass
