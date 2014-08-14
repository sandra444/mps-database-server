// ADMIN PANEL CONFIGURATION

// Enter apps in any order
// Original app name should map to ORDER_INDEX, DESIRED_NAME
// ORDER_INDEX numbers don't need to be consecutive
// Something that needs to be at the end may have index 100

var APPS = {
    'Auth': [10, 'Authentication'],
    'Microdevices': [2, 'MPS Centers & Models'],
    'Compounds': [4, 'Compound'],
    'Bioactivities': [6, 'External Compound/Drug Bioactivity'],
    'Drugtrials': [7, 'MPS & External Drug Effects'],
    'Cellsamples': [8, 'Cell Characteristics'],
    'Assays': [5, 'MPS Assays'],
    'Resources': [3, 'Resources'],
    'Sites': [100, 'MPS Host']
};

// Enter apps/models

// Original model name should map to:
// ORDER_INDEX, DESIRED_NAME, INDENT, HIDE

// You need to specify HIDE_REMOVE item only if model needs to be hidden

// WARNING: It appears to be the case that 5 indents is the maximum indentation!
//Can change maximum indentation allowed in admintools under indent = ...

var MODELS = {
    'Auth': {
        'Groups': [1, 'Groups', 0],
        'Users': [2, 'Users', 1]
    },
    'Microdevices': {
        'Microphysiology centers': [1, 'Microphysiology Centers', 0],
        'Microdevices': [8, 'Devices', 2],
        'Organ models': [4, 'Organ models', 1]
    },
    'Assays': {
        'Assay tests': [0, 'Tests and Results', 0],
        'Assay test results': [2, 'Test Results', 0],
        'Assay findings': [3, 'Findings', 1],
        'Assay finding types': [4, 'Finding Types', 2, true],
        'Assay device readouts': [5, 'Readouts', 1],
        'Readout units': [20, 'Readout Units', 2, true],
        'Assay models': [8, 'Assays', 2],
        'Assay runs': [7, 'Runs', 2],
        'Assay model types': [9, 'Assay Types', 3, true],
        'Assay layouts': [11, 'Assay Layouts', 2],
        'Assay base layouts': [13, 'Base Layouts', 3],
        'Assay layout formats': [15, 'Layout Formats', 4],
        'Assay well types': [17, 'Virtual Well Types', 3, true],
        'Assay readers': [19, 'Reader Devices', 2],
        'Physical Units': [21, 'Units of Measurement', 0, true],
        'Time Units' : [23, 'Units of Time', 0, true]
    },
    'Compounds': {
        'Compounds': [1, 'Compounds/Drugs', 0]
    },
    'Bioactivities': {
        'Assays': [1, 'External Assays', 1],
        'Bioactivities': [0, 'Bioactivities', 0],
        'Targets': [3, 'Targets', 1]
    },
    'Cellsamples': {
        'Cell samples': [2, 'Cell Samples', 0],
        'Cell types': [3, 'Cell Types', 1],
        'Cell subtypes': [4, 'Cell Subtypes', 2],
        'Suppliers': [5, 'Suppliers', 1],
        'Organs': [1, 'Organs', 0]
    },
    'Drugtrials': {
        'Drug trials': [1, 'Drug Trials', 0],
        'Species': [2, 'Species', 1],
        'Participants': [3, 'Participants', 2],
        'Tests': [4, 'Tests', 1],
        'Findings': [6, 'Findings', 1],
        'Trial sources': [8, 'Trial Sources', 1, true],
        'Finding types': [7, 'Finding Types', 2],
        'Test types': [5, 'Test Types', 2],
        'Result descriptors': [13, 'Result Descriptors', 0, true]
    },
    'Resources':{
        'Resources': [1, 'Resources', 0],
        'Resource types': [4, 'Resource Types', 1],
        'Resource subtypes': [7, 'Resource Subtypes', 2]
    },
    'Sites': {
        'Sites': [1, 'MPS Host (Do not change)', 0]
    }
};
