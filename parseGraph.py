import os
import requests
import networkx as nx
import pandas as pd
import geopandas as gpd
from pyvis.network import Network
from IPython.display import display, HTML, Code
from IPython.display import clear_output



'''the output of the LLM is stored in 'response': which has the code for the graph operations for which the next step is
   to generate python code for each node and travaerse the map '''


