include_guard()

include(ExternalProject)

function(external_project_spdlog)
    cmake_parse_arguments(
        ARG
        "" # no value
        "INSTALL_PREFIX;VERSION" # single value
        "" # multi value
        ${ARGN}
    )

    if(NOT DEFINED ARG_INSTALL_PREFIX)
        message(FATAL_ERROR "[spdlog] install prefix not defined!")
    else()
        message(STATUS "[spdlog] install prefix: ${ARG_INSTALL_PREFIX}")
    endif()


    if(NOT DEFINED ARG_VERSION)
        set(ARG_VERSION "v1.10.0")
    endif()

    message(STATUS "[spdlog] use version: ${ARG_VERSION}")

    ExternalProject_Add(spdlog
        GIT_REPOSITORY    "git@github.com:gabime/spdlog.git"
        GIT_TAG           "${ARG_VERSION}"
        CMAKE_ARGS        "-DCMAKE_INSTALL_PREFIX:PATH=${ARG_INSTALL_PREFIX}"
                          "-DSPDLOG_BUILD_SHARED:BOOL=ON"
    )

endfunction()
