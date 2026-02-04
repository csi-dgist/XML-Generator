# DDS QoS XML Generator

DDS QoS 테스트 케이스를 위한 XML 파일 자동 생성 도구입니다. 16개 파라미터의 조합을 Pairwise 테스트 방식으로 생성하여 효율적인 테스트 케이스를 만듭니다.




### 전체 파라미터 개요

#### 1. ENTITY_FACTORY
- **조합**: (True, True), (False, False)

#### 2. DATA_EXISTS
- **설명**: PARTITION, USER_DATA, GROUP_DATA, TOPIC_DATA를 통합한 파라미터
- **조합**: (exists, exists), (not_exists, not_exists)

#### 3. RELIABILITY
- **값 종류**: Reliable, Best_effort
- **조합**: 2 × 2 = 4개

#### 4. DURABILITY
- **값 종류**: Volatile, Transient_Local, Transient, Persistent
- **조합**: 4 × 4 = 16개

#### 5. DEADLINE
- **값 종류**: 
  - `PP`: D < 2×PP 케이스
  - `2×PP`: D ≥ 2×PP 케이스
  - `DURATION_INFINITY`: 무한대
- **조합**: 3 × 3 = 9개

#### 6. LIVELINESS
- **값 종류**: 
  - `(AUTOMATIC, 0.5×PP)`: lease_duration < 2×PP
  - `(AUTOMATIC, PP)`: lease_duration < 2×PP
  - `(AUTOMATIC, 2×PP)`: lease_duration ≥ 2×PP
  - `(AUTOMATIC, DURATION_INFINITY)`: 무한대
  - `(MANUAL_BY_PARTICIPANT, None)`
  - `(MANUAL_BY_TOPIC, None)`
- **조합**: 6 × 6 = 36개

#### 7. HISTORY
- **값 종류**: 
  - `(KEEP_ALL, None)`: KEEP_ALL
  - `(KEEP_LAST, 1)`: depth=1
  - `(KEEP_LAST, <(RTT/PP)+2)`: depth < (RTT/PP)+2
  - `(KEEP_LAST, =(RTT/PP)+2)`: depth = (RTT/PP)+2
  - `(KEEP_LAST, >(RTT/PP)+2)`: depth > (RTT/PP)+2
- **조합**: 5 × 5 = 25개

#### 8. RESOURCE_LIMITS_MAX_SAMPLES_PER_INSTANCE
- **값 종류**: 
  - `1`: = 1
  - `<(RTT/PP)+2`: < (RTT/PP)+2
  - `=(RTT/PP)+2`: = (RTT/PP)+2
  - `>(RTT/PP)+2`: > (RTT/PP)+2
- **조합**: 4 × 4 = 16개

#### 9. RESOURCE_LIMITS_MAX_SAMPLES
- **값 종류**: `1`, `(RTT/PP+3)×PP`
- **조합**: 2 × 2 = 4개

#### 10. LIFESPAN
- **값 종류**: `0.5×RTT`, `DURATION_INFINITY`
- **조합**: 2 × 2 = 4개

#### 11. OWNERSHIP
- **값 종류**: `SHARED`, `EXCLUSIVE`
- **조합**: 2 × 2 = 4개

#### 12. DESTINATION_ORDER
- **값 종류**: `BY_RECEPTION_TIMESTAMP`, `BY_SOURCE_TIMESTAMP`
- **조합**: 2 × 2 = 4개

#### 13. WRITER_DATA_LIFECYCLE
- **설명**: Publisher에만 적용되는 파라미터
- **값 종류**: `True`, `False`
- **조합**: 2개

#### 14. READER_DATA_LIFECYCLE_NO_WRITER
- **설명**: Subscriber에만 적용되는 파라미터
- **값 종류**: `0`, `3`
- **조합**: 2개

#### 15. READER_DATA_LIFECYCLE_DISPOSED
- **설명**: Subscriber에만 적용되는 파라미터
- **값 종류**: `0`, `3`
- **조합**: 2개

---

## Pairwise 테스트 케이스 생성 방식

Pairwise 테스트는 모든 파라미터 쌍의 조합을 최소 한 번씩 커버하는 최소 테스트 케이스를 생성하는 방법




### 실제 실행 결과 (PP=0.1, RTT=0.2)

```
총 853개의 테스트 케이스 생성
XML 파일: 1,706개 (853개 케이스 × 2 파일)
  - pub_qos_case_00001.xml ~ pub_qos_case_00853.xml
  - sub_qos_case_00001.xml ~ sub_qos_case_00853.xml
```

---

## 실행 방법

### 1. 필수 요구사항

- Python 3.6 이상
- 필수 라이브러리:


- Pairwise 알고리즘 라이브러리:
  ```bash
  pip install allpairspy
  ```

### 2. 파일 구조

```
XML Generator/
├── xml_generator.py      # 메인 코드
├── xml/
│   ├── pub_qos.xml       # Publisher 템플릿
│   └── sub_qos.xml       # Subscriber 템플릿
└── output/               # 생성된 XML 파일 저장 디렉토리
```

### 3. 실행 방법

```bash
cd "/home/user/ros2_ws/src/XML Generator"
python3 xml_generator.py
```

실행 시 다음 정보를 입력합니다:
- **PP (Publication Period)**: Publication Period 값 (초)
- **RTT (Round Trip Time)**: Round Trip Time 값 (초)


### 4. 실행 예시

```
============================================================
DDS QoS XML Generator
============================================================
PP (Publication Period) 값을 입력하세요 (초): 0.1
RTT (Round Trip Time) 값을 입력하세요 (초): 0.2

입력된 값:
  PP: 0.1 초
  RTT: 0.2 초
  RTT/PP: 2.00
테스트 케이스 조합 생성 중...
총 853개의 테스트 케이스 생성

XML 파일 생성 중...
진행 중: 100/853 (11%)
진행 중: 200/853 (23%)
...
진행 중: 800/853 (93%)

완료! 총 853개의 테스트 케이스가 생성되었습니다.
출력 디렉토리: output/
```

### 6. 주의사항

- **PP 값**: 0보다 큰 값이어야 합니다.
- **기존 파일**: 같은 이름의 파일이 있으면 덮어씁니다.
- **디렉토리**: `output/` 디렉토리가 없으면 자동으로 생성됩니다.

---
