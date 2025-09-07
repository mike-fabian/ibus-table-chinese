cmake_minimum_required(VERSION 3.12...4.0)

# Default CMAKE_INSTALL_PREFIX should be set before PROJECT()
SET(CMAKE_INSTALL_PREFIX "/usr" CACHE PATH "Install dir prefix")

####################################################################
# Project specific information
#
PROJECT(
ibus-table-chinese
VERSION 1.8.14
DESCRIPTION "Chinese input tables for IBus"
HOMEPAGE_URL http://mike-fabian.github.io/ibus-table/
LANGUAGES NONE # skip compiler checks, no compilers are needed
)
SET(PRJ_SUMMARY "Chinese input tables for IBus")

SET(PRJ_DESCRIPTION
"ibus-table-chinese is provides the infrastructure for Chinese input methods.
Input tables themselves are in subpackages."
    )

INCLUDE(GNUInstallDirs)
SET(DATA_DIR ${CMAKE_INSTALL_DATADIR})

####################################################################
# Building
#
ADD_SUBDIRECTORY(tables)

####################################################################
# Installing
#
SET(PRJ_DOC_DIR "${CMAKE_INSTALL_DOCDIR}")
INSTALL(FILES AUTHORS README ChangeLog COPYING DESTINATION ${PRJ_DOC_DIR})

