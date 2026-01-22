#! /usr/bin/env python3
# Author: Alexei Raspereza (October 2025)
# mu->tau FR SF measurement
# Plotting scale factors 
import ROOT
import math
import TauFW.Fitter.MuTauFR.utils as utils
import TauFW.Fitter.MuTauFR.styles as styles
import TauFW.Fitter.MuTauFR.analysisMuTauFR as analysis
from array import array
import os
from TauFW.Plotter.plot.utils import ensuredir

#################################
#     definition of cuts        #
#################################

colors = [ROOT.kBlack,ROOT.kRed,ROOT.kBlue,ROOT.kGreen]
markers = [20,21,22,23]

def Plot(hists, suffix, **kwargs):

    era = kwargs.get('era','2024')
    coarse = kwargs.get('coarse',False)
    
    i = 0
    for hist in hists:
        hists[hist].GetYaxis().SetRangeUser(0.,2.5)
        styles.InitData(hists[hist])
        hists[hist].SetMarkerColor(colors[i % len(colors)])
        hists[hist].SetLineColor(colors[i % len(colors)])
        hists[hist].SetMarkerStyle(markers[i % len(markers)])
        i += 1
              
    # canvas and pads
    canvas = styles.MakeCanvas("canv","",600,600)

    isFirst = True
    for hist in hists:
        if isFirst:
            hists[hist].Draw('e1')
            isFirst = False
        else:
            hists[hist].Draw('e1same')
    
    leg = ROOT.TLegend(0.23,0.2,0.5,0.4)
    styles.SetLegendStyle(leg)
    leg.SetTextSize(0.03)
    for hist in hists:
        leg.AddEntry(hists[hist],hist,'lp')
    leg.Draw()

    text = ROOT.TText(0.22,0.83,'%s'%(suffix))
    text.SetTextSize(0.045)
    text.SetNDC()
    text.Draw()
    
    styles.CMS_label(canvas,era=era)

    canvas.Modified()
    canvas.RedrawAxis()
    canvas.Update()
    print('')
    print('Creating SF plot')

    outfolder = ensuredir(utils.figuresFolder+'/ScaleFactors')
    outfile = '%s/SF_%s_%s.png'%(outfolder,era,suffix)
    if coarse:
        outfile = '%s/SF_%s_%s_coarse.png'%(outfolder,era,suffix)
    canvas.Print(outfile)
    
def get_hist(inputFile, wpJet, wpMu, wpE):
    name = '%sVsJet_%sVsMu_%sVsE' % (wpJet, wpMu, wpE)
    hist = inputFile.Get('muTauFR_' + name)
    if not hist:
        print("WARNING: Missing histogram:", name)
        return None
    return hist

############
#   MAIN   #
############

if __name__ == "__main__":

    styles.InitROOT()
    styles.SetStyle()

    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-e', '--era', dest='era', default='UL2017', choices=['2024','2015','UL2017','UL2016_preVFP','UL2016_postVFP'])
    parser.add_argument('-discr','--discr',dest='discr',default='VsMu',choices=['VsMu','VsJet','VsE'])
    parser.add_argument('-coarse','--coarse',dest='coarse',action='store_true') # coarse binning
    parser.add_argument('--single', dest='single', action='store_true', help='Produce one plot per WP combination')

    args = parser.parse_args()

    era = args.era
    coarse = args.coarse
    wpVsJet = ['Loose', 'Medium', 'Tight']
    wpVsE   = ['VVLoose', 'Loose', 'Medium', 'Tight']
    wpVsMu  = ['VLoose', 'Tight']

    cmssw_base = os.getenv('CMSSW_BASE')
    filename = '%s/src/TauFW/Fitter/MuTauFR/ScaleFactors/%s_ScaleFactors.root'%(cmssw_base,era)
    if coarse:
        filename = '%s/src/TauFW/Fitter/MuTauFR/ScaleFactors/%s_ScaleFactors_coarse.root'%(cmssw_base,era)
    if os.path.isfile(filename):
        print('opening file %s'%(filename))
    else:
        print('file %s is not found'%(filename))
        print('Extract and dump scale factors for all considered WPs to RooT files and merge all files for one era into one...')
        exit()

    inputFile = ROOT.TFile(filename,'READ')

    # -------------------------------
    # SINGLE PLOTS MODE (one plot per combination)
    # -------------------------------
    if args.single:

        for jet in wpVsJet:
            for ele in wpVsE:
                for mu in wpVsMu:

                    hist = get_hist(inputFile, jet, mu, ele)
                    if not hist:
                        continue

                    suffix = '%sVsJet_%sVsMu_%sVsE' % (jet, mu, ele)

                    hdict = {}
                    hdict['FR'] = hist

                    print("Plotting single:", suffix)

                    Plot(hdict,
                         suffix=suffix,
                         era=era,
                         coarse=coarse)

    # ------------------------------------
    # MERGED MODE (VsMu / VsJet / VsE)
    # ------------------------------------
    else:

        if args.discr == 'VsMu':
            scanwps = wpVsMu
            fixedJets = wpVsJet
            fixedEs   = wpVsE

            for jet in fixedJets:
                for ele in fixedEs:

                    hists = {}

                    for mu in scanwps:
                        hist = get_hist(inputFile, jet, mu, ele)
                        if not hist:
                            continue

                        hname = mu + 'VsMu'
                        hists[hname] = hist

                    suffix = '%sVsJet_%sVsE' % (jet, ele)

                    print("Plotting merged VsMu:", suffix)

                    Plot(hists,
                         suffix=suffix,
                         era=era,
                         coarse=coarse)

        elif args.discr == 'VsJet':
            print("VsJet merging not implemented yet")

        elif args.discr == 'VsE':
            print("VsE merging not implemented yet")