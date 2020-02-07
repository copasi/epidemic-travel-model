#!/usr/bin/env python

import COPASI
import make_model.process_travel_data
import sys

def expand_model(input_file_path, output_file_path):
  """expands the model in the given file."""

  assert COPASI.CRootContainer.getRoot() != None
  # create a new datamodel
  dataModel = COPASI.CRootContainer.addDatamodel()
  assert COPASI.CRootContainer.getDatamodelList().size() == 1
  
  # load the base model
  dataModel.loadModel(input_file_path)
  
  # get the model from the datamodel
  model = dataModel.getModel()
  assert model != None
  
  modelName = 'SEIR State Travel'
  
  model.setObjectName(modelName)
  
  US_states = make_model.process_travel_data.stateKeysLoad('travel_data/state_county_FIPS.csv')
  
  US_state_populations = make_model.process_travel_data.statePopsLoad('travel_data/countypops_2013.csv')
  
  US_state_land_areas = make_model.process_travel_data.stateAreasLoad('state_land_area.txt')
  
  # Only model states which have population data and land area
  US_states = {key: value for (key, value) in US_states.items() if key in US_state_populations and value in US_state_land_areas}
  
  # Get the reverse mapping
  state_abrev_to_key = {value: key for (key, value) in US_states.items()}
  
  # Get the state-centric flows in and out
  state_fluxes = make_model.process_travel_data.makeStateFluxes('travel_data/commute_flow_counts.csv')
  
  # Get the periodic travel movement events ready.
  home_to_work_event = model.createEvent('home to work event')
  home_to_work_trigger_expression = 'sin(2*pi*<CN=Root,Model={0},Reference=Time>) > 0'.format(modelName)
  home_to_work_event.setTriggerExpression(home_to_work_trigger_expression)
  work_to_home_event = model.createEvent('work to home event')
  work_to_home_trigger_expression = 'sin(2*pi*(<CN=Root,Model={0},Reference=Time>+0.34)) > 0'.format(modelName)
  work_to_home_event.setTriggerExpression(work_to_home_trigger_expression)
  
  
  modelElementsToExpand = COPASI.CModelExpansion_SetOfModelElements()
  compartmentToReplicate = model.getCompartment(0)
  
  compartmentToReplicate.setObjectName('US')
  
  metabsToReplicate = {metab.getObjectName(): metab for metab in model.getMetabolites()}
  
  reactionsToReplicate = [reac for reac in model.getReactions()]
  
  flow_weight_template = '({0}*<{1}>/<{2}>)'
  
  total_adj_flow_template = '({0})/{1}'
  
  # Map of compartment species to CN, for use in event assignment creation
  comp_metab_CN = dict()
  
  # Make something to iterate over for event assignments, which with also have US_state_keys
  compartment_names_new = dict()
  
  # Map for the state keys to the new compartment names
  US_state_key_to_comp = dict()
  
  # Create all the replicate compartments (and species and reactions)
  for US_state_key, US_state_abrev in US_states.iteritems():
  
      # need an empty elements map, each time
      elementsMap = COPASI.CModelExpansion_ElementsMap()
      modelElementsToExpand.addCompartment(compartmentToReplicate)
  
      for metab in metabsToReplicate.values():
          modelElementsToExpand.addMetab(metab)
          
      for reaction in reactionsToReplicate:
          modelElementsToExpand.addReaction(reaction)
  
      modelElementsToExpand.fillDependencies(model)
      expansion = COPASI.CModelExpansion(model)
      expansion.duplicate(modelElementsToExpand, '_' + US_state_abrev, elementsMap)
  
      # Get the new metabs, for use below
      metabs = {name: elementsMap.getDuplicateFromObject(metabsToReplicate[name]) for name in metabsToReplicate.keys()}
  
      # change the particle numbers for the copied 'S' and 'N', to the given US state's population
      metabs['S'].setInitialValue(US_state_populations[US_state_key])
      metabs['N'].setInitialValue(US_state_populations[US_state_key])
  
      # set the compartment area to that of the state land area
      this_state_area = US_state_land_areas[US_state_abrev]
      elementsMap.getDuplicateFromObject(compartmentToReplicate).setInitialValue(this_state_area)
  
      # Add this (keyed) compartment name, for use in building event assignments
      compartment_name_new = elementsMap.getDuplicateFromObject(compartmentToReplicate).getObjectName()
      compartment_names_new[US_state_key] = compartment_name_new
  
      # Add the new CNs to the compartment+metab to ValueReference CN mapping
      for metab_name, metab in metabsToReplicate.iteritems():
          comp_metab_CN[(compartment_name_new, metab_name)] = elementsMap.getDuplicateFromObject(metab).getValueReference().getCN()
  
  # Build the event assignments
  for compartment_name in compartment_names_new.values():
  
      # Need the actual compartment metabs, because the metab concentration, not the particle number, needs to be the target
      compartment = model.getCompartments().getByName(compartment_name)
      compartment_metabs = compartment.getMetabolites()
  
      # Grab the land area, for use in creating the target as a concentration
      land_area = compartment.getInitialValue()
  
      # Work-around to match compartment names generated by CModelExpansionDuplicate to ones pulled in from the US_states
      state_abrev = compartment_name.replace(compartmentToReplicate.getObjectName() + '_', '') 
  
      # Load the data about how many move in and out
      state_flux = state_fluxes[state_abrev_to_key[state_abrev]]
      
      # Create assignment objects for all but the 'N' species
  #    event_assignments = {metab_name: movement_event.createAssignment() for metab_name in metabsToReplicate.keys() if metab_name is not 'N'}
  
  
  
      N_val_CN = comp_metab_CN[(compartment_name, 'N')]
  
      for metab_name in metabsToReplicate.keys():
          if metab_name is 'N':
              continue
          metab = compartment_metabs.getByName(metab_name)
          metab_val_CN = comp_metab_CN[(compartment_name, metab_name)]
      
          # Morning commute event flows
          # Build the list of morning event in-flow terms to string join
          inTermListMorning = list()
          inTermListMorning.append('<' + str(metab_val_CN) + '>') # particles before change
          for state_key, inFlow in state_flux[0].iteritems():
              name_compartment_from = compartment_names_new[state_key]
              this_N_val_CN = comp_metab_CN[(name_compartment_from, 'N')]
              this_metab_val_CN = comp_metab_CN[(name_compartment_from, metab_name)]
              inTerm = flow_weight_template.format(str(inFlow), str(this_metab_val_CN),str(this_N_val_CN))
              inTermListMorning.append(inTerm)
  

          # Build the list of morning event out-flow terms to string join
          outTermListMorning = list()
          for state_key, outFlow in state_flux[1].iteritems():
              outTerm = flow_weight_template.format(str(outFlow), str(metab_val_CN),str(N_val_CN))
              outTermListMorning.append(outTerm)
  

          flow_terms_morning = '+'.join(inTermListMorning) + '-' + '-'.join(outTermListMorning)
          full_expression_morning = total_adj_flow_template.format(flow_terms_morning, land_area)
 
          assignmentMorning = home_to_work_event.createAssignment()
          assignmentMorning.setTargetCN(metab.getCN())
          assignmentMorning.setExpression(full_expression_morning)

          # Evening return from work event flows
          # Build the list of evening event in-flow terms to string join
          inTermListEvening = list()
          inTermListEvening.append('<' + str(metab_val_CN) + '>') # particles before change
          for state_key, inFlow in state_flux[1].iteritems():
              name_compartment_from = compartment_names_new[state_key]
              this_N_val_CN = comp_metab_CN[(name_compartment_from, 'N')]
              this_metab_val_CN = comp_metab_CN[(name_compartment_from, metab_name)]
              inTerm = flow_weight_template.format(str(inFlow), str(this_metab_val_CN),str(this_N_val_CN))
              inTermListEvening.append(inTerm)
  

          # Build the list of evening event out-flow terms to string join
          outTermListEvening = list()
          for state_key, outFlow in state_flux[0].iteritems():
              outTerm = flow_weight_template.format(str(outFlow), str(metab_val_CN),str(N_val_CN))
              outTermListEvening.append(outTerm)
  

          flow_terms_evening = '+'.join(inTermListEvening) + '-' + '-'.join(outTermListEvening)
          full_expression_evening = total_adj_flow_template.format(flow_terms_evening, land_area)
 
          assignmentEvening = work_to_home_event.createAssignment()
          assignmentEvening.setTargetCN(metab.getCN())
          assignmentEvening.setExpression(full_expression_evening)
  
  print('Number of assigments = ' + str(home_to_work_event.getAssignments().size()) + '\n')
  print('Number of assigments = ' + str(work_to_home_event.getAssignments().size()) + '\n')
  
  model.forceCompile()
  
  dataModel.saveModel(output_file_path, True)


if __name__ == "__main__": 
  if len(sys.argv) < 3: 
    print("Usage: use_modelexpansion <input copasi file> <output copasi file>")
    sys.exit(1)
  else:
    expand_model(sys.argv[1], sys.argv[2])
