import COPASI
import sys

def expand_model(input_file, output_file):
  """expands the model in the given file, by creating a chain."""
  
  dm = COPASI.CRootContainer.addDatamodel()
  
  if not dm.loadModel(input_file):
    print("couldn't load model, aborting")
    return
  
  model = dm.getModel()
  
  modelelementsToExpand = COPASI.CModelExpansion_SetOfModelElements()
  map = COPASI.CModelExpansion_ElementsMap()
  speciesSet = COPASI.DataObjectSet()
  
  for comp in model.getCompartments(): 
  
    modelelementsToExpand.addCompartment(comp)
    
    for species in comp.getMetabolites(): 
      speciesSet.insert(species)
  
  modelelementsToExpand.fillDependencies(model)
  expansion = COPASI.CModelExpansion(model)
  expansion.createLinearArray(modelelementsToExpand, 5, speciesSet);
  
  dm.saveModel(output_file, True)
  

if __name__ == "__main__": 
  if len(sys.argv) < 3: 
    print("Usage: use_modelexpansion <input copasi file> <output copasi file>")
    sys.exit(1)
  expand_model(sys.argv[1], sys.argv[2])