# Unit tests for MplCpp library
set(TEST_FILES
    ArtistTest.h
    AxesTest.h
    ColormapTest.h
    ColorConverterTest.h
    CyclerTest.h
    FigureTest.h
    Line2DTest.h
    MantidColormapTest.h
    ScalarMappableTest.h
    ZoomerTest.h
    QBackendExtractTest.h
    PlotTest.h)

if(NOT APPLE)
  list(APPEND TEST_FILES
              ColorsTest.h
              FigureCanvasQtTest.h)
endif()

set(CXXTEST_EXTRA_HEADER_INCLUDE
    ${CMAKE_CURRENT_LIST_DIR}/MplCppTestInitialization.h)

mtd_add_qt_tests(TARGET_NAME MantidQtWidgetsMplCppTest
                 QT_VERSION 5
                 INCLUDE_DIRS
                   ${CMAKE_CURRENT_LIST_DIR}/../inc
                 SRC
                   ${TEST_FILES}
                 LINK_LIBS
                   Kernel
                   API
                   PythonInterfaceCore
                   ${Boost_LIBRARIES}
                   ${PYTHON_LIBRARIES}
                   ${POCO_LIBRARIES}
                 MTD_QT_LINK_LIBS
                   MantidQtWidgetsMplCpp
                   MantidQtWidgetsCommon
                 PARENT_DEPENDENCIES
                   GUITests)
