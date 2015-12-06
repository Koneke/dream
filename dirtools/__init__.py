import os

def getName(path):
    return getFullPath(path).split('\\')[-1];

def getFullPath(path):
    return os.getcwd() + '\\' + path;

def getDirectory(path):
    return '\\'.join(getFullPath(path).split('\\')[:-1]);
