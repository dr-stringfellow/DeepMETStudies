'''
some useful functions to sync the pt and nvtx bins,
and prepare some variables (uparal, uperp, responses, and paral_diff) 
for the RDataFrame
'''
def getpTBins():
    import numpy as np
    '''
    xbins_qT = np.zeros(18)
    for ibin in range(0,4):
        xbins_qT[ibin] = 5*ibin
    for ibin in range(4,8):
        xbins_qT[ibin] = 10*ibin-20
    for ibin in range(8,13):
        xbins_qT[ibin] = 20*ibin-100
    for ibin in range(13,18):
        xbins_qT[ibin] = 30*ibin-230
    '''
    xbins_qT = np.array([0., 20., 40., 60., 80., 100., 120., 160., 200., 300., 500.])
    return xbins_qT

def getnVtxBins():
    import numpy as np
    #xbins_nVtx = np.array([0.,5.5, 7.5, 9.5, 11.5, 13.5, 15.5, 17.5, 19.5, 21.5, 23.5, 25.5, 27.5, 29.5, 31.5, 33.5, 38.5, 43.5, 50.5])
    #xbins_nVtx = np.array([0.,5.5, 7.5, 9.5, 11.5, 13.5, 15.5, 17.5, 19.5, 21.5, 23.5, 27.5, 31.5, 35.5, 40.5, 50.5, 60.5])
    xbins_nVtx = np.array([0.,10.,20.,30.,40.,50.,60.])
    return xbins_nVtx

def prepVars(rdf, u, utruth):
    """
    prepare the u_paral, perp, response and paral_diff variables
    """
    f_uparal = "( {U}_x * {UTRUTH}_x + {U}_y * {UTRUTH}_y ) / {UTRUTH}_pt".format(U=u, UTRUTH=utruth)
    f_uperp  = "(-{U}_x * {UTRUTH}_y + {U}_y * {UTRUTH}_x ) / {UTRUTH}_pt".format(U=u, UTRUTH=utruth)
    f_ureponse    = "{U}_paral / {UTRUTH}_pt".format(U=u, UTRUTH=utruth)
    f_uparal_diff = "{U}_paral - {UTRUTH}_pt".format(U=u, UTRUTH=utruth)

    rdf = rdf.Define("{U}_paral"     .format(U=u),     f_uparal ) \
             .Define("{U}_perp"      .format(U=u),     f_uperp  ) \
             .Define("{U}_response"  .format(U=u),     f_ureponse ) \
             .Define("{U}_paral_diff".format(U=u),     f_uparal_diff)

    return rdf
    
get_response_code = '''
float get_response(float qt, TProfile* h_response)
{
    int maxbin = h_response->GetNbinsX();
    int ibin = h_response->FindBin( qt );
    if( ibin>maxbin ){
        ibin = maxbin;
    }
    return h_response->GetBinContent( ibin );
}
'''
