// ADMIN PANEL CONFIGURATION

// Enter apps in any order
// Original app name should map to ORDER_INDEX, DESIRED_NAME
// ORDER_INDEX numbers don't need to be consecutive
// Something that needs to be at the end may have index 100

var APPS = {
    'Microdevices': [2, 'MPS Centers & Models'],
    'Assays': [4, 'MPS Assays'],
    'Cellsamples': [6, 'Cell Characteristics'],
    'Compounds': [8, 'Compound'],
    'Bioactivities': [10, 'External Compound/Drug Bioactivity'],
    'Drugtrials': [12, 'MPS & External Drug Effects'],
    'Resources': [14, 'Resources'],
    'Auth': [20, 'Authentication'],
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
    //Order modified
    'Assays': {
        'Chip Results': [2, 'Chip Results', 0],
        'Result types': [4, 'Result Types', 1, true],
        'Functions': [6, 'Functions', 2, true],
        'Chip Readouts': [8, 'Chip Readouts', 1],
        'Assay runs': [10, 'Runs', 2],
        'Assay plate test results' : [11, 'Plate Results', 0],
        'Plate Readouts': [12, 'Plate Readouts', 1],
        'Assay models': [16, 'Assays', 2],
        'Assay model types': [18, 'Assay Types', 3, true],
        'Assay layouts': [22, 'Assay Layouts', 2],
        'Assay base layouts': [24, 'Base Layouts', 3],
        'Assay layout formats': [26, 'Layout Formats', 4],
        'Assay well types': [30, 'Virtual Well Types', 4, true],
        'Assay readers': [32, 'Reader Devices', 2],
        'Readout units': [36, 'Readout Units', 0, true],
        'Physical Units': [38, 'Measurement Units', 0, true],
        'Time Units' : [40, 'Time Units', 0, true],
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
