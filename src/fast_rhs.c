#include <math.h>
#include "fast_rhs_c.h"

void rhs(double constants[24], double states[4], double specifieds[1], double xdot[4])
{

double l_L = constants[0];
double d_L = constants[1];
double d_T = constants[2];
double m_L = constants[3];
double m_T = constants[4];
double I_L = constants[5];
double I_T = constants[6];
double g = constants[7];
double k_00 = constants[8];
double k_01 = constants[9];
double k_02 = constants[10];
double k_03 = constants[11];
double k_10 = constants[12];
double k_11 = constants[13];
double k_12 = constants[14];
double k_13 = constants[15];
double s_00 = constants[16];
double s_01 = constants[17];
double s_02 = constants[18];
double s_03 = constants[19];
double s_10 = constants[20];
double s_11 = constants[21];
double s_12 = constants[22];
double s_13 = constants[23];

double theta_a = states[0];
double theta_h = states[1];
double omega_a = states[2];
double omega_h = states[3];

double a = specified[0];

double z_0 = d_T*d_T;
double z_1 = d_T*l_L*cos(theta_h);
double z_2 = 1/(I_L + I_T + d_L*d_L*m_L + m_T*(l_L*l_L + z_0 + 2*z_1));
double z_3 = d_T*m_T;
double z_4 = theta_a + theta_h;
double z_5 = a*z_3*cos(z_4) + g*z_3*sin(z_4);
double z_6 = d_L*m_L;
double z_7 = a*cos(theta_a);
double z_8 = l_L*m_T;
double z_9 = g*sin(theta_a);
double z_10 = d_T*l_L*m_T*sin(theta_h);
double z_11 = -k_00*s_00*theta_a - k_01*s_01*theta_h - k_02*omega_a*s_02 - k_03*omega_h*s_03 + 2*omega_a*omega_h*z_10 + omega_h*omega_h*z_10 + z_5 + z_6*z_7 + z_6*z_9 + z_7*z_8 + z_8*z_9;
double z_12 = I_T + m_T*(z_0 + z_1);
double z_13 = (-k_10*s_10*theta_a - k_11*s_11*theta_h - k_12*omega_a*s_12 - k_13*omega_h*s_13 - omega_a*omega_a*z_10 - z_11*z_12*z_2 + z_5)/(I_T + m_T*z_0 - z_12*z_12*z_2);

xdot[0] = omega_a;
xdot[1] = omega_h;
xdot[2] = z_2*(z_11 - z_12*z_13);
xdot[3] = z_13;

}
