import matplotlib.pyplot as plt
import streamlit as st



x = [25, 30, 35, 40, 45]
y = [46, 41, 37, 33, 30]

plt.plot(x,y)
plt.xlabel('Well Distance from the River [m]')
plt.ylabel('Bank Filtration Fraction [%]')

plt.title('Bank Filtrate Fraction vs Well Distance from the River')
plt.grid()

fig = plt.show()

st.pyplot(fig)