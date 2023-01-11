# -*- coding: utf-8 -*-
"""
Created on Fri Apr 16 13:12:07 2021

@author: robin grapin
"""
import warnings

warnings.filterwarnings("ignore")

import time
import unittest
import numpy as np

from smoot.smoot import MOO
from smoot.zdt import ZDT

from smt.sampling_methods import LHS
from smt.problems import Branin
from smt.utils.sm_test_case import SMTestCase

from pymoo.indicators.gd import GD


class TestMOO(SMTestCase):
    def test_Branin(self):
        n_iter = 5
        fun = Branin()
        criterion = "EI"

        mo = MOO(
            n_iter=n_iter,
            criterion=criterion,
            xlimits=fun.xlimits,
            random_state=42,
        )
        print("running test Branin 2D -> 1D")
        start = time.time()
        mo.optimize(fun=fun)
        x_opt, y_opt = mo.result.X[0][0], mo.result.F[0][0]
        print("x_opt :", x_opt)
        print("y_opt :", y_opt)
        print("seconds taken Branin: ", time.time() - start, "\n")
        self.assertTrue(
            np.allclose([[-3.14, 12.275]], x_opt, rtol=0.5)
            or np.allclose([[3.14, 2.275]], x_opt, rtol=0.5)
            or np.allclose([[9.42, 2.475]], x_opt, rtol=0.5)
        )
        self.assertAlmostEqual(0.39, float(y_opt), delta=1)

    def test_zdt(self, type=1, criterion="EHVI", ndim=2, n_iter=5):
        fun = ZDT(type=type, ndim=ndim)

        mo = MOO(
            n_iter=n_iter,
            criterion=criterion,
            random_state=1,
        )
        print("running test ZDT", type, ": " + str(ndim) + "D -> 2D,", criterion)
        start = time.time()
        mo.optimize(fun=fun)
        print("seconds taken :", time.time() - start)
        exact = fun.pareto(random_state=1)[1]
        gd = GD(exact)
        dist = gd(mo.result.F)
        print("distance to the exact Pareto front", dist, "\n")
        self.assertLess(dist, 2.5)

    def test_zdt_2(self):
        self.test_zdt(type=2, criterion="WB2S")

    def test_zdt_3(self):
        self.test_zdt(type=3, criterion="PI")

    def test_zdt_2_3Dto2D(self):
        self.test_zdt(type=2, criterion="EHVI", ndim=3)

    def test_train_pts_known(self):
        fun = ZDT()
        xlimits = fun.xlimits
        sampling = LHS(xlimits=xlimits, random_state=42)
        xt = sampling(20)  # generating data as if it were known data
        yt = fun(xt)  # idem : "known" datapoint for training
        mo = MOO(n_iter=5, criterion="MPI", xdoe=xt, ydoe=yt, random_state=42)
        print("running test ZDT with known training points")
        start = time.time()
        mo.optimize(fun=fun)
        print("seconds taken :", time.time() - start)
        exact = fun.pareto(random_state=1)[1]
        gd = GD(exact)
        dist = gd(mo.result.F)
        print("distance to the exact Pareto front", dist, "\n")
        self.assertLess(dist, 2.5)


if __name__ == "__main__":
    unittest.main()
