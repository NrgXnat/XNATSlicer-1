from __main__ import vtk, ctk, qt, slicer

import os
import sys
import shutil
import urllib2

from XnatView import *
from XnatTimer import *


comment = """
XnatTreeView is a subclass of both the XnatView class and the
qt.QTreeWidget class.  It presents XNAT file system accessed
in a tree-node hierarchy, with customized columns masks to avoid 
visual clutter and maximize interactibility.

The view classes (and subclasses) ultimately communicate
with the load and save workflows.   

TODO:
"""



class XnatTreeView(XnatView, qt.QTreeWidget):
    """ Inherits the XnatView class and the qt.QTreeWidget class. 
    """  
    
    def setup(self):
        """ Setup function for XnatTreeView.
        """
        
        #----------------------
        # TreeView
        #----------------------
        qt.QTreeWidget.__init__(self)
        self.setHeaderHidden(False)       
        #treeWidgetSize = qt.QSize(100, 200)
        #self.setBaseSize(treeWidgetSize)

        
        
        #----------------------
        # TreeView Columns
        #----------------------
        self.initColumns()

        

        #----------------------
        # Fonts
        #----------------------
        self.itemFont_folder = qt.QFont("Arial", self.MODULE.GLOBALS.FONT_SIZE, 25, False)
        self.itemFont_file = qt.QFont("Arial", self.MODULE.GLOBALS.FONT_SIZE, 75, False)
        self.itemFont_category = qt.QFont("Arial", self.MODULE.GLOBALS.FONT_SIZE, 25, True)
        self.itemFont_searchHighlighted = qt.QFont("Arial", self.MODULE.GLOBALS.FONT_SIZE, 75, False)

        
        
        #----------------------
        # Tree-related globals
        #----------------------
        self.dirText = None     
        self.currItem = None
        self.currLoadable = None        


        
        #----------------------
        # Scene globals
        #----------------------
        self.lastButtonClicked = None 

        
        
        #----------------------
        # Clear Scene dialog
        #----------------------
        self.initClearDialog()


        
        #----------------------
        # Folder masks
        #----------------------
        self.applySlicerFolderMask = True
        self.hideSlicerHelperFolders = True


        
        #----------------------
        # Delete dialog
        #----------------------
        self.deleteDialog = qt.QMessageBox()   


        
        #--------------------
        # NOTE: fixes a scaling error that occurs with the scroll 
        # bar.  Have yet to pinpoint why this happens.
        #--------------------
        self.verticalScrollBar().setStyleSheet('width: 15px')


        

    def initColumns(self):
        """ Intializes the columns of the qTreeViewWidget
            tailoring XNAT metadata to columns.  There are merged 
            columns that blend two or more columns together
            and there are single columns associated with single
            XNAT metadata values.
        """
        self.columns = {}
        for key in self.MODULE.utils.XnatMetadataTags_all:
            self.columns[key] = {}


            
        #-----------------------
        # Apply metadata key to the columns.  Manuplulate
        # the string values of the tags to make them more
        # human-readable.
        #----------------------
        for key in self.columns:
            strVal = key.replace('_',' ').title()
            strVal = strVal.replace('Pi', 'PI')
            strVal = strVal.replace('Uri', 'URI')
            strVal = strVal.replace(' 497', '')
            strVal = strVal.replace('Id', 'ID')
            self.columns[key]['displayname'] = strVal


            
        #----------------------
        # MERGED_LABEL, and XNAT_LEVEL columns are not 
        # part of the metadata set so we're adding them. 
        #---------------------- 
        self.columns['MERGED_LABEL'] = {}  
        self.columns['MERGED_LABEL']['displayname'] = 'Name/ID/Label'   
        self.columns['XNAT_LEVEL'] = {}  
        self.columns['XNAT_LEVEL']['displayname'] = 'Level'      
        self.columns['MERGED_INFO'] = {}  
        self.columns['MERGED_INFO']['displayname'] = 'Info' 


        
        #----------------------
        # Define column keys based on XNAT_LEVEL.  
        # More columns can be added by uncommenting.
        #---------------------- 
        self.columnKeyOrder = {}
        self.columnKeyOrder['ALL'] = [
            'MERGED_LABEL',
            'XNAT_LEVEL',
            'MERGED_INFO'
        ]


        
        #---------------------- 
        # Merge 'self.columnKeyOrder' with
        # the XnatIo's 'relevantMetadataDict'
        #---------------------- 
        self.columnKeyOrder = dict(self.columnKeyOrder.items() + 
                                   self.MODULE.XnatIo.relevantMetadataDict.items())
        


        #---------------------- 
        # Create a union of all the self.columnKeyOrder 
        # arrays (i.e. 'allHeaders')
        #---------------------- 
        allHeaders = self.MODULE.utils.uniqify(self.columnKeyOrder['ALL'] + 
                                                # NOTE: Leaving this out as it will become part of MERGED_LABELS
                                                # via self.getMergedLabelByLevel, which determines the relevant
                                                # metadata tag for the given XNAT level.
                                                # self.columnKeyOrder['LABELS'] + 
                                                self.columnKeyOrder['projects'] + 
                                                self.columnKeyOrder['subjects'] + 
                                                self.columnKeyOrder['experiments'] + 
                                                self.columnKeyOrder['resources'] + 
                                                self.columnKeyOrder['scans'] + 
                                                self.columnKeyOrder['files'] + 
                                                self.columnKeyOrder['slicer']
                                                )


        
        #---------------------- 
        # Create columns based on 'allHeaders'
        #----------------------         
        self.setColumnCount(len(allHeaders))
        headerLabels = []
        for header in allHeaders:
            try:
                #
                # Set other column key/values.
                #
                self.columns[header]['location'] = len(headerLabels)
                #
                # Set the headerLabels.
                #
                headerLabels.append( self.columns[header]['displayname'])
            except Exception, e:
                #print e, "column init stuff"
                continue
        self.setHeaderLabels(headerLabels)
        self.showColumnsByNodeLevel()



        
    def getMergedLabelTagByLevel(self, level):
        """ Points the MERGED_LABEL column tag to the relevant
            XNAT metadata tag.  This is for the Name/ID/Label column.
        """ 
        level = level.lower()
        if level == 'projects': 
            #
            # NOTE: this would be in all caps if there were no query arguments.
            # since we only query projects that the user has access to, we have to 
            # use a lowercase 'id'.
            #
            return 'id'
        elif level == 'scans':
            return 'ID'
        elif level == 'subjects' or level == 'experiments':
            return 'label'
        elif level == 'files' or level == 'slicer':
            return 'Name'           



        
    def setValuesToTreeNode(self, treeNode = None, metadata = None):
        """ Fills the row values for a given set of columns for
            a tree node.  The columns correspond to the keys of
            the 'metadata' argument.
        """

        level = metadata['XNAT_LEVEL']

        #print "\nSET VALUES", treeNode, metadata
        
        #------------------
        # Cycle through all metadata keys to set their
        # equivalents in self.columns.
        #------------------
        for key in metadata:
            #
            # For keys that aren't traditionally
            # part of the columns (subject_id, subject_label).
            # Those keys are usually the result of a search where
            # you search for an experiment, but you also ask for the 'subject'
            # columns.
            #    
            if not key in self.columns:
                continue
                
            value = metadata[key]

            #
            # Filtered projects return a lowercase 'id'
            # need to convert this back to uppercase.
            #
            if key == 'id':
                key = 'ID'



            self.columns[key]['value'] = value


                
            if 'location' in self.columns[key]:
                treeNode.setText(self.columns[key]['location'], value)
                treeNode.setFont(self.columns[key]['location'], self.itemFont_folder)
                if key != 'MERGED_LABEL' and key != 'XNAT_LEVEL':
                    #
                    # Combine non-essential columns into MERGED_INFO column
                    #
                    #self.hideColumn(self.columns[key]['location'])
                    col = self.columns['MERGED_INFO']['location']
                    if value and len(value) > 1:
                        treeNode.setText(col, treeNode.text(col) + self.columns[key]['displayname'] + ': ' + value + ' ')
                    treeNode.setFont(col, self.itemFont_folder)                  
                

                    
        #-------------------
        # Set the value for MERGED_LABEL.
        #-------------------   
        #print self.MODULE.utils.lf(), level,  self.getMergedLabelTagByLevel(level), metadata    
        value = metadata[self.getMergedLabelTagByLevel(level)]

        
        
        #-------------------
        # Return out if value is not defined.
        #-------------------
        if not value or value == None or len(value) == 0:
            return

        

        #-------------------
        # Set 'value' key in self.columns and text on qTreeWidgetItem.
        #-------------------
        self.columns['MERGED_LABEL']['value'] = value
        treeNode.setText(self.columns['MERGED_LABEL']['location'], value)


        
        #-------------------
        # Set aesthetics.
        #-------------------
        treeNode.setFont(self.columns['MERGED_LABEL']['location'], self.itemFont_folder) 
        treeNode.setFont(self.columns['XNAT_LEVEL']['location'], self.itemFont_category) 
        self.changeFontColor(treeNode, False, "grey", self.columns['XNAT_LEVEL']['location'])
        if 'Slicer' in metadata['XNAT_LEVEL'] or 'files' in metadata['XNAT_LEVEL']:
            self.changeFontColor(treeNode, False, "green", self.columns['MERGED_LABEL']['location'])

        return treeNode


    
        
    def getColumn(self, metadataKey):
        """ Returns a column location within the qTreeWidget
            based on it's metadata key.
        """
        return self.columns[metadataKey]['location']



    
    def getCurrItemName(self):
        """ Returns the 'MERGED_LABEL' value of the currenly 
            selectedItem
        """
        return self.currentItem().text(self.columns['MERGED_LABEL']['location'])
        


    
    def removeCurrItem(self):
        """ Returns the currentItem
        """
        self.currentItem().parent().removeChild(self.currentItem())

    

    
    def resizeColumns(self):
        """ As stated.  Resizes the columns according to the content
            by calling on the qt.QTreeWidget 'resizeColumnToContents' function.
        """
        for key in self.columns:
            if 'location' in self.columns[key]:
                self.resizeColumnToContents(self.columns[key]['location'])



                
    def showColumnsByNodeLevel(self, levels = None):
        """ Displays the relevant treeView columns based on
            the level of the selected treeItem node.
        """
        
        #----------------------
        # Hide all
        #----------------------
        #for i in range(0, len(self.columns)):
        #    self.hideColumn(i)


            
        #----------------------
        # Keep everything hidden if no level enetered.
        #----------------------
        if levels == None or len(levels) == 0:
            return


        
        #----------------------
        # Internal function: shows column based 
        # on the 'location' key.
        #----------------------
        def showByKeys(keys):
            for key in keys:
                if key in self.columns and 'location' in self.columns[key]:
                    location = self.columns[key]['location']
                    self.showColumn(location)

                    

        #----------------------
        # Show the required row values for 
        # the required columns (MERGED_LABEL, XNAT_LEVEL)
        #----------------------
        showByKeys(self.columnKeyOrder['ALL'])


        # TEMP
        print self.MODULE.utils.lf(), " keeping other columns hidden."
        return
        
        #----------------------
        # Show the row values pertaining specifically
        # to the level of the tree node.
        #----------------------
        for level in levels:
            showByKeys(self.columnKeyOrder[level])

        

        #----------------------
        # Resize columns
        #----------------------
        self.resizeColumns()
            


            
    def loadProjects(self, filters = None, projectContents = None):
        """ Specific method for loading projects.  'Project'-level
            nodes necessiate for special handling in terms of assigning
            parents and filtering.
        """

        #----------------------
        # Add projects only if they are specified 
        # in the arguments.
        #----------------------
        if projectContents:
            #
            # Make tree Items from projects.
            #               
            projectContents['XNAT_LEVEL'] = ['projects' for p in projectContents['id']]
            projectContents['MERGED_LABEL'] = [p for p in projectContents['id']]
            self.makeTreeItems(parentItem = self, 
                               children = projectContents['MERGED_LABEL'], 
                               metadata = projectContents, 
                               expandible = [0] * len(projectContents['MERGED_LABEL']))
            self.showColumnsByNodeLevel(['projects', 'subjects'])
            self.connect("itemExpanded(QTreeWidgetItem *)", self.onTreeItemExpanded)
            #self.connect("itemClicked(QTreeWidgetItem *, int)", self.manageTreeNode)
            self.connect("currentItemChanged(QTreeWidgetItem *, QTreeWidgetItem *)", self.manageTreeNode)


        #----------------------
        # Define filter functions
        #----------------------            
        def filter_accessed():
            self.sortItems(self.columns['last_accessed_497']['location'], 1)
            self.MODULE.treeViewManager.setButtonDown(category = 'sort' , name = 'accessed', isDown = True, callSignals = False)
            def hideEmpty(child):
                accessedText = child.text(self.columns['last_accessed_497']['location'])
                if accessedText == '': 
                    child.setHidden(True)  
            self.loopProjectNodes(hideEmpty)


        def filter_all():
            self.sortItems(self.columns['MERGED_LABEL']['location'], 0)
            def showChild(child):
                child.setHidden(False)
            self.loopProjectNodes(showChild)           

        
            
        #----------------------
        # If no 'filters'...
        #----------------------
        defaultFilterButton = self.MODULE.treeViewManager.buttons['sort']['accessed']
        defaultFilterFunction = filter_accessed
        if not filters or len(filters) == 0:
            #
            # Run the default filter function
            #
            defaultFilterFunction()
            #
            # Count and compare hidden nodes with all nodes
            #
            self.nodeCount = 0
            self.hiddenNodeCount = 0
            def checkEmpty(child):
                if child.isHidden():
                    self.hiddenNodeCount += 1
                self.nodeCount += 1
            self.loopProjectNodes(checkEmpty) 
            #
            # If there are no visible nodes, uncheck the default filter button,
            # so the filter reverts to 'all'.
            #
            if self.nodeCount > 0 and self.nodeCount == self.hiddenNodeCount:
                defaultFilterButton.click()
            return True

        
        
        #----------------------
        # If filter is 'accessed' (i.e. 'Last Accessed')
        #----------------------        
        elif filters[0] == 'accessed':
            filter_accessed()
            return True


        
        #----------------------
        # If filter is 'all'
        #----------------------        
        elif filters[0] == 'all':
            filter_all()
            return True
        return True

    
    

    def loopProjectNodes(self, callback):
        """ Loops through all of the top level
            treeItems (i.e. 'projects') and allows the user
            to run a callback.
        """
        ind = 0
        currChild = self.topLevelItem(ind)
        while currChild:
            callback(currChild)
            ind += 1
            currChild = self.topLevelItem(ind)


            

    def makeRequiredSlicerFolders(self, path = None):  
        """ Puts the required 'Slicer' folders in the reuqired location
            of the current XNAT host.
        """     
        if self.sessionManager.sessionArgs:
            self.MODULE.XnatIo.makeDir(os.path.dirname(self.sessionManager.sessionArgs['saveUri']))




            
    def initClearDialog(self):
        """ Initiates/resets dialog for window to clear 
            the current scene.
        """
        try: 
            self.clearSceneDialog.delete()
        except: pass
        self.clearSceneDialog = qt.QMessageBox()
        self.clearSceneDialog.setStandardButtons(qt.QMessageBox.Yes | qt.QMessageBox.No)
        self.clearSceneDialog.setDefaultButton(qt.QMessageBox.No)
        self.clearSceneDialog.setText("Clear the current scene?")



    
    def constructXnatUri(self, parents = None):
        """ Constructs a directory structure based on the default Xnat 
            organizational scheme, utilizing the tree hierarchy. Critical to 
            communication with Xnat. Ex. parents = [exampleProject, testSubj, 
            testExpt, scan1, images], then returns: 
            'projects/exampleProject/subjects/testSubj/experiments/testExpt/scans/scan1/resources/images'  
        """  
        isResource = False
        isSlicerFile = False
        dirStr = "/"        


        
        #------------------------
        # Make the parents if they're not
        # provided.
        #------------------------
        if not parents:
            parents = self.getParents(self.currentItem())


            
        #------------------------
        # Construct preliminary URI based on the 'parents' array.
        #------------------------
        XnatDepth = 0        
        for item in parents: 
            #         
            # For resource folders
            #
            if 'resources' in item.text(self.columns['XNAT_LEVEL']['location']).strip(" "): 
                isResource = True    
            #
            # For masked slicer folders
            #
            elif ((self.MODULE.utils.slicerFolderName in item.text(self.columns['XNAT_LEVEL']['location'])) 
                  and self.applySlicerFolderMask): 
                isSlicerFile = True
            #
            # Construct directory string
            #
            dirStr += "%s/%s/"%(item.text(self.columns['XNAT_LEVEL']['location']).strip(" "), 
                                item.text(self.columns['MERGED_LABEL']['location']))
            XnatDepth+=1


            
        #------------------------
        # Modify if URI has 'resources' in it.
        #------------------------
        if isResource:    
            #     
            # Append "files" if resources folder 
            #         
            if 'resources' in parents[-1].text(self.columns['XNAT_LEVEL']['location']).strip(" "):
                dirStr += "files" 
            #
            # Cleanup if at files level 
            #           
            elif 'files'  in parents[-1].text(self.columns['XNAT_LEVEL']['location']).strip(" "):
                dirStr = dirStr[:-1]  
            #
            # If on a files      
            #    
            else:
                dirStr =  "%s/files/%s"%(os.path.dirname(dirStr), 
                                         os.path.basename(dirStr))  

                
        #------------------------
        # Modify URI for Slicer files.
        #------------------------
        if isSlicerFile:
            #print self.MODULE.utils.lf() + "IS SLICER FILE!" 
            self.currLoadable = "scene"
            dirStr = ("%s/resources/%s/files/%s"%(os.path.dirname(os.path.dirname(os.path.dirname(dirStr))),
                                                  self.MODULE.utils.slicerFolderName,
                                                  os.path.basename(os.path.dirname(dirStr))))   

            
        #------------------------
        # For all other URIs.
        #------------------------
        else:
            if XnatDepth < 4: 
                dirStr += self.MODULE.utils.xnatDepthDict[XnatDepth] 
        return dirStr



    
    def getParents(self, item):
        """ Returns the parents of a specific treeNode 
            all the way to the "project" level
        """
        parents = []
        while(item):
          parents.insert(0, item)
          item = item.parent()
        return parents




    
    def determineExpanded(self, item):
        """Determines if the current treeItem is expanded.
        """      
        if item.childIndicatorPolicy() == 0:
            self.getChildren(item, expanded = True) 



            
    def onTreeItemExpanded(self, item):
        """ When the user interacts with the treeView, 
            this is a hook method that gets the branches 
            of a treeItem and expands them.
        """ 
        self.manageTreeNode(item, 0)
        self.setCurrentItem(item)
        self.currItem = item
        if not 'files' in item.text(self.columns['XNAT_LEVEL']['location']):
            self.getChildren(item, expanded = True) 
        self.resizeColumns()


            
            
    def getChildrenNotExpanded(self, item):
        """ When the user interacts with the treeView, this 
            is a hook method that gets the branches of a treeItem 
            and does not expand them 
        """ 
        self.manageTreeNode(item, 0)
        self.setCurrentItem(item)
        self.currItem = item
        if not 'files' in item.text(self.columns['XNAT_LEVEL']['location']):
            self.getChildren(item, expanded = False)



            
    def manageTreeNode(self, item, col):
        """ Broad-scoped function. Conducts the necessary filtering, 
            column visibility, buttonEnabling, nodeMasking and 'loadable' 
            analysis. 
            
            NOTE: Consider refactoring into specific methods.
        """
        if item==None:
            item = self.currItem
        else:
            self.currItem = item

            
        self.setCurrentItem(item)
        self.currLoadable = None

        

        #------------------------
        # Check if at saveable/loadable level 
        #------------------------
        isProject = 'project' in item.text(self.columns['XNAT_LEVEL']['location']).strip(" ")
        isSubject = 'subjects' in item.text(self.columns['XNAT_LEVEL']['location']).strip(" ")
        isResource = 'resources' in item.text(self.columns['XNAT_LEVEL']['location']).strip(" ")
        isExperiment = 'experiments' in item.text(self.columns['XNAT_LEVEL']['location']).strip(" ")
        isScan = 'scans' in item.text(self.columns['XNAT_LEVEL']['location']).strip(" ")
        isFile = 'files' in item.text(self.columns['XNAT_LEVEL']['location']).strip(" ")
        isSlicerFile = self.MODULE.utils.slicerFolderName.replace("/","") in item.text(self.columns['XNAT_LEVEL']['location']).strip(" ")

        

        #-------------------------
        # Show columns
        #-------------------------
        if isProject:
            self.showColumnsByNodeLevel(['projects', 'subjects'])
                
        elif isSubject:
            self.showColumnsByNodeLevel(['subjects', 'experiments'])
                
        elif isExperiment:
            self.showColumnsByNodeLevel(['experiments', 'scans', 'files'])

        elif isScan or isFile or isSlicerFile:
            self.showColumnsByNodeLevel(['scans', 'files'])


            
        #------------------------
        # Enable load/save at the default save level
        #------------------------
        self.MODULE.XnatButtons.setEnabled('save', False)
        self.MODULE.XnatButtons.setEnabled('load', False)
        self.MODULE.XnatButtons.setEnabled('delete', False)
        self.MODULE.XnatButtons.setEnabled('addProj', True)
        if isExperiment or isScan:
            self.MODULE.XnatButtons.setEnabled('save', True)
            self.MODULE.XnatButtons.setEnabled('load', True)
        elif isFile or isSlicerFile or isResource:
            self.MODULE.XnatButtons.setEnabled('save', True)
            self.MODULE.XnatButtons.setEnabled('load', True)
            self.MODULE.XnatButtons.setEnabled('delete', True)


            
        #------------------------
        # If mask is enabled, determine if item is a slicer file
        #------------------------
        if self.applySlicerFolderMask:
            if item.text(self.columns['XNAT_LEVEL']['location']) == self.MODULE.utils.slicerFolderName:
                isFile = True    


                
        #------------------------
        # Determine how to load the file by applying a 
        # type to the node.  This sets the self.currLoadable variable.
        #------------------------
        if isFile or isSlicerFile:
            ext = item.text(self.columns['MERGED_LABEL']['location']).rsplit(".")
            #
            # Check extension
            #
            if (len(ext)>1):
                #
                # Recognizable extensions  
                #      
                if self.MODULE.utils.isRecognizedFileExt(ext[1]):
                    #
                    # Scene package
                    #
                    for ext_ in self.MODULE.utils.packageExtensions:
                        if ext_.replace(".","") in ext[1]: 
                            #
                            # Set currloadable to scene   
                            #                     
                            self.currLoadable = "scene"
                    #
                    # Generic file
                    #
                    else:
                        self.currLoadable = "file"
 


                    
        #------------------------
        # If the user is at the default load/save level, 
        # set default loader to DICOM.     
        #------------------------
        if self.MODULE.utils.defaultXnatSaveLevel in item.text(self.columns['XNAT_LEVEL']['location']).strip(" "):
            self.currLoadable = "mass_dicom" 



        #------------------------
        # Resize columns.
        #------------------------
        self.resizeColumns()

        
        #------------------------
        # Selectively pull the relevant columns, based on
        # the node level to construct the dictionary that
        # feeds the 'Details' GroupBox.
        #------------------------
        columnTags = self.MODULE.utils.getMetadataTagsByXnatLevel(item.text(self.columns['XNAT_LEVEL']['location']).strip(" "))
        detailsDict = {}
        for tag in columnTags:
            if 'location' in self.columns[tag]:
                detailsDict[tag] = item.text(self.columns[tag]['location']).strip(' ')
        #
        # Run the callbacks that feeds the dictionary
        # into the Details GroupBox.
        #    
        self.runNodeChangedCallbacks(detailsDict)

        

        
    def getXnatUriObject(self, item):    
        """ Helper function that constructs a number of useful
            key-value pairs related to a given qTreeItem, for 
            communicating with XNAT and the qTreeWidget.
        """
        pathObj = {}
        pathObj['pathDict'] = {
            'projects' : None,
            'subjects' : None,
            'experiments' : None,
            'scans' : None,
            'Slicer' : None
        }


        
        #-------------------------
        # Construct various URIs (current, and children)
        # based on the locaiton of the treeNode.
        #-------------------------
        pathObj['parents'] = self.getParents(item)
        xnatDir = self.constructXnatUri(pathObj['parents'])
        pathObj['childQueryUris'] = [xnatDir if not '/scans/' in xnatDir else xnatDir + "files"]
        pathObj['currUri'] = os.path.dirname(pathObj['childQueryUris'][0])  
        pathObj['currLevel'] = xnatDir.split('/')[-1] if not '/scans/' in xnatDir else 'files'


        
        #------------------------
        # Construct URI dictionary by splitting the currUri from slashes.
        #------------------------
        splitter = [ s for s in pathObj['currUri'].split("/") if len(s) > 0 ]
        for i in range(0, len(splitter)):
            key = splitter[i]
            if key in pathObj['pathDict'] and i < len(splitter) - 1:
                pathObj['pathDict'][key] = splitter[i+1]

            

        #-------------------------
        # Construct child Xnat level.
        #-------------------------          
        pathObj['childXnatLevel'] = os.path.basename(pathObj['childQueryUris'][0])

        
        
        #-----------------------------
        # Specific key-value pairs for Slicer files...
        #-------------------------------
        if pathObj['childQueryUris'][0].endswith('/scans'):
            pathObj['slicerQueryUris'] = []
            pathObj['slicerQueryUris'].append(pathObj['currUri'] + '/resources/Slicer/files')
            pathObj['slicerMetadataTag'] = 'Name'



        return pathObj


        
            
    def isDICOMFolder(self, item):  
        """ Probes the children of a tree item to determine if the folder
            is a DICOM folder.
        """     
        dicomCount = 0
        for x in range(0, item.childCount()):          
            try:
                child = item.child(x)
                ext = child.text(self.columns['MERGED_LABEL']['location']).rsplit(".")[1]            
                if self.MODULE.utils.isDICOM(ext):
                    dicomCount +=1
            except Exception, e:
                pass        
        if dicomCount == item.childCount():
                return True
        return False



    
    def setCurrItemToChild(self, item = None, childFileName = None):
        """ Scans the children a given tree item for those that have 
            'childFileName' and sets the selected qTreeViewWidget item
            to that child.  Does nothing if a child with 'childFileName' 
            is not found.
        """
        #----------------------
        # Set self.currItem to the item provided in the 
        # argument.
        #----------------------
        if not item:
            item = self.currItem    

        #----------------------
        # Expand self.currItem
        #----------------------
        self.onTreeItemExpanded(item)


        #----------------------
        # Search children only if 'childFileName' is not None.
        #----------------------
        if childFileName:
            for x in range(0, item.childCount()):
                child = item.child(x)
                if child.text(self.columns['MERGED_LABEL']['location']) == childFileName:
                    self.setCurrentItem(child)
                    self.currItem = child;
                    return   



                
    def changeFontColor(self, item, bold = True, color = "black", column = 0):
        """ As stated.
        """
        b = qt.QBrush()
        c = qt.QColor(color)
        b.setColor(c)
        item.setForeground(column, b)



        
    def startNewSession(self, sessionArgs, method="currItem"):
        """ Starts a new session based on XNAT interaction.  
        """
        if method=="currItem":            
            
            # Sometimes we have to reset the curr item
            if not self.currentItem(): 
                self.setCurrentItem(self.currItem)
                
            # Derive parameters based on currItem
            self.sessionManager.startNewSession(sessionArgs)




            
    def findChild(self, item, childName, expanded=True):
        """ Loops through the children of a given node
            to see if there is a string match for the childName
            argument based on the 'MERGED_LABEL' column.
        """
        for i in range(0, item.childCount()):
            if str(childName) in item.child(i).text(self.columns['MERGED_LABEL']['location']):
                if expanded:
                    self.onTreeItemExpanded(item.child(i))
                return item.child(i)



            
    def selectItem_byUri(self, pathStr):
        """  Selects a qTreeWidgetItem based on the URI.  Breaks
             down the URI and traverses the tree for th relevant strings.
        """
             
        #------------------------
        # Break apart pathStr to its Xnat categories
        #------------------------
        pathDict = self.MODULE.utils.makeXnatUriDictionary(pathStr)


        
        #------------------------
        # Reload projects if it can't find the project initially
        #------------------------
        if not self.findItems(pathDict['projects'],1): 
            self.loadProjects()


            
        #------------------------
        # Start by setting the current item at the project level, get its children
        #------------------------
        self.setCurrentItem(self.findItems(pathDict['projects'],1)[0])
        self.onTreeItemExpanded(self.currentItem())


        
        #------------------------
        # Proceed accordingly to its lower levels
        #------------------------
        if (pathDict['subjects']):
            self.setCurrentItem(self.findChild(self.currentItem(), pathDict['subjects']))
            if (pathDict['experiments']):
                self.setCurrentItem(self.findChild(self.currentItem(), pathDict['experiments']))
                if (pathDict['scans']):
                    self.setCurrentItem(self.findChild(self.currentItem(), pathDict['scans']))
        if (pathDict['resources']):
            self.setCurrentItem(self.findChild(self.currentItem(), pathDict['resources']))
            if (pathDict['files']):
                self.setCurrentItem(self.findChild(self.currentItem(), pathDict['files']))





    
        
    def getChildren(self, item, expanded, setCurrItem = True):
        """ Gets the branches of a particular treeItem 
            via an XnatIo.   
        """       

        #--------------------
        # Selected Item management
        #--------------------  
        if not item: return
        if setCurrItem: self.currItem = item
        self.setCurrentItem(item)              


        
        #--------------------
        # Remove existing children for reload
        #--------------------
        item.takeChildren()

        
            
        #--------------------
        # Get path 
        #--------------------           
        pathObj = self.getXnatUriObject(item)
        currXnatLevel = pathObj['currLevel']

        
            
        #--------------------
        # SPECIAL CASE: this filters out image
        # folders with no images in them.
        #-------------------- 
        queryArguments = None
        if currXnatLevel == 'experiments':
            queryArguments = ['imagesonly']


                
        #--------------------
        # Get folder contents via metadata.  
        # Set nodeNames from metadata.
        #-------------------- 
        metadata = self.MODULE.XnatIo.getFolderContents(pathObj['childQueryUris'], self.MODULE.utils.XnatMetadataTagsByLevel(currXnatLevel), queryArguments)



        #--------------------
        # Return out of the childkeys dont exist.
        # (Means that there are no children to the 
        # node).
        #--------------------        
        xnatLabel = self.getMergedLabelTagByLevel(currXnatLevel)
        if not xnatLabel in metadata:
            print "NO XNAT LABEL"
            return


        
        #--------------------
        # Set the child names based on the level, metadata key
        #--------------------
        childNames = metadata[xnatLabel]

        
        
        #--------------------
        # Set the categories of the children.
        #--------------------
        metadata['XNAT_LEVEL'] = [pathObj['childXnatLevel'] for x in range(len(childNames))]


        
        #--------------------
        # Special case for children with Slicer URIs
        #--------------------
        if 'slicerQueryUris' in pathObj:
            slicerMetadata = self.MODULE.XnatIo.getFolderContents(pathObj['slicerQueryUris'], self.MODULE.utils.XnatMetadataTagsByLevel('files'))
            #
            # Proceed only if the relevant metadata to retrieve Slicer
            # files exists 
            #
            if self.getMergedLabelTagByLevel('files') in slicerMetadata:
                slicerChildNames = slicerMetadata[self.getMergedLabelTagByLevel('files')]
                prevLen = len(childNames)
                childNames = childNames + slicerChildNames 
                #
                # Merge slicerMetadata with metadata
                #
                for key in slicerMetadata:
                    if not key in metadata:
                        #
                        # Set empty strings for keys that aren't shared.  For instance, Scans do not
                        # share the 'Name' key, even though they are displayed at the same
                        # depth in the tree hierarchy.
                        #
                        metadata[key] = [''] * prevLen
                        metadata[key] += slicerMetadata[key]

                        if (key == 'Size'):
                            for i in range(0, len(metadata[key])):
                                if metadata[key][i]:
                                    metadata[key][i] = '%i MB'%(int(round(self.MODULE.utils.bytesToMB(metadata[key][i]))))
                metadata['XNAT_LEVEL'] = metadata['XNAT_LEVEL'] + ['Slicer' for x in range(len(slicerChildNames))]  
                

            
        #--------------------
        # Determine expandibility of the child node.
        #--------------------    
        expandible = []
        for i in range(0, len(metadata['XNAT_LEVEL'])):
            level = metadata['XNAT_LEVEL'][i]
            #
            # 'files' and 'Slicer' category are
            # immediately ruled as unexpandable (1).
            #
            if (level == 'files' or level == 'Slicer') :
                expandible.append(1)
            else:
                expandible.append(0)


                
        #--------------------
        # Make the treeItems
        #-------------------- 
        self.makeTreeItems(parentItem = item, children = childNames, metadata = metadata, expandible = expandible)
        item.setExpanded(True)
        self.setCurrentItem(item) 
            

        
            
    def condenseDicomsToOneName(self, names):
        """ Takes a list of DICOM files and condenses 
            them into one name.

            NOTE: Consider moving this to XnatUtils.py.
        """
        returnName = names[0]
        stopIndex = len(returnName) - 1

        
        for i in range(1, len(names)):
            #
            # Cycle through characters in name.
            #
            for j in range(0, len(names[i])):
                #print (j, names[i], returnName, len(names[i]), len(returnName))
                if j > len(returnName) - 1:
                    break
                elif j == len(returnName) - 1 or returnName[j] != names[i][j]:
                    stopIndex = j

        return [returnName[0:stopIndex] + "..."]


    
    
    def makeTreeItems(self, parentItem, children = [],  metadata = {}, expandible = None):
        """Creates a set of items to be put into the 
           QTreeWidget based upon its parents, its children 
           and the metadata provide.
        """
        #print self.MODULE.utils.lf(), "MAKE TREE ITEMS", metadata, 
        #print self.MODULE.utils.lf(), children
        #----------------
        # Do nothing if no children.
        #----------------
        if len(children) == 0: return


        
        #----------------
        # Convert string children to arrays
        #----------------       
        if isinstance(children, basestring):
            children = [children]


            
        #----------------
        # convert string expandible to array
        #----------------
        if isinstance(expandible, int):
            expandible = [expandible]

            
            
        #----------------
        # Get the DICOM count if at 'scans' level
        #----------------
        
        if (metadata['XNAT_LEVEL'][0] == 'files'):
            pathObj = self.getXnatUriObject(parentItem.parent())
            parentXnatLevel = pathObj['currLevel']
            if parentXnatLevel == 'scans':
                if self.isDICOMFolder(parentItem):                
                    children = self.condenseDicomsToOneName(children)
                    
        
        
        #------------------------
        # Add children to parentItem
        #------------------------
        treeItems = []
        for i in range(0, len(children)):
            #print "\n\nCHILDREN: ", children[i]

            
            treeNode = qt.QTreeWidgetItem(parentItem)
            #
            # Set expanded (0 = expandable, 1 = not)
            #
            expandPolicy = 0
            if metadata['XNAT_LEVEL'][i] == 'files' or metadata['XNAT_LEVEL'][i] == 'Slicer':
                expandPolicy = 1
            treeNode.setChildIndicatorPolicy(expandPolicy)   
            #
            # Set other metadata
            #
            treeNodeMetadata = {}
            for key in metadata:
                #print '\n\n', key, i, len(metadata[key]), metadata, len(children), children
                if i < len(metadata[key]):
                    treeNodeMetadata[key] = metadata[key][i]
                    #print "TREE NODE METADATA", treeNodeMetadata

            treeNode = self.setValuesToTreeNode(treeNode, treeNodeMetadata)
            #
            # Add the items array
            #
            if treeNode:
                treeItems.append(treeNode) 


                
        #------------------------    
        # SPECIAL CASE: If at project level, set parents accordingly.
        #------------------------
        if str(parentItem.__class__) == "<class 'XnatTreeView.XnatTreeView'>":
            parentItem.addTopLevelItems(treeItems)
            return
        

        
        #------------------------    
        # Items array gets added to parentItem.
        #------------------------
        parentItem.addChildren(treeItems)





            
        
    def searchEntered(self):
        """
            Qt::MatchExactly	0	Performs QVariant-based matching.
            Qt::MatchFixedString	8	Performs string-based matching. String-based comparisons are case-insensitive unless the MatchCaseSensitive flag is also specified.
            Qt::MatchContains	1	The search term is contained in the item.
            Qt::MatchStartsWith	2	The search term matches the start of the item.
            Qt::MatchEndsWith	3	The search term matches the end of the item.
            Qt::MatchCaseSensitive	16	The search is case sensitive.
            Qt::MatchRegExp	4	Performs string-based matching using a regular expression as the search term.
            Qt::MatchWildcard	5	Performs string-based matching using a string with wildcards as the search term.
            Qt::MatchWrap	32	Perform a search that wraps around, so that when the search reaches the last item in the model, it 
                                begins again at the first item and continues until all items have been examined.
            Qt::MatchRecursive	64	Searches the entire hierarchy.
        """

        print self.MODULE.utils.lf(), "Disconnecting item expanded."
        self.disconnect("itemExpanded(QTreeWidgetItem *)", self.onTreeItemExpanded)
        #SEARCH_TIMER = XnatTimer(self.MODULE)


        
        #------------------------
        # Deslect any selected items.
        #------------------------  
        for selectedItem in self.selectedItems():
            selectedItem.setSelected(False)


            
        #------------------------
        # Get searchString from MODULE.  Remove starting 
        # and ending white spaces via '.strip()'
        #------------------------
        searchString = self.MODULE.XnatSearchBar.getText()


        
        #------------------------
        # Return out if searchString is all
        # white spaces. 
        # NOTE: .strip() is called on it above.
        #------------------------
        if len(searchString) == 0:
            return


        
        #------------------------
        # Set all visible if searchString == ''
        # and return out.
        #------------------------
        if len(searchString) == 0:
            def showAll(child):
                child.setHidden(False)
            self.loopProjectNodes(showAll)  
            return          
            
        
        
        #------------------------
        # Search existing tree items
        #------------------------
        #SEARCH_TIMER.start("Search existing", "search exist")
        self.searchTreeItems = self.searchAndShowExisting(searchString)
        #SEARCH_TIMER.stop()


        
        
        #------------------------
        # First pass: Hide all items that don't
        # fit the search criteria.
        #------------------------
        def hideEqual(child):
            if child in self.searchTreeItems:
                child.setHidden(False)
            else:
                child.setHidden(True)
        self.loopProjectNodes(hideEqual)

        

        #------------------------
        # Second pass: Re-show any ancestor nodes of the 
        # search nodes.
        #------------------------
        #SEARCH_TIMER.start("Reshow ancestors")
        for searchTreeItem in self.searchTreeItems:
            #
            # Get parent
            #
            parent = searchTreeItem.parent()
            while parent:
                #
                # Show parent
                #
                parent.setHidden(False)
                #
                # Expand the ancestor
                #
                parent.setExpanded(True)
                parent = parent.parent()

                #SEARCH_TIMER.stop()
                





        #**************************************************************
        #
        #              CONDUCT SEARCH ON SERVER
        #
        #**************************************************************


        
        #------------------------
        # Run the search method in the
        # XnatIo.
        #------------------------
        #SEARCH_TIMER.start("Server search")
        serverQueryResults = self.MODULE.XnatIo.search(searchString)
        #SEARCH_TIMER.stop()

        

        #------------------------
        # Establish searchable levels: 
        # projects, subjects and experiments
        #------------------------
        levels = ['projects', 'subjects', 'experiments']



        #------------------------
        # Cycle through search query results by level
        #------------------------       
        for level in levels:
            for serverQueryResult in serverQueryResults[level]:

                
                #-------------------
                # Create the item in the tree (i.e. the 
                # user hasn't browsed there yet).  This node will never
                # be a project, because projects that have met the search
                # criteria are shown above.
                #-------------------
                if level != 'projects':
                    
                    #
                    # Get the 'project' of the node and make sure it's visible.
                    # The project folder of every subject and experiment are
                    # provided in the metadata json from REST get calls.
                    #
                    #SEARCH_TIMER.start("Getting projects after server query.")
                    project = self.findItems(serverQueryResult['project'], 1 , self.columns['ID']['location'])[0]
                    #
                    # Show the ancestor 'project'.
                    #
                    project.setHidden(False)
                    #
                    # Expand the ancestor 'project' (events are disabled, so
                    # there's no querying happening).
                    #
                    project.setExpanded(True)
                    #SEARCH_TIMER.stop()
                    
                    #
                    # Get MERGED_LABEL tag.
                    # 
                    mergedLabel = self.getMergedLabelTagByLevel(level)
                    
                    #
                    # Construct metadata dictionary.
                    #
                    metadata = {}
                    for key in serverQueryResult:
                        metadata[key] = [serverQueryResult[key]]  

                        
                    #
                    # Construct the custom/merged columns.
                    #
                    metadata['XNAT_LEVEL'] = [level]
                    metadata['MERGED_LABEL'] = [serverQueryResult[mergedLabel]]
                    metadata['MERGED_INFO'] = [mergedLabel]


                    
                    #--------------------
                    # Make 'subject' items that match the search 
                    # criteria. 
                    #--------------------
                    if level == 'subjects':
                        #
                        # Make the child items of the project, which will be the subject
                        # nodes.
                        #
                        self.makeTreeItems(parentItem = project, children = serverQueryResult[mergedLabel], metadata = metadata, expandible = [0])
                        #
                        # Find the child nodes in the tree.
                        #
                        project.setExpanded(True)


                        
                    #--------------------
                    # Make 'experiment' items that match the search 
                    # criteria. 
                    #--------------------
                    elif level == 'experiments':
                        
                        #
                        # Construct necessary metadata dictionary
                        # for the parent 'subject'.
                        #
                        experimentName = metadata['MERGED_LABEL']
                        subjectLabel = metadata['subject_label']
                        subjectMetadata = {}
                        subjectMetadata['XNAT_LEVEL'] = ['subjects']
                        subjectMetadata['MERGED_LABEL'] = subjectLabel
                        subjectMetadata['MERGED_INFO'] = ['Info']
                        subjectMetadata['ID'] = metadata['subject_ID']
                        subjectMetadata['label'] = subjectLabel
                        
                        #
                        # Check if the 'subject' is already a child
                        # of the 'project'.  This happens as a result of the 'makeTreeItems'
                        # line below being called, and subsequent experiments being created.
                        #
                        subject = self.findItems(serverQueryResult['subject_ID'], 1 | 64 , self.columns['ID']['location'])
                        if len(subject) > 0:
                            subject = subject[0]
                            
                        #
                        # If the parent 'subject' doesn't exist, make the parent
                        # 'subject' a child of the 'project'.
                        #
                        if not subject:
                            self.makeTreeItems(parentItem = project, children = [subjectLabel], metadata = subjectMetadata, expandible = [0])
                            subject = self.findItems(serverQueryResult['subject_label'], 1 | 64 , self.columns['MERGED_LABEL']['location'])[0]
                            subject.setHidden(False)
                            
                        #
                        # Make 'experiment' as child of parent 'subject'.
                        #
                        self.makeTreeItems(parentItem = subject, children = experimentName, metadata = metadata, expandible = [0]) 
                        
                        #
                        # Expand the parent 'subject'.
                        # 
                        subject.setExpanded(True)   
                        

        #
        # Highlight all nodes that meet the search
        # criteria.
        #
        self.searchAndShowExisting(searchString)
        #
        # Reconnect the event listeners for expandning
        # the QTreeWidgetItems.
        #
        print self.MODULE.utils.lf(), "Re-connecting item expanded."
        self.connect("itemExpanded(QTreeWidgetItem *)", self.onTreeItemExpanded)
        self.resizeColumns()

    
        

    def searchAndShowExisting(self, searchString):
        """ Searches through all columns using 'Qt::MatchContains'
            for a match.  Highlights and selects treeItems that
            match.
        """
        
        #--------------------
        # Allow for multi-node selection
        #--------------------
        self.setSelectionMode(2)


        
        #--------------------
        # Get the items that match the string
        # by looking through every column and
        # every node. columns * O(n) at least.
        #--------------------
        items = []
        for columnNumber in range(0, self.columnCount):
            results = self.findItems(searchString, 1 | 64 , columnNumber)
            if results:
                #
                # 'results' is returned as a tuple, so
                # we cannot simply add the array.
                #
                for result in results:
                    items.append(result)



        #--------------------
        # If the items are found
        #--------------------
        if len(items) > 0:
            for item in items:
                #
                # Select the item.
                #
                item.setSelected(True)
                #
                # Make the tree node bold.
                #                     
                item.setFont(0, self.itemFont_searchHighlighted)
                #
                # If the node his hidden...
                #
                if item.isHidden():
                    #
                    # Show the item
                    #
                    item.setHidden(False)

                #
                # Show the parents if it's not a 'project'
                #
                parent = item.parent()
                while parent:
                    parent.setHidden(False)
                    parent.setExpanded(True)
                    parent = parent.parent()

                        
        self.resizeColumns()
        return items
        
