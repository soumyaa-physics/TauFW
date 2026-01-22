import ROOT 
import math
from array import array
import numpy as np
import os

############################
## mu->tau FR measurement ##
##### General settings #####
############################

#########################
# folder for picotuples #
#########################
#picoFolder='/eos/cms/store/group/phys_tau/TauFW/pico2024/TES_variations'
picoFolder= {
    '2024': '/eos/cms/store/group/phys_tau/TauFW/pico2024/mutau_FR',
    'UL2017': '/eos/cms/store/group/phys_tau/rasp/Run2_UL',
    'UL2016_preVFP': '/eos/cms/store/group/phys_tau/rasp/Run2_UL',
    }
####################################################
# folders needs to be set by user                  #
# outputFolder - folder to store output RooT files #
#                with histograms after selection   #
# condorFolder - folder to store scripts           #
#                for submitting jobs to condor     #
####################################################
outputFolder = '/afs/.cern.ch/user/s/svashish/CMSSW_14_1_0_pre4/src/TauFW/Fitter/smv_MuTauFR/selection' 
condorFolder = '/afs/.cern.ch/user/s/svashish/CMSSW_14_1_0_pre4/src/TauFW/Fitter/smv_MuTauFR/condor' 
figuresFolder = '/eos/user/s/svashish/MuTauFR/plots'

###################
# Cross sections  #
###################

# k-factors for cross sections at 13.6 TeV
kfactor_dy_powheg = 6282.6/6731.99 # LO->NNLO+NLO_EW k-factor computed for 13.6 TeV
kfactor_dy=6282.6/5455.0 # LO->NNLO+NLO_EW k-factor computed for 13.6 TeV
kfactor_wj=0.93 # LO->NNLO+NLO_EW k-factor computed for 13.6 TeV
kfactor_ttbar=923.6/762.1 # NLO->NNLO k-factor computed for 13.6 TeV
kfactor_ww=1.524 # LO->NNLO+NLO_EW computed for 13.6 TeV
kfactor_zz=1.524 # LO->NNLO+NLO_EW computed for 13.6 TeV
kfactor_wz=1.414 # LO->NNLO+NLO_EW computed for 13.6 TeV 

mc_samples = {
    '2024': {
        #      Name  :  (xsec, nevts, group, split by genmatch_2)
        #    nevts = -1 implies that total number of events is
        #               taken from bin 16 of the cutflow histogram
        "DYto2Mu_Bin-MLL-10to50"   : (6744.0, -1, "DY", ['ZTT','ZL','ZJ']),
        "DYto2Mu_Bin-MLL-50to120"  : (2219*kfactor_dy_powheg, -1, "DY", ['ZTT','ZL','ZJ']),
        "DYto2Mu_Bin-MLL-120to200" : (21.65*kfactor_dy_powheg,-1, "DY", ['ZTT','ZL','ZJ']),
        "DYto2Tau_Bin-MLL-50to120" : (2219*kfactor_dy_powheg, -1, "DY", ['ZTT','ZL','ZJ']),
        "DYto2Tau_Bin-MLL-120to200" : (21.65*kfactor_dy_powheg, -1, "DY", ['ZTT','ZL','ZJ']),
        "WtoMuNu-2Jets" : (22666.*kfactor_wj, -1, "WJ", ['W']),
        "WtoTauNu-2Jets" : (22666.*kfactor_wj, -1, "WJ", ['W']),
        "TTto2L2Nu" : (80.9*kfactor_ttbar, -1, "TT", ['TTT','TTL','TTJ']),
        "TTtoLNu2Q" : (334.8*kfactor_ttbar, -1, "TT", ['TTT','TTL', 'TTJ']),
        "TWminustoLNu2Q" : (15.8, -1, "ST", ['VV']),
        "TWminusto2L2Nu" : (3.8, -1, "ST", ['VV']),
        "TbarWplustoLNu2Q" : (15.9, -1, "ST", ['VV']),
        "TbarWplusto2L2Nu" : (3.8, -1, "ST", ['VV']),
        "WZ" : (29.1*kfactor_wz, -1, "VV", ['VV']),
        "ZZ" : (12.75*kfactor_zz, -1, "VV", ['VV']),
        "WWto2L2Nu" : (11.79*kfactor_ww, -1, "VV", ['VV']),
        "WWtoLNu2Q" : (48.94*kfactor_ww, -1, "VV", ['VV']),
    },
    # taken from file TauFW/Fitter/MuTauFR/samples_v10.py
    # cross section are taken from HighPT analysis
    'UL2017': {
        "DYJetsToLL_M-10to50" :     (21167.,  68480179.0, "DY", ['ZTT','ZL','ZJ']),
        "DYJetsToLL_M-50"     :     ( 6077., 205238822.0, "DY", ['ZTT','ZL','ZJ']),
        "WJetsToLNu"          :     (61526.,  78981243.0, "WJ", ['W']),
        "TTTo2L2Nu"           :     ( 88.29, 105859990.0, "TT", ['TTT','TTL','TTJ']),
        "TTToSemiLeptonic"    :     (365.35, 352462632.0, "TT", ['TTT','TTL','TTJ']),
        "WWTo2L2Nu"           :     ( 11.09,   7071358.0, "VV", ['VV']),
        "WZTo2Q2L"            :     ( 6.419,  18136498.0, "VV", ['VV']),
        "WZTo3LNu"            :     ( 5.213,   6826898.0, "VV", ['VV']),
        "ZZTo2L2Nu"           :     (0.6008,  40753260.0, "VV", ['VV']),
        "ZZTo2Q2L"            :     (3.676,   19134840.0, "VV", ['VV']),
        "ST_t-channel_top"    :     (136.02, 121728252.0, "ST", ['VV']),
        "ST_t-channel_antitop":     ( 80.95,  65821722.0, "ST", ['VV']),
        "ST_tW_top"           :     ( 35.85,   8506765.0, "ST", ['VV']),
        "ST_tW_antitop"       :     ( 35.85,   8433562.0, "ST", ['VV']),
    },
    #cross-section is the same as UL2017, changed the number of gen weights
    'UL2016_preVFP': { 
        "DYJetsToLL_M-10to50" :     (21167.,  25799525.0, "DY", ['ZTT','ZL','ZJ']),
        "DYJetsToLL_M-50"     :     ( 6077., 95170542.0, "DY", ['ZTT','ZL','ZJ']),
        "WJetsToLNu"          :     (61526.,  74676454.0, "WJ", ['W']),
        "TTTo2L2Nu"           :     ( 88.29, 37202074.0, "TT", ['TTT','TTL','TTJ']),
        "TTToSemiLeptonic"    :     (365.35, 131106830.0, "TT", ['TTT','TTL','TTJ']),
        "WWTo2L2Nu"           :     ( 11.09,  3006596.0, "VV", ['VV']),
        "WZTo2Q2L"            :     ( 6.419,  9780392.0, "VV", ['VV']),
        "WZTo3LNu"            :     ( 5.213,   6363896.0, "VV", ['VV']),
        "ZZTo2L2Nu"           :     (0.6008,  16826232.0, "VV", ['VV']),
        "ZZTo2Q2L"            :     (3.676,   10406942.0, "VV", ['VV']),
        "ST_t-channel_top"    :     (136.02, 52437432.0, "ST", ['VV']),
        "ST_t-channel_antitop":     ( 80.95,  29205918.0, "ST", ['VV']),
        "ST_tW_top"           :     ( 35.85,   3294485.0, "ST", ['VV']),
        "ST_tW_antitop"       :     ( 35.85,   3176335.0, "ST", ['VV']),
    }
}

data_samples = {
    '2024': ['Muon0_Run2024C','Muon0_Run2024D','Muon0_Run2024E','Muon0_Run2024F','Muon0_Run2024G','Muon0_Run2024H','Muon0_Run2024I','Muon1_Run2024C','Muon1_Run2024D','Muon1_Run2024E','Muon1_Run2024F','Muon1_Run2024G','Muon1_Run2024H','Muon1_Run2024I'],
    'UL2017': ['SingleMuon_Run2017B','SingleMuon_Run2017C','SingleMuon_Run2017D','SingleMuon_Run2017E','SingleMuon_Run2017F'],
    'UL2016_preVFP': ['SingleMuon_Run2016B','SingleMuon_Run2016C','SingleMuon_Run2016D','SingleMuon_Run2016E','SingleMuon_Run2016F'], #needs to be changed

}

zptweightName = {
    '2024' : 'zptweight_nnlo',
    'UL2017' : 'zptweight',
    'UL2016_preVFP' : 'zptweight',
    'UL2016_postVFP' : 'zptweight',
    }

eraLumi = {
    '2024'   : 109080.,
    'UL2017' :  41480.,
    'UL2016_preVFP' : 19500.,  
    'UL_2016_postVFP' :  16800.,
}

################
# Data samples #
################

procs = ['ZTT','ZL','ZJ','TTT','TTL','TTJ','W','VV']

tauVsEleWPs = {
    'VVVLoose': "1",
    'VVLoose' : "2",
    'VLoose'  : "3",
    'Loose'   : "4",
    'Medium'  : "5",
    'Tight'   : "6",
    'VTight'  : "7",
    'VVTight' : "8"
}

tauVsEleIntWPs = {
    'VVVLoose': 1,
    'VVLoose' : 2,
    'VLoose'  : 3,
    'Loose'   : 4,
    'Medium'  : 5,
    'Tight'   : 6,
    'VTight'  : 7,
    'VVTight' : 8
}

tauVsMuWPs = {
    'VLoose'  : "1",
    'Loose'   : "2",
    'Medium'  : "3",
    'Tight'   : "4"
}

tauVsMuIntWPs = {
    'VLoose'  : 1,
    'Loose'   : 2,
    'Medium'  : 3,
    'Tight'   : 4
}

tauVsJetWPs = {
    'Loose': "4",
    'Medium': "5",
    'Tight': "6",
    'VTight': "7",
    'VVTight': "8"
}

tauVsJetIntWPs = {
    'Loose': 4,
    'Medium': 5,
    'Tight': 6,
    'VTight': 7,
    'VVTight': 8    
}

# os labels 
os_labels = ['os','ss']
# sys labels
sys_labels = ['up','down']
# reg labels
reg_labels = ['pass','fail']
# dm labels
dm_labels = ['incl','1prong','DM0','DM1','3prong']

lib_histos = {
    'm_vis': [40,0,200],
    'pt_1' : [40,0,200],
    'pt_2' : [40,0,200],
    'eta_1': [24,-2.4,2.4],
    'eta_2': [25,-2.5,2.5],
    'met'  : [40,0,200],
    'mt_1' : [40,0,200],
    'dm_2' : [12,-0.5,11.5],
    'rawDeepTau2018v2p5VSmu_2' : [50,0.,1.]
}

etabins = {
    'eta0p0to0p4' : [0.0,0.4],
    'eta0p4to0p8' : [0.4,0.8],
    'eta0p8to1p2' : [0.8,1.2],
    'eta1p2to1p7' : [1.2,1.7],
    'eta1p7to2p5' : [1.7,2.5],
}

etaRanges1 = {
    'eta0p0to0p4' : [0.0,0.4],
    'eta0p4to0p8' : [0.4,0.8],
    'eta0p8to1p2' : [0.8,1.2],
    'eta1p2to1p7' : [1.2,1.7],
    'eta1p7to2p5' : [1.7,2.5],
}

etaRanges2 = {
    'eta0p0to0p4' : [0.0,0.4],
    'eta0p4to0p8' : [0.4,0.8],
    'eta0p8to1p2' : [0.8,1.2],
    'eta1p2to2p5' : [1.2,2.5],
}

etaTitle = {
    'eta0p0to0p4' : '|#eta|<0.4',
    'eta0p4to0p8' : '0.4<|#eta|<0.8',
    'eta0p8to1p2' : '0.8<|#eta|<1.2',
    'eta1p2to1p7' : '1.2<|#eta|<1.7',
    'eta1p7to2p5' : '1.7<|#eta|<2.5',
}

def defineSuffix(channel,era,wpVsJet,wpVsMu,wpVsE,applySF):
    suffix = f'{channel}_{era}_{wpVsJet}VsJet_{wpVsMu}VsMu_{wpVsE}VsE'
    if applySF:
        suffix += '_SF'
    return suffix

def rebinHisto(hist,bins,suffix):
    nbins = hist.GetNbinsX()
    newbins = len(bins)-1
    name = hist.GetName()+"_"+suffix
    newhist = ROOT.TH1D(name,"",newbins,array('d',list(bins)))
    for ib in range(1,nbins+1):
        centre = hist.GetBinCenter(ib)
        bin_id = newhist.FindBin(centre)
        xbin = hist.GetBinContent(ib)
        ebin = hist.GetBinError(ib)
        xnew = newhist.GetBinContent(bin_id)
        enew = newhist.GetBinError(bin_id)
        x_update = xbin + xnew;
        e_update = math.sqrt(ebin*ebin + enew*enew);
        newhist.SetBinContent(bin_id,x_update)
        newhist.SetBinError(bin_id,e_update)
    return newhist

def createBins(nbins,xmin,xmax):
    binwidth = (xmax-xmin)/float(nbins)
    bins = []
    for i in range(0,nbins+1):
        xb = xmin + float(i)*binwidth
        bins.append(xb)
    return bins

def zeroBinErrors(hist):
    nbins = hist.GetNbinsX()
    for i in range(1,nbins+1):
        hist.SetBinError(i,0.)

def zeroBinContentErrors(hist):
    nbins = hist.GetNbinsX()
    for i in range(1,nbins+1):
        hist.SetBinError(i,0.)
        hist.SetBinContent(i,0.)

def removeNegativeBins(hist):
    nbins = hist.GetNbinsX()
    for i in range(1,nbins+1):
        x = hist.GetBinContent(i)
        if x<0.1:
            hist.SetBinContent(i,0.1)
        
        
def createUnitHisto(hist,histName):
    nbins = hist.GetNbinsX()
    unitHist = hist.Clone(histName)
    for i in range(1,nbins+1):
        x = hist.GetBinContent(i)
        e = hist.GetBinError(i)
        if x>0:
            rat = e/x
            unitHist.SetBinContent(i,1.)
            unitHist.SetBinError(i,rat)
    return unitHist

def dividePassProbe(passHist,failHist,histName):
    nbins = passHist.GetNbinsX()
    hist = passHist.Clone(histName)
    for i in range(1,nbins+1):
        xpass = passHist.GetBinContent(i)
        epass = passHist.GetBinError(i)
        xfail = failHist.GetBinContent(i)
        efail = failHist.GetBinError(i)
        xprobe = xpass+xfail
        ratio = 1
        eratio = 0
        if xprobe>1e-4:
            ratio = xpass/xprobe
            dpass = xfail*epass/(xprobe*xprobe)
            dfail = xpass*efail/(xprobe*xprobe)
            eratio = math.sqrt(dpass*dpass+dfail*dfail)
        hist.SetBinContent(i,ratio)
        hist.SetBinError(i,eratio)
    return hist

def divideHistos(numHist,denHist,histName):
    nbins = numHist.GetNbinsX()
    hist = numHist.Clone(histName)
    for i in range(1,nbins+1):
        xNum = numHist.GetBinContent(i)
        eNum = numHist.GetBinError(i)
        xDen = denHist.GetBinContent(i)
        eDen = denHist.GetBinError(i)
        ratio = 0
        eratio = 0
        if xDen>1e-5 and xNum>1e-5:
            ratio = xNum/xDen
            rNum = eNum/xNum
            rDen = eDen/xDen
            rratio = math.sqrt(rNum*rNum+rDen*rDen)
            eratio = rratio * ratio
#        else:
#            ratio = 0.5*eNum/xDen
#            eratio = ratio
            
        hist.SetBinContent(i,ratio)
        hist.SetBinError(i,eratio)
    return hist

def histoRatio(numHist,denHist,histName):
    nbins = numHist.GetNbinsX()
    hist = numHist.Clone(histName)
    for i in range(1,nbins+1):
        xNum = numHist.GetBinContent(i)
        eNum = numHist.GetBinError(i)
        xDen = denHist.GetBinContent(i)
        ratio = 0
        eratio = 0
        if xNum>1e-7 and xDen>1e-7:
            ratio = xNum/xDen
            eratio = eNum/xDen
        hist.SetBinContent(i,ratio)
        hist.SetBinError(i,eratio)
    return hist

#######################################
# Creating shape systematic templates #
#######################################
def ComputeSystematics(h_central, h_sys, name):
    h_up = h_central.Clone(name+"Up")
    h_down = h_central.Clone(name+"Down")
    nbins = h_central.GetNbinsX()
    for i in range(1,nbins+1):
        x_up = h_sys.GetBinContent(i)
        x_central = h_central.GetBinContent(i)
        x_down = max(0,2.0*x_central-x_up)
        h_up.SetBinContent(i,x_up)
        h_down.SetBinContent(i,x_down)
    return h_up, h_down

