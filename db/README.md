# DB 안내

<a id="current"></a>

DB 실행·저장 구조·마이그레이션의 진입점이다. DB 관련 변경은 해당 주제 문서를 함께 갱신한다. 설명은 목적별로 나누고 현재 계약·사용법·미정만 적는다. 실행 경과와 선택 근거는 담당 Task에 둔다.

| 확인할 내용                                     | 담당 문서                                    |
| ----------------------------------------------- | -------------------------------------------- |
| 빈 로컬 DB 최초 준비·계정·실패 대응             | [최초 구동](bootstrap/README.md#current)     |
| 공통 6개 표의 역할·참조·남은 결정               | [공통 표](model/common-tables.md#current)    |
| 생성 전 물리 구조·지역 이력·갱신·업무 권한 후보 | [물리 배치안](model/table-layout.md#current) |
| 구조 SQL 배치·적용·검증                         | [마이그레이션](migration/README.md#current)  |

## 현재 상태

- 최초 준비 쉘/SQL과 Compose·Spring/Flyway 접속 분리는 구현했다. 새 격리 DB의 검증은 [실행 근거](../work/records/phase-001/issue-43/artifacts/task-001-bootstrap-verification.md#results)를 따른다.
- 공통 도메인 표·매핑·저장/조회는 설계 중이며 제품 마이그레이션 SQL은 아직 없다. 문서의 계약을 실제 설치 상태로 해석하지 않는다.
- 실제 게임 자료·개인 `.env`·기존 개발 DB/볼륨은 현재 작업에서 조회·변경하지 않는다.
- #43의 새 테이블 생성 직전에는 [전체 구조를 사용자에게 다시 확인](migration/README.md#precreation-confirmation)받는다. 현재 후보 문서의 존재는 생성 승인이 아니다.

제품 의미와 공통 개발 기준은 [개발 기준](<../docs/개발 기준.md#current>)의 담당 문서, 계획·승인·잔여와 완료 판단은 [Task 43-001](../work/records/phase-001/issue-43/task-001.md#summary)이 소유한다. 같은 상세 계약을 여러 파일에 복사하지 않고 담당 구역으로 연결한다.
