"""
Quick History Selection UI for Maya (ver 0.1)
Scripting Language: PYTHON
Development Environment: Maya 2011 x64

Author: Andrew Glisinski
First Release: Feb 5 2016

Updates:
February 5 2016 - Initial Release (0.1)

-------------------
Q: What does this do?
    Quick History Selection opens up a window that can temporarily hold selection sets 
    (not the built-in Maya sets) that you can easily toggle between.

Q: Why not just use regular quick selection sets?
    Primarily because sometimes you just want to save a selection 
    of something (ie. vertices) for a short period of time.
    Saving out as sets seems a little unnecessary, and this is 
    just a quick and dirty approach with some key features that
    relay a little more information at glance than selection sets.
    
Q: What versions of Maya support this?
    Hopefully all of them? I developed this and tested it 
    in Maya 2011 (yeah, it's an old copy!) I don't provide any sort of
    assistance or guarantees with this script beyond claiming it will 
    work. Don't use it in a commercial environment until it's fully
    tested to do what you expect. No modifications to the scene are 
    made unless it's the 'globalSelectionDictionary' dictionary object
    that we instantiate before running the script
-------------------

Usage: 
- Include agMayaQuickSelect.py in scripts folder
- in maya's python script editor run:

    # this can be named anything you want, just make sure to pass it in to the selectHistoryUI next
    globalSelectionDictionary = {}  
   
    # if you want to make a shelf button, just drag the following lines to the shelf
    import agMayaQuickSelect as qsh
    reload(qsh) # just in case
    qsh.selectHistoryUI(globalSelectionDictionary)
   
------------------
Further Notes:

- Since 'globalSelectionDictionary' is a dictionary being instantiated in Maya's local space, it should stick around between closing/opening
  the UI window. Since this is not saved in any way after the program exits, all that data will be lost. Maybe in the future I'll
  add an option for JSON or something.
  
- Don't re-instantiate the dictionary unless you wish for all your selection data to be deleted! 

"""
import maya.cmds as cmds

def selectHistoryUI(mainSelDict):
    windowWidth = 300
    windowHeight = 350
    horizontalSpacing = int(windowHeight * 0.01)
    verticalSpacing = int(windowWidth * 0.02)
    
    if cmds.window("selectHistory", q=1, exists=True):
        cmds.deleteUI("selectHistory")
    
    selectHistoryWindow = cmds.window("selectHistory", title = "Selection History",
                                      w=windowWidth, h=windowHeight,
                                      mnb=True, mxb=False, sizeable=False)
    #layout
    mainLayout = cmds.columnLayout("selhisLayout", rowSpacing=horizontalSpacing, w=windowWidth, h=windowHeight)
    
    cmds.text(label="Selection History Recorded: ", parent=mainLayout, width=windowWidth, align="center")
    
    cmds.textScrollList("selectHistoryList", 
                        deleteKeyCommand=lambda *args: selectHistoryCommand(mainSelDict, command="remove"), 
                        doubleClickCommand= lambda *args: selectHistoryCommand(mainSelDict, command="select"),
                        annotation="Tip: 'Double-click' to Select or 'Delete' key to Remove Selected Entry ", 
                        width=windowWidth, 
                        numberOfRows=8, 
                        parent=mainLayout)
    
    if len( mainSelDict.keys() ) > 0:
        for key in mainSelDict.keys():
            cmds.textScrollList("selectHistoryList", e=1, append=key)
    
    cmds.text(label="Modify Current Selection in Scene: ", parent=mainLayout, width=windowWidth, align="center")
    cmds.radioButtonGrp("selectType", width=windowWidth, labelArray3=['Single', 'Add', 'Remove'], select=1, numberOfRadioButtons=3 )
    cmds.button("SelectButton", label="Select", 
                backgroundColor=[0.37993082404136658, 0.60194522142410278, 0.71764707565307617], 
                width=windowWidth, 
                c= lambda *args: selectHistoryCommand(mainSelDict, command="select"), 
                parent = mainLayout)
    
    cmds.separator(parent=mainLayout)
    
    cmds.text(label="Nickname (Alias) for Selection: ", parent=mainLayout, width=windowWidth, align="center")
    reqName = cmds.textField("selNickname", width=windowWidth, 
                             annotation="Tip: Keypad 'Enter' key to add entry", 
                             enterCommand=lambda *args: selectHistoryCommand(mainSelDict, command="add"), 
                             parent=mainLayout)
    
    cmds.button("AddSelection", label="Add Selection", 
                backgroundColor=[0.46045002341270447, 0.81176471710205078, 0.41065746545791626], 
                width=windowWidth, 
                c= lambda *args: selectHistoryCommand(mainSelDict, command="add"), 
                parent = mainLayout)
    
    cmds.showWindow(selectHistoryWindow)

def selectHistoryCommand(mainSelDict, command="add"):
    
    if command == "add":
        nickname = cmds.textField("selNickname", text=1, q=1)
        selection = cmds.ls(sl=1, fl=1)
        if nickname == "":
            nickname = "[{0} : {1}]".format(selection[0], selection[-1])
        else:
            nickname += " [{0} : {1}]".format(selection[0], selection[-1])
        
        cmds.textScrollList("selectHistoryList", e=1, append=nickname)

        mainSelDict[nickname] = selection
        
    elif command == "remove":
        indexToRemove = cmds.textScrollList("selectHistoryList", q=1, selectIndexedItem=1)
        nameToRemove = cmds.textScrollList("selectHistoryList", q=1, selectItem=1)[0]
        cmds.textScrollList("selectHistoryList", e=1, removeIndexedItem=indexToRemove)
        
        del mainSelDict[nameToRemove]
        
    elif command == "select":
        if cmds.textScrollList("selectHistoryList", q=1, selectItem=True) == None:
            cmds.error("No Nicknames Selected.")
        
        enumSelect = cmds.radioButtonGrp("selectType", q=1, select=1)
        
        if   enumSelect <= 1:
             addV = 0
             remV = 0
        elif enumSelect == 2:
             addV = 1
             remV = 0
        elif enumSelect == 3:
             addV = 0
             remV = 1
        
        indexSelected = cmds.textScrollList("selectHistoryList", q=1, selectIndexedItem=True)[0]
        itemSelected = cmds.textScrollList("selectHistoryList", q=1, selectItem=1)[0]
        cmds.select( mainSelDict[itemSelected], add=addV, deselect= remV)
