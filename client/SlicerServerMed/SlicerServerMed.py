#======================================================================================
#  A simple 3D Slicer plugin template for remote processing                           # 
#          Automatic Spine Landmarks Detection                                        #
#                                                                                     #
#  Contributers: Ibraheem Al-Dhamari,  ia@idhamari                                    #
#                                                                                     #
#-------------------------------------------------------------------------------------#
#  Slicer 5.6                                                                         #    
#  Updated: 30.6.2024                                                                 #    
#=====================================================================================#
# TODOs:
#  - Support multiple users
#    - create a folder for each user in the server
#  - Add option to handle the type of volume e.g. (Scalar, Label, Segmentation, Model)
#  - Add option to add a folder then process the files at once e.g
#     - Loop through the files, send, process, save the result
#  - Add cleaning and removing temp files 
#  - Add progress bar

import os, re , datetime, time ,shutil, unittest, logging, zipfile, urllib.request,urllib.parse, stat,  inspect
from pathlib import Path
from urllib.error import URLError, HTTPError

import sitkUtils, sys ,math, platform, subprocess  
import numpy as np, SimpleITK as sitk
import vtkSegmentationCorePython as vtkSegmentationCore
from __main__ import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *   
from copy import deepcopy
from collections import defaultdict
from os.path import expanduser
from os.path import isfile
from os.path import basename
from PythonQt import BoolResult
from shutil import copyfile
from decimal import *
from multiprocessing.dummy import Pool as ThreadPool
from multiprocessing.dummy import Process  
import SampleData


#===================================================================
#                           Main Class
#===================================================================

class SlicerServerMed(ScriptedLoadableModule):
  def __init__(self, parent):
        ScriptedLoadableModule.__init__(self, parent)
        parent.title = "ServerMed"
        parent.categories = ["SEAI"]
        parent.dependencies = []
        parent.contributors = ["Ibraheem Al-Dhamari" ]
        self.parent.helpText += self.getDefaultModuleDocumentationLink()
        #TODO: add sponsor
        parent.acknowledgementText = " This work is sponsored by ................ "
        self.parent = parent
    
#===================================================================
#                           Main Widget
#===================================================================
class SlicerServerMedWidget(ScriptedLoadableModuleWidget):
  def setup(self):
    print("=======================================================")   
    print("   RGSE Slicer ServerMed                               ")
    print("=======================================================")           
        
    ScriptedLoadableModuleWidget.setup(self)
    
    # to access logic class functions and setup global variables
    self.logic = SlicerServerMedLogic()
    #------------------------------------------------------------
    #                     Create the GUI interface
    #------------------------------------------------------------
    # Create main collapsible Button 
    self.mainCollapsibleBtn = ctk.ctkCollapsibleButton()
    self.mainCollapsibleBtn.setStyleSheet("ctkCollapsibleButton { background-color: DarkSeaGreen  }")
    self.mainCollapsibleBtn.text = "RGSE ServerMed"
    self.layout.addWidget(self.mainCollapsibleBtn)
    self.mainFormLayout = qt.QFormLayout(self.mainCollapsibleBtn)
  
    # Create input Volume Selector
    self.inputSelectorCoBx = slicer.qMRMLNodeComboBox()
    self.inputSelectorCoBx.nodeTypes = ["vtkMRMLScalarVolumeNode","vtkMRMLLabelMapVolumeNode","vtkMRMLSegmentationNode","vtkMRMLModelNode"]
    self.inputSelectorCoBx.setFixedWidth(200)
    self.inputSelectorCoBx.selectNodeUponCreation = True
    self.inputSelectorCoBx.addEnabled = False
    self.inputSelectorCoBx.removeEnabled = False
    self.inputSelectorCoBx.noneEnabled = False
    self.inputSelectorCoBx.showHidden = False
    self.inputSelectorCoBx.showChildNodeTypes = False
    self.inputSelectorCoBx.setMRMLScene( slicer.mrmlScene )
    self.inputSelectorCoBx.setToolTip("select the volume node")
    self.inputSelectorCoBx.connect("currentNodeChanged(vtkMRMLNode*)", self.onInputSelectorCoBxChange)   
    self.mainFormLayout.addRow("Input Volume Node: ", self.inputSelectorCoBx)


    # Process ID: to allow different processing 
    self.processIDLbl = qt.QLabel()
    self.processIDLbl.setText("Process ID")        
    self.processIDLbl.setFixedHeight(20)
    self.processIDLbl.setFixedWidth(150)
    #self.processIDNames = ["1","2","3"]
    self.processIDBx = qt.QComboBox()
    self.processIDBx.addItems(self.logic.processNames)
    print("processIDNames: ", len(self.logic.processNames))
    self.processIDBx.setCurrentIndex(2)
    self.processIDBx.setFixedHeight(20)
    self.processIDBx.setFixedWidth(200)        
    self.processIDBx.connect("currentIndexChanged(int)", self.onProcessIDCoBxChange)                  
    self.mainFormLayout.addRow( self.processIDLbl, self.processIDBx)    

    # Server: to allow different servers
    self.serverUrlLbl = qt.QLabel()
    self.serverUrlLbl.setText("Server URL:")        
    self.serverUrlLbl.setFixedHeight(20)
    self.serverUrlLbl.setFixedWidth(150)
    self.serverUrlTxtBx = qt.QLineEdit()
    self.serverUrlTxtBx.text = self.logic.serverURL
    print("serverURL: ", len(self.logic.serverURL))
    self.serverUrlTxtBx.setFixedHeight(20)
    self.serverUrlTxtBx.setFixedWidth(200)        
    self.serverUrlTxtBx.connect("currentIndexChanged(int)", self.onProcessIDCoBxChange)                  
    self.mainFormLayout.addRow( self.serverUrlLbl, self.serverUrlTxtBx)    

    # Create a time label
    self.timeLbl = qt.QLabel(" Process Time: 00:00")
    self.timeLbl.setFixedWidth(500)   
    self.tmLbl = self.timeLbl
    
    # Create a button to run the process
    self.applyBtn = qt.QPushButton("Run")
    self.applyBtn.setFixedHeight(50)
    self.applyBtn.setFixedWidth (150)
    self.applyBtn.setStyleSheet("QPushButton{ background-color: DarkSeaGreen  }")
    self.applyBtn.toolTip = ('How to use:' ' Load an images into Slicer then click Run to process')
    self.applyBtn.connect('clicked(bool)', self.onApplyBtnClick)
    self.mainFormLayout.addRow(self.applyBtn, self.timeLbl)
    self.runBtn = self.applyBtn

    
    self.layout.addStretch(1) # Collapsible button is held in place when collapsing/expanding.
    lm = slicer.app.layoutManager();    lm.setLayout(2)

  #------------------------------------------------------------------------
  #                        Define GUI Elements Functions
  #------------------------------------------------------------------------
  
  # Select a vertebra
  def onInputSelectorCoBxChange(self):  
        print("onInputSelectorCoBxChange")    
        currentNode = self.inputSelectorCoBx.currentNode()
        processID   = self.processIDBx.currentIndex + 1
        slicer.app.processEvents()
        slicer.app.layoutManager().resetThreeDViews()
        slicer.app.layoutManager().resetSliceViews()
  
      
  # Select a vertebra
  def onProcessIDCoBxChange(self):
      print("onProcessIDCoBxChange")
  
  
  def onApplyBtnClick(self):
      self.runBtn.setText("...please wait")
      self.runBtn.setStyleSheet("QPushButton{ background-color: red  }")
      slicer.app.processEvents()
      self.stm=time.time()
      print("time:" + str(self.stm))
      self.timeLbl.setText("                 Time: 00:00")      
      inputVolumeNode = self.inputSelectorCoBx.currentNode() 
      inputVolumeName = inputVolumeNode.GetName()
      inputVolumePath = os.path.join(slicer.app.temporaryPath, f"input.nrrd")
      slicer.util.saveNode(inputVolumeNode, inputVolumePath)
      processID   = self.processIDBx.currentIndex 
      serverURL   = self.serverUrlTxtBx.text
      print("inputVolumePath: ",inputVolumePath)
      print("process      : ",processID, self.logic.processNames[processID])
      print("serverURL      : ",serverURL)
      try:
         if (not inputVolumeNode is None):
             resultNode = self.logic.run(inputVolumePath, processID,serverURL)
         else:
             print("Error : onApplyBtnClick!")   
      except Exception as e:
                print("STOPPED: error in input selection")
                print(e)
          
      self.etm=time.time()
      tm=self.etm - self.stm
      self.timeLbl.setText("Time: "+str(tm)+"  seconds")
      self.runBtn.setText("Run")
      self.runBtn.setStyleSheet("QPushButton{ background-color: DarkSeaGreen  }")
      slicer.app.processEvents()
       
#===================================================================
#                           Logic
#===================================================================
class SlicerServerMedLogic(ScriptedLoadableModuleLogic):
 
  processNames = ["Copy","Resampling","DNN_Segmentation"]
  serverURL    = "http://192.168.178.124:5001"
  
  def send_file_to_server(self, file_path, server_url, process_id="0"):
        print(f'Sending file to server: {file_path}')
        print("please wait ....")
        result_file_path = ""
        boundary = '------WebKitFormBoundary7MA4YWxkTrZu0gW'
        headers = {
            'Content-Type': f'multipart/form-data; boundary={boundary}'
        }

        # Read file content
        with open(file_path, 'rb') as f:
            file_content = f.read()

        # Prepare the multipart form data
        data = (
            f'--{boundary}\r\n'
            f'Content-Disposition: form-data; name="file"; filename="{os.path.basename(file_path)}"\r\n'
            'Content-Type: application/octet-stream\r\n\r\n'
        ).encode() + file_content + (
            f'\r\n--{boundary}\r\n'
            f'Content-Disposition: form-data; name="process_id"\r\n\r\n'
            f'{process_id}\r\n'
            f'--{boundary}--\r\n'
        ).encode()

        # Make the request
        req = urllib.request.Request(server_url, data=data, headers=headers)
        try:
            with urllib.request.urlopen(req) as response:
                response_data = response.read()
                parent_directory, old_fnm = os.path.split(file_path)
                extensions = old_fnm.split('.')
                fnm = extensions[0]
                extensions = extensions[1:]
                fnm = fnm + "_result" + ''.join(['.' + x for x in extensions])
                result_file_path = os.path.join(parent_directory, fnm)

                with open(result_file_path, 'wb') as f:
                    f.write(response_data)

                print(f'Result file saved to {result_file_path}')

        except urllib.error.URLError as e:
            print(f'An error occurred: {e}')
        return result_file_path
    
  def run( self, inputVolumePath, processID, serverURL):             
      print ("logic run")           
      result_file_path = self.send_file_to_server(inputVolumePath, serverURL + "/upload", str(processID))  
      print("result_file_path : ",result_file_path)
      resultNode = slicer.util.loadVolume(result_file_path)
      resultNode.SetName("result")
      return resultNode
#===================================================================
#                           Test
#===================================================================
class SlicerServerMedTest(ScriptedLoadableModuleTest):

  def setUp(self):
      slicer.mrmlScene.Clear(0)

  def runTest(self):
      self.setUp()
      self.testSlicerServerMeds()

  
  def testSlicerServerMeds(self, imgPath=None , inputPoints=None, methodID=None):
      self.delayDisplay("Starting testSlicerServerMeds")

      # record duration of the test    
      self.stm=time.time()

      self.delayDisplay('Test testSlicerServerMeds passed!') 
