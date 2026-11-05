# DFA-GPT2 Dataset

This repository contains the datasets and data generation script used in the DFA-GPT2 study.

## 1. Dataset Description

The main dataset consists of two subsets:

- `train.jsonl`: Training dataset containing 10,000 samples.
- `test.jsonl`: Test dataset containing 1,000 samples.

The repository also includes CSV versions of the training and test datasets.

All datasets are provided in JSON Lines (JSONL) or CSV format.

## 2. Data Format

Each JSONL record contains a DFA-related input and its corresponding target output.

The records include:

- DFA states
- Input alphabet
- Transition table
- Initial state
- Final states
- Input string
- Simulation steps
- Final state
- Acceptance or rejection result

## 3. Out-of-Distribution (OOD) Datasets

Three out-of-distribution (OOD) datasets are included in this repository:

- `ood_len_13_20.jsonl`: DFAs with input strings of lengths between 13 and 20.
- `ood_len_21_30.jsonl`: DFAs with input strings of lengths between 21 and 30.
- `ood_states_9_12.jsonl`: DFAs containing between 9 and 12 states, with input strings of lengths between 0 and 12.

Each OOD dataset contains 300 samples.

The OOD datasets were generated using `ood.py`. The generation procedure excludes exact DFA signatures found in the training and test datasets and avoids duplicate signatures across the generated OOD subsets.

## 4. OOD Dataset Generation

### Requirements

- Python 3
- Python standard library

### Usage

Run the following command from the repository's root directory:

```bash
python ood.py --train train.jsonl --test test.jsonl --n 300 --seed 2025 --out .
```

The script generates the three OOD JSONL files in the repository's root directory.

## 5. Repository Structure

```text
dfadata/
├── README.md
├── ood.py
├── train.jsonl
├── test.jsonl
├── train.csv
├── test.csv
├── ood_len_13_20.jsonl
├── ood_len_21_30.jsonl
└── ood_states_9_12.jsonl
```

## 6. Data Availability

The training dataset, test dataset, OOD datasets, and OOD data generation script are publicly available at:

https://github.com/babyshark023/dfadata
