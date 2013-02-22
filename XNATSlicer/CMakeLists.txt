#-----------------------------------------------------------------------------
set(MODULE_NAME XNATSlicer)

#-----------------------------------------------------------------------------
set(MODULE_PYTHON_SCRIPTS
  ${MODULE_NAME}.py
  ${MODULE_NAME}Lib/__init__.py
  ${MODULE_NAME}Lib/XNATAddProjEditor.py
  ${MODULE_NAME}Lib/XNATBrowser.py
  ${MODULE_NAME}Lib/XNATCommunicator.py
  ${MODULE_NAME}Lib/XNATFileInfo.py
  ${MODULE_NAME}Lib/XNATInstallWizard.py
  ${MODULE_NAME}Lib/XNATLoadWorkflow.py
  ${MODULE_NAME}Lib/XNATMRMLParser.py
  ${MODULE_NAME}Lib/XNATSaveDialog.py
  ${MODULE_NAME}Lib/XNATSaveWorkflow.py
  ${MODULE_NAME}Lib/XNATScenePackager.py
  ${MODULE_NAME}Lib/XNATSessionManager.py
  ${MODULE_NAME}Lib/XNATSettings.py
  ${MODULE_NAME}Lib/XNATTimer.py
  ${MODULE_NAME}Lib/XNATTreeView.py
  ${MODULE_NAME}Lib/XNATUtils.py
  ${MODULE_NAME}Lib/XNATView.py
  )

set(MODULE_PYTHON_RESOURCES
  Resources/Icons/${MODULE_NAME}.png
  ${MODULE_NAME}Lib/icons/addproj.jpg
  ${MODULE_NAME}Lib/icons/delete.jpg
  ${MODULE_NAME}Lib/icons/load.jpg
  ${MODULE_NAME}Lib/icons/save.jpg
  ${MODULE_NAME}Lib/icons/update.jpg
  ${MODULE_NAME}Lib/icons/wrench.png
  ${MODULE_NAME}Lib/python_mod/win32/ez_setup.py
  ${MODULE_NAME}Lib/python_mod/win32/lxml-2.2.8-py2.6-win32.egg
  ${MODULE_NAME}Lib/python_mod/win64/ez_setup.py
  ${MODULE_NAME}Lib/python_mod/win64/lxml-2.2.8-py2.6-win-amd64.egg
  ${MODULE_NAME}Lib/python_mod/win64/DLLs/bz2.pyd
  ${MODULE_NAME}Lib/python_mod/win64/DLLs/py.ico
  ${MODULE_NAME}Lib/python_mod/win64/DLLs/pyc.ico
  ${MODULE_NAME}Lib/python_mod/win64/DLLs/pyexpat.pyd
  ${MODULE_NAME}Lib/python_mod/win64/DLLs/select.pyd
  ${MODULE_NAME}Lib/python_mod/win64/DLLs/sqlite3.dll
  ${MODULE_NAME}Lib/python_mod/win64/DLLs/tcl85.dll
  ${MODULE_NAME}Lib/python_mod/win64/DLLs/tclpip85.dll
  ${MODULE_NAME}Lib/python_mod/win64/DLLs/tk85.dll
  ${MODULE_NAME}Lib/python_mod/win64/DLLs/unicodedata.pyd
  ${MODULE_NAME}Lib/python_mod/win64/DLLs/winsound.pyd
  ${MODULE_NAME}Lib/python_mod/win64/DLLs/_bsddb.pyd
  ${MODULE_NAME}Lib/python_mod/win64/DLLs/_ctypes.pyd
  ${MODULE_NAME}Lib/python_mod/win64/DLLs/_ctypes_test.pyd
  ${MODULE_NAME}Lib/python_mod/win64/DLLs/_elementtree.pyd
  ${MODULE_NAME}Lib/python_mod/win64/DLLs/_hashlib.pyd
  ${MODULE_NAME}Lib/python_mod/win64/DLLs/_msi.pyd
  ${MODULE_NAME}Lib/python_mod/win64/DLLs/_multiprocessing.pyd
  ${MODULE_NAME}Lib/python_mod/win64/DLLs/_socket.pyd
  ${MODULE_NAME}Lib/python_mod/win64/DLLs/_sqlite3.pyd
  ${MODULE_NAME}Lib/python_mod/win64/DLLs/_ssl.pyd
  ${MODULE_NAME}Lib/python_mod/win64/DLLs/_testcapi.pyd
  ${MODULE_NAME}Lib/python_mod/win64/DLLs/_tkinter.pyd
  ${MODULE_NAME}Lib/python_mod/win64/Lib/distutils/archive_util.py
  ${MODULE_NAME}Lib/python_mod/win64/Lib/distutils/bcppcompiler.py
  ${MODULE_NAME}Lib/python_mod/win64/Lib/distutils/ccompiler.py
  ${MODULE_NAME}Lib/python_mod/win64/Lib/distutils/cmd.py
  ${MODULE_NAME}Lib/python_mod/win64/Lib/distutils/config.py
  ${MODULE_NAME}Lib/python_mod/win64/Lib/distutils/core.py
  ${MODULE_NAME}Lib/python_mod/win64/Lib/distutils/cygwinccompiler.py
  ${MODULE_NAME}Lib/python_mod/win64/Lib/distutils/debug.py
  ${MODULE_NAME}Lib/python_mod/win64/Lib/distutils/dep_util.py
  ${MODULE_NAME}Lib/python_mod/win64/Lib/distutils/dir_util.py
  ${MODULE_NAME}Lib/python_mod/win64/Lib/distutils/dist.py
  ${MODULE_NAME}Lib/python_mod/win64/Lib/distutils/emxccompiler.py
  ${MODULE_NAME}Lib/python_mod/win64/Lib/distutils/errors.py
  ${MODULE_NAME}Lib/python_mod/win64/Lib/distutils/extension.py
  ${MODULE_NAME}Lib/python_mod/win64/Lib/distutils/fancy_getopt.py
  ${MODULE_NAME}Lib/python_mod/win64/Lib/distutils/filelist.py
  ${MODULE_NAME}Lib/python_mod/win64/Lib/distutils/file_util.py
  ${MODULE_NAME}Lib/python_mod/win64/Lib/distutils/log.py
  ${MODULE_NAME}Lib/python_mod/win64/Lib/distutils/msvc9compiler.py
  ${MODULE_NAME}Lib/python_mod/win64/Lib/distutils/msvccompiler.py
  ${MODULE_NAME}Lib/python_mod/win64/Lib/distutils/mwerkscompiler.py
  ${MODULE_NAME}Lib/python_mod/win64/Lib/distutils/spawn.py
  ${MODULE_NAME}Lib/python_mod/win64/Lib/distutils/sysconfig.py
  ${MODULE_NAME}Lib/python_mod/win64/Lib/distutils/text_file.py
  ${MODULE_NAME}Lib/python_mod/win64/Lib/distutils/unixccompiler.py
  ${MODULE_NAME}Lib/python_mod/win64/Lib/distutils/util.py
  ${MODULE_NAME}Lib/python_mod/win64/Lib/distutils/version.py
  ${MODULE_NAME}Lib/python_mod/win64/Lib/distutils/versionpredicate.py
  ${MODULE_NAME}Lib/python_mod/win64/Lib/distutils/__init__.py
  ${MODULE_NAME}Lib/python_mod/win64/Lib/distutils/command/bdist.py
  ${MODULE_NAME}Lib/python_mod/win64/Lib/distutils/command/bdist_dumb.py
  ${MODULE_NAME}Lib/python_mod/win64/Lib/distutils/command/bdist_msi.py
  ${MODULE_NAME}Lib/python_mod/win64/Lib/distutils/command/bdist_rpm.py
  ${MODULE_NAME}Lib/python_mod/win64/Lib/distutils/command/bdist_wininst.py
  ${MODULE_NAME}Lib/python_mod/win64/Lib/distutils/command/build.py
  ${MODULE_NAME}Lib/python_mod/win64/Lib/distutils/command/build_clib.py
  ${MODULE_NAME}Lib/python_mod/win64/Lib/distutils/command/build_ext.py
  ${MODULE_NAME}Lib/python_mod/win64/Lib/distutils/command/build_py.py
  ${MODULE_NAME}Lib/python_mod/win64/Lib/distutils/command/build_scripts.py
  ${MODULE_NAME}Lib/python_mod/win64/Lib/distutils/command/clean.py
  ${MODULE_NAME}Lib/python_mod/win64/Lib/distutils/command/config.py
  ${MODULE_NAME}Lib/python_mod/win64/Lib/distutils/command/install.py
  ${MODULE_NAME}Lib/python_mod/win64/Lib/distutils/command/install_data.py
  ${MODULE_NAME}Lib/python_mod/win64/Lib/distutils/command/install_egg_info.py
  ${MODULE_NAME}Lib/python_mod/win64/Lib/distutils/command/install_headers.py
  ${MODULE_NAME}Lib/python_mod/win64/Lib/distutils/command/install_lib.py
  ${MODULE_NAME}Lib/python_mod/win64/Lib/distutils/command/install_scripts.py
  ${MODULE_NAME}Lib/python_mod/win64/Lib/distutils/command/register.py
  ${MODULE_NAME}Lib/python_mod/win64/Lib/distutils/command/sdist.py
  ${MODULE_NAME}Lib/python_mod/win64/Lib/distutils/command/upload.py
  ${MODULE_NAME}Lib/python_mod/win64/Lib/distutils/command/wininst-6.0.exe
  ${MODULE_NAME}Lib/python_mod/win64/Lib/distutils/command/wininst-7.1.exe
  ${MODULE_NAME}Lib/python_mod/win64/Lib/distutils/command/wininst-8.0.exe
  ${MODULE_NAME}Lib/python_mod/win64/Lib/distutils/command/wininst-9.0-amd64.exe
  ${MODULE_NAME}Lib/python_mod/win64/Lib/distutils/command/wininst-9.0.exe
  ${MODULE_NAME}Lib/python_mod/win64/Lib/distutils/command/__init__.py
  ${MODULE_NAME}Lib/python_mod/win64/Lib/distutils/tests/setuptools_build_ext.py
  ${MODULE_NAME}Lib/python_mod/win64/Lib/distutils/tests/setuptools_extension.py
  ${MODULE_NAME}Lib/python_mod/win64/Lib/distutils/tests/support.py
  ${MODULE_NAME}Lib/python_mod/win64/Lib/distutils/tests/test_bdist_wininst.py
  ${MODULE_NAME}Lib/python_mod/win64/Lib/distutils/tests/test_build_ext.py
  ${MODULE_NAME}Lib/python_mod/win64/Lib/distutils/tests/test_build_py.py
  ${MODULE_NAME}Lib/python_mod/win64/Lib/distutils/tests/test_build_scripts.py
  ${MODULE_NAME}Lib/python_mod/win64/Lib/distutils/tests/test_config.py
  ${MODULE_NAME}Lib/python_mod/win64/Lib/distutils/tests/test_core.py
  ${MODULE_NAME}Lib/python_mod/win64/Lib/distutils/tests/test_dist.py
  ${MODULE_NAME}Lib/python_mod/win64/Lib/distutils/tests/test_filelist.py
  ${MODULE_NAME}Lib/python_mod/win64/Lib/distutils/tests/test_install.py
  ${MODULE_NAME}Lib/python_mod/win64/Lib/distutils/tests/test_install_lib.py
  ${MODULE_NAME}Lib/python_mod/win64/Lib/distutils/tests/test_install_scripts.py
  ${MODULE_NAME}Lib/python_mod/win64/Lib/distutils/tests/test_msvc9compiler.py
  ${MODULE_NAME}Lib/python_mod/win64/Lib/distutils/tests/test_register.py
  ${MODULE_NAME}Lib/python_mod/win64/Lib/distutils/tests/test_sdist.py
  ${MODULE_NAME}Lib/python_mod/win64/Lib/distutils/tests/test_sysconfig.py
  ${MODULE_NAME}Lib/python_mod/win64/Lib/distutils/tests/test_unixccompiler.py
  ${MODULE_NAME}Lib/python_mod/win64/Lib/distutils/tests/test_upload.py
  ${MODULE_NAME}Lib/python_mod/win64/Lib/distutils/tests/test_util.py
  ${MODULE_NAME}Lib/python_mod/win64/Lib/distutils/tests/test_versionpredicate.py
  ${MODULE_NAME}Lib/python_mod/win64/Lib/distutils/tests/__init__.py
  ${MODULE_NAME}Lib/python_mod/win64/libs/bz2.lib
  ${MODULE_NAME}Lib/python_mod/win64/libs/pyexpat.lib
  ${MODULE_NAME}Lib/python_mod/win64/libs/python26.lib
  ${MODULE_NAME}Lib/python_mod/win64/libs/select.lib
  ${MODULE_NAME}Lib/python_mod/win64/libs/unicodedata.lib
  ${MODULE_NAME}Lib/python_mod/win64/libs/winsound.lib
  ${MODULE_NAME}Lib/python_mod/win64/libs/_bsddb.lib
  ${MODULE_NAME}Lib/python_mod/win64/libs/_ctypes.lib
  ${MODULE_NAME}Lib/python_mod/win64/libs/_ctypes_test.lib
  ${MODULE_NAME}Lib/python_mod/win64/libs/_elementtree.lib
  ${MODULE_NAME}Lib/python_mod/win64/libs/_hashlib.lib
  ${MODULE_NAME}Lib/python_mod/win64/libs/_msi.lib
  ${MODULE_NAME}Lib/python_mod/win64/libs/_multiprocessing.lib
  ${MODULE_NAME}Lib/python_mod/win64/libs/_socket.lib
  ${MODULE_NAME}Lib/python_mod/win64/libs/_sqlite3.lib
  ${MODULE_NAME}Lib/python_mod/win64/libs/_ssl.lib
  ${MODULE_NAME}Lib/python_mod/win64/libs/_testcapi.lib
  ${MODULE_NAME}Lib/python_mod/win64/libs/_tkinter.lib
  )

#-----------------------------------------------------------------------------
slicerMacroBuildScriptedModule(
  NAME ${MODULE_NAME}
  SCRIPTS "${MODULE_PYTHON_SCRIPTS}"
  RESOURCES "${MODULE_PYTHON_RESOURCES}"
  )

#-----------------------------------------------------------------------------
if(BUILD_TESTING)

  # this will regiester the unittest subclass in the main script
  # as a ctest (note that it is also usable as a runtime test).
  slicer_add_python_unittest(SCRIPT ${MODULE_NAME}.py)

  # additional build-time testing goes in here
  add_subdirectory(Testing)
endif()