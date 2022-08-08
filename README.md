# dep_spdlog

## development plan

+ override `setuptools.Distribution`

  currently workaround is to build the cpp code every time called `setup.py`
  and inject into `sdist`

  a better approach might be analyze the command, and only do relative stuff
  when building `bdist`

  also, override `setuptools.Distribution` can simplify the platform handling
  code

+ support manylinux
+ support windows
