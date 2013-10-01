import os, sys, token, tokenize, zmq, re
from StringIO import StringIO
from os.path import exists
import os
import json

ws = re.compile('^\s+$')

class corpusModel(object):
    def __init__(self, readCorpus=None, writeCorpus=None, logFilePath=None, estimateNgramPath=None):
        self.readCorpus = (readCorpus or os.getenv("ucCorpus", "/tmp/ucCorpus"))
        self.writeCorpus = (writeCorpus or os.getenv("ucWriteCorpus", self.readCorpus))
        self.logFilePath = (logFilePath or os.getenv("ucLogFile", "/tmp/ucLog-%i" % os.getpid()))
        self.mitlmSocketPath = "ipc://%s-%i-%i" % (os.path.dirname(self.logFilePath), os.getpid(), id(self))
        self.estimateNgramPath = (estimateNgramPath or os.getenv("ESTIMATENGRAM", os.popen('which estimate-ngram').read()))
    def startMitlm(self):
        assert exists(self.readCorpus), "No such corpus."
        assert exists(self.estimateNgramPath), "No such estimate-ngram."
        self.mitlmPID = os.fork()
        if self.mitlmPID == 0:
            os.execv(self.estimateNgramPath, ["-t", self.readCorpus, "-o", order+1, "-s", "ModKN", "-u", "-live-prob", self.mitlmSocketPath])
            assert false, "Failed to exec."
        print "Started MITLM as PID %i." % self.mitlmPID
        self.mitlmSocket = zctx.socket(zmq.REQ)
        self.mitlmSocket.connect(mitlmSocketPath)
        self.mitlmSocket.send("for ( i =")
        r = float(self.mitlmSocket.recv().data())
        print "MITLM said %f" % r
        

def toBool(inputString):
    return json.loads(inputString)

    
def corpify1(lexeme):
    if ws.match(str(lexeme['value'])) :
        return '<'+lexeme['type']+'>'
    elif len(lexeme['value']) > 0 :
        return lexeme['value']
    else:
        return '<'+lexeme['type']+'>'
    
    
def corpify(inputLexed):
    return " ".join(map(corpify1, inputLexed))
    

#corpusFH = open(writeCorpus, "a")
forceTrain = toBool(os.getenv("ucForceTrain", "false"))
forceValidate = toBool(os.getenv("ucValidate", "false"))

zctx = zmq.Context()