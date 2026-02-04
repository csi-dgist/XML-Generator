#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
XML Generator for DDS QoS Test Cases
"""

import os
import xml.etree.ElementTree as ET
from typing import Dict, List, Tuple, Any
import xml.dom.minidom


# allpairspy 라이브러리 사용
try:
    from allpairspy import AllPairs
except ImportError:
    print("오류: allpairspy가 설치되지 않았습니다.")
    print("설치하세요: pip install allpairspy")
    raise

# DDS QoS 테스트 케이스 XML 생성기
class XMLGenerator:
    
    def __init__(self, pp: float, rtt: float):

        self.pp = pp # publish period(s)
        self.rtt = rtt # round trip time(s)
        self.rtt_over_pp = rtt / pp if pp > 0 else 0
        self.parameters = self._define_parameters()
    
    # ============================================================================
    # 파라미터 정의
    # ============================================================================
    
    def _define_parameters(self) -> Dict[str, Dict[str, Any]]:
        rtt_pp = self.rtt_over_pp
        
        return {
            'ENTITY_FACTORY': {
                'pub': [True, False],
                'sub': [True, False],
                'type': 'boolean'
            },
            'DATA_EXISTS': {
                'pub': ['exists', 'not_exists'],  # USER/GROUP/TOPIC_DATA 통합
                'sub': ['exists', 'not_exists'],  # pub와 sub는 항상 동일
                'type': 'string'
            },
            'PARTITION': {
                'pub': ['exists', 'not_exists'],
                'sub': ['exists', 'not_exists'],
                'type': 'string'
            },
            'RELIABILITY': {
                'pub': ['RELIABLE', 'BEST_EFFORT'],
                'sub': ['RELIABLE', 'BEST_EFFORT'],
                'type': 'enum'
            },
            'DURABILITY': {
                'pub': ['TRANSIENT_LOCAL', 'VOLATILE', 'TRANSIENT', 'PERSISTENT'],  
                'sub': ['TRANSIENT_LOCAL', 'VOLATILE', 'TRANSIENT', 'PERSISTENT'],  
                'type': 'enum'
            },
            'DEADLINE': {
                'pub': [self.pp, 2*self.pp, 'DURATION_INFINITY'],
                'sub': [self.pp, 2*self.pp, 'DURATION_INFINITY'],
                'type': 'duration'
            },
            'LIVELINESS': {
                'pub': [
                    ('AUTOMATIC', 0.5*self.pp),  
                    ('AUTOMATIC', self.pp),      
                    ('AUTOMATIC', 2*self.pp),     
                    ('AUTOMATIC', 'DURATION_INFINITY'),
                    ('MANUAL_BY_PARTICIPANT', None),
                    ('MANUAL_BY_TOPIC', None)
                ],
                'sub': [
                    ('AUTOMATIC', 0.5*self.pp),  
                    ('AUTOMATIC', self.pp),      
                    ('AUTOMATIC', 2*self.pp),    
                    ('AUTOMATIC', 'DURATION_INFINITY'),
                    ('MANUAL_BY_PARTICIPANT', None),
                    ('MANUAL_BY_TOPIC', None)
                ],
                'type': 'liveliness_combined'
            },
            'HISTORY': {
                'pub': [
                    ('KEEP_ALL', None),
                    ('KEEP_LAST', 1),                                   
                    ('KEEP_LAST', max(1, int(rtt_pp)+1)),               
                    ('KEEP_LAST', int(rtt_pp)+2),                       
                    ('KEEP_LAST', int((rtt_pp)+2)*int(self.pp))        
                ],
                'sub': [
                    ('KEEP_ALL', None),
                    ('KEEP_LAST', 1),                                  
                    ('KEEP_LAST', max(1, int(rtt_pp)+1)),              
                    ('KEEP_LAST', int(rtt_pp)+2),                       
                    ('KEEP_LAST', int((rtt_pp)+2)*int(self.pp))         
                ],
                'type': 'history_combined'
            },
            'RESOURCE_LIMITS_MAX_SAMPLES_PER_INSTANCE': {
                'pub': [
                    1,                                    
                    max(1, int(rtt_pp)+1),              
                    int(rtt_pp)+2,                       
                    int((rtt_pp)+2)*int(self.pp)         
                ],
                'sub': [
                    1,                                   
                    max(1, int(rtt_pp)+1),              
                    int(rtt_pp)+2,                      
                    int((rtt_pp)+2)*int(self.pp)        
                ],
                'type': 'number'
            },
            'RESOURCE_LIMITS_MAX_SAMPLES': {
                'pub': [1, int((rtt_pp)+3)*int(self.pp)],
                'sub': [1, int((rtt_pp)+3)*int(self.pp)],
                'type': 'number'
            },
            'LIFESPAN': {
                'pub': [0.5*self.rtt, 'DURATION_INFINITY'],
                'sub': [0.5*self.rtt, 'DURATION_INFINITY'],
                'type': 'duration'
            },
            'OWNERSHIP': {
                'pub': ['SHARED', 'EXCLUSIVE'],
                'sub': ['SHARED', 'EXCLUSIVE'],
                'type': 'enum'
            },
            'DESTINATION_ORDER': {
                'pub': ['BY_RECEPTION_TIMESTAMP', 'BY_SOURCE_TIMESTAMP'],
                'sub': ['BY_RECEPTION_TIMESTAMP', 'BY_SOURCE_TIMESTAMP'],
                'type': 'enum'
            },
            'WRITER_DATA_LIFECYCLE': {
                'pub': [True, False],  # pub만
                'sub': None,
                'type': 'boolean'
            },
            'READER_DATA_LIFECYCLE_NO_WRITER': {
                'pub': None,  # sub만
                'sub': [0, 3],
                'type': 'number'
            },
            'READER_DATA_LIFECYCLE_DISPOSED': {
                'pub': None,  # sub만
                'sub': [0, 3],
                'type': 'number'
            }
        }
    
    # ============================================================================
    # 조합 생성
    # ============================================================================
    
    def _get_param_values(self, param_name: str) -> List[Dict[str, Any]]:

        # 파라미터의 가능한 pub/sub 값 조합 리스트 반환
        param = self.parameters[param_name]
        pub_vals = param['pub'] if param['pub'] else [None]
        sub_vals = param['sub'] if param['sub'] else [None]
        
        combinations = []
        
        # 케이스 1: READER_DATA_LIFECYCLE - sub 값만 사용
        if param_name in ('READER_DATA_LIFECYCLE_NO_WRITER', 'READER_DATA_LIFECYCLE_DISPOSED'):
            for val in sub_vals:
                combinations.append({
                    'param': param_name,
                    'pub': None,
                    'sub': val
                })
        
        # 케이스 2: ENTITY_FACTORY, DATA_EXISTS, PARTITION - pub=sub로 제한 
        elif param_name in ('ENTITY_FACTORY', 'DATA_EXISTS', 'PARTITION'):
            for val in pub_vals:
                combinations.append({
                    'param': param_name,
                    'pub': val,
                    'sub': val
                })
        
        # 케이스 3: 나머지 파라미터 - pub와 sub 독립 설정
        else:
            for pub_val in pub_vals:
                for sub_val in sub_vals:
                    combinations.append({
                        'param': param_name,
                        'pub': pub_val,
                        'sub': sub_val
                    })
        
        return combinations
    
    def generate_pairwise_combinations(self) -> List[Dict[str, Any]]:
        # 모든 파라미터 쌍의 조합을 최소 한 번씩 커버하는 최소 케이스 생성 (Pairwise 테스트 케이스)

        # 파라미터 이름 수집 (PARTITION 제외 - 원래 853개 케이스 유지)
        param_names = [
            name for name in self.parameters.keys() 
            if name != 'PARTITION' and  # PARTITION은 별도로 처리
            (self.parameters[name]['pub'] is not None or 
             self.parameters[name]['sub'] is not None)
        ]
        
        # 각 파라미터의 가능한 값들을 리스트로 준비
        param_value_lists = []
        param_index_map = {}
        
        for idx, param_name in enumerate(param_names):
            param_values = self._get_param_values(param_name)
            param_value_lists.append([(idx, val) for val in param_values])
            param_index_map[idx] = param_name
        
        # allpairspy 라이브러리 사용 
        print("  [알고리즘] allpairspy 라이브러리 사용 (IPOG 알고리즘)")
        pairwise_cases = []
        for pairs in AllPairs(param_value_lists):
            test_case = {}
            
            # 각 파라미터 값 설정
            for param_idx, param_value in pairs:
                param_name = param_index_map[param_idx]
                test_case[param_name] = {
                    'pub': param_value['pub'],
                    'sub': param_value['sub']
                }
            
            # READER_DATA_LIFECYCLE 제약 조건 체크
            if ('READER_DATA_LIFECYCLE_NO_WRITER' in test_case and 
                'READER_DATA_LIFECYCLE_DISPOSED' in test_case):
                if (test_case['READER_DATA_LIFECYCLE_NO_WRITER']['sub'] != 
                    test_case['READER_DATA_LIFECYCLE_DISPOSED']['sub']):
                    continue  # 서로 다른 값이면 제외
            
            # PARTITION을 DATA_EXISTS와 동일하게 설정 (원래 동작 유지)
            if 'DATA_EXISTS' in test_case:
                test_case['PARTITION'] = {
                    'pub': test_case['DATA_EXISTS']['pub'],
                    'sub': test_case['DATA_EXISTS']['sub']
                }
            
            pairwise_cases.append(test_case)
        
        return pairwise_cases
    
    # ============================================================================
    # XML 생성 유틸리티
    # ============================================================================
    
    
    def _format_duration(self, value: Any) -> Tuple[str, str]:
    # duration 값을 (sec, nanosec) 튜플로 변환  
        if value == 'DURATION_INFINITY':
            return ('DURATION_INFINITY', '0')
        elif isinstance(value, (int, float)):
            sec = int(value)
            nanosec = int((value - sec) * 1e9)
            return (str(sec), str(nanosec))
        else:
            return ('0', '0')
    
    def _update_xml_element(self, root: ET.Element, xpath: str, value: Any, value_type: str = None):
    # XML 요소 업데이트
        try:
            element = root.find(xpath)
            if element is not None:
                if value_type == 'boolean':
                    element.text = str(value).lower()
                elif value_type == 'duration':
                    sec, nanosec = self._format_duration(value)
                    sec_elem = element.find('.//sec')
                    nanosec_elem = element.find('.//nanosec')
                    if sec_elem is not None:
                        sec_elem.text = sec
                    if nanosec_elem is not None:
                        nanosec_elem.text = nanosec
                else:
                    element.text = str(value)
        except Exception as e:
            print(f"Warning: Could not update {xpath}: {e}")
    
    def _pretty_print_xml(self, tree: ET.ElementTree, output_path: str):
        root = tree.getroot()
        
        # 네임스페이스 접두사 제거
        for elem in root.iter():
            if elem.tag.startswith('{'):
                elem.tag = elem.tag.split('}')[1]
            for key in list(elem.attrib.keys()):
                if key.startswith('{'):
                    new_key = key.split('}')[1]
                    elem.attrib[new_key] = elem.attrib.pop(key)
        
        # 네임스페이스 속성 제거
        if 'xmlns' in root.attrib:
            root.attrib.pop('xmlns')
        if 'xmlns:ns0' in root.attrib:
            root.attrib.pop('xmlns:ns0')
        
        rough_string = ET.tostring(root, encoding='unicode')
        reparsed = xml.dom.minidom.parseString(rough_string)
        pretty_xml = reparsed.toprettyxml(indent="    ", encoding=None)
        
        # XML 선언 줄 수정
        lines = pretty_xml.split('\n')
        if lines[0].startswith('<?xml'):
            lines[0] = '<?xml version="1.0" encoding="UTF-8" ?>'
        
        # 빈 줄 제거 및 정리
        cleaned_lines = []
        prev_empty = False
        for line in lines:
            if line.strip():
                cleaned_lines.append(line)
                prev_empty = False
            elif not prev_empty:
                cleaned_lines.append('')
                prev_empty = True
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(cleaned_lines))
    
    # ============================================================================
    # XML 파일 생성
    # ============================================================================
    
    def generate_pub_xml(self, test_case: Dict[str, Dict[str, Any]], 
                        output_path: str, case_num: int):

        tree = ET.parse('xml/pub_qos.xml')
        root = tree.getroot()
        
        # 네임스페이스 제거 (find가 제대로 작동하도록)
        for elem in root.iter():
            if '}' in elem.tag:
                elem.tag = elem.tag.split('}')[1]
        
        # QoS 파라미터 설정
        if 'ENTITY_FACTORY' in test_case:
            self._update_xml_element(
                root, 
                './/entity_factory/autoenable_created_entities',
                test_case['ENTITY_FACTORY']['pub'],
                'boolean'
            )
        
        # PARTITION (별도 처리)
        if 'PARTITION' in test_case:
            partition_exists = test_case['PARTITION']['pub'] == 'exists'
            partition_name = root.find('.//partition/names/name')
            if partition_name is not None:
                partition_name.text = 'a' if partition_exists else ''
        
        # DATA_EXISTS (USER_DATA, GROUP_DATA, TOPIC_DATA 통합)
        if 'DATA_EXISTS' in test_case:
            data_exists = test_case['DATA_EXISTS']['pub'] == 'exists'
            
            # USER_DATA
            user_data_value = root.find('.//userData/value')
            if user_data_value is not None:
                user_data_value.text = '56.30.0.1' if data_exists else ''
            
            # GROUP_DATA
            group_data_value = root.find('.//groupData/value')
            if group_data_value is not None:
                group_data_value.text = '5.3.1.0.F1' if data_exists else ''
            
            # TOPIC_DATA (pub XML에서도 <topic> 안에 있음)
            topic_data_value = root.find('.//topic/topicData/value')
            if topic_data_value is not None:
                topic_data_value.text = '5.3.1.0' if data_exists else ''
        
        # RELIABILITY
        if 'RELIABILITY' in test_case:
            self._update_xml_element(
                root,
                './/reliability/kind',
                test_case['RELIABILITY']['pub']
            )
        
        # DURABILITY
        if 'DURABILITY' in test_case:
            self._update_xml_element(
                root,
                './/durability/kind',
                test_case['DURABILITY']['pub']
            )
        
        # DEADLINE
        if 'DEADLINE' in test_case:
            self._update_xml_element(
                root,
                './/deadline/period',
                test_case['DEADLINE']['pub'],
                'duration'
            )
        
        # LIVELINESS 
        if 'LIVELINESS' in test_case:
            liveliness_value = test_case['LIVELINESS']['pub']
            if isinstance(liveliness_value, tuple):
                kind, lease_duration = liveliness_value
                self._update_xml_element(
                    root,
                    './/liveliness/kind',
                    kind
                )
                if lease_duration is not None:
                    self._update_xml_element(
                        root,
                        './/liveliness/lease_duration',
                        lease_duration,
                        'duration'
                    )
        
        # HISTORY (통합)
        if 'HISTORY' in test_case:
            history_value = test_case['HISTORY']['pub']
            if isinstance(history_value, tuple):
                kind, depth = history_value
                self._update_xml_element(
                    root,
                    './/historyQos/kind',
                    kind
                )
                if depth is not None:
                    self._update_xml_element(
                        root,
                        './/historyQos/depth',
                        depth
                    )
        
        # RESOURCE_LIMITS_MAX_SAMPLES_PER_INSTANCE
        if 'RESOURCE_LIMITS_MAX_SAMPLES_PER_INSTANCE' in test_case:
            self._update_xml_element(
                root,
                './/resourceLimitsQos/max_samples_per_instance',
                int(test_case['RESOURCE_LIMITS_MAX_SAMPLES_PER_INSTANCE']['pub'])
            )
        
        # RESOURCE_LIMITS_MAX_SAMPLES
        if 'RESOURCE_LIMITS_MAX_SAMPLES' in test_case:
            self._update_xml_element(
                root,
                './/resourceLimitsQos/max_samples',
                int(test_case['RESOURCE_LIMITS_MAX_SAMPLES']['pub'])
            )
        
        # LIFESPAN
        if 'LIFESPAN' in test_case:
            self._update_xml_element(
                root,
                './/lifespan/duration',
                test_case['LIFESPAN']['pub'],
                'duration'
            )
        
        # OWNERSHIP
        if 'OWNERSHIP' in test_case:
            self._update_xml_element(
                root,
                './/ownership/kind',
                test_case['OWNERSHIP']['pub']
            )
        
        # DESTINATION_ORDER
        if 'DESTINATION_ORDER' in test_case:
            self._update_xml_element(
                root,
                './/destinationOrder/kind',
                test_case['DESTINATION_ORDER']['pub']
            )
        
        # WRITER_DATA_LIFECYCLE
        if 'WRITER_DATA_LIFECYCLE' in test_case:
            self._update_xml_element(
                root,
                './/writerDataLifecycle/autodispose_unregistered_instances',
                test_case['WRITER_DATA_LIFECYCLE']['pub'],
                'boolean'
            )
        
        # Profile name 설정
        publisher = root.find('.//publisher')
        if publisher is not None:
            publisher.set('profile_name', f'Publisher{case_num}')
        
        # XML 저장
        self._pretty_print_xml(tree, output_path)
    
    def generate_sub_xml(self, test_case: Dict[str, Dict[str, Any]], 
                        output_path: str, case_num: int):
    
        tree = ET.parse('xml/sub_qos.xml')
        root = tree.getroot()
        
        # 네임스페이스 제거 (find가 제대로 작동하도록)
        for elem in root.iter():
            if '}' in elem.tag:
                elem.tag = elem.tag.split('}')[1]
        
        # QoS 파라미터 설정
        if 'ENTITY_FACTORY' in test_case:
            self._update_xml_element(
                root,
                './/entity_factory/autoenable_created_entities',
                test_case['ENTITY_FACTORY']['sub'],
                'boolean'
            )
        
        # PARTITION (별도 처리)
        if 'PARTITION' in test_case:
            partition_exists = test_case['PARTITION']['sub'] == 'exists'
            partition_name = root.find('.//partition/names/name')
            if partition_name is not None:
                partition_name.text = 'a' if partition_exists else ''
        
        # DATA_EXISTS (USER_DATA, GROUP_DATA, TOPIC_DATA 통합)
        if 'DATA_EXISTS' in test_case:
            data_exists = test_case['DATA_EXISTS']['sub'] == 'exists'
            
            # USER_DATA
            user_data_value = root.find('.//userData/value')
            if user_data_value is not None:
                user_data_value.text = '56.30.0.1' if data_exists else ''
            
            # GROUP_DATA
            group_data_value = root.find('.//groupData/value')
            if group_data_value is not None:
                group_data_value.text = '5.3.1.0.F1' if data_exists else ''
            
            # TOPIC_DATA (sub XML에서는 <topic> 안에 있음)
            topic_data_value = root.find('.//topic/topicData/value')
            if topic_data_value is not None:
                topic_data_value.text = '5.3.1.0' if data_exists else ''
        
        # RELIABILITY
        if 'RELIABILITY' in test_case:
            self._update_xml_element(
                root,
                './/reliability/kind',
                test_case['RELIABILITY']['sub']
            )
        
        # DURABILITY
        if 'DURABILITY' in test_case:
            self._update_xml_element(
                root,
                './/durability/kind',
                test_case['DURABILITY']['sub']
            )
        
        # DEADLINE
        if 'DEADLINE' in test_case:
            self._update_xml_element(
                root,
                './/deadline/period',
                test_case['DEADLINE']['sub'],
                'duration'
            )
        
        # LIVELINESS 
        if 'LIVELINESS' in test_case:
            liveliness_value = test_case['LIVELINESS']['sub']
            if isinstance(liveliness_value, tuple):
                kind, lease_duration = liveliness_value
                self._update_xml_element(
                    root,
                    './/liveliness/kind',
                    kind
                )
                if lease_duration is not None:
                    self._update_xml_element(
                        root,
                        './/liveliness/lease_duration',
                        lease_duration,
                        'duration'
                    )
        
        # HISTORY 
        if 'HISTORY' in test_case:
            history_value = test_case['HISTORY']['sub']
            if isinstance(history_value, tuple):
                kind, depth = history_value
                self._update_xml_element(
                    root,
                    './/historyQos/kind',
                    kind
                )
                if depth is not None:
                    self._update_xml_element(
                        root,
                        './/historyQos/depth',
                        depth
                    )
        
        # RESOURCE_LIMITS_MAX_SAMPLES_PER_INSTANCE
        if 'RESOURCE_LIMITS_MAX_SAMPLES_PER_INSTANCE' in test_case:
            self._update_xml_element(
                root,
                './/resourceLimitsQos/max_samples_per_instance',
                int(test_case['RESOURCE_LIMITS_MAX_SAMPLES_PER_INSTANCE']['sub'])
            )
        
        # RESOURCE_LIMITS_MAX_SAMPLES
        if 'RESOURCE_LIMITS_MAX_SAMPLES' in test_case:
            self._update_xml_element(
                root,
                './/resourceLimitsQos/max_samples',
                int(test_case['RESOURCE_LIMITS_MAX_SAMPLES']['sub'])
            )
        
        # LIFESPAN
        if 'LIFESPAN' in test_case:
            self._update_xml_element(
                root,
                './/lifespan/duration',
                test_case['LIFESPAN']['sub'],
                'duration'
            )
        
        # OWNERSHIP
        if 'OWNERSHIP' in test_case:
            self._update_xml_element(
                root,
                './/ownership/kind',
                test_case['OWNERSHIP']['sub']
            )
        
        # DESTINATION_ORDER
        if 'DESTINATION_ORDER' in test_case:
            self._update_xml_element(
                root,
                './/destinationOrder/kind',
                test_case['DESTINATION_ORDER']['sub']
            )
        
        # READER_DATA_LIFECYCLE
        if 'READER_DATA_LIFECYCLE_NO_WRITER' in test_case:
            self._update_xml_element(
                root,
                './/readerDataLifecycle/autopurge_no_writer_samples_delay/sec',
                int(test_case['READER_DATA_LIFECYCLE_NO_WRITER']['sub'])
            )
        if 'READER_DATA_LIFECYCLE_DISPOSED' in test_case:
            self._update_xml_element(
                root,
                './/readerDataLifecycle/autopurge_disposed_samples_delay/sec',
                int(test_case['READER_DATA_LIFECYCLE_DISPOSED']['sub'])
            )
        
        # Profile name 설정
        subscriber = root.find('.//subscriber')
        if subscriber is not None:
            subscriber.set('profile_name', f'Subscriber{case_num}')
        
        # XML 저장
        self._pretty_print_xml(tree, output_path)
    
    # ============================================================================
    # 메인 실행 함수
    # ============================================================================
    
    def generate_all_test_cases(self, output_dir: str = 'output'):

        # 출력 디렉토리 생성
        os.makedirs(output_dir, exist_ok=True)
        
        # 테스트 케이스 조합 생성
        print("테스트 케이스 조합 생성 중...")
        test_cases = self.generate_pairwise_combinations()
        total = len(test_cases)
        print(f"총 {total:,}개의 테스트 케이스 생성")
        
        # XML 파일 생성
        print(f"\nXML 파일 생성 중...")
        for i, test_case in enumerate(test_cases, 1):
            pub_path = os.path.join(output_dir, f'pub_qos_case_{i:05d}.xml')
            sub_path = os.path.join(output_dir, f'sub_qos_case_{i:05d}.xml')
            
            self.generate_pub_xml(test_case, pub_path, i)
            self.generate_sub_xml(test_case, sub_path, i)
            
            if i % 100 == 0:
                print(f"진행 중: {i}/{total} ({i*100//total}%)")
        
        # PARTITION 값이 PUB와 SUB가 다른 특별 케이스 추가
        print(f"\nPARTITION 불일치 케이스 추가 중...")
        partition_mismatch_case = {}
        
        # 모든 파라미터에 기본값 설정 (첫 번째 조합에서 가져옴)
        if test_cases:
            partition_mismatch_case = test_cases[0].copy()
        
        # PARTITION만 PUB와 SUB가 다르게 설정
        partition_mismatch_case['PARTITION'] = {
            'pub': 'exists',
            'sub': 'not_exists'
        }
        
        case_num = total + 1
        pub_path = os.path.join(output_dir, f'pub_qos_case_{case_num:05d}.xml')
        sub_path = os.path.join(output_dir, f'sub_qos_case_{case_num:05d}.xml')
        
        self.generate_pub_xml(partition_mismatch_case, pub_path, case_num)
        self.generate_sub_xml(partition_mismatch_case, sub_path, case_num)
        
        final_total = total + 1
        print(f"\n완료! 총 {final_total}개의 테스트 케이스가 생성되었습니다.")
        print(f"  - 일반 테스트 케이스: {total}개")
        print(f"  - PARTITION 불일치 케이스: 1개 (케이스 {case_num})")
        print(f"출력 디렉토리: {output_dir}/")


# ============================================================================
# 프로그램 진입점
# ============================================================================

def main():
    print("=" * 60)
    print("DDS QoS XML Generator")
    print("=" * 60)
    
    # PP와 RTT 값 입력받기
    try:
        pp = float(input("PP (Publication Period) 값을 입력하세요 (초): "))
        rtt = float(input("RTT (Round Trip Time) 값을 입력하세요 (초): "))
    except ValueError:
        print("오류: 숫자를 입력해주세요.")
        return
    
    if pp <= 0:
        print("오류: PP는 0보다 큰 값이어야 합니다.")
        return
    
    print(f"\n입력된 값:")
    print(f"  PP: {pp} 초")
    print(f"  RTT: {rtt} 초")
    print(f"  RTT/PP: {rtt/pp:.2f}")
    
    # XML Generator 생성 및 실행
    generator = XMLGenerator(pp, rtt)
    generator.generate_all_test_cases()


if __name__ == '__main__':
    main()
