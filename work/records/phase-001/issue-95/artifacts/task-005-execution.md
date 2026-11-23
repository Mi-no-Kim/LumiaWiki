# Task 95-005 수행 기록

- Task: [Task 95-005](../task-005.md#summary)
- 기록 기준: [Task 공통 절차](<../../../../../harness/Task 공통 절차.md#recording-proposal>)

<!-- execution-rule:recording
Task당 한 파일을 쓰고 이 주석은 머리말에 한 번만 둔다. 착수한 할 일은 구역 구조만 주석 없이 추가해 본문과 왕복 연결하고 실제 내용으로 채운다.
할 일의 태그·배정 조건에 따라 실제 조치·선택과 이유·근거를 남긴다. 파일 수정 없는 논의도 기록하고 제안·미결·합의·철회를 구별한다.
논의·사용자 결정은 실제 응답으로, AI 결정은 명시 위임·실제 선택으로 확인한다. 필수 논의를 생략하지 않는다.
확인은 계획·전달본을 참조하고 실제 대상·방법·관찰·판정·근거·한계를 남긴다. 변경본은 검증한 버전·범위를 식별하고 달라진 영향만 다시 확인한다.
진행·검수·수용에 필요한 결정은 Task에 결론·이유·조건·상세 링크를 남긴다. 공통 상세는 한 구역만 참조하며 잔여는 해당 할 일의 미해결·재개 조건이다.
보완·재시도는 같은 구역을 갱신한다. 식별자는 순서와 구별하고 삭제·분할·병합에도 수행·판단/실패 근거·당시 기준·본문 연결을 보존한다.
코드·diff·테스트 원문·명령별 로그를 복사·누적하지 않는다. 미발생 승인·결과나 단순 확인용 증명 파일을 만들지 않는다.
세부 작성 조건은 위 기록 기준을 따르고 생성 양식으로 돌아가지 않는다.
-->

<a id="work-records"></a>

## 기록 통합 후보 검수와 #43 인계 준비

- 할 일: [기록 통합 후보 검수와 #43 인계 준비](../task-005.md#work-records)
- 조치·판단: Phase 보유 목록과 현황, Issue의 출처·수용, Task 95-004 취소 근거를 대조했다. [95-001 보존 결과](task-001-execution.md#work-preserve), [95-002 파일별 조사](task-002-execution.md#file-map), [95-003 사용자 결정](task-003-execution.md#work-decide)을 재사용하고 아래 #43 재개 자료를 정리했다.
- 확인: Phase 기준 `cc7338c16bf3ef4fd3fb0b758bb41d048f6e1dff` 대비 후보는 [`work/records/phase-001/issue-95/`](../issue.md#summary), [Phase 계획](../../phase.md#backend-approval-review)과 [현황](../../../../현황.md#current)의 Markdown 변경이다. 코드·설정·Compose·SQL·프런트 파일은 기준과 동일하다. 원래 보존 문서 6개, 철회 패치, V1 백업의 SHA-256을 Task 95-001과 대조해 8개가 일치했다. 실제 백엔드 동작·격리 DB·V5 갱신을 이번에 재실행하지 않았다.
- 잔여: Task PR squash 결과, Issue PR 안내·CI와 Phase merge SHA·diff·병합 후 CI를 확인하고 [원래 대화](codex://threads/01a20764-c112-72f3-9e64-9b461020cf7a)에 실제 링크와 결과를 인계한다.
- 검수: `f4b2160` 대비 실제 인덱스 6개와 Phase 기준 대비 누적 Markdown 18개를 자체·별도 검수했다. 별도 검토자는 로컬·고정 참조 51개, Task별 실제 근거와 V5 지문·checksum을 대조했다. 주석·공백 검사를 통과했고 필수 지적은 없다.

<a id="catalog-handoff"></a>

### #43 catalog 범위와 선행 영향

조사 기준은 [#43 부모 `1dc6fa1`](https://github.com/Mi-no-Kim/LumiaWiki/commit/1dc6fa18a22c795f0cb984bee4f4fb4b3a294b48)이다. 사용자가 후속 정정 대상으로 지목한 것은 `backend/src/main/java/io/github/minokim/lumiawiki/catalog/`이다. 직접 관련 테스트와 연결 설정은 영향을 확인할 대상이며, 각 파일의 처리와 구현은 #43에서 범위를 결정한다. 구체 파일의 증거는 [95-002의 변경 표](task-002-execution.md#file-map)를 사용한다.

| 작업   | 실제 반영과 확인할 영향                                                                                                                                                                                                                                                                                                                                                                                                          |
| ------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 43-001 | [PR #71](https://github.com/Mi-no-Kim/LumiaWiki/pull/71) `8fe8329`. `CommonCatalogService`, `CommonCatalogStore`, 공통 엔티티·참조, `CommonCatalogServiceTests`·`CommonCatalogStoreTests`, V1의 공통 식별·패치·지역 기반이 해당한다. 당시 DDL·Java 매핑·저장/조회·DB 없는 테스트 지시와 실제 DB·역할 범위의 별도 승인을 보존한다. 정정 후 V1 이력과 기존 행·참조, `db/bootstrap` 및 앱·마이그레이션 역할 연결의 영향을 확인한다. |
| 43-002 | [PR #79](https://github.com/Mi-no-Kim/LumiaWiki/pull/79) `c64a809`. `ItemCatalogService`, `ItemVersion`과 능력치·스킬 관련 엔티티, 공통 저장소와 `common/api/ApiFailure.java`, 당시에 추가된 V2·V3 및 관련 테스트를 확인한다. 43-001의 참조 계약, #42 오류 계약과 V1→V3 갱신·기존 행 보존의 영향을 별도 판정한다. Task 결과·병합 지시와 직접 파일 변경 승인 근거를 함께 대조한다.                                                |
| 43-003 | [PR #91](https://github.com/Mi-no-Kim/LumiaWiki/pull/91) `f21439d` 및 후속 기록 `1dc6fa1`. `ItemCatalogService`, `CommonCatalogStore`, `ItemPatchPlan`, `ItemAcquisition`, 참조 검사와 `CommonCatalogIntegrationTests`·`ItemCatalogServiceTests`·`ItemStorageMigrationTests`, V4·V5를 대조한다. 별도 커밋·격리 검증·개발 DB V5 적용의 근거와 후속 일괄 저장 결과 합의를 각각 보존한다.                                           |

<a id="resume-v5"></a>

### #43 재개 순서와 V5 확인 조건

1. [43-003 마무리와 43-004 준비](codex://threads/01a20764-c112-72f3-9e64-9b461020cf7a)에서 기존 43-003 문서 변경 4개와 #43 부모 DB 문서 2개, 철회 패치와 V1 백업을 보존한다. Phase 기록 반영 → `issue/43-item-persistence` → `task/43-003-item-relations-r2` 순서로 상위 변경을 반영하고, 각 브랜치의 실제 diff와 관련 후속 조건을 확인한다.
2. #43 `catalog`의 실제 변경과 승인 근거를 분리해 파일별 정정 범위를 결정한다. 43-001 및 43-002의 영향과 재검증은 각각 위 기준으로 보고한다. 초기 파일 원본 바이트와 일부 직접 승인 근거는 [출처 조사](task-002-execution.md#user-source)의 미확인을 이어받는다.
3. 43-003 기록에는 같은 요청의 신규 획득 행끼리 중복·겹침이 있거나 기존 행과 충돌하면 **그 요청의 신규 행 전부를 저장하지 않고 기존 행을 보존**한다고 적는다. 별도 동시 요청은 **먼저 커밋된 행을 보존하고 충돌 요청을 거부**한다. 이 동작의 Spring 설계·구현, #69 사용자 수용·종료와 #45 실제 자료 작업은 보류한다.
4. 현재 Phase 통합은 문서만 다루므로 #43과 결합한 V5 실행은 이번에 재수행하지 않았다. #43에서 연결 동작이 바뀌면 격리 PostgreSQL에서 빈 DB의 V1–V5 적용과 보존한 V1 백업에서 V2–V5 갱신을 확인한다. 이력·checksum·기존 행과 참조, 역할·소유·권한, 앱 기동과 V5 획득 충돌 제약을 대조한다. 기준 V5 SQL의 SHA-256은 `5d4f89df8bc351e08157e437edf173872de25eb8b6fd3067e77f4436673ab5c3`이며, 기록된 Flyway checksum은 `488000002`다. 공유 개발 DB의 V5 적용은 [기존 적용 기록](https://github.com/Mi-no-Kim/LumiaWiki/blob/1dc6fa18a22c795f0cb984bee4f4fb4b3a294b48/work/records/phase-001/issue-43/artifacts/task-003-execution.md#development-db-v5)을 따른다.

#43의 Phase 병합과 Phase의 main 병합은 범위 밖이다. Spring 파일 생성·관리 규칙과 hook은 별도 하네스 Issue 초안에서 논의한다.
