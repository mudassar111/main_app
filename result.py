import streamlit as st
import time
import numpy as np
import pandas as pd
from streamlit.elements.plotly_chart import SHARING_MODES
import sympy
from sympy.core.symbol import symbols
from sympy.solvers.diophantine.diophantine import descent, length
from sympy.solvers.solvers import solve
from db_fxns import create_table,add_data,view_all_data,view_unique_data,get_id,edit_well_id,delete_id
from db_fxns_aq import create_table_aq,view_all_data_aq,add_data_aq,view_unique_data_aq,get_id_aq,edit_aq_id, delete_id_aq
from db_fxns_aq import view_all_data_clg
import base64
import pathlib
import matplotlib.pyplot as plt
from matplotlib import cm, colors
from matplotlib.patches import Rectangle
from matplotlib.ticker import StrMethodFormatter
import model_pro
import contrib
from PIL import Image
from plot import *


def app():

	#st.subheader("View Stored Values")
	results_aq = view_all_data_aq()
	results = view_all_data()
	results_clg = view_all_data_clg()

	#st.sidebar.markdown('---')
	#st.sidebar.markdown(""" **Stored Values:** """)
	

	#st.sidebar.markdown('---')
	
	st.title("Results According to Entered Values:")

	st.markdown("---")

	#menu = ["Wells", "Rivers", "No Flow"]
	#choice = st.sidebar.selectbox("Please Select Boundary Condition", menu)
	aem_model = model_pro.Model(k = results_aq[0][4], H = results_aq[0][1], h0 = results_aq[0][5], Qo_x=results_aq[0][2])
	if len(results_clg) == 0:
		st.info("No Clogging Factor is Added!")
	else:
		aem_model.calc_clogging(results_clg[0][1], results_clg[0][2])
	if len(results) == 0:
		st.error("Please add atleast one Well")

	else:
		for j in range(6):
			if j == len(results):
				for i in range(j):
					well = model_pro.Well(aem_model, Q = results[i][1], rw = 0.2, x = results[i][2], y = results[i][3])

		c1, c2 = st.columns(2)

#------------------------------------------------------------------Stream / Potential Lines for Multiple Wells-----------------------------
		with c1:
			st.subheader("Well(s) in Flow Field:")
			plot1=plotting(0, 100, -20, 150, 100)
			b, fig1 = plot1.plot2d(aem_model, levels=8, sharey=False, quiver=False, streams=True, figsize = (18,12))
			st.pyplot(fig1)

#------------------------------------------------------------------CR, TT, RL for One Well ------------------------------------------------
		with c2:
			if len(results) > 1:

				#st.error(" ** Note: ** Enter Exactly One Well to get the solution for Bank Filtrate Ratio, Capture Length.")
				st.sidebar.markdown("---")
				st.sidebar.info("After entering one well, The options will available here.")
			else:
				solv = contrib.river_length(aem_model)

				#st.write("River Capture Length, Capture Position, Contribution Discharge")
				length, riv_coords, capture_fraction = solv.solve_river_length()
				#st.write(length, riv_coords, capture_fraction)
				tt, ys, avgtt, mintt, traj_array = solv.time_travel(results_aq[0][3], delta_s=0.4, calculate_trajectory=True)
				
				#st.write("Average Time: {}".format(avgtt))
				#st.write("Average Time: {}".format(mintt))

				with c2:
					st.sidebar.markdown("---")
					st.sidebar.title("Contribution Ratio:")
					if st.sidebar.checkbox("Bank Filtrate Contribution"):
						st.subheader("Bank Filterate Contribution:")
						plot=plotting(0, 100, -20, 150, 100, riv_coords)
						b, fig = plot.plot2d(aem_model, sharey = False, traj_array = traj_array, levels=8, quiver=False, streams=True)
						st.pyplot(fig)
					#------------------------------------------------------Capture Fraction Result---------------------------------
						bf_ratio = capture_fraction*100
						bf_ratio_rounded = bf_ratio.round(decimals = 0)
						st.sidebar.metric(label = "Bank Filtrate Ratio:", value="{} %".format(int(bf_ratio_rounded)))

					#------------------------------------------------------River Length Result-------------------------------------

						riv_length_rounded = length.round(decimals = 0)
						st.sidebar.metric(label="River Capture Length:", value="{} m".format(int(riv_length_rounded)))

					#------------------------------------------------------Capture Coordinates-------------------------------------

						riv_0 = riv_coords[0]
						riv_1 = riv_coords[1]
						riv_0_rounded = riv_0.round(decimals = 0)
						riv_1_rounded = riv_1.round(decimals = 0)
						st.sidebar.metric(label="Capture Length Location on Y-Axis:", value="{} m & %.2f m".format(int(riv_0_rounded)) %(int(riv_1_rounded)))
		st.markdown("---")					
	#---------------------------------------------------------------------------Travel Time---------------------------------------------------------------------------
		
		if len(results) > 1:
			st.error(" ** Note: ** Enter Exactly One Well to get the solution for Bank Filtrate Ratio, Capture Length and Time of Travel.")
		else:
			st.sidebar.markdown("---")
			st.sidebar.title("Time of Travel:")
			if st.sidebar.checkbox("Time of Travel"):
				st.subheader("Time of Travel:")
				plot2=plotting(0, 100, -20, 150, 100, riv_coords)
				c, fig2 = plot2.plot2d(aem_model, tt=tt, ys=ys, traj_array=traj_array, levels=8, sharey=True, quiver=False, streams=True, figsize = (18,12))
				st.pyplot(fig2)

				#--------------------------------------------------------------------Avgtt & mintt-------------------------------------------------------------------------------------
				avg_tt_rounded = avgtt.round(decimals = 0)
				min_tt_rounded = mintt.round(decimals = 0)
				st.sidebar.metric(label="Average Travel Time:", value="{} Days".format(avg_tt_rounded))
				st.sidebar.metric(label="Minimum Travel Time:", value="{} Days".format(min_tt_rounded))
				st.markdown("---")
	#------------------------------------------------------------------------------Download Files----------------------------------------------------------------------------------------
		plot3=plotting(0, 100, -20, 150, 100)

		h0, psi0 = plot3.fix_to_mesh(aem_model) 
		dfh = pd.DataFrame(data = h0)
		df_psi = pd.DataFrame(data = psi0)
		dfh_rounded = dfh.round(decimals=3)
		df_psi_rounded = df_psi.round(decimals=3)
		csv = dfh_rounded.to_csv(sep="\t", index=False)
		csv_psi = df_psi_rounded.to_csv(sep="\t", index=False)
		#b64 = base64.b64encode(csv.encode()).decode()

		st.sidebar.markdown("---")	
		st.sidebar.title("Download \u03C8 & Head:")
		#st.sidebar.subheader("Download Head:")
		st.sidebar.download_button(label="Download H in CSV", data=csv, mime="csv")
		#st.sidebar.subheader("Download PSI:")
		st.sidebar.download_button(label="Download \u03C8 in CSV", data=csv_psi, mime="csv")


	st.sidebar.markdown("---")