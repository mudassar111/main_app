import streamlit as st
from multiapp import MultiApp
import home, theory, result, help_page, data_col # import your app modules here

app = MultiApp()
st.set_page_config(
        page_title="Riverbank Filtration Online Tool",
        layout="wide",

        )


# Add all your application here
app.add_app("Home", home.app)
app.add_app("Theory", theory.app)
app.add_app("Data Collection", data_col.app)
#app.add_app("Calculations", calculations.app)
app.add_app("Results", result.app)
app.add_app("Case Study", help_page.app)

# The main app
app.run()
