#!/usr/bin/env python
# Time-stamp: <2019-09-25 14:44:07 taoliu>

import unittest
import StringIO
from numpy.testing import assert_equal,  assert_almost_equal, assert_array_equal

from MACS2.IO.ScoreTrack import *

class Test_TwoConditionScores(unittest.TestCase):

    def setUp(self):
        self.t1bdg = bedGraphTrackI()
        self.t2bdg = bedGraphTrackI()
        self.c1bdg = bedGraphTrackI()
        self.c2bdg = bedGraphTrackI()
        self.test_regions1 = [("chrY",0,70,0.00,0.01),
                              ("chrY",70,80,7.00,0.5),
                              ("chrY",80,150,0.00,0.02)]
        self.test_regions2 = [("chrY",0,75,20.0,4.00),
                              ("chrY",75,90,35.0,6.00),
                              ("chrY",90,150,10.0,15.00)]
        for a in self.test_regions1:
            self.t1bdg.safe_add_loc(a[0],a[1],a[2],a[3])
            self.c1bdg.safe_add_loc(a[0],a[1],a[2],a[4])

        for a in self.test_regions2:
            self.t2bdg.safe_add_loc(a[0],a[1],a[2],a[3])
            self.c2bdg.safe_add_loc(a[0],a[1],a[2],a[4])

        self.twoconditionscore = ScoreTrack.TwoConditionScores( self.t1bdg,
                                                                self.c1bdg,
                                                                self.t2bdg,
                                                                self.c2bdg,
                                                                1.0,
                                                                1.0 )
        self.twoconditionscore.build()
        self.twoconditionscore.finalize()
        (self.cat1,self.cat2,self.cat3) = twoconditionscore.call_peaks(min_length=10, max_gap=10, cutoff=3)

            
class Test_ScoreTrackII(unittest.TestCase):

    def setUp(self):
        # for initiate scoretrack
        self.test_regions1 = [("chrY",10,100,10),
                              ("chrY",60,10,10),
                              ("chrY",110,15,20),
                              ("chrY",160,5,20),
                              ("chrY",210,20,5)]
        self.treat_edm = 10
        self.ctrl_edm = 5
        # for different scoring method
        self.p_result = [60.49, 0.38, 0.08, 0.0, 6.41] # -log10(p-value), pseudo count 1 added
        self.q_result = [58.17, 0.0, 0.0, 0.0, 5.13] # -log10(q-value) from BH, pseudo count 1 added
        self.l_result = [58.17, 0.0, -0.28, -3.25, 4.91] # log10 likelihood ratio, pseudo count 1 added
        self.f_result = [0.96, 0.00, -0.12, -0.54, 0.54] # note, pseudo count 1 would be introduced.
        self.d_result = [90.00, 0, -5.00, -15.00, 15.00]
        self.m_result = [10.00, 1.00, 1.50, 0.50, 2.00]
        # for norm
        self.norm_T = np.array([[ 10, 100,  20,   0],
                                [ 60,  10,  20,   0],
                                [110,  15,  40,   0],
                                [160,   5,  40,   0],
                                [210,  20,  10,   0]]).transpose()
        self.norm_C = np.array([[ 10,  50,  10,   0],
                                [ 60,   5,  10,   0],
                                [110,   7.5,  20,   0],
                                [160,   2.5,  20,   0],
                                [210,  10,   5,   0]]).transpose()
        self.norm_M = np.array([[ 10,  10,   2,   0],
                                [ 60,   1,   2,   0],
                                [110,   1.5,   4,   0],
                                [160,   0.5,   4,   0],
                                [210,   2,   1,   0]]).transpose()
        self.norm_N = np.array([[ 10, 100,  10,   0],  # note precision lost
                                [ 60,  10,  10,   0],
                                [110,  15,  20,   0],
                                [160,   5,  20,   0],
                                [210,  20,   5,   0]]).transpose()

        # for write_bedGraph
        self.bdg1 = """chrY	0	10	100.00000
chrY	10	60	10.00000
chrY	60	110	15.00000
chrY	110	160	5.00000
chrY	160	210	20.00000
"""
        self.bdg2 = """chrY	0	60	10.00000
chrY	60	160	20.00000
chrY	160	210	5.00000
"""
        self.bdg3 = """chrY	0	10	60.48912
chrY	10	60	0.37599
chrY	60	110	0.07723
chrY	110	160	0.00006
chrY	160	210	6.40804
"""
        # for peak calls
        self.peak1 = """chrY	0	60	peak_1	60.48912
chrY	160	210	peak_2	6.40804
"""
        self.summit1 = """chrY	5	6	peak_1	60.48912
chrY	185	186	peak_2	6.40804
"""
        self.xls1    ="""chr	start	end	length	abs_summit	pileup	-log10(pvalue)	fold_enrichment	-log10(qvalue)	name
chrY	1	60	60	6	100.00	63.27251	9.18182	-1.00000	MACS_peak_1
chrY	161	210	50	186	20.00	7.09102	3.50000	-1.00000	MACS_peak_2
"""
        
    def assertEqual_float ( self, a, b, roundn = 5 ):
        self.assertEqual( round( a, roundn ), round( b, roundn ) )

    def test_compute_scores(self):
        s1 = scoreTrackII( self.treat_edm, self.ctrl_edm )
        s1.add_chromosome( "chrY", 5 )
        for a in self.test_regions1:
            s1.add( a[0],a[1],a[2],a[3] )

        s1.set_pseudocount ( 1.0 )

        s1.change_score_method( ord('p') )
        r = s1.get_data_by_chr("chrY")
        self.assertListEqual( map(lambda x:round(x,2),list(r[3])), self.p_result )

        s1.change_score_method( ord('q') )
        r = s1.get_data_by_chr("chrY")
        self.assertListEqual( map(lambda x:round(x,2),list(r[3])), self.q_result )
        
        s1.change_score_method( ord('l') )
        r = s1.get_data_by_chr("chrY")
        self.assertListEqual( map(lambda x:round(x,2),list(r[3])), self.l_result )

        s1.change_score_method( ord('f') )
        r = s1.get_data_by_chr("chrY")
        self.assertListEqual( map(lambda x:round(x,2),list(r[3])), self.f_result )

        s1.change_score_method( ord('d') )
        r = s1.get_data_by_chr("chrY")
        self.assertListEqual( map(lambda x:round(x,2),list(r[3])), self.d_result )

        s1.change_score_method( ord('m') )
        r = s1.get_data_by_chr("chrY")
        self.assertListEqual( map(lambda x:round(x,2),list(r[3])), self.m_result )

    def test_normalize(self):
        s1 = scoreTrackII( self.treat_edm, self.ctrl_edm )
        s1.add_chromosome( "chrY", 5 )
        for a in self.test_regions1:
            s1.add( a[0],a[1],a[2],a[3] )

        s1.change_normalization_method( ord('T') )
        r = s1.get_data_by_chr("chrY")
        assert_array_equal( r, self.norm_T )

        s1.change_normalization_method( ord('C') )
        r = s1.get_data_by_chr("chrY")
        assert_array_equal( r, self.norm_C )

        s1.change_normalization_method( ord('M') )
        r = s1.get_data_by_chr("chrY")
        assert_array_equal( r, self.norm_M )

        s1.change_normalization_method( ord('N') )
        r = s1.get_data_by_chr("chrY")
        assert_array_equal( r, self.norm_N )

    def test_writebedgraph ( self ):
        s1 = scoreTrackII( self.treat_edm, self.ctrl_edm )
        s1.add_chromosome( "chrY", 5 )
        for a in self.test_regions1:
            s1.add( a[0],a[1],a[2],a[3] )

        s1.change_score_method( ord('p') )

        strio = StringIO.StringIO()
        s1.write_bedGraph( strio, "NAME", "DESC", 1 )
        self.assertEqual( strio.getvalue(), self.bdg1 )
        strio = StringIO.StringIO()        
        s1.write_bedGraph( strio, "NAME", "DESC", 2 )
        self.assertEqual( strio.getvalue(), self.bdg2 )
        strio = StringIO.StringIO()        
        s1.write_bedGraph( strio, "NAME", "DESC", 3 )
        self.assertEqual( strio.getvalue(), self.bdg3 )

    def test_callpeak ( self ):
        s1 = scoreTrackII( self.treat_edm, self.ctrl_edm )
        s1.add_chromosome( "chrY", 5 )
        for a in self.test_regions1:
            s1.add( a[0],a[1],a[2],a[3] )

        s1.change_score_method( ord('p') )
        p = s1.call_peaks( cutoff = 0.10, min_length=10, max_gap=10 )
        strio = StringIO.StringIO()
        p.write_to_bed( strio, trackline = False )
        self.assertEqual( strio.getvalue(), self.peak1 )

        strio = StringIO.StringIO()
        p.write_to_summit_bed( strio, trackline = False )
        self.assertEqual( strio.getvalue(), self.summit1 )

        strio = StringIO.StringIO()
        p.write_to_xls( strio )
        self.assertEqual( strio.getvalue(), self.xls1 )        


if __name__ == '__main__':
    unittest.main()
