cmake_minimum_required(VERSION 3.17...3.24)
project(dep_spdlog)

message(STATUS "current source dir: ${CMAKE_CURRENT_SOURCE_DIR}")
message(STATUS "current binary dir: ${CMAKE_CURRENT_BINARY_DIR}")
message(STATUS "current install dir: ${CMAKE_INSTALL_PREFIX}")

list(PREPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_SOURCE_DIR})
include(spdlog)

external_project_spdlog(INSTALL_PREFIX ${CMAKE_INSTALL_PREFIX})
