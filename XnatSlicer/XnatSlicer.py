import imp, os, inspect, sys, slicer



#
# Widget path needs to be globally recognized by Python.
# Appending to global path here.
#
WIDGETPATH = os.path.normpath(os.path.realpath(os.path.abspath(os.path.split(inspect.getfile( inspect.currentframe()))[0])))
#
# Inlcude testing folders.
#
sys.path.append(os.path.join(WIDGETPATH, 'Testing'))
#
# Include lib folder.
#
WIDGETPATH = os.path.join(WIDGETPATH, "XnatSlicerLib")
sys.path.append(WIDGETPATH)
#
# Include UI folder.
#
sys.path.append(os.path.join(WIDGETPATH, 'UI'))



from XnatFileInfo import *
from XnatAddProjEditor import *
from XnatLoadWorkflow import *
from XnatUtils import *
from XnatScenePackager import *
from XnatSessionManager import *
from XnatTimer import *
from XnatSettings import *
from XnatTreeView import *
from XnatCommunicator import *
from XnatLoginMenu import *
from XnatButtons import *
from XnatView import *
from XnatPopup import *
from XnatDicomLoadWorkflow import *
from XnatSceneLoadWorkflow import *
from XnatFileLoadWorkflow import *
from XnatFilter import *
from XnatSlicerTest import *
from XnatError import *



comment = """
XnatSlicer.py contains the central classes for managing 
all of the XnatSlicer functions and abilities.  XnatSlicer.py
is the point where the module talks to Slicer, arranges the gui, and
registers it to the Slicer modules list.  It is where all of the 
XnatSlicerLib classes and methods come together.

TODO:
"""


class XnatSlicer:
  """ The class that ultimately registers the module
      with Slicer.
  """
  def __init__(self, parent):

      parent.title = "XNATSlicer"
      parent.categories = ["XNATSlicer"]
      parent.dependencies = []
      parent.contributors = ["Sunil Kumar (Moka Creative, LLC), Dan Marcus (WashU-St. Louis), Steve Pieper (Isomics)"] 
      parent.helpText = """ The XNATSlicer 1.0"""
      parent.acknowledgementText = """Sunil Kumar for the Neuroinformatics Research Group - sunilk@mokacreativellc.com""" 
      self.parent = parent


      
      #--------------------------------
      # Add this test to the SelfTest module's list for discovery when the module
      # is created.  Since this module may be discovered before SelfTests itself,
      # create the list if it doesn't already exist.
      #--------------------------------
      try:
          slicer.selfTests
      except AttributeError:
          slicer.selfTests = {}
          slicer.selfTests['XnatSlicer'] = self.runTest
          
      def runTest(self):
          tester = XnatSlicerTest()
          tester.runTest()


          

class XnatSlicerWidget:
    """  The class that manages all of the XNATSlicer-specific
         libraries.
    """
    
    def __init__(self, parent = None):
        """ Init function.
        """
        if not parent:
            self.parent = slicer.qMRMLWidget()
            self.parent.setLayout(qt.QVBoxLayout())
            self.parent.setMRMLScene(slicer.mrmlScene)
        else:
            self.parent = parent
        if not parent:
            self.setup()
            self.parent.show()


            
        #--------------------------------
        # Init Xnat Utils
        #--------------------------------
        self.utils = XnatUtils()   



        #--------------------------------
        # Construct all needed directories
        # if not there...
        #--------------------------------
        self.utils.constructNecessaryModuleDirectories()

        
        
        #--------------------------------
        # Set the layout
        #--------------------------------
        self.layout = self.parent.layout()

        
        
        #--------------------------------
        # Collapse the 'Data Probe' button.
        #--------------------------------
        dataProbeButton = slicer.util.findChildren(text='Data Probe')[0]
        dataProbeButton.setChecked(False)


        
        #--------------------------------
        # Xnat settings
        #--------------------------------
        self.settings = XnatSettings(slicer.qMRMLWidget(), self.utils.MODULE_URIS['settings'], self)
        self.settingsPopup = XnatSettingsWindow(self)


            
        #--------------------------------
        # Xnat Communicator
        #--------------------------------
        self.XnatCommunicator = XnatCommunicator()


      
        #--------------------------------
        # Xnat Filter
        #--------------------------------
        self.XnatFilter = XnatFilter(self)
        

        
        #--------------------------------
        # Login Menu
        #--------------------------------
        self.XnatLoginMenu = XnatLoginMenu(parent = self.parent, browser = self)
        self.XnatLoginMenu.loadDefaultHost()   


      
        #--------------------------------
        # Viewer
        #--------------------------------
        self.XnatView = XnatTreeView(parent = self.parent, browser = self)  
        
        
        
        #--------------------------------
        # Xnat Buttons
        #--------------------------------
        self.XnatButtons = XnatButtons(self.parent, browser=self)  
        
        
        
        #--------------------------------
        # Popups
        #--------------------------------
        self.downloadPopup = XnatDownloadPopup(browser = self)
        #self.uploadPopup = XnatDownloadPopup(browser = self)


      
        #--------------------------------
        # Layouts
        #--------------------------------
        self.viewerLayout = None
        self.loginLayout = None
        self.XnatViewLayout = qt.QGridLayout()
        
        
        
        #--------------------------------
        # LoadWorkflows
        #--------------------------------
        self.XnatSceneLoadWorkflow = XnatSceneLoadWorkflow(self)
        self.XnatFileLoadWorkflow = XnatFileLoadWorkflow(self)
        self.XnatDicomLoadWorkflow = XnatDicomLoadWorkflow(self)
        
        
        
        #--------------------------------
        # Init gui
        #--------------------------------
        self.initGUI()
        
        
        
        #--------------------------------
        # Listeners/observers from gui
        #--------------------------------
        slicer.mrmlScene.AddObserver(slicer.mrmlScene.EndCloseEvent, self.sceneClosedListener)
        slicer.mrmlScene.AddObserver(slicer.mrmlScene.EndImportEvent, self.sceneImportedListener)



        #--------------------------------
        # Tester
        #--------------------------------
        self.tester = XnatSlicerTest(self)
        
        self.parent.show()


      

      
    def onReload(self, moduleName = "XnatSlicer"):
      """ Generic reload method for any scripted module.
          ModuleWizard will subsitute correct default moduleName.
          Provided by Slicer.
      """
      
      widgetName = moduleName + "Widget"


      #--------------------------------
      # Reload the source code:
      # - set source file path
      # - load the module to the global space
      #--------------------------------
      filePath = eval('slicer.modules.%s.path' % moduleName.lower())
      p = os.path.dirname(filePath)
      if not sys.path.__contains__(p):
        sys.path.insert(0,p)
      fp = open(filePath, "r")
      globals()[moduleName] = imp.load_module(
          moduleName, fp, filePath, ('.py', 'r', imp.PY_SOURCE))
      fp.close()


      
      #--------------------------------
      # Rebuild the widget:
      # - find and hide the existing widget
      # - create a new widget in the existing parent
      #--------------------------------
      parent = slicer.util.findChildren(name='%s Reload' % moduleName)[0].parent()
      for child in parent.children():
        try:
          child.hide()
        except AttributeError:
          pass


        
      #--------------------------------  
      # Remove spacer items.
      #--------------------------------
      item = parent.layout().itemAt(0)
      while item:
        parent.layout().removeItem(item)
        item = parent.layout().itemAt(0)


        
      #--------------------------------
      # Create new widget inside existing parent.
      #--------------------------------
      globals()[widgetName.lower()] = eval('globals()["%s"].%s(parent)' % (moduleName, widgetName))
      globals()[widgetName.lower()].setup()



      
    def onReloadAndTest(self, moduleName = "ScriptedExample"):
        """ Also provided by Slicer.  Runs the tests on the
            reload.
        """
        try:
            self.onReload()
            evalString = 'globals()["%s"].%sTest()' % (moduleName, moduleName)
            tester = eval(evalString)
            tester.runTest()
        
        except Exception, e:
            import traceback
            traceback.print_exc()
            qt.QMessageBox.warning(slicer.util.mainWindow(), 
                                   "Reload and Test", 'Exception!\n\n' + str(e) + "\n\nSee Python Console for Stack Trace")
    


        
    def sceneClosedListener(self, caller, event):
        """Actions for when the user closes a scene from the GUI.
        """ 
        #print("'Close Scene' called. Resetting Xnat session data.")    
        self.XnatView.sessionManager.clearCurrentSession()  



        
    def sceneImportedListener(self, caller, event): 
        """Actions for when the user imports a scene from the GUI.
           NOTE: This technically is not used, as the user must refer to files from an 
           Xnat location. Nonetheless, it is implemented in the event that it is needed.
        """
        if self.XnatView.lastButtonClicked == None:
            #print("'Import Data' called. Resetting Xnat session data.")
            self.XnatView.sessionManager.clearCurrentSession() 
    

            
            
    def initGUI(self):  
        """ As stated.
        """
        
        #--------------------------------
        # Login Section
        #--------------------------------
        loginCollapsibleButton = ctk.ctkCollapsibleButton()
        loginCollapsibleButton.text = "XNAT Login"


        
        #--------------------------------
        # Viewer Section
        #--------------------------------
        viewerCollapsibleButton = ctk.ctkCollapsibleButton()
        viewerCollapsibleButton.text = "XNAT Viewer"


        #--------------------------------
        # Tools Section
        #--------------------------------
        toolsCollapsibleButton = ctk.ctkCollapsibleButton()
        toolsCollapsibleButton.text = "Tools"

        
        
        #--------------------------------
        # Add all sections to parent layout.
        #--------------------------------
        self.layout.addWidget(loginCollapsibleButton)
        self.layout.addWidget(viewerCollapsibleButton)
        self.layout.addWidget(toolsCollapsibleButton)

        
        
        #--------------------------------
        # Define section layouts.
        #--------------------------------
        self.loginLayout = qt.QVBoxLayout(loginCollapsibleButton)
        self.viewerLayout = qt.QVBoxLayout(viewerCollapsibleButton) 
        self.toolsLayout = qt.QVBoxLayout(toolsCollapsibleButton) 


        

        #--------------------------------
        # Clean the temp dir
        #--------------------------------
        self.cleanCacheDir(200)



        #--------------------------------
        # Top Widgets Row 
        #--------------------------------
        self.topButtonRowLayout = qt.QHBoxLayout()
        #
        # Search
        #
        searchLabel = qt.QLabel("Search:")
        self.topButtonRowLayout.addWidget(searchLabel)
        self.searchBox = qt.QLineEdit()
        self.searchBox.connect("returnPressed()", self.XnatView.searchEntered)
        self.topButtonRowLayout.addWidget(self.searchBox)

        
        
        #--------------------------------
        # Load/Save buttons
        #--------------------------------
        self.buttonColumnLayout = qt.QVBoxLayout()
        self.buttonColumnLayout.addWidget(self.XnatButtons.buttons['io']['load'])#, 2, 0)
        self.buttonColumnLayout.addWidget(self.XnatButtons.buttons['io']['save'])#, 0, 0) 


        
        #--------------------------------
        # Tool Row (XNAT IO)
        #--------------------------------
        self.toolRowLayout = qt.QHBoxLayout()
        self.toolRowLayout.addWidget(self.XnatButtons.buttons['io']['delete'])
        self.toolRowLayout.addSpacing(15)
        self.toolRowLayout.addWidget(self.XnatButtons.buttons['io']['addProj'])
        self.toolRowLayout.addSpacing(15)
        self.toolRowLayout.addWidget(self.XnatButtons.buttons['io']['test'])
        self.toolRowLayout.addStretch()
        #
        # Filter
        #
        self.toolRowLayout.addStretch()
        filterLabel = qt.QLabel("Project filter:")
        self.toolRowLayout.addWidget(filterLabel)
        self.toolRowLayout.addSpacing(15)
        self.toolRowLayout.addWidget(self.XnatButtons.buttons['filter']['accessed'])

        
        #--------------------------------
        # XnatViewer
        #--------------------------------
        self.XnatViewLayout.addLayout(self.topButtonRowLayout, 0, 0, 1, 1)
        self.XnatViewLayout.addWidget(self.XnatView.viewWidget, 2, 0)
        self.XnatViewLayout.addLayout(self.buttonColumnLayout, 2, 1)
       

        
        #--------------------------------
        # Apply to globals
        #--------------------------------      
        self.loginLayout.addLayout(self.XnatLoginMenu.loginLayout)
        self.viewerLayout.addLayout(self.XnatViewLayout)
        self.toolsLayout.addLayout(self.toolRowLayout)


        
        
    def cleanCacheDir(self, maxSize):
        """ Empties contents of the temp directory based upon maxSize
        """
        import math
        folder = self.utils.CACHE_URI
        folder_size = 0


        
        #--------------------------------
        # Loop through files to get file sizes.
        #--------------------------------
        for (path, dirs, files) in os.walk(folder):
          for file in files:
            folder_size += os.path.getsize(os.path.join(path, file))
        #print ("XnatSlicer Data Folder = %0.1f MB" % (folder_size/(1024*1024.0)))


        
        #--------------------------------
        # If the folder size exceeds limit, remove contents.
        #--------------------------------
        folder_size = math.ceil(folder_size/(1024*1024.0))
        if folder_size > maxSize:
            self.utils.removeFilesInDir(folder)    




                
    def beginXnat(self):
        """ Opens the view class linked to the Xnat REST API.
            Runs a test for the relevant libraries (i.e. SSL)
            before allowing the login process to begin.
        """

        #--------------------
        # Can SSL be imported?
        #--------------------
        print("XnatSlicer Module: Checking if SSL is installed...")
        try:      
            import ssl
            httplib.HTTPSConnection
            print("XnatSlicer Module: SSL is installed!")

            

        #--------------------
        # If not, kick back OS error
        #--------------------
        except Exception, e:
            strs = "XnatSlicer cannot operate on this system as SSL is not installed."
            print("XnatSlicer Module: %s"%(strs))
            qt.QMessageBox.warning(slicer.util.mainWindow(), "No SSL", "%s"%(strs))
            return
                

        
        #--------------------
        # Init communicator.
        #--------------------
        self.XnatCommunicator.setup(browser = self, 
                                    host = self.settings.getAddress(self.XnatLoginMenu.hostDropdown.currentText), 
                                    user = self.XnatLoginMenu.usernameLine.text, password=self.XnatLoginMenu.passwordLine.text)

        

        #--------------------
        # Begin communicator
        #--------------------
        self.XnatView.begin()
        return
        try:
            self.XnatView.begin()
        except Exception, e:
            print("XnatSlicer Module Login Error: %s"%(str(e)))
            qt.QMessageBox.warning(slicer.util.mainWindow(), "Login error!", "%s"%('There appears to be a login error.'))

      
