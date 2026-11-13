# DB 안내

<a id="current"></a>

DB 실행·저장 구조·마이그레이션의 진입점이다. DB 관련 변경은 해당 주제 문서를 함께 갱신한다. 설명은 목적별로 나누고 현재 계약·사용법·미정만 적는다. 실행 경과와 선택 근거는 담당 Task에 둔다.

| 확인할 내용                             | 담당 문서                                   |
| --------------------------------------- | ------------------------------------------- |
| 빈 로컬 DB 최초 준비·계정·실패 대응     | [최초 구동](bootstrap/README.md#current)    |
| 공통 6개 표의 역할·참조·남은 결정       | [공통 표](model/common-tables.md#current)   |
| 전체 물리 구조·지역 이력·갱신·업무 권한 | [물리 구조](model/table-layout.md#current)  |
| 구조 SQL 배치·적용·검증                 | [마이그레이션](migration/README.md#current) |

## 현재 상태

- 공통 8개 표를 새 격리 DB에서 검증한 뒤 승인한 로컬 lumiawiki/public에 적용했다. [적용 결과](migration/application-status.md#current)에서 대상·구조 지문·계정/소유·검증 한계를 확인한다.
- DDL·JPA 매핑·저장/조회 코드와 단위/격리 통합 검사를 작성했다. [구현 안내](model/implementation.md#current)는 코드 사용 범위와 검사 명령을 소유한다.
- 로컬 제품 표는 모두 0행이며 실제 게임 자료 조사·변환·등록은 계속 보류한다.
- 이후 신규 표도 [생성 직전 전체 구조 확인](migration/README.md#precreation-confirmation)을 받는다. 승인 범위 밖의 기존 객체·역할·소유 변경을 자동 실행하지 않는다.

제품 의미와 공통 개발 기준은 [개발 기준](<../docs/개발 기준.md#current>)의 담당 문서, 계획·승인·잔여와 완료 판단은 [Task 43-001](../work/records/phase-001/issue-43/task-001.md#summary)이 소유한다. 같은 상세 계약을 여러 파일에 복사하지 않고 담당 구역으로 연결한다.
