#!/bin/tcsh
cd /afs/cern.ch/user/s/svashish/CMSSW_14_1_0_pre4/src
setenv SCRAM_ARCH el9_amd64_gcc10
#export SCRAM_ARCH=el9_amd64_gcc10
cmsenv
cd TauFW/Fitter/MuTauFR
echo $PWD
./scripts/RunSelectionMuTau.py --era UL2017 --sample SingleMuon_Run2017F --start 0 --period 10000000 --wpVsJet Tight --wpVsMu Loose --wpVsE Tight
