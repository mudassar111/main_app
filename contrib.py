import numpy as np
import streamlit as st
import sympy
from scipy.optimize import fsolve
import itertools


class river_length():
    def __init__(self, model):
        self.model = model
    
    def solve_river_length(self):
        if (len(self.model.aem_elements) > 1) | (len(self.model.aem_elements) == 0):
            st.write("Failed to drive solution")
        else:
            y = sympy.symbols('y')
            elem = self.model.aem_elements[0]
            Q = elem.Q
            xw = elem.x
            yw = elem.y
            d = np.abs(self.model.river_a*xw + self.model.river_b*yw + self.model.river_c) / np.sqrt(self.model.river_a**2 + self.model.river_b**2)
            Qx = -self.model.Qo_x

            ex_st_points = Q /(np.pi*d*Qx)

            if ex_st_points <= 1:
                st.write("There is no staganation Point")
            else:
                equation = sympy.Eq(-d**2 + d*Q/(np.pi*Qx)-y**2,0)
                sols = sympy.solveset(equation, y, domain = sympy.S.Reals)
                sol_el = []
                for i in sols:
                    sol_el.append(np.float64(i+yw))
                length = np.abs(sol_el[0]-sol_el[1])
                Q_river = self.model.calc_psi(0, sol_el[0]) - self.model.calc_psi(0, sol_el[1]) + Q
                contrib = Q_river/Q

                return length, sol_el, contrib

    def time_travel(self, ne, delta_s = 0.1, calculate_trajectory=False, min_dist_est=0.1):

        length, sol_el, contrib = self.solve_river_length()

        ys = np.linspace(sol_el[0]+min_dist_est, sol_el[1]-min_dist_est, 20)
        xs = np.repeat(0.1, ys.shape[0])
        tt = []
        
        if calculate_trajectory:
            traj_array = []



        elem = self.model.aem_elements[0]
        Q = elem.Q
        xw = elem.x
        yw = elem.y
        d = np.abs(self.model.river_a*xw + self.model.river_b*yw + self.model.river_c)/np.sqrt(self.model.river_a**2 + self.model.river_b**2)
        Qx = self.model.Qo_x
        rw = elem.rw


        def qx(x, y, Q, Qx, xw, yw, d):
            head = self.model.calc_head(x,y)
            if head > self.model.H:
                z = self.model.H
            else:
                z = head

            return -1*(-Qx + Q/(4*np.pi)*((2*(x-xw)/((x-xw)**2+(y-yw)**2))-(2*(x-(xw-2*d)))/((x-(xw-2*d))**2+(y-yw)**2)))/z

        def qy(x, y, Q, Qx, xw, yw, d):
            head = self.model.calc_head(x,y)
            if head > self.model.H:
                z = self.model.H
            else:
                z = head

            return -1*(Q/(4*np.pi)*((2*(y-yw)/((x-xw)**2+(y-yw)**2))-(2*(y-yw))/((x-(xw-2*d))**2+(y-yw)**2)))/z
            
        def equation_x(x_a, psi, y_2, Q, Qx, xw, yw, d):
            return -Qx*y_2 + (Q/(2*np.pi))*(np.arctan2((y_2-yw), (x_a-xw)) - np.arctan2((y_2-yw), (x_a-(xw-2*d))))-psi
        
        def equation_y(y_a, psi, x_2, Q, Qx, xw, yw, d):
            return -Qx*y_a + (Q/(2*np.pi))*(np.arctan2((y_a-yw), (x_2-xw)) - np.arctan2((y_a-yw), (x_2-(xw-2*d))))-psi

        for x,y in zip(xs, ys):

            if calculate_trajectory:
                xss = []
                xss.append(x)
                yss = []
                yss.append(y)

            t_arr = []
            x1 = x
            y1 = y
            psi = self.model.calc_psi(x,y)
            breakin_dists = []

            while np.sqrt((x1-xw)**2+(y1-yw)**2) > 5*rw:
                dista1 = np.sqrt((x1-xw)**2+(y1-yw)**2)
                qx1 = qx(x1, y1, Q, Qx, xw, yw, d)
                qy1 = qy(x1, y1, Q, Qx, xw, yw, d)
                vx = qx1/ne
                vy = qy1/ne
                v_i = np.sqrt(vx**2+vy**2)

                y_2 = np.float(y1 + delta_s*vy/v_i)
                x_2 = np.float(x1 + delta_s*vx/v_i)

                if np.sqrt((x_2-xw)**2+(y_2-yw)**2) < rw:
                    break

                if vx > vy:
                    sols_y = fsolve(equation_y, y_2, (psi, x_2, Q, Qx, xw, yw, d), xtol=1e-4)
                    sol_el_y = sols_y[0]
                    y_2 = sol_el_y

                else:
                    sols = fsolve(equation_x, x_2, (psi, y_2, Q, Qx, xw, yw, d), xtol=1e-4)
                    sol_el_x = sols[0]
                    x_2 = sol_el_x

                dist = np.sqrt((x_2-x1)**2 + (y_2-y1)**2)

                qx2 = qx(x_2, y_2, Q, Qx, xw, yw, d)
                qy2 = qy(x_2, y_2, Q, Qx, xw, yw, d)
                vx2 = qx2/ne
                vy2 = qy2/ne

                vxm = np.mean([vx, vx2])
                vym = np.mean([vy, vy2])

                vm = np.sqrt(vxm**2+vym**2)

                t_arr.append(dist/vm)

                x1 = x_2
                y1 = y_2

                if calculate_trajectory:
                    xss.append(x1)
                    yss.append(y1)

            tt.append(np.sum(np.array(t_arr)))

            if calculate_trajectory:
                traj_arr = np.vstack((np.array(xss), np.array(yss)))
                traj_array.append(traj_arr)


        qs = []
        for x,y in zip(xs,ys):
            qx1 = qx(x, y, Q, Qx, xw, yw, d)
            qy1 = qy(x, y, Q, Qx, xw, yw, d)
            q = np.sqrt(qx1**2+qy1**2)
            qs.append(q)

        qs = np.array(qs)
        tt = np.array(tt)

        avgtt = np.sum(qs*tt)/np.sum(qs)

        mintt = np.min(tt)

        if calculate_trajectory:
            return tt, ys, avgtt, mintt, traj_array

        else:

            return tt, ys, avgtt, mintt       



        '''def qx(x,y):
            return -1*(-Qx + Q/(4*np.pi)*((2*(x-xw)/((x-xw)**2 + (y-yw)**2)) - (2*(x-(xw-2*d)))/((x-(xw-2*d))**2 + (y-yw)**2))) / self.model.calc_head(x,y)
        def qy(x,y):
            return -1*(Q/(4*np.pi)*((2*(y-yw)/((x-xw)**2 + (y-yw)**2))-(2*(y-yw))/((x-(xw-2*d))**2+(y-yw)**2))) / self.model.calc_head(x,y)


        for x,y in zip(xs, ys):

            dis_arr = []
            v_arr = []

            x1 = x
            y1 = y
            while np.sqrt((x1-xw)**2+(y1-yw)**2) > 1.5*delta_s:
                dista1 = np.sqrt((x1-xw)**2+(y1-yw)**2)
                qx1 = qx(x1, y1)
                qy1 = qy(x1, y1)
                vx = qx1/ne
                vy = qy1/ne
                v_i = np.sqrt(vx**2 + vy**2)
                v_arr.append(v_i)

                x_2 = np.float(x1 + delta_s*vx/v_i)
                y_2 = np.float(y1 + delta_s*vy/v_i)

                psi = self.model.calc_psi(x,y)

                def equation_x(x_a):
                    return Qx*y_2 + (Q/(2*np.pi))*(np.arctan2((y_2-yw), (x_a-xw))-np.arctan2((y_2-yw), (x_a-(xw-2*d)))) - psi
                sols = fsolve(equation_x, x_2)
                sol_el_x = sols[0]

                def equation_y(y_a):
                    return Qx*y_a + (Q/(2*np.pi)) * (np.arctan2((y_a-yw), (x_2-xw))- np.arctan2((y_a-yw), (x_2-(xw-2*d)))) - psi
                sols_y = fsolve(equation_y, y_2)
                sol_el_y = sols_y[0]


                pos_locs_y = [(sol_el_x, y_2)]
                pos_locs_x = [(x_2, sol_el_y)]
                pos_locs = pos_locs_x + pos_locs_y

                dista = 1e9

                for xp, yp in pos_locs:
                    dist = np.sqrt((xp-x1)**2+(yp-y1)**2)
                    if dist < dista:
                        x_2 = xp
                        y_2 = yp
                        dista = dist

                dis_arr.append(dista)

                x1 = x_2
                y1 = y_2
                dista_2 = np.sqrt((x1-xw)**2+(y1-yw)**2)
                if dista_2 > dista1:
                    break

            dis_arr = np.array(dis_arr)
            v_arr = np.array(v_arr)
            tt.append(np.sum(dis_arr/v_arr))

        return tt'''



