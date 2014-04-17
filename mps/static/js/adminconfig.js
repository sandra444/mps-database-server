// ADMIN PANEL CONFIGURATION

// Enter apps in any order
// Original app name should map to ORDER_INDEX, DESIRED_NAME
// ORDER_INDEX numbers don't need to be consecutive
// Something that needs to be at the end may have index 100

var APPS = {
    'Auth': [10, 'Authentication'],
    'Microdevices': [2, 'MPS Centers & Models'],
    'Compounds': [6, 'Compound'],
    'Bioactivities': [7, 'External Compound/Drug Bioactivity'],
    'Drugtrials': [8, 'MPS & External Drug Effects'],
    'Cellsamples': [4, 'Cell Characteristics'],
    'Assays': [7, 'MPS Assays'],
    'Sites': [100, 'MPS Host']
};

// Enter apps/models

// Original model name should map to:
// ORDER_INDEX, DESIRED_NAME, INDENT, HIDE

// You need to specify HIDE_REMOVE item only if model needs to be hidden

// WARNING: It appears to be the case that 3 indents is the maximum indentation!

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
        'Assay tests': [0, 'Assay Tests and Results', 0],
        'Assay device readouts': [1, 'Assay Readouts', 1],
        'Assay models': [2, 'Assays', 2],
        'Assay model types': [3, 'Assay Types', 3],
        'Assay layouts': [4, 'Assay Layouts', 2],
        'Assay base layouts': [5, 'Base Layouts', 3],
        'Assay layout formats': [6, 'Layout Formats', 3],
        'Assay well types': [7, 'Virtual Well Types', 3],
        'Assay readers': [8, 'Assay Reader Devices', 2],
        'Physical Units': [9, 'Physical Units of Measurement', 0],
        'Time Units' : [10, 'Units of Time', 0]
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
    'Sites': {
        'Sites': [1, 'MPS Host (Do not change)', 0]
    }
};
