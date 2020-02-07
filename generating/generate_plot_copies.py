#!/usr/bin/env python

import COPASI
import make_model.copasi_plot_utils as mmcpu
from lxml import etree
from copy import deepcopy
import sys

def replicate_plots(input_file_path, output_file_path):
    """Generate plots for the other compartmens, like
    for the first one.
    """

    tree = etree.parse(input_file_path)
    root_element = tree.getroot()

    plot_list_elem = mmcpu.plots_list_element(root_element)
    plot_spec_elem_orig = mmcpu.first_plot_spec_element(plot_list_elem)

    statesList = [
    ('US_FL', 'Florida'),
    ('US_WA', 'Washington'),
    ('US_CA', 'California'),
    ('US_VT', 'Vermont'),
    ('US_TN', 'Tennessee'),
    ('US_AL', 'Alabama'),
    ('US_AK', 'Alaska'),
    ('US_AZ', 'Arizona'),
    ('US_AR', 'Arkansas'),
    ('US_CO', 'Colorado'),
    ('US_CT', 'Connecticut'),
    ('US_DE', 'Delaware'),
    ('US_DC', 'District of Columbia'),
    ('US_GA', 'Georgia'),
    ('US_HI', 'Hawaii'),
    ('US_ID', 'Idaho'),
    ('US_IL', 'Illinois'),
    ('US_IN', 'Indiana'),
    ('US_IA', 'Iowa'),
    ('US_KS', 'Kansas'),
    ('US_KY', 'Kentucky'),
    ('US_LA', 'Louisiana'),
    ('US_ME', 'Maine'),
    ('US_MD', 'Maryland'),
    ('US_MA', 'Massachusetts'),
    ('US_MI', 'Michigan'),
    ('US_MN', 'Minnesota'),
    ('US_MS', 'Mississippi'),
    ('US_MO', 'Missouri'),
    ('US_MT', 'Montana'),
    ('US_NE', 'Nebraska'),
    ('US_NV', 'Nevada'),
    ('US_NH', 'New Hampshire'),
    ('US_NJ', 'New Jersey'),
    ('US_NM', 'New Mexico'),
    ('US_NY', 'New York'),
    ('US_NC', 'North Carolina'),
    ('US_ND', 'North Dakota'),
    ('US_OH', 'Ohio'),
    ('US_OK', 'Oklahoma'),
    ('US_OR', 'Oregon'),
    ('US_PA', 'Pennsylvania'),
    ('US_RI', 'Rhode Island'),
    ('US_SC', 'South Carolina'),
    ('US_SD', 'South Dakota'),
    ('US_TX', 'Texas'),
    ('US_UT', 'Utah'),
    ('US_VA', 'Virginia'),
    ('US_WV', 'West Virginia'),
    ('US_WI', 'Wisconsin'),
    ('US_WY', 'Wyoming'),
    ]

    for compartment, state in statesList:
        plot_spec_elem_copy = deepcopy(plot_spec_elem_orig)
        mmcpu.rename_plot_parts(plot_spec_elem_copy, state, compartment)
        plot_list_elem.append(plot_spec_elem_copy)

    tree.write(output_file_path)

if __name__ == "__main__": 
  if len(sys.argv) < 3: 
    print("Usage: use_modelexpansion <input copasi file> <output copasi file>")
    sys.exit(1)
  else:
    replicate_plots(sys.argv[1], sys.argv[2])
