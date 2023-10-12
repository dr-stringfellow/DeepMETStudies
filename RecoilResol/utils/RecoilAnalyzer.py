from collections import OrderedDict
import sys
from CMSPLOTS.myFunction import getResolution, getErrors
from utils.utils import prepVars

class RecoilAnalyzer(object):
    """
    produce the response and resolution of different recoil estimators.
    To make use of the 'lazy' actions in RDataFrame, for all the responses and 
    resolutions, we try to 'prepare' them all together first, and then 'get' all 
    of them. In this case the event loop only need to be run once!
    """
    def __init__(self, rdf, recoils):
        self.rdf = rdf
        self.recoils = recoils
        self.profs = OrderedDict()
        self.histo2ds_paral_diff = OrderedDict()
        self.histo2ds_perp       = OrderedDict()
        self.histos1d_paral_diff = OrderedDict()
        self.histos1d_perp       = OrderedDict()

    def prepareVars(self):
        # prepare the paral, perp, paral_diff, response, etc 
        # vars with respect to u_GEN in RDataFrame 
        # for the response and resolution calculations
        for itype in self.recoils:
            self.rdf = prepVars(self.rdf, "u_{RECOIL}".format(RECOIL=itype), "u_GEN")

    def prepareResponses(self, xvar, xbins, option="s"):
        self.profs[xvar] = OrderedDict()
        # xbins should be numpy arrays
        nbins_x = xbins.size-1 
        for itype in self.recoils:
            hparal = "h_{RECOIL}_paral_VS_{XVAR}".format(RECOIL=itype, XVAR=xvar)
            print(hparal, hparal, nbins_x, xbins, option, xvar, "u_{RECOIL}_paral".format(RECOIL=itype))
            self.profs[xvar][itype] = self.rdf.Profile1D((hparal, hparal, nbins_x, xbins, option), xvar, "u_{RECOIL}_paral".format(RECOIL=itype))
        # add GEN
        hparal_Gen = "h_GEN_VS_{XVAR}".format(XVAR=xvar)
        self.profs[xvar]['GEN'] = self.rdf.Profile1D((hparal_Gen, hparal_Gen, nbins_x, xbins, option), xvar, "u_GEN_pt")

    def prepareResolutions(self, xvar, xbins, nbins_y, ymin, ymax, weight="1.0"):
        # for the resolutions
        # do both paral_diff and perp
        self.histo2ds_paral_diff[xvar] = OrderedDict()
        self.histo2ds_perp[xvar]       = OrderedDict()
        nbins_x = xbins.size-1
        for itype in self.recoils:
            h_paral_diff  = "h_{RECOIL}_paral_diff_VS_{XVAR}".format(RECOIL=itype, XVAR=xvar)
            h_perp        = "h_{RECOIL}_perp_VS_{XVAR}".format(RECOIL=itype, XVAR=xvar)

            self.histo2ds_paral_diff[xvar][itype] = self.rdf.Histo2D((h_paral_diff, h_paral_diff, nbins_x, xbins, nbins_y, ymin, ymax), xvar, "u_{RECOIL}_paral_diff".format(RECOIL=itype))
            self.histo2ds_perp[xvar][itype]       = self.rdf.Histo2D((h_perp,       h_perp,       nbins_x, xbins, nbins_y, ymin, ymax), xvar, "u_{RECOIL}_perp".format(RECOIL=itype))

    def getResponses(self, xvar):
        hresponses = OrderedDict()
        for itype in self.recoils:
            print(xvar, itype)
            hresponses[itype] = self.profs[xvar][itype].Clone( self.profs[xvar][itype].GetName()+ "_response" )
            hresponses[itype].Divide( self.profs[xvar]['GEN'].GetValue() )
        return hresponses
            

    def getResolutions(self, xvar):
        hresols_paral = OrderedDict()
        hresols_perp  = OrderedDict()
        for itype in self.recoils:
            hresols_paral[itype] = getResolution( self.histo2ds_paral_diff[xvar][itype] )
            hresols_perp[itype]  = getResolution( self.histo2ds_perp[xvar][itype] )
        return hresols_paral, hresols_perp

    def prepareResolutions1D(self, nbins_x, xmin, xmax):
        for itype in self.recoils:
            h_paral_diff_1D = "h_{RECOIL}_paral_diff_1D".format(RECOIL=itype)
            h_perp_1D = "h_{RECOIL}_perp_1D".format(RECOIL=itype)

            self.histos1d_paral_diff[itype] = self.rdf.Histo1D((h_paral_diff_1D, h_paral_diff_1D, nbins_x, xmin, xmax), "u_{RECOIL}_paral_diff".format(RECOIL=itype))
            self.histos1d_perp[itype]       = self.rdf.Histo1D((h_perp_1D,       h_perp_1D,       nbins_x, xmin, xmax), "u_{RECOIL}_perp".format(RECOIL=itype))
            #for b in range(self.histos1d_perp[itype].GetNbinsX()):
            #    print(b)

    def getResolutions1D(self):
        vresols_paral = OrderedDict()
        vresols_perp  = OrderedDict()
        import numpy as np
        probs = np.array([0.50, 0.16, 0.84])
        quants = np.array([0., 0., 0.])

        for itype in self.recoils:
            self.histos1d_paral_diff[itype].GetQuantiles(3, quants, probs)
            vresols_paral[itype] = (quants[0], (quants[2]-quants[1])/2.0, quants[0]-quants[1], quants[2]-quants[0])

            self.histos1d_perp[itype].GetQuantiles(3, quants, probs)
            vresols_perp[itype] = (quants[0], (quants[2]-quants[1])/2.0, quants[0]-quants[1], quants[2]-quants[0])
    
        return vresols_paral, vresols_perp

