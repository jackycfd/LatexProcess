#!/usr/bin/env python
#


"""Process a LaTex Project."""

__author__ = "Zhihua Ma"

__version__ = "1.0"

import sys
import math
import os
import re
import textwrap
import optparse
import xml.parsers.expat

#To judge whether a latex file line is commented with '%'
def commentedLatex(string):
    iscomment=False
    comP=string.find("%")

    if comP==0:
        iscomment=True
    elif comP>0:
        if string[0:comP]==" "*comP:
            iscomment=True
        else:
            iscomment=False

    return(iscomment)

#To judge whether a latex file line commented with Emacs END '%%%'
def commentedLatexEND(string):
    iscomment=False
    comP=string.find("%%%")

    if comP==0:
        iscomment=True
    else:
        iscomment=False

    return(iscomment)

#To judge whether a latex file is inputted or included
def inputLatex(string):
    isinput=False
    if commentedLatex(string): #commented line
        isinput=False
    else:
        myIn="\input{" in string or "\include{" in string

        if myIn:
            isinput=True
        else:
            isinput=False
            
    return(isinput)
        
#To get the name of the file to input        
def getInputLatexFileName(linestring):
    if not inputLatex(linestring): #nothing to input
        return (False)
    else:
        comP0=0;
        if "\input" in linestring:
            comP0=linestring.find("\input")
        else:
            comP0=linestring.find("\include")

        comP1=linestring.find("{",comP0)
        comP2=linestring.find("}",comP1)
        fileName=linestring[comP1+1:comP2]+".tex"
        return (fileName)


#To judge whether a graphics file needs to be input
def graphicsToInput(linestring):
    if not commentedLatex(linestring):
        comP=linestring.find("\includegraphics")
        if comP>=0:
            return (True)
        else:
            return (False)
    else:
        return(False)

#To judge whether a movie file needs to be input
def movieToInput(linestring):
    if not commentedLatex(linestring):
        comP=linestring.find("\includemovie")
        if comP>=0:
            return (True)
        else:
            return (False)
    else:
        return(False)


#To get the name of the graphics file
def getGraphicsFileName(linestring):
    comP0=linestring.find("\includegraphics")
    comP1=linestring.find("{",comP0)
    comP2=linestring.find("}",comP1)
    fileName0=linestring[comP1+1:comP2]
    fileName1=fileName0.replace(".eps","")
    fileName2=fileName1.replace(".eps","")
    return fileName2

#To get the name of the movie file
def getMovieFileName(linestring):
    #print "getMovieFileName"
    comP0=linestring.find("\includemovie")
    #print linestring[comP0:]
    comP1=linestring.find("]",comP0)
    #print linestring[comP1:]
    comP2=linestring.find("{",comP1) #width
    #print linestring[comP2:]
    comP3=linestring.find("}",comP2)
    #print linestring[comP3:]
    comP4=linestring.find("{",comP3) #height
    #print linestring[comP4:]
    comP5=linestring.find("}",comP4)
    #print linestring[comP5]
    comP6=linestring.find("{",comP5) #movie file
    #print linestring[comP6]
    comP7=linestring.find("}",comP6)
    #print linestring[comP6:]
    fileName=linestring[comP6+1:comP7]
    #print fileName
    return fileName

#new name of the graphics file
def getNewGraphicsFileName(oldname):
    comL=oldname.find("/")
    comR=oldname.rfind("/")
    
    if comL<0:
        return (oldname)
    else:
        newname=oldname[comR+1:]
        return (newname)

#new name of the movie file
def getNewMovieFileName(oldname):
    #print "get new move file name"
    comL=oldname.find("/")
    comR=oldname.rfind("/")
    
    if comL<0:
        return (oldname)
    else:
        newname=oldname[comR+1:]
        return (newname)

#get a numbered graphics file name
def getNumberedGraphicsFileName(oldname,number):
    #numbersting="{:02d}".format(number)
    #if number<10:
    #    newname="fig-0"+str(number)+"-"+oldname
    #    return (newname)
    #else:
    #    newname="fig-"+str(number)+"-"+oldname
    #    return (newname)

    newname="%04d" %(number)
    #newname="fig-"+newname+"-"+oldname
    newname="fig-"+newname
    return (newname)

#to judge whether the documentclass is declared
def declaredClass(string):
    if commentedLatex(string):
        return (False)
    else:
        if "\documentclass" in string:
            return (True)
        else:
            return (False)

def getDocumentclassType(string):
    comP0=string.find("\documentclass")
    comP1=string.find("{",comP0)
    comP2=string.rfind("}",comP1)
    typeName=string[comP1+1:comP2]
    return (typeName)

#to judge whether the bibstyle is declared
def declaredBibStyle(string):
    if commentedLatex(string):
        return (False)
    else:
        if "bibliographystyle{" in string:
            return (True)
        else:
            return (False)

def getBibStyle(string):
    comP0=string.find("{")
    comP1=string.find("}")
    bibStyle=string[comP0+1:comP1]
    return (bibStyle)

#to judge whether the bibfile is declared
def declaredBibFile(string):
    if commentedLatex(string):
        return (False)
    else:
        if "bibliography{" in string:
            return (True)
        else:
            return (False)

#to get old bib file
def getBibFile(string):
    comP0=string.find("{")
    comP1=string.find("}")
    bibFile=string[comP0+1:comP1]
    return (bibFile)

#to get a Clean File Name
def getCleanFileName(oldname):
    comL=oldname.find("/")
    comR=oldname.rfind("/")
    
    if comL<0:
        return (oldname)
    else:
        newname=oldname[comR+1:]
        return (newname)

class Main:
    """Main program."""

    processDir="pythonProcess"

    masterFileName=""
    totalMasterFileLine=[]
    totalRawFileLine=[]

    latexModel=True
    pdflatexModel=True
    compileModel=""
    toCompile=False

    toCompress=False

    targetFileName0="masterFull.tex"
    targetFileName=processDir+"/"+targetFileName0
    
    documentclass=""
    bibStyle=""
    bibFile=""
    newBibFile=""
    

    def main(self):
        """Main program."""
        print "Hello python class"

        print "  This program assembles a latex project to the folder pythonProcess"
        print "\t 1) combine multiple source files into a single source file masterFull.tex"
        print "\t 2) copy the scattered graphics and media files to pythonProcess"
        print "\t 3) copy the documentclass, bibliographystyle and bib files to pythonProcess"
        print "\t 4) rename the names of the graphics files as sorted"
        print "\t 5) update the graphics and media files with correct names"
        print "\t 6) compile the latex project to generate a PDF and clean temporary files"
        print "  It provides several options to users"
        print "\t A) the source latex project file"
        print "\t B) choose between latex or pdflatex model"
        print "\t C) to compile to project or not"
        print "\t D) choose to compress the assembled project or not"

        self.prepareProcessDir()
        
        self.readMasterFile()
        
        self.setLatexModel()

        self.setToCompile()

        self.setToCompress()

        #The raw target file
        lineIndex=0;
        figureIndex=0;

        targetFile=open(self.targetFileName,"w")

        for line in self.totalMasterFileLine:
            lineIndex+=1            
            if inputLatex(line):
                inputFileName=getInputLatexFileName(line)
                targetFile.write("%%%%%%To input file "+inputFileName+"\n")
                #input the file
                inputFile=open(inputFileName,"r")
                inputFileLine=inputFile.readlines()
                #output
                for subline in inputFileLine:
                    targetFile.write(subline)
            else:
                targetFile.write(line)
        targetFile.close()

        self.readRawTargetFile()

        self.processRawTargetFile()

        self.copyLatexOtherFile()

        self.compileLatex()
        
        self.compressLatex()

    def compressLatex(self):
        classFileName=self.documentclass+".cls"
        bibStyleFileName=self.bibStyle+".bst"
        bibFileName=self.newBibFile+".bib"
        newTargetFileName=self.targetFileName0.replace(".tex","New.tex")
        baseDir=os.getcwd()
        newWorkingDir=baseDir+"/"+self.processDir

        if self.toCompress:
            print "compress the files to submit.zip"
            os.chdir(newWorkingDir)
            os.system('zip -q submit.zip *.eps *.pdf *.swf '+newTargetFileName+' '+classFileName+' '+bibStyleFileName+' '+bibFileName)
            os.chdir(baseDir)

    def compileLatex(self):
        sourceName=self.targetFileName0.replace(".tex","New.tex")

        baseDir=os.getcwd()
        newWorkingDir=baseDir+"/"+self.processDir
        
        compileCommand="latex "
        if self.pdflatexModel:
            compileCommand="pdflatex "
            
        if self.toCompile:
            os.chdir(newWorkingDir)

            os.system(compileCommand+sourceName)
            os.system('bibtex '+sourceName.replace(".tex",".aux"))
            os.system(compileCommand+sourceName)
            os.system(compileCommand+sourceName)
            if self.latexModel:
                os.system('dvipdf '+sourceName.replace(".tex",".dvi"))

            os.system('rm -f *.aux *.bbl *.blg *.log *.out *.dvi *.pdfsync *.synctex.gz *.toc *.lof *.spl')
            os.chdir(baseDir)

    def copyLatexOtherFile(self):
        classFileName=self.documentclass+".cls"
        bibStyleFileName=self.bibStyle+".bst"
        bibFileName=self.bibFile+".bib"
        newBibFileName=self.newBibFile+".bib"

        print "classFileName=%s" %(classFileName)
        print "bibStyleFileName=%s" %(bibStyleFileName)
        print "bibFileName=%s" %(bibFileName)
        print "newBibFileName=%s" %(newBibFileName)

        if os.path.exists(classFileName):
            os.system('cp '+classFileName+" "+self.processDir+"/"+classFileName)
            
        if os.path.exists(bibStyleFileName):
            os.system('cp '+bibStyleFileName+" "+self.processDir+"/"+bibStyleFileName)

        if os.path.exists(bibFileName):
            os.system('cp '+bibFileName+" "+self.processDir+"/"+newBibFileName)

    def processRawTargetFile(self):
        figureIndex=0

        newTargetFileName=self.targetFileName.replace(".tex","New.tex")
        newTargetFile=open(newTargetFileName,"w")
        for line in self.totalRawFileLine:
            if not commentedLatex(line):
                if graphicsToInput(line):
                    figureIndex+=1
                    #print "Input graphics from file=%s  Content=%s" %(inputFileName,subline)
                    oldGraphicsName=getGraphicsFileName(line)
                    newGraphicsName=getNewGraphicsFileName(oldGraphicsName)
                    numberedGraphicsFileName=getNumberedGraphicsFileName(newGraphicsName,figureIndex)
                    
                    #print "\toldGraphicsName=%s numberGraphicsName=%s" %(oldGraphicsName,numberedGraphicsFileName)
                    newline=line.replace(oldGraphicsName,numberedGraphicsFileName)
                    newTargetFile.write(newline)

                    copyCommand1="cp "+oldGraphicsName+".eps"+"\t"+self.processDir+"/"+numberedGraphicsFileName+".eps\n"
                    copyCommand2="cp "+oldGraphicsName+".pdf"+"\t"+self.processDir+"/"+numberedGraphicsFileName+".pdf\n"

                    if self.latexModel:
                        os.system(copyCommand1)
                    else:
                        os.system(copyCommand2)
                        
                elif movieToInput(line):
                    oldMovieName=getMovieFileName(line)
                    newMovieName=getNewMovieFileName(oldMovieName)
                    newline=line.replace(oldMovieName,newMovieName)
                    newTargetFile.write(newline)

                    copyCommand="cp "+oldMovieName+"\t"+self.processDir+"/"+newMovieName+"\n"
                    os.system(copyCommand)

                    #print 'oldMovieName:',oldMovieName
                    #print 'newMovieName:',newMovieName

                elif declaredClass(line):
                    newTargetFile.write(line)
                    self.documentclass=getDocumentclassType(line)

                elif declaredBibStyle(line):
                    newTargetFile.write(line)
                    self.bibStyle=getBibStyle(line)

                elif declaredBibFile(line):
                    self.bibFile=getBibFile(line)
                    self.newBibFile=getCleanFileName(self.bibFile)
                    newline=line.replace(self.bibFile,self.newBibFile)
                    newTargetFile.write(newline)
                else:
                    newTargetFile.write(line)
        newTargetFile.close()
        
        #rm the RawTargetFile
        os.system("rm -f "+self.targetFileName)
    def prepareProcessDir(self):
        """clean or make the folder"""
        if os.path.exists(self.processDir):            
            os.system('rm -f '+self.processDir+'/*')
        else:
            os.system('mkdir '+self.processDir)
    
    def readMasterFile(self):
        """read master source file"""
        print "list all the latex source files"
        os.system("ls -l *.tex")
        self.masterFileName=raw_input("  Please give the name of the master latex  source file: ")
        masterFile=open(self.masterFileName,"r")
        self.totalMasterFileLine=masterFile.readlines();
        masterFile.close()
        #print self.totalMasterFileLine

    def readRawTargetFile(self):
        file=open(self.targetFileName,"r")
        self.totalRawFileLine=file.readlines()
        file.close()
        #print self.totalRawFileLine

    def setLatexModel(self):
        self.latexModel=True
        self.pdflatexModel=True

        #choose latex or pdflatex model
        self.compileModel=raw_input("  Please choose compile model latex or pdflatex: ")
        if self.compileModel=="latex":
            self.latexModel=True
            self.pdflatexModel=False
        else:
            self.pdflatexModel=True
            self.latexModel=False

    def setToCompile(self):
        self.toCompile=False
        tmp=raw_input("  To compile the project or not? yes/no: ")
        if tmp[0]=="y" or tmp[0]=="Y":
            self.toCompile=True
        else:
            self.toCompile=False

    def setToCompress(self):
        self.toCompress=False
        tmp=raw_input("  To compress the project or not? yes/no: ")
        if tmp[0]=="y" or tmp[0]=="Y":
            self.toCompress=True
        else:
            self.toCompress=False



if __name__ == '__main__':
    Main().main()
