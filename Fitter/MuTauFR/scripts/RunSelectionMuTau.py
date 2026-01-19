#! /usr/bin/env python3
# Author: Alexei Raspereza (October 2025)
# mu->tau FR SF measurement
# Script to run mu+tau selection
import ROOT
import math
from array import array
import os
import TauFW.Fitter.MuTauFR.utils as utils
import TauFW.Fitter.MuTauFR.styles as styles
import TauFW.Fitter.MuTauFR.analysisMuTauFR as analysis
from TauFW.Fitter.MuTauFR.TauScaleFactors import TauScaleFactor
from TauFW.Plotter.plot.utils import ensuredir

############
#   MAIN   #
############

if __name__ == "__main__":

    styles.InitROOT()
    styles.SetStyle()

    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('-e', '--era', dest='era', default='2024', choices=['2024','2025','UL2017','UL2016_preVFP','UL2016_postVFP'])
    parser.add_argument('-wpVsJet','--wpVsJet', dest='wpVsJet', default='Medium', choices=['Loose','Medium','Tight','VTight'])
    parser.add_argument('-wpVsMu','--wpVsMu', dest='wpVsMu', default='VLoose', choices=['VLoose','Loose','Medium','Tight'])
    parser.add_argument('-wpVsE','--wpVsE', dest='wpVsE', default='VVLoose', choices=['VVLoose','Loose','Medium','Tight'])
    parser.add_argument('-sample','--sample',dest='sample',default='TTTo2L2Nu')
    parser.add_argument('-applySF','--applySF',dest='applySF',action='store_true')
    parser.add_argument('-start','--start',dest='start',type=int,default=0)
    parser.add_argument('-period','--period',dest='period',type=int,default=10000000)
    args = parser.parse_args()

    era = args.era
    channel = 'mutau'
    start = args.start 
    period = args.period
    
    wpVsJet = args.wpVsJet
    wpVsMu = args.wpVsMu
    wpVsE = args.wpVsE

    applySF = args.applySF
    sample = args.sample

    scaleFactor = None
    if applySF:
        cmssw_base = os.getenv('CMSSW_BASE')
        filename = '%s/src/TauFW/Fitter/MuTauFR/ScaleFactors/%s_ScaleFactors.root'%(cmssw_base,era)
        scaleFactor = TauScaleFactor(filename=filename,wpVsJet=wpVsJet,wpVsMu=wpVsMu,wpVsE=wpVsE)
    
    sampleToProcess = analysis.sampleMuTauFR(era,channel,sample)
    sampleToProcess.SetMuTauConfig(scaleFactor,
                                   antiJet = utils.tauVsJetIntWPs[wpVsJet],
                                   antiMu = utils.tauVsMuIntWPs[wpVsMu],
                                   antiE = utils.tauVsEleIntWPs[wpVsE])
    hists = sampleToProcess.CreateHistosMuTau(start,period)

    suffix = f'{wpVsJet}VsJet_{wpVsMu}VsMu_{wpVsE}VsE'
    if applySF:
        suffix += '_SF'

    subfolder = f'mutau_{era}_{suffix}'   
    outputfolder = ensuredir(utils.outputFolder+'/'+subfolder)
    filename = f'{sample}_{start}.root'
    outputfileName = outputfolder+'/'+filename
    print('opening file %s'%(outputfileName))
    outputFile = ROOT.TFile(outputfileName,'recreate')
    outputFile.cd('')
    for hist in hists:
        hists[hist].Write(hist)
    outputFile.Close()
    
        
