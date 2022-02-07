# wubi-haifeng
# It takes very long to generate the table from scratch
#ADD_CUSTOM_COMMAND(OUTPUT wubi-haifeng86.UTF-8
#    COMMAND convertTable.sh
#    COMMENT "Building wubi-haifeng86.UTF-8"
#    )

MAKE_TABLE_SOURCE_TXT(${CMAKE_CURRENT_BINARY_DIR}/wubi-haifeng86.txt
    ${CMAKE_SOURCE_DIR}/tables/wubi-haifeng/wubi-haifeng86.head
    ${CMAKE_SOURCE_DIR}/tables/wubi-haifeng/wubi-haifeng86.UTF-8
    ${CMAKE_SOURCE_DIR}/tables/wubi-haifeng/wubi-haifeng86.tail)
CONVERT_DB(wubi-haifeng "${CMAKE_CURRENT_BINARY_DIR}/wubi-haifeng86.txt")

