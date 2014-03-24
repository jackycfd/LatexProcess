#!/usr/bin/env python
#


"""Process a LaTex Project."""

__author__ = "Zhihua Ma"

__version__ = "1.1"

import sys
import os
import re

latexElement={'classKey':     r"\documentclass", 
              'bibStyleKey':  r"\bibliographystyle{",
              'bibFileKey':   r"\bibliography{",
              'graphicsKey':  r"\includegraphics",
              'movieKey':     r"\includemovie",
              'inputKey':     r"\input{",
              'includeKey':   r"\include{",
              'sectionKey':   r"\section",
              'chapterKey':   r"\chap"}

def hasLatexObject(lobj,string):
    """To judge whether the string has a latex element lobj"""
    if not commentedLatex(string):
        if lobj in string:
            return (True)
        else:
            return (False)
    else:
        return (False)

def commentedLatex(string):
    """#To judge whether a latex file line is commented with '%'"""
    if string.lstrip(" ")[0]=="%":
        return (True)
    else:
        return (False)

def commentedLatexEND(string):
    """#To judge whether a latex file line commented with Emacs END '%%%'"""
    iscomment=False
    comP=string.find("%%%")

    if comP==0:
        iscomment=True
    else:
        iscomment=False

    return(iscomment)


def inputLatex(string):
    """#To judge whether a latex file is inputted or included"""
    isinput=hasLatexObject(latexElement['inputKey'],string) or hasLatexObject(latexElement['includeKey'],string)
            
    return(isinput)

def getInputLatexFileName(linestring):
    """#To get the name of the file to input        """
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

def getGraphicsFileName(linestring):
    """#To get the name of the graphics file"""
    comP0=linestring.find("\includegraphics")
    comP1=linestring.find("{",comP0)
    comP2=linestring.find("}",comP1)
    fileName0=linestring[comP1+1:comP2]
    fileName1=fileName0.replace(".eps","")
    fileName2=fileName1.replace(".eps","")
    return fileName2


def getMovieFileName(linestring):
    """#To get the name of the movie file"""
    comP0=linestring.find("\includemovie")
    comP1=linestring.find("]",comP0)
    comP2=linestring.find("{",comP1) #width
    comP3=linestring.find("}",comP2)
    comP4=linestring.find("{",comP3) #height
    comP5=linestring.find("}",comP4)
    comP6=linestring.find("{",comP5) #movie file
    comP7=linestring.find("}",comP6)
    fileName=linestring[comP6+1:comP7]
    return fileName

def getCleanFileName(oldname):
    """#to get a Clean File Name"""
    comL=oldname.find("/")
    comR=oldname.rfind("/")
    
    if comL<0:
        return (oldname)
    else:
        newname=oldname[comR+1:]
        return (newname)

def getNumberedGraphicsFileName(oldname,number):
    """#get a numbered graphics file name"""
    newname="fig-" + "%04d" %(number)
    #newname="fig-"+newname
    return (newname)

def getDocumentclassType(string):
    comP0=string.find("\documentclass")
    comP1=string.find("{",comP0)
    comP2=string.rfind("}",comP1)
    typeName=string[comP1+1:comP2]
    return (typeName)

def getBibStyle(string):
    comP0=string.find("{")
    comP1=string.find("}")
    bibStyle=string[comP0+1:comP1]
    return (bibStyle)

def getBibFile(string):
    """#to get old bib file"""
    comP0=string.find("{")
    comP1=string.find("}")
    bibFile=string[comP0+1:comP1]
    return (bibFile)

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

        #scan latex source files
        self.scanLatexSource()

        self.preProcessRawTargetFile()

        self.readRawTargetFile()

        self.processRawTargetFile()

        self.copyLatexOtherFile()

        self.compileLatex()
        
        self.compressLatex()

    def scanLatexSource(self):
        lineIndex=0;
        figureIndex=0;

        targetFile=open(self.targetFileName,"w")

        for line in self.totalMasterFileLine:
            lineIndex+=1            
            if hasLatexObject(latexElement['inputKey'],line) or hasLatexObject(latexElement['includeKey'],line):
                inputFileName=getInputLatexFileName(line)
                targetFile.write("%%%%%%To input file "+inputFileName+"\n")
                #input the file
                inputFile=open(inputFileName,"r")
                inputFileLine=inputFile.readlines()
                inputFile.close()
                #output
                targetFile.writelines(inputFileLine)
            else:
                targetFile.write(line.rstrip(" "))
        targetFile.close()
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

    def preProcessRawTargetFile(self):
        """seperate single graphics include command into multiple lines"""

        file=open(self.targetFileName,"r")
        self.totalRawFileLine=file.readlines()
        file.close()
                
        #file2=open(self.targetFileName.replace(".tex","2.tex"),"w")
        file2=open(self.targetFileName,"w")

        for line in self.totalRawFileLine:
            if not commentedLatex(line):
                graphicsCount=line.count("\includegraphics")
                if graphicsCount<=1:
                    file2.write(line)
                else:
                    P0=line.find("\includegraphics")
                    P1=line.find("\includegraphics",P0+1)
                    newline=line[0:P1]+line[P1:].replace("\includegraphics","\n  \includegraphics")
                    file2.write(newline)
        file2.close()
            
    def processRawTargetFile(self):
        figureIndex=0

        newTargetFileName=self.targetFileName.replace(".tex","New.tex")
        newTargetFile=open(newTargetFileName,"w")
        for line in self.totalRawFileLine:
            if not commentedLatex(line):
                if hasLatexObject(latexElement['graphicsKey'],line):
                    figureIndex+=1

                    oldGraphicsName=getGraphicsFileName(line)
                    newGraphicsName=getCleanFileName(oldGraphicsName)
                    numberedGraphicsFileName=getNumberedGraphicsFileName(newGraphicsName,figureIndex)
                    
                    newline=line.replace(oldGraphicsName,numberedGraphicsFileName)
                    newTargetFile.write(newline)

                    copyCommand1="cp "+oldGraphicsName+".eps"+"\t"+self.processDir+"/"+numberedGraphicsFileName+".eps\n"
                    copyCommand2="cp "+oldGraphicsName+".pdf"+"\t"+self.processDir+"/"+numberedGraphicsFileName+".pdf\n"

                    if self.latexModel:
                        os.system(copyCommand1)
                    else:
                        os.system(copyCommand2)

                elif hasLatexObject(latexElement['movieKey'],line):
                    oldMovieName=getMovieFileName(line)
                    newMovieName=getCleanFileName(oldMovieName)
                    newline=line.replace(oldMovieName,newMovieName)
                    newTargetFile.write(newline)

                    copyCommand="cp "+oldMovieName+"\t"+self.processDir+"/"+newMovieName+"\n"
                    os.system(copyCommand)

                elif hasLatexObject(latexElement['classKey'],line):
                    newTargetFile.write(line)
                    self.documentclass=getDocumentclassType(line)

                elif hasLatexObject(latexElement['bibStyleKey'],line):
                    newTargetFile.write(line)
                    self.bibStyle=getBibStyle(line)

                elif hasLatexObject(latexElement['bibFileKey'],line):
                    self.bibFile=getBibFile(line)
                    self.newBibFile=getCleanFileName(self.bibFile)
                    newline=line.replace(self.bibFile,self.newBibFile)
                    newTargetFile.write(newline)

                elif hasLatexObject(latexElement['sectionKey'],line):
                    #newTargetFile.write("%%"+"-"*90+"%%\n")
                    newTargetFile.write(line)                    
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

    def readRawTargetFile(self):
        file=open(self.targetFileName,"r")
        self.totalRawFileLine=file.readlines()
        file.close()

    def setLatexModel(self):
        self.latexModel=True
        self.pdflatexModel=True

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
