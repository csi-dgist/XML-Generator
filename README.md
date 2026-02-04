# DDS QoS XML Generator

This tool automatically generates XML files for DDS (Data Distribution Service) QoS test cases. It utilizes the Pairwise Testing methodology to create an efficient set of test cases by combining 16 different parameters.



### Parameter Overview

#### 1. ENTITY_FACTORY
- **Combinations**: (True, True), (False, False)

#### 2. DATA_EXISTS
- **Description**: Integrated parameter for PARTITION, USER_DATA, GROUP_DATA, and TOPIC_DATA.
- **Combinations**: (exists, exists), (not_exists, not_exists)

#### 3. RELIABILITY
- **Values**: Reliable, Best_effort
- **Combinations**: 2 × 2 = 4cases

#### 4. DURABILITY
- **Values**: Volatile, Transient_Local, Transient, Persistent
- **Combinations**: 4 × 4 = 16cases

#### 5. DEADLINE
- **Values**: 
  - `PP`: D < 2×PP 
  - `2×PP`: D ≥ 2×PP 
  - `DURATION_INFINITY`
- **Combinations**: 3 × 3 = 9cases

#### 6. LIVELINESS
- **Values**: 
  - `(AUTOMATIC, 0.5×PP)`: lease_duration < 2×PP
  - `(AUTOMATIC, PP)`: lease_duration < 2×PP
  - `(AUTOMATIC, 2×PP)`: lease_duration ≥ 2×PP
  - `(AUTOMATIC, DURATION_INFINITY)`
  - `(MANUAL_BY_PARTICIPANT, None)`
  - `(MANUAL_BY_TOPIC, None)`
- **Combinations**: 6 × 6 = 36cases

#### 7. HISTORY
- **Values**: 
  - `(KEEP_ALL, None)`: KEEP_ALL
  - `(KEEP_LAST, 1)`: depth=1
  - `(KEEP_LAST, <(RTT/PP)+2)`: depth < (RTT/PP)+2
  - `(KEEP_LAST, =(RTT/PP)+2)`: depth = (RTT/PP)+2
  - `(KEEP_LAST, >(RTT/PP)+2)`: depth > (RTT/PP)+2
- **Combinations**: 5 × 5 = 25cases

#### 8. RESOURCE_LIMITS_MAX_SAMPLES_PER_INSTANCE
- **Values**: 
  - `1`: = 1
  - `<(RTT/PP)+2`: < (RTT/PP)+2
  - `=(RTT/PP)+2`: = (RTT/PP)+2
  - `>(RTT/PP)+2`: > (RTT/PP)+2
- **Combinations**: 4 × 4 = 16cases

#### 9. RESOURCE_LIMITS_MAX_SAMPLES
- **Values**: `1`, `(RTT/PP+3)×PP`
- **Combinations**: 2 × 2 = 4cases

#### 10. LIFESPAN
- **Values**: `0.5×RTT`, `DURATION_INFINITY`
- **Combinations**: 2 × 2 = 4cases

#### 11. OWNERSHIP
- **Values**: `SHARED`, `EXCLUSIVE`
- **Combinations**: 2 × 2 = 4cases

#### 12. DESTINATION_ORDER
- **Values**: `BY_RECEPTION_TIMESTAMP`, `BY_SOURCE_TIMESTAMP`
- **Combinations**: 2 × 2 = 4cases

#### 13. WRITER_DATA_LIFECYCLE
- **Description**: Parameter applicable to Publisher only.
- **Values**: `True`, `False`
- **Combinations**: 2cases

#### 14. READER_DATA_LIFECYCLE_NO_WRITER
- **Description**: Parameter applicable to Subscriber only.
- **Values**: `0`, `3`
- **Combinations**: 2cases

#### 15. READER_DATA_LIFECYCLE_DISPOSED
- **Description**: Parameter applicable to Subscriber only.
- **Values**: `0`, `3`
- **Combinations**: 2cases

---

## Pairwise Testing Methodology

Pairwise testing is a combinatorial software testing method that, for each pair of input parameters to a system, tests all possible discrete combinations of those parameters. This ensures high test coverage with a significantly reduced number of test cases.



### Execution Results (Example: PP=0.1, RTT=0.2)

```
Total Test Cases Generated: 853
XML Files: 1,706 total (853 cases × 2 files per case)
  - pub_qos_case_00001.xml ~ pub_qos_case_00853.xml
  - sub_qos_case_00001.xml ~ sub_qos_case_00853.xml
```

---

## How to Use

### 1. Prerequisites

- Python 3.6 or higher
- Pairwise Algorithm Library:
  ```bash
  pip install allpairspy
  ```

### 2. Project Structure

```
XML Generator/
├── xml_generator.py      # Main execution script
├── xml/
│   ├── pub_qos.xml       # Publisher template
│   └── sub_qos.xml       # Subscriber template
└── output/               # Directory for generated XML files
```

### 3. Execution

```bash
cd "/home/user/ros2_ws/src/XML Generator"
python3 xml_generator.py
```

Provide the following inputs when prompted:
- **PP (Publication Period)**: Publication Period 
- **RTT (Round Trip Time)**: Round Trip Time 


### 4. Execution Example

```
============================================================
DDS QoS XML Generator
============================================================
Enter PP (Publication Period) in seconds: 0.1
Enter RTT (Round Trip Time) in seconds: 0.2

Input Values:
  PP: 0.1 sec
  RTT: 0.2 sec
  RTT/PP: 2.00
Generating test case combinations...
Total 853 test cases generated.

Generating XML files...
Progress: 100/853 (11%)
Progress: 200/853 (23%)
...
Progress: 800/853 (93%)

Complete! A total of 853 test cases have been generated.
Output Directory: output/
```

### 6. Precautions

- **PP Value**: Must be a value greater than 0.
- **File Overwriting**: Existing files with the same name in the output/ directory will be overwritten.
- **Directory Creation**: The `output/` directory will be created automatically if it does not exist.

---
