#!/bin/bash

########################################
# Strict error handling
########################################
set -e
set -o pipefail

########################################
# Configuration
########################################
ERA="UL2017"

# FULL TARGET GRID
WP_VS_JET=( "Tight" ) #Loose, Medium - already done  
WP_VS_MU=( "Tight" ) #VLoose ,  "Loose" "Medium" - already done
WP_VS_E=(  "VVLoose" ) # Tight
# error in tight loose tight combination- in extracting SFs- combine showed error: Best fit r: 1.28731  -1.28731/+18.7127  (68% CL)
# error in tight tight tight combination- in extracting SFs- combine showed error
#  --- FitDiagnostics ---
# Best fit r: 1.40834  -1.40834/+18.5917  (68% CL)
# 25 log messages saved to combine_logger.out

# Store logs and ScaleFactors in EOS
LOGDIR="/eos/user/s/svashish/MuTauFR/logs_${ERA}"
SF_DIR="/eos/user/s/svashish/MuTauFR/Scalefactors"
MERGED_SF_FILE="${SF_DIR}/${ERA}_ScaleFactors.root"

mkdir -p "${LOGDIR}"
mkdir -p "${SF_DIR}"

########################################
# Utility functions
########################################
timestamp() {
  date +"%Y-%m-%d %H:%M:%S"
}

run_step() {
  local STEP_NAME=$1
  local LOGFILE=$2
  shift 2

  echo "[$(timestamp)] Starting: ${STEP_NAME}"
  echo "Command: $@" | tee -a "${LOGFILE}"

  "$@" &>> "${LOGFILE}"

  echo "[$(timestamp)] Finished: ${STEP_NAME}"
  echo >> "${LOGFILE}"
}

wait_for_condor() {
  echo "[$(timestamp)] Waiting for Condor jobs to finish..."
  while true; do
    RUNNING=$(condor_q ${USER} -autoformat ClusterId | wc -l)
    if [ "${RUNNING}" -eq "0" ]; then
      echo "[$(timestamp)] Condor queue empty — continuing"
      break
    fi
    echo "[$(timestamp)] Condor jobs still running: ${RUNNING}"
    sleep 90
  done
}

already_done() {
  local key="${1}_${2}_${3}"
  case $key in
   Tight_Loose_Tight)
      return 0 ;;
    *) return 1 ;;
  esac
}

########################################
# Main loop
########################################
echo "==========================================" | tee "${LOGDIR}/master.log"
echo " MuTau Production Pipeline — ${ERA}" | tee -a "${LOGDIR}/master.log"
echo "==========================================" | tee -a "${LOGDIR}/master.log"

for wpJet in "${WP_VS_JET[@]}"; do
  for wpMu in "${WP_VS_MU[@]}"; do
    for wpE in "${WP_VS_E[@]}"; do

      # Skip already processed combinations
      if already_done "${wpJet}" "${wpMu}" "${wpE}"; then
        echo "Skipping already processed: ${wpJet} ${wpMu} ${wpE}" | tee -a "${LOGDIR}/master.log"
        continue
      fi

      TAG="Jet${wpJet}_Mu${wpMu}_E${wpE}"
      TAGLOG="${LOGDIR}/${TAG}.log"

      echo "==========================================" | tee -a "${LOGDIR}/master.log"
      echo " Running WP set: ${TAG}" | tee -a "${LOGDIR}/master.log"
      echo "==========================================" | tee -a "${LOGDIR}/master.log"

      ################################
      # Run selection + prepare Condor
      ################################
      run_step "RunSelectionMuTau" "${TAGLOG}" \
        ./scripts/RunSelectionMuTau.py --era "${ERA}" --wpVsMu "${wpMu}" --wpVsJet "${wpJet}" --wpVsE "${wpE}" --period 1000

      run_step "PrepareSubmit" "${TAGLOG}" \
        ./scripts/PrepareSubmit.py --era "${ERA}" --wpVsMu "${wpMu}" --wpVsJet "${wpJet}" --wpVsE "${wpE}"

      ################################
      # Automatic Condor submission
      ################################
      CONDOR_DIR="/afs/cern.ch/user/s/svashish/MuTauFR/condor/mutau_${ERA}_${wpJet}VsJet_${wpMu}VsMu_${wpE}VsE"
      SUBMIT_SCRIPT="${CONDOR_DIR}/submit.bash"

      if [ ! -f "${SUBMIT_SCRIPT}" ]; then
        echo "ERROR: submit.bash not found: ${SUBMIT_SCRIPT}" | tee -a "${TAGLOG}"
        exit 1
      fi

      run_step "CondorSubmit" "${TAGLOG}" bash "${SUBMIT_SCRIPT}"
      wait_for_condor

      ################################
      # Merge condor outputs
      ################################
      run_step "HaddSamples" "${TAGLOG}" \
        ./scripts/HaddSamples.py --era "${ERA}" --wpVsMu "${wpMu}" --wpVsJet "${wpJet}" --wpVsE "${wpE}"

      ################################
      # Control plots
      ################################
      run_step "ControlPlotsMuTau" "${TAGLOG}" \
        ./scripts/ControlPlotsMuTau.py --era "${ERA}" --wpVsMu "${wpMu}" --wpVsJet "${wpJet}" --wpVsE "${wpE}"

      ################################
      # Measurements + SF extraction
      ################################
      run_step "RunMeasurements" "${TAGLOG}" \
        ./scripts/RunMeasurements.py --era "${ERA}" --wpVsMu "${wpMu}" --wpVsJet "${wpJet}" --wpVsE "${wpE}"

      run_step "RunMeasurementsFit" "${TAGLOG}" \
        ./scripts/RunMeasurements.py --era "${ERA}" --wpVsMu "${wpMu}" --wpVsJet "${wpJet}" --wpVsE "${wpE}" --extractSF --runFit

      ################################
      # Plot MuTau
      ################################
      run_step "PlotMuTau" "${TAGLOG}" \
        ./scripts/PlotMuTau.py --era "${ERA}" --wpVsMu "${wpMu}" --wpVsJet "${wpJet}" --wpVsE "${wpE}"

      ################################
      # Extract ScaleFactors
      ################################
      run_step "ExtractScaleFactors" "${TAGLOG}" \
        ./scripts/ExtractScaleFactors.py --era "${ERA}" --wpVsMu "${wpMu}" --wpVsJet "${wpJet}" --wpVsE "${wpE}"

    done
  done
done

########################################
# Merge ALL ScaleFactors at the end
########################################
echo "[$(timestamp)] Merging all ScaleFactors into ${MERGED_SF_FILE}" | tee -a "${LOGDIR}/master.log"
hadd -f "${MERGED_SF_FILE}" "${SF_DIR}"/*.root &>> "${LOGDIR}/master.log"

########################################
# Final summary
########################################
echo "==========================================" | tee -a "${LOGDIR}/master.log"
echo " Production finished successfully" | tee -a "${LOGDIR}/master.log"
echo " Logs stored in: ${LOGDIR}" | tee -a "${LOGDIR}/master.log"
echo "==========================================" | tee -a "${LOGDIR}/master.log"