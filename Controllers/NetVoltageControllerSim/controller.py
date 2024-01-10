import numpy as np
import cvxpy as cp
import pandapower as pp

class controller_python:
    def __init__(self, net, room):
        self.net=net
        self.uproom_p=room['uproom_p']
        self.uproom_q=room['uproom_q']
        self.downroom_p=room['downroom_p']
        self.downroom_q=room['downroom_q']
        self.upvollimit=room['upvollimit']
        self.downvollimit=room['downvollimit']

    def sensitivitycal(self):
        m1 = np.zeros(((len(self.net.bus)), (len(self.net.bus))))
        m2 = np.zeros(((len(self.net.bus)), (len(self.net.bus))))
        # pp.runpp(net, algorithm='nr')#, algorithm='nr'
        n = 0
        for i in self.net.load.bus:
            pp.runpp(self.net, algorithm='nr')
            avoltagei = self.net.res_bus.vm_pu
            self.net.load.p_mw[n] = self.net.load.p_mw[n] + 0.0001
            pp.runpp(self.net, algorithm='nr')
            bvoltagei = self.net.res_bus.vm_pu
            m1[i] = (avoltagei - bvoltagei) / 0.0001
            self.net.load.p_mw[n] = self.net.load.p_mw[n] - 0.0001
            n = n + 1
            # senp=m[2:,2:]
            # senp=np.transpose(m1)
            senp = m1

        n = 0
        for i in self.net.load.bus:
            pp.runpp(self.net, algorithm='nr')
            avoltagei = self.net.res_bus.vm_pu
            self.net.load.q_mvar[n] = self.net.load.q_mvar[n] + 0.0001
            pp.runpp(self.net, algorithm='nr')
            bvoltagei = self.net.res_bus.vm_pu
            m2[i] = (avoltagei - bvoltagei) / 0.0001
            self.net.load.q_mvar[n] = self.net.load.q_mvar[n] - 0.0001
            n = n + 1
            # senq=m[2:,2:]
            # senq=np.transpose(m2)
            senq = m2
        return senp, senq

    def optcentral(self, sen_p, sen_q,voltage):
        # adjust b_p and b_q
        opt_p = np.zeros(len(self.net.bus))
        opt_q = np.zeros(len(self.net.bus))
        vol = np.ones(len(self.net.bus))
        x = cp.Variable(len(self.net.bus))
        y = cp.Variable(len(self.net.bus))
        constraints = [x >= self.uproom_p,
                       y >= self.uproom_q,
                       x <= self.downroom_p,
                       y <= self.downroom_q,
                       voltage + sen_p * x + sen_q * y <= self.upvollimit * vol,
                       voltage + sen_p * x + sen_q * y >= self.downvollimit * vol]
        objective = cp.Minimize(cp.atoms.norm1(x) + cp.atoms.norm1(y))  # need to change!!!
        prob = cp.Problem(objective, constraints)
        prob.solve()  # Returns the optimal value.
        if x.value is not None:
            opt_p = x.value
            opt_q = y.value
        else:
            print('need more flex energy- centralized')
            xx = cp.Variable(len(self.net.bus))
            yy = cp.Variable(len(self.net.bus))
            constraints = [xx >= self.uproom_p,
                           yy >= self.uproom_q,
                           xx <= self.downroom_p,
                           yy <= self.downroom_q]
            objective = cp.Minimize(cp.sum_squares(voltage + sen_p * xx + sen_q * yy - vol))  # need to change!!!
            # objective = cp.Minimize(cp.atoms.norm1(x) + cp.atoms.norm1(y))
            prob = cp.Problem(objective, constraints)
            prob.solve()  # Returns the optimal value.
            opt_p = xx.value
            opt_q = yy.value
            print("cannot regulate")
        return opt_p, opt_q


    def control(self, p_mw,q_mvar,vm_pu,attr_names):

        # def control(self,soc , pv_gen, load_dem, wind_gen):

        p_mw=list(p_mw)
        p_mw.insert(0, 0)
        q_mvar=list(q_mvar)
        q_mvar.insert(0, 0)
        vm_pu=list(vm_pu)
        vm_pu.insert(0, 1)
        for activei in self.net.load.bus.index:
            self.net.load.p_mw[activei] = p_mw[activei]
            self.net.load.q_mvar[activei]=q_mvar[activei]

        sen_p, sen_q =self.sensitivitycal()
        action_ptcentral = np.zeros(len(self.net.bus))
        action_qtcentral = np.zeros(len(self.net.bus))
        (action_ptcentral, action_qtcentral)  = self.optcentral( sen_p, sen_q,vm_pu)
        p_mw_update=p_mw
        q_mvar_update=q_mvar
        re_params={}
        for activei in self.net.load.bus.index:
            p_mw_update[activei]=p_mw[activei]-action_ptcentral[self.net.load.bus[activei]]
            q_mvar_update[activei]=q_mvar[activei]-action_qtcentral[self.net.load.bus[activei]]
            re_params.update({
                f'p_m_update{activei}': p_mw_update[activei],
                f'q_mvar_update{activei}': q_mvar_update[activei]
            })

        return re_params