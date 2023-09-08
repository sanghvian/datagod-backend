import graphviz
from graphviz import Digraph

def concept_mapping(openai_output_text):
    dot = Digraph('ConceptGraph', format='png')
    exec(openai_output_text)
    print(dot.source)
    dot.render('ConceptMap', view=True)

openai_output_text = '''
# Main Concept
dot.node('A', 'Wildfires')

# Causes
dot.node('B', 'Occurrence')
dot.node('C', 'Natural')
dot.node('D', 'Human Activity')
dot.edge('A', 'B')
dot.edge('B', 'C')
dot.edge('B', 'D')

# Elements for start
dot.node('E', 'Elements for Wildfire Start')
dot.node('F', 'Fuel')
dot.node('G', 'Air (Oxygen)')
dot.node('H', 'Heat Sources')
dot.edge('A', 'E')
dot.edge('E', 'F')
dot.edge('E', 'G')
dot.edge('E', 'H')

# Fuel sources
dot.node('I', 'Live or Dead Trees')
dot.node('J', 'Dry Vegetation')
dot.node('K', 'Other Organic Matter')
dot.edge('F', 'I')
dot.edge('F', 'J')
dot.edge('F', 'K')

# Heat sources
dot.node('L', 'Lightning Strikes')
dot.node('M', 'Human Sources (e.g., Campfires, Cigarettes)')
dot.edge('H', 'L')
dot.edge('H', 'M')

# Natural Wildfires
dot.node('N', 'Natural Wildfires')
dot.node('O', 'Low Precipitation, Dry Weather, Droughts')
dot.node('P', 'Dry Vegetation as Fuel')
dot.node('Q', 'Lightning Strikes Ignition')
dot.node('R', 'Aid: Strong Winds, Elevated Temperatures')
dot.edge('A', 'N')
dot.edge('N', 'O')
dot.edge('N', 'P')
dot.edge('N', 'Q')
dot.edge('N', 'R')

# Vegetation dryness stats
dot.node('S', 'Vegetation Dryness')
dot.node('T', 'Increase in Wildfire Hazard')
dot.node('U', '65% of California’s Vegetation drier in June 2021 than previous year')
dot.edge('A', 'S')
dot.edge('S', 'T')
dot.edge('S', 'U')
'''

concept_mapping(openai_output_text)