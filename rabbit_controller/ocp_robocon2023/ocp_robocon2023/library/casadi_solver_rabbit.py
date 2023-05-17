import numpy as np
import casadi as ca
import math

from .rabbit_omni import RabbitModel

class CasadiNMPC:

    def __init__(self,
        initX, initU,
        lowX, highX,
        lowU, highU,
        mat_Q, mat_R,
        N, dt, sim_time
    ):
        super(CasadiNMPC, self).__init__()
        #Model
        self.rabbit_model = RabbitModel()

        self.initX = initX
        self.initU = initU
        self.lowX = lowX
        self.highX = highX
        self.lowU = lowU
        self.highU = highU
        self.mat_Q = mat_Q
        self.mat_R = mat_R

        self.N = N
        self.dt = dt
        self.sim_time = sim_time
        self.index = 0

        self.rot_3d_z = lambda theta: ca.vertcat(
            ca.horzcat(ca.cos(theta), ca.sin(theta), 0),
            ca.horzcat(-ca.sin(theta),  ca.cos(theta), 0),
            ca.horzcat(         0,           0, 1)
        )

    
    def casadi_model_setup(self, type="track"):
        if type=="point":
            x = ca.SX.sym('x')
            y = ca.SX.sym('y')
            theta = ca.SX.sym('theta')
            states = ca.vertcat(x, y, theta)
            n_states = states.numel()
            ## Controls
            v1 = ca.SX.sym('v1')
            v2 = ca.SX.sym('v2')
            v3 = ca.SX.sym('v3')
            v4 = ca.SX.sym('v4')
            controls = ca.vertcat(v1, v2, v3, v4)
            n_controls = controls.numel()

            # Matrix containing all states
            X = ca.SX.sym('X', n_states, self.N+1)
            # Matrix containing all controls
            U = ca.SX.sym('U', n_controls, self.N)
            # Matrix containing
            P = ca.SX.sym('P', n_states+n_states)
            # State weight matrix
            Q = np.diag(self.mat_Q)
            # Control weight matrix
            R = np.diag(self.mat_R)
            # RHS

            RHS = self.rabbit_model.forward_kinematic(v1, v2, v3, v4, theta, "sym")
            # nonlinear function for mpc model
            f = ca.Function('f', [states, controls], [RHS])
            # cost and constraint
            cost_fn = 0
            g = X[:, 0] - X_ref[:, 0]
            # Euler
            for k in range(self.N):
                st = X[:, k] - P[:, k]
                con = U[:, k]
                cost_fn = cost_fn + st.T@Q@st + con.T@R@con
                st_next = X[:, k+1]
                f_value = f(X[:, k], U[:, k])
                st_next_euler = X[:, k] + (self.dt*f_value)
                g = ca.vertcat(g, st_next-st_next_euler)

            optimal_var = ca.vertcat(ca.reshape(X, -1, 1), ca.reshape(U, -1, 1))
            optimal_par = ca.vertcat(ca.reshape(X_ref, -1, 1), ca.reshape(U_ref, -1, 1))
            nlp_prob = {'f': cost_fn, 'x': optimal_var, 'p': optimal_par, 'g': g}
            opts = {
                    'ipopt.max_iter': 5000,
                    'ipopt.print_level': 0,
                    'ipopt.acceptable_tol': 1e-6,
                    'ipopt.acceptable_obj_change_tol': 1e-4,
                    'print_time': 0}
            solver = ca.nlpsol('solver', 'ipopt', nlp_prob, opts)

            lbx = ca.DM.zeros((n_states*(self.N+1) + n_controls*self.N, 1))
            ubx = ca.DM.zeros((n_states*(self.N+1) + n_controls*self.N, 1))

            lbx[0: n_states*(self.N+1): n_states] = self.lowX[0]
            lbx[1: n_states*(self.N+1): n_states] = self.lowX[1]
            lbx[2: n_states*(self.N+1): n_states] = self.lowX[2]


            ubx[0: n_states*(self.N+1): n_states] = self.highX[0]
            ubx[1: n_states*(self.N+1): n_states] = self.highX[1]
            ubx[2: n_states*(self.N+1): n_states] = self.highX[2]


            lbx[n_states*(self.N+1): n_states*(self.N+1)+n_controls*self.N: 4] = self.lowU[0]
            lbx[n_states*(self.N+1)+1: n_states*(self.N+1)+n_controls*self.N: 4] = self.lowU[1]
            lbx[n_states*(self.N+1)+2: n_states*(self.N+1)+n_controls*self.N: 4] = self.lowU[2]
            lbx[n_states*(self.N+1)+3: n_states*(self.N+1)+n_controls*self.N: 4] = self.lowU[3]


            ubx[n_states*(self.N+1): n_states*(self.N+1)+n_controls*self.N: 4] = self.highU[0]
            ubx[n_states*(self.N+1)+1: n_states*(self.N+1)+n_controls*self.N: 4] = self.highU[1]
            ubx[n_states*(self.N+1)+2: n_states*(self.N+1)+n_controls*self.N: 4] = self.highU[2]
            ubx[n_states*(self.N+1)+3: n_states*(self.N+1)+n_controls*self.N: 4] = self.highU[3]


            args = {
                'lbg': ca.DM.zeros((n_states*(self.N+1), 1)),
                'ubg': ca.DM.zeros((n_states*(self.N+1), 1)),
                'lbx': lbx,
                'ubx': ubx
            }

            return f, solver, args

        if type=="track":
            ## States
            x = ca.SX.sym('x')
            y = ca.SX.sym('y')
            theta = ca.SX.sym('theta')
            states = ca.vertcat(x, y, theta)
            n_states = states.numel()
            ## Controls
            v1 = ca.SX.sym('v1')
            v2 = ca.SX.sym('v2')
            v3 = ca.SX.sym('v3')
            v4 = ca.SX.sym('v4')
            controls = ca.vertcat(v1, v2, v3, v4)
            n_controls = controls.numel()

            # Matrix containing all states
            X = ca.SX.sym('X', n_states, self.N+1)
            # Matrix containing all controls
            U = ca.SX.sym('U', n_controls, self.N)
            # Matrix containing all states_ref
            X_ref = ca.SX.sym('X_ref', n_states, self.N+1)
            # Matrix containing all controls_ref
            U_ref = ca.SX.sym('U_ref', n_controls, self.N)
            # State weight matrix
            Q = np.diag(self.mat_Q)
            # Control weight matrix
            R = np.diag(self.mat_R)

            RHS = self.rabbit_model.forward_kinematic_tran(v1, v2, v3, v4, theta, "sym")

            # nonlinear function for mpc model
            f = ca.Function('f', [states, controls], [RHS])
            # cost and constraint
            cost_fn = 0
            g = X[:, 0] - X_ref[:, 0]
            # Euler
            for k in range(self.N):
                st_err = X[:, k] - X_ref[:, k]
                con_err = U[:, k] - U_ref[:, k]
                cost_fn = cost_fn + st_err.T @ Q @ st_err + con_err.T @ R @ con_err
                st_next = X[:, k+1]
                st_next_euler = X[:, k] + self.dt*f(X[:, k], U[:, k])
                g = ca.vertcat(g, st_next-st_next_euler)

            cost_fn = cost_fn + (X[:, self.N]-X_ref[:, self.N]).T@Q@(X[:, self.N]-X_ref[:, self.N])

            optimal_var = ca.vertcat(
                ca.reshape(X, -1, 1),
                ca.reshape(U, -1, 1))
            optimal_par = ca.vertcat(
                ca.reshape(X_ref, -1, 1),
                ca.reshape(U_ref, -1, 1))
            
            nlp_prob = {'f': cost_fn,
                        'x': optimal_var,
                        'p': optimal_par,
                        'g': g}
            opts = {
                    'ipopt.max_iter': 5000,
                    'ipopt.print_level': 0,
                    'ipopt.acceptable_tol': 1e-6,
                    'ipopt.acceptable_obj_change_tol': 1e-4,
                    'print_time': 0}
            
            solver = ca.nlpsol('solver', 'ipopt', nlp_prob, opts)

            lbx = ca.DM.zeros((n_states*(self.N+1) + n_controls*self.N, 1))
            ubx = ca.DM.zeros((n_states*(self.N+1) + n_controls*self.N, 1))

            lbx[0: n_states*(self.N+1): n_states] = self.lowX[0]
            lbx[1: n_states*(self.N+1): n_states] = self.lowX[1]
            lbx[2: n_states*(self.N+1): n_states] = self.lowX[2]


            ubx[0: n_states*(self.N+1): n_states] = self.highX[0]
            ubx[1: n_states*(self.N+1): n_states] = self.highX[1]
            ubx[2: n_states*(self.N+1): n_states] = self.highX[2]


            lbx[n_states*(self.N+1)  : n_states*(self.N+1)+n_controls*self.N: 4] = self.lowU[0]
            lbx[n_states*(self.N+1)+1: n_states*(self.N+1)+n_controls*self.N: 4] = self.lowU[1]
            lbx[n_states*(self.N+1)+2: n_states*(self.N+1)+n_controls*self.N: 4] = self.lowU[2]
            lbx[n_states*(self.N+1)+3: n_states*(self.N+1)+n_controls*self.N: 4] = self.lowU[3]


            ubx[n_states*(self.N+1)  : n_states*(self.N+1)+n_controls*self.N: 4] = self.highU[0]
            ubx[n_states*(self.N+1)+1: n_states*(self.N+1)+n_controls*self.N: 4] = self.highU[1]
            ubx[n_states*(self.N+1)+2: n_states*(self.N+1)+n_controls*self.N: 4] = self.highU[2]
            ubx[n_states*(self.N+1)+3: n_states*(self.N+1)+n_controls*self.N: 4] = self.highU[3]


            args = {
                'lbg': ca.DM.zeros((n_states*(self.N+1), 1)),
                'ubg': ca.DM.zeros((n_states*(self.N+1), 1)),
                'lbx': lbx,
                'ubx': ubx
            }

            return f, solver, args