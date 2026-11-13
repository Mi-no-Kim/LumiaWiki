# 공통 표의 구조와 남은 결정

<a id="current"></a>

Task 43-001의 공통 6개 표를 설계할 때 읽는다. 아래는 확정 계약과 미정이며 실제 생성된 제품 표 목록이 아니다. 전체 필드·자료형·NULL·검사 계약은 [공통 DB 모델](<../../docs/details/development/공통 DB 모델.md#common-six-storage-contract>)을 단일 원천으로 사용한다.

총 8개 표의 R-A·즉시 UNIQUE/단건 기본 U-A·교정용 소속 행 DELETE A-A를 채택했다. 사용자 확인을 받은 저장 구조는 [6개 공통 표](table-layout.md#current)·[지역 구성/이력](region-layout.md#current)·[갱신/검사](writes-and-checks.md#current)·[업무 권한/설치](permissions-and-installation.md#current)로 나눈다. region에는 작업용 표시 이름을 필수·빈값 금지·중복 금지로 저장하고 업무 UPDATE를 허용한다. 후속 획득은 [C-A 참조](consumer-references.md#current), 관련 수정은 L-A 잠금, PK/설치는 8개 보호·한 파일의 M-A를 따른다. 실제 자료·DB 작업과 구현 파일 생성은 보류하며 [생성 직전 전체 구조 확인](../migration/README.md#precreation-confirmation)을 유지한다.

## 담당과 참조

| 표              | 담당 정보                                 | 참조·저장 경계                                                                  |
| --------------- | ----------------------------------------- | ------------------------------------------------------------------------------- |
| `season`        | 시즌 번호·표시 이름·실제 이름·정렬·기간   | 시즌 번호 업무 UNIQUE. 실제 이름/시작·종료일 NULL 허용(D1)                      |
| `game_patch`    | 시즌 내 메이저/마이너·이름·정렬·적용 시각 | 시즌 참조·번호 조합/정렬 UNIQUE. 이름/적용 시각 NULL 허용. 번호 각각 0~99 CHECK |
| `region`        | 지속 지역 ID·작업용 표시 이름             | display_name TEXT NOT NULL·UNIQUE. 공개 이름·순서는 지도 구성 소속 행에서 조회  |
| `item_category` | 버전 없는 현재 종류·부모                  | 부모 0~1개인 트리. 확인된 루트만 부모 NULL. 같은 부모/루트의 동명 금지          |
| `item_grade`    | 등급 이름·표시 순서                       | 지정 관리자 판단과 기본 검사. 등급 목록 안 동명·동순위 금지                     |
| `weapon_type`   | 별도 무기 종류 대상                       | 무기 종류마다 아이템 종류 정확히 1개, 종류에는 무기 종류 최대 1개               |

공통 내부 ID는 `BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY`다. 일반 FK는 비지연 검사·참조 중 삭제 RESTRICT를 사용한다. 자기 부모는 CHECK로 거부하고 기존 공통 PK의 일반 변경은 DB trigger와 Spring 검사로 보호하는 계약이다. 이 보호 장치의 제품 DDL은 아직 생성하지 않았다.

종류 이름·계층은 현재 기준으로 조회한다. 아이템 자체의 소속 변경은 아이템 버전에 보존한다. 아이템·스킬·제작 재료의 버전 참조는 [공유 관계 계약](../../work/records/phase-001/issue-43/artifacts/task-001-version-references.md#current)을 따르며, 후속 Task가 실제 키·복합 참조 검사를 정한다.

<a id="pending"></a>

## 남은 결정

| 항목                                             | 필요한 판단·입력                                                                           | 결정 시점                                                      |
| ------------------------------------------------ | ------------------------------------------------------------------------------------------ | -------------------------------------------------------------- |
| [D1 이름·날짜·시각](names-and-dates.md#current)  | 5개 메타정보 NULL 등록 허용은 확정. 실제 값/누락 이유·조회 추가 구분은 담당 확인           | 정책 재선택 없음. 자료 작업 재개 뒤 실제 값 확인               |
| [D2 범위·중복](ranges-and-uniqueness.md#current) | 번호 각각 0~99는 사용자 확인. 정렬 UNIQUE·이름 비교 C·시즌/패치 이름 추가 UNIQUE 없음 확정 | 실제 입력은 자료 재개 뒤 확인, 제약별 이름은 DDL 초안에서 제시 |
| D3 무기 대응                                     | weapon_type.category_id NOT NULL FK + UNIQUE 채택. 실제 제약명·입력 확인은 남음            | 제약명은 DDL 전, 실제 대응은 자료 작업 재개 뒤                 |
| D4 지역 이력 상세                                | 지속 ID·작업용 이름·지도 2개 표의 열/키와 C-A 참조 채택. 후속 소비 행 배치는 003/004 담당  | 공통 구조는 생성 직전 재확인, 소비 행은 담당 구현 전           |

N1~N5는 확정했으며 저장/조회는 Spring 서비스·저장소 코드와 격리 통합 테스트/재현 절차를 초기 범위로 삼는다. 새 HTTP API·관리 화면은 필요한 기능에서 설계한다. 번호 범위의 사실 근거는 사용자 응답이며 다른 자료 의존 값은 미확인으로 유지한다. 새 선택이 생기면 대안·추천 이유를 먼저 제시한다. 담당·필요 입력·결정 시점과 보류/재개는 [잔여 계획](../../work/records/phase-001/issue-43/artifacts/task-001-pending.md#remaining-review)을 따른다.
