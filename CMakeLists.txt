cmake_minimum_required(VERSION 2.6.2)

# Default CMAKE_INSTALL_PREFIX should be set before PROJECT()
SET(CMAKE_INSTALL_PREFIX "/usr" CACHE PATH "Install dir prefix")

####################################################################
# Project specific information
#
PROJECT(ibus-table-chinese NONE)
SET(PRJ_SUMMARY "Chinese input tables for IBus")

SET(PRJ_DESCRIPTION
"ibus-table-chinese is provides the infrastructure for Chinese input methods.
Input tables themselves are in subpackages."
    )

IF(CMAKE_SYSTEM_PROCESSOR MATCHES "64")
    SET(LIB_DIR "${CMAKE_INSTALL_PREFIX}/lib64" CACHE PATH "Library dir")
ELSE(CMAKE_SYSTEM_PROCESSOR MATCHES "64")
    SET(LIB_DIR "${CMAKE_INSTALL_PREFIX}/lib" CACHE PATH "Library dir")
ENDIF(CMAKE_SYSTEM_PROCESSOR MATCHES "64")
SET(LIBEXEC_DIR "${LIB_DIR}" CACHE PATH "LIBEXEC dir")
SET(DATA_DIR "/usr/share")

####################################################################
# Building
#
ADD_SUBDIRECTORY(tables)

####################################################################
# Installing
#
SET(PRJ_DOC_DIR "${DATA_DIR}/doc/ibus-table-chinese")
INSTALL(FILES AUTHORS README ChangeLog COPYING DESTINATION ${PRJ_DOC_DIR})

