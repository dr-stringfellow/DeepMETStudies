import ROOT
import sys
from CMSPLOTS.myFunction import DrawHistos
from collections import OrderedDict
from utils.utils import getpTBins, getnVtxBins, get_response_code
from utils.RecoilAnalyzer import RecoilAnalyzer
import argparse

ROOT.gROOT.SetBatch(True)

ROOT.ROOT.EnableImplicitMT(10)

ROOT.gSystem.Load("Functions_cc.so")

parser = argparse.ArgumentParser()
parser.add_argument("--era", default="2016", help="Era")
parser.add_argument("--applySc", action="store_true", help="Apply response corrections and include the plots in the output")
parser.add_argument("--no-applySc", action="store_false", dest="applySc", help="Do not apply response corrections and do not include the plots in the output")
parser.set_defaults(applySc=True)

args = parser.parse_args()

doTest = (args.era == "test")
do2016 = (args.era == "2016")
do2017 = (args.era == "2017")
do2018 = (args.era == "2018")
do2022 = (args.era == "2022")

assert doTest + do2016 + do2017 + do2018 + do2022 == 1, "Please specify an era: test, 2016, 2017, 2018"

era = args.era
basedir = "/stash/user/bmaier/public/metpaper/ntuples/nAODv9/"
outdir = f"/stash/user/bmaier/public/metpaper/plots/Data/{era}"

applySc = args.applySc
print("apply Response corrections: ", applySc)

#rdf = ROOT.ROOT.RDataFrame("Events", "/eos/cms/store/user/yofeng/WRecoilNanoAOD_Skimmed_v10_tempMET/myNanoProdMc2016_NANO_[1-9]_Skim.root")
if doTest:
   chain = ROOT.TChain("Events")
   chain.Add("/eos/uscms/store/user/lpcsusyhiggs/ntuples/nAODv9/2016/SingleMuon_Run2016G/all_SingleMuon_Run2016G_file070_part_*_Muons.root")
   rdf_org = ROOT.ROOT.RDataFrame(chain)
   rdf_org1 = rdf_org.Filter("(HLT_IsoMu24 || HLT_IsoTkMu24)")
if do2016:
   chain = ROOT.TChain("Events")
   chain.Add("/eos/uscms/store/user/lpcsusyhiggs/ntuples/nAODv9/2016/SingleMuon_Run2016G/*root")
   chain.Add("/eos/uscms/store/user/lpcsusyhiggs/ntuples/nAODv9/2016/SingleMuon_Run2016H/*root")
   rdf_org = ROOT.ROOT.RDataFrame(chain)
   rdf_org1 = rdf_org.Filter("(HLT_IsoMu24 || HLT_IsoTkMu24)")
elif do2017:
   chain = ROOT.TChain("Events")
   chain.Add(basedir+"/"+args.era+"/SingleMuon_Run2017B/*root")
   #chain.Add(basedir+"/"+args.era+"/SingleMuon_Run2017C/*root")
   #chain.Add(basedir+"/"+args.era+"/SingleMuon_Run2017D/*root")
   #chain.Add(basedir+"/"+args.era+"/SingleMuon_Run2017E/*root")
   #chain.Add(basedir+"/"+args.era+"/SingleMuon_Run2017F/*root")
   rdf_org = ROOT.ROOT.RDataFrame(chain)
   rdf_org1 = rdf_org.Filter("HLT_IsoMu27")
elif do2018:
   chain = ROOT.TChain("Events")
   chain.Add("/eos/uscms/store/user/lpcsusyhiggs/ntuples/nAODv9/2018/SingleMuon_Run2018A/*root")
   chain.Add("/eos/uscms/store/user/lpcsusyhiggs/ntuples/nAODv9/2018/SingleMuon_Run2018B/*root")
   chain.Add("/eos/uscms/store/user/lpcsusyhiggs/ntuples/nAODv9/2018/SingleMuon_Run2018C/*root")
   chain.Add("/eos/uscms/store/user/lpcsusyhiggs/ntuples/nAODv9/2018/SingleMuon_Run2018D/*root")
   rdf_org = ROOT.ROOT.RDataFrame(chain)
   rdf_org1 = rdf_org.Filter("HLT_IsoMu27 || HLT_IsoMu30")
elif do2022:
   chain = ROOT.TChain("Events")
   chain.Add("/uscms_data/d3/yfeng/nano/*root")
   rdf_org = ROOT.ROOT.RDataFrame(chain)
   rdf_org1 = rdf_org.Filter("HLT_IsoMu27")

rdf_org2 = rdf_org1.Filter("nMuon > 1")
#rdf_org2 = rdf_org2.Define("Muon_pass0", "Muon_pt[0] > 25.0 && abs(Muon_eta[0]) < 2.4 && abs(Muon_dxy[0]) < 0.05 && abs(Muon_dz[0]) < 0.10 && Muon_pfRelIso04_all[0] < 0.15 && Muon_tightId[0]")
#rdf_org2 = rdf_org2.Define("Muon_pass1", "Muon_pt[1] > 25.0 && abs(Muon_eta[1]) < 2.4 && abs(Muon_dxy[1]) < 0.05 && abs(Muon_dz[1]) < 0.10 && Muon_pfRelIso04_all[1] < 0.15 && Muon_tightId[1]")
rdf_org2 = rdf_org2.Define("Muon_pass0", "Muon_pt[0] > 30.0 && abs(Muon_eta[0]) < 2.4 && Muon_tightId[0]")
rdf_org2 = rdf_org2.Define("Muon_pass1", "Muon_pt[1] > 30.0 && abs(Muon_eta[1]) < 2.4 && Muon_tightId[1]")

rdf_org3 = rdf_org2.Filter("Muon_pass0 && Muon_pass1")
#rdf = rdf_org1.Define("Muon_pt0", "Muon_pt[0]").Filter("Muon_pt0 > 25.0")

rdf3 = rdf_org3.Define("Mass", "TMath::Sqrt(2*Muon_pt[0]*Muon_pt[1]*(TMath::CosH(Muon_eta[0]-Muon_eta[1]) - TMath::Cos(Muon_phi[0]-Muon_phi[1])))")

rdf = rdf3.Filter("Mass > 80.0 && Mass < 100.0")

rdf = rdf.Define("pT_muons", "TMath::Sqrt(Muon_pt[0]*Muon_pt[0] + Muon_pt[1]*Muon_pt[1] + 2*Muon_pt[0]*Muon_pt[1]*TMath::Cos(Muon_phi[0]-Muon_phi[1]))")
rdf = rdf.Define("phi_muons", "TMath::ATan2(Muon_pt[0]*TMath::Sin(Muon_phi[0]) + Muon_pt[1]*TMath::Sin(Muon_phi[1]), Muon_pt[0]*TMath::Cos(Muon_phi[0]) + Muon_pt[1]*TMath::Cos(Muon_phi[1]))")

rdf = rdf.Define("GenMET_pt", "0.").Define("GenMET_phi", "0.")

rdf = rdf.Define("u_PUPPI_x",  "-(pT_muons*TMath::Cos(phi_muons) + PuppiMET_pt*TMath::Cos(PuppiMET_phi))") \
         .Define("u_PUPPI_y",  "-(pT_muons*TMath::Sin(phi_muons) + PuppiMET_pt*TMath::Sin(PuppiMET_phi))") \
         .Define("u_PUPPI_pt", "TMath::Sqrt(u_PUPPI_x * u_PUPPI_x + u_PUPPI_y * u_PUPPI_y)") \
         .Define("u_PF_x",     "-(pT_muons*TMath::Cos(phi_muons) + MET_pt*TMath::Cos(MET_phi))") \
         .Define("u_PF_y",     "-(pT_muons*TMath::Sin(phi_muons) + MET_pt*TMath::Sin(MET_phi))") \
         .Define("u_PF_pt",    "TMath::Sqrt(u_PF_x * u_PF_x + u_PF_y * u_PF_y)") \
         .Define("u_GEN_x",    "-(pT_muons * TMath::Cos(phi_muons) + GenMET_pt * TMath::Cos(GenMET_phi))") \
         .Define("u_GEN_y",    "-(pT_muons * TMath::Sin(phi_muons) + GenMET_pt * TMath::Sin(GenMET_phi))") \
         .Define("u_GEN_pt",   "TMath::Sqrt(u_GEN_x * u_GEN_x + u_GEN_y * u_GEN_y)") \
         .Define("u_DeepMET_x",  "-(pT_muons*TMath::Cos(phi_muons) + DeepMETResolutionTune_pt*TMath::Cos(DeepMETResolutionTune_phi))") \
         .Define("u_DeepMET_y",  "-(pT_muons*TMath::Sin(phi_muons) + DeepMETResolutionTune_pt*TMath::Sin(DeepMETResolutionTune_phi))") \
         .Define("u_DeepMET_pt", "TMath::Sqrt(u_DeepMET_x * u_DeepMET_x + u_DeepMET_y * u_DeepMET_y)")

recoils = ["PUPPI", "PF", "DeepMET"]
if do2022:
   recoils = ["PUPPI", "DeepMET"]

colors = {
            "PF": 1,
            "PUPPI": 2,
            "GEN": 6,
            "DeepMET": 4,
         }

labels = {
            "TK": "TK",
            "PF": "PF",
            "PUPPI": "PUPPI",
            "GEN": "GEN",
            "TKPHO": "TK+Photon",
            "DeepMET": "DeepMET",
         }

xbins_qT = getpTBins()
xbins_nVtx = getnVtxBins() 

recoilanalyzer = RecoilAnalyzer(rdf, recoils)
recoilanalyzer.prepareVars()
recoilanalyzer.prepareResponses(   'u_GEN_pt', xbins_qT)
recoilanalyzer.prepareResolutions( 'u_GEN_pt', xbins_qT, 400, -600, 600)
recoilanalyzer.prepareResponses(   'PV_npvsGood', xbins_nVtx)
recoilanalyzer.prepareResolutions( 'PV_npvsGood', xbins_nVtx, 400, -600, 600)

hresponses = recoilanalyzer.getResponses('u_GEN_pt')
hresols_paral_diff, hresols_perp = recoilanalyzer.getResolutions('u_GEN_pt')
hresponses_nVtx = recoilanalyzer.getResponses('PV_npvsGood')
hresols_paral_diff_VS_nVtx, hresols_perp_VS_nVtx = recoilanalyzer.getResolutions('PV_npvsGood')


if applySc:
   ROOT.gInterpreter.Declare(get_response_code)
   # create branch with the scale factors
   for itype in recoils:
       #"dynamic scopes" to create a variable holding histograms
       ROOT.gInterpreter.ProcessLine("auto hprof_{RECOIL}= {HNAME} ".format(RECOIL=itype, HNAME=hresponses[itype].GetName()))
       rdf = rdf.Define("{RECOIL}_scale".format(RECOIL=itype), '1.0/get_response(u_GEN_pt, hprof_{RECOIL})'.format(RECOIL=itype)) \
                .Define("u_{RECOIL}Sc_x".format(RECOIL=itype), "{RECOIL}_scale * u_{RECOIL}_x".format(RECOIL=itype)) \
                .Define("u_{RECOIL}Sc_y".format(RECOIL=itype), "{RECOIL}_scale * u_{RECOIL}_y".format(RECOIL=itype))

   #for itype in recoils:
   #    # prepare the paral, perp, response, diff variables
   #    rdf = prepVars(rdf, "u_{RECOIL}Sc".format(RECOIL=itype), "u_GEN")

   recoilsSc = [itype + "Sc" for itype in recoils]
   recoilanalyzerSc = RecoilAnalyzer(rdf, recoilsSc)
   recoilanalyzerSc.prepareVars()
   recoilanalyzerSc.prepareResponses(   'u_GEN_pt', xbins_qT)
   recoilanalyzerSc.prepareResolutions( 'u_GEN_pt', xbins_qT, 400, -200, 200)
   recoilanalyzerSc.prepareResponses(   'PV_npvsGood', xbins_nVtx)
   recoilanalyzerSc.prepareResolutions( 'PV_npvsGood', xbins_nVtx, 400, -200, 200)

   hresponsesSc = recoilanalyzerSc.getResponses('u_GEN_pt')
   hresolsSc_paral_diff, hresolsSc_perp = recoilanalyzerSc.getResolutions('u_GEN_pt')
   hresponsesSc_nVtx = recoilanalyzerSc.getResponses('PV_npvsGood')
   hresolsSc_paral_diff_VS_nVtx, hresolsSc_perp_VS_nVtx = recoilanalyzerSc.getResolutions('PV_npvsGood')

hresponsesSc = recoilanalyzerSc.getResponses('u_GEN_pt')
hresolsSc_paral_diff, hresolsSc_perp = recoilanalyzerSc.getResolutions('u_GEN_pt')
hresponsesSc_nVtx = recoilanalyzerSc.getResponses('PV_npvsGood')
hresolsSc_paral_diff_VS_nVtx, hresolsSc_perp_VS_nVtx = recoilanalyzerSc.getResolutions('PV_npvsGood')

qtmax = 500.0

DrawHistos(hresponses.values(), [labels[itype] for itype in hresponses.keys()], 0, qtmax, "q_{T} [GeV]", 0., 1.15, "Reponse -<u_{#parallel}>/<q_{T}>", "reco_recoil_response", drawashist=True, dology=False, legendPos=[0.70, 0.17, 0.88, 0.36], mycolors=[colors[itype] for itype in hresponses.keys()], noLumi=True, outdir=outdir)

DrawHistos(hresols_paral_diff.values(), [labels[itype] for itype in hresols_paral_diff.keys()], 0, qtmax, "q_{T} [GeV]", 0, 39.0, "#sigma u_{#parallel} [GeV]", "reco_recoil_resol_paral", drawashist=True, dology=False, legendPos=[0.20, 0.73, 0.38, 0.92], mycolors=[colors[itype] for itype in hresols_paral_diff.keys()], noLumi=True, outdir=outdir)

DrawHistos(hresols_perp.values(), [labels[itype] for itype in hresols_perp.keys()], 0, qtmax, "q_{T} [GeV]", 0, 32.0, "#sigma u_{#perp } [GeV]", "reco_recoil_resol_perp", drawashist=True, dology=False, legendPos=[0.20, 0.73, 0.40, 0.92], mycolors=[colors[itype] for itype in hresols_perp.keys()], noLumi=True, outdir=outdir)

DrawHistos(hresponses_nVtx.values(), [labels[itype] for itype in hresponses_nVtx.keys()], 0, 65., "# Vertices", 0., 1.15, "Reponse -<u_{#parallel}>/<q_{T}>", "reco_recoil_response_VS_nVtx", drawashist=True, dology=False, legendPos=[0.70, 0.17, 0.88, 0.36], mycolors=[colors[itype] for itype in hresponses.keys()], noLumi=True, outdir=outdir)

DrawHistos(hresols_paral_diff_VS_nVtx.values(), [labels[itype] for itype in hresols_paral_diff_VS_nVtx.keys()], 0, 65., "# Vertices", 0, 30.0, "#sigma u_{#parallel} [GeV]", "reco_recoil_resol_paral_VS_nVtx", drawashist=True, dology=False, legendPos=[0.20, 0.73, 0.38, 0.92], mycolors=[colors[itype] for itype in hresols_paral_diff_VS_nVtx.keys()], noLumi=True, outdir=outdir)

DrawHistos(hresols_perp_VS_nVtx.values(), [labels[itype] for itype in hresols_perp_VS_nVtx.keys()], 0, 65., "# Vertices", 0, 30.0, "#sigma u_{#perp } [GeV]", "reco_recoil_resol_perp_VS_nVtx", drawashist=True, dology=False, legendPos=[0.20, 0.73, 0.40, 0.92], mycolors=[colors[itype] for itype in hresols_perp_VS_nVtx.keys()], noLumi=True, outdir=outdir)

<<<<<<< HEAD
##
## Scaled 
##
DrawHistos(hresponsesSc.values(), [labels[itype] for itype in hresponses.keys()], 0, qtmax, "q_{T} [GeV]", 0., 1.15, "Scaled Reponse -<u_{#parallel}>/<q_{T}>", "reco_recoil_response_Scaled", drawashist=True, dology=False, legendPos=[0.70, 0.17, 0.88, 0.36], mycolors=[colors[itype] for itype in hresponses.keys()], noLumi=True, outdir=outdir)
#
DrawHistos(hresolsSc_paral_diff.values(), [labels[itype] for itype in hresols_paral_diff.keys()], 0, qtmax, "q_{T} [GeV]", 0, 60.0, "Scaled #sigma u_{#parallel} [GeV]", "reco_recoil_resol_paral_Scaled", drawashist=True, dology=False, legendPos=[0.20, 0.73, 0.38, 0.92], mycolors=[colors[itype] for itype in hresols_paral_diff.keys()], noLumi=True, outdir=outdir)
#
DrawHistos(hresolsSc_perp.values(), [labels[itype] for itype in hresols_perp.keys()], 0, qtmax, "q_{T} [GeV]", 0, 50.0, "Scaled #sigma u_{#perp} [GeV]", "reco_recoil_resol_perp_Scaled", drawashist=True, dology=False, legendPos=[0.20, 0.73, 0.40, 0.92], mycolors=[colors[itype] for itype in hresols_perp.keys()], noLumi=True, outdir=outdir)
#
DrawHistos(hresponsesSc_nVtx.values(), [labels[itype] for itype in hresponses_nVtx.keys()], 0, 50., "# Vertices", 0., 1.15, "Scaled Reponse -<u_{#parallel}>/<q_{T}>", "reco_recoil_response_VS_nVtx_Scaled", drawashist=True, dology=False, legendPos=[0.70, 0.17, 0.88, 0.36], mycolors=[colors[itype] for itype in hresponses.keys()], noLumi=True, outdir=outdir)
#
DrawHistos(hresolsSc_paral_diff_VS_nVtx.values(), [labels[itype] for itype in hresols_paral_diff_VS_nVtx.keys()], 0, 50., "# Vertices", 0, 50.0, "Scaled #sigma u_{#parallel} [GeV]", "reco_recoil_resol_paral_VS_nVtx_Scaled", drawashist=True, dology=False, legendPos=[0.20, 0.73, 0.38, 0.92], mycolors=[colors[itype] for itype in hresols_paral_diff_VS_nVtx.keys()], noLumi=True, outdir=outdir)
#
DrawHistos(hresolsSc_perp_VS_nVtx.values(), [labels[itype] for itype in hresols_perp_VS_nVtx.keys()], 0, 50., "# Vertices", 0, 50.0, "Scaled #sigma u_{#perp} [GeV]", "reco_recoil_resol_perp_VS_nVtx_Scaled", drawashist=True, dology=False, legendPos=[0.20, 0.73, 0.40, 0.92], mycolors=[colors[itype] for itype in hresols_perp_VS_nVtx.keys()], noLumi=True, outdir=outdir)
=======
if applySc:
   #
   # Scaled 
   #
   DrawHistos(hresponsesSc.values(), [labels[itype] for itype in hresponses.keys()], 0, qtmax, "q_{T} [GeV]", 0., 1.15, "Scaled Reponse -<u_{#parallel}>/<q_{T}>", "reco_recoil_response_Scaled", drawashist=True, dology=False, legendPos=[0.70, 0.17, 0.88, 0.36], mycolors=[colors[itype] for itype in hresponses.keys()], noLumi=True, outdir=outdir)

   DrawHistos(hresolsSc_paral_diff.values(), [labels[itype] for itype in hresols_paral_diff.keys()], 0, qtmax, "q_{T} [GeV]", 0, 60.0, "Scaled #sigma u_{#parallel} [GeV]", "reco_recoil_resol_paral_Scaled", drawashist=True, dology=False, legendPos=[0.20, 0.73, 0.38, 0.92], mycolors=[colors[itype] for itype in hresols_paral_diff.keys()], noLumi=True, outdir=outdir)

   DrawHistos(hresolsSc_perp.values(), [labels[itype] for itype in hresols_perp.keys()], 0, qtmax, "q_{T} [GeV]", 0, 50.0, "Scaled #sigma u_{#perp} [GeV]", "reco_recoil_resol_perp_Scaled", drawashist=True, dology=False, legendPos=[0.20, 0.73, 0.40, 0.92], mycolors=[colors[itype] for itype in hresols_perp.keys()], noLumi=True, outdir=outdir)

   DrawHistos(hresponsesSc_nVtx.values(), [labels[itype] for itype in hresponses_nVtx.keys()], 0, 50., "# Vertices", 0., 1.15, "Scaled Reponse -<u_{#parallel}>/<q_{T}>", "reco_recoil_response_VS_nVtx_Scaled", drawashist=True, dology=False, legendPos=[0.70, 0.17, 0.88, 0.36], mycolors=[colors[itype] for itype in hresponses.keys()], noLumi=True, outdir=outdir)

   DrawHistos(hresolsSc_paral_diff_VS_nVtx.values(), [labels[itype] for itype in hresols_paral_diff_VS_nVtx.keys()], 0, 50., "# Vertices", 0, 50.0, "Scaled #sigma u_{#parallel} [GeV]", "reco_recoil_resol_paral_VS_nVtx_Scaled", drawashist=True, dology=False, legendPos=[0.20, 0.73, 0.38, 0.92], mycolors=[colors[itype] for itype in hresols_paral_diff_VS_nVtx.keys()], noLumi=True, outdir=outdir)

   DrawHistos(hresolsSc_perp_VS_nVtx.values(), [labels[itype] for itype in hresols_perp_VS_nVtx.keys()], 0, 50., "# Vertices", 0, 50.0, "Scaled #sigma u_{#perp} [GeV]", "reco_recoil_resol_perp_VS_nVtx_Scaled", drawashist=True, dology=False, legendPos=[0.20, 0.73, 0.40, 0.92], mycolors=[colors[itype] for itype in hresols_perp_VS_nVtx.keys()], noLumi=True, outdir=outdir)
>>>>>>> 704f681e09bd114efd4a88e2166f8d5d88e8914e


#f1 = ROOT.TFile("root_h/output.root", "RECREATE")
#for h2 in h2ds_perp_VS_qT.values():
#    h2.SetDirectory(f1)
#    h2.Write()
#f1.Close()
