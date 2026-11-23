# Task 95-001 수행 기록

- Task: [Task 95-001](../task-001.md#summary)
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

<a id="work-preserve"></a>

## Phase·#43 상태와 복구 근거 대조

- 할 일: [작업 상태와 복구 근거 확인](../task-001.md#work-preserve)
- 조치·판단: GitHub milestone·PR·원격 ref를 조회하고 로컬 Git 객체와 기존 워크트리의 스테이징·파일 지문을 읽기 전용으로 대조했다. V1 백업과 철회 패치의 파일 형식·경로·지문을 확인했다.
- 확인: 사용자 지정 두 기준과 관련 PR·로컬 원본을 아래 경로에서 다시 찾을 수 있다. 공유 개발 DB V5는 이전 적용 기록으로 확인했다. 이 Task에서 개발 DB 조회나 백업 재복원은 실행하지 않았다.
- 검수: 등록 커밋 `856b5e2` 기준 두 문서의 인덱스를 자체·별도 대조했다. 별도 검토자도 두 기준 SHA, 기존 변경 6개와 패치·백업의 지문, 과거 복원 기록을 확인했다. 공백·기록 검사를 통과했고 필수 결함은 발견하지 못했다.
- 잔여: Task 95-002는 아래 기준에서 출처·승인·영향을 대조한다. 격리 V5 호환 확인은 정정 승인과 후보가 생긴 뒤 수행한다.

### Git 기준과 PR

| 항목            | 실제 근거                                                                                                                                                                                                                                                                                                                                    |
| --------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Phase 조사·분기 | 원격 `phase/001-item-foundation`과 로컬 `origin/phase/001-item-foundation`이 `cc7338c16bf3ef4fd3fb0b758bb41d048f6e1dff`로 일치했다. #95 워크트리는 이 SHA에서 분기했다.                                                                                                                                                                      |
| #43 조사        | 원격 `issue/43-item-persistence`와 두 보존 워크트리 HEAD가 `1dc6fa18a22c795f0cb984bee4f4fb4b3a294b48`로 일치했다. Phase SHA가 이 커밋의 조상이다.                                                                                                                                                                                            |
| #42 Phase 유입  | [#66](https://github.com/Mi-no-Kim/LumiaWiki/pull/66) `0239caa`. 하위 [#54](https://github.com/Mi-no-Kim/LumiaWiki/pull/54) `3ffeb6d` · [#59](https://github.com/Mi-no-Kim/LumiaWiki/pull/59) `2ca4efd` · [#62](https://github.com/Mi-no-Kim/LumiaWiki/pull/62) `8a21c74` · [#63](https://github.com/Mi-no-Kim/LumiaWiki/pull/63) `355b9db`. |
| #43 부모 반영   | [#71](https://github.com/Mi-no-Kim/LumiaWiki/pull/71) `8fe8329` · [#79](https://github.com/Mi-no-Kim/LumiaWiki/pull/79) `c64a809` · [#91](https://github.com/Mi-no-Kim/LumiaWiki/pull/91) `f21439d`이 각각 #43 부모에 반영됐다. `f46f1d2`는 과거 V1 복구용 빌드 기준이다.                                                                    |

### 기존 원본과 미스테이징 변경

아래 경로는 원래 저장소 루트 기준이다. 두 워크트리의 스테이징 변경은 없었으며 각 표의 파일만 수정 상태였다. SHA-256은 커밋이 아닌 원본 파일의 당시 내용 지문이다.

| 워크트리                          | 파일                                                               | SHA-256                                                            |
| --------------------------------- | ------------------------------------------------------------------ | ------------------------------------------------------------------ |
| `.tmp/issue-43-acquisition-batch` | `work/records/phase-001/issue-43/artifacts/task-003-assignment.md` | `de2535b67b9c8e1e7a7aced1495054cab59dd9e3ad3bc2f7de702e3c12b7aad5` |
| 같은 워크트리                     | `work/records/phase-001/issue-43/artifacts/task-003-execution.md`  | `beea0036e672c6d8b7e5c60eea2d501d07541dc835773ee182d3dd3e4fdf3d1c` |
| 같은 워크트리                     | `work/records/phase-001/issue-43/issue.md`                         | `a2a2e360871dccf9b808eb02aeb301a3113920e772c6e0a5764b2b3bead15617` |
| 같은 워크트리                     | `work/records/phase-001/issue-43/task-003.md`                      | `c63db31ae534e3d40cc5fce9312501733ae5d39f40d77438e98dea57fc029b02` |
| `.tmp/issue-43-pr91-merge`        | `db/migration/README.md`                                           | `a50183c0177f48ac2b32d5a54dc5abc30ce7a6a50cebd34dfd6dc231c9dfb8ba` |
| 같은 워크트리                     | `db/migration/application-status.md`                               | `9194fd05a9fb38fbb7eb08bf37d468093381272dfe12675499082326a84af7e2` |

- 철회 패치 `.tmp/issue-43-acquisition-batch/.tmp/withdrawn-acquisition-spring/previous-candidate.patch` · 32,095바이트 · SHA-256 `bcb062d64ad8a2d12a6af70f88f82c3d8e492937d0ce7685f4a78321c58fcfe3`. `ItemCatalogService.java`, `CommonCatalogIntegrationTests.java`, 43-003 기록 4개의 diff 표식을 확인했다.
- V1 백업 `.tmp/issue-43-pr91-backup/lumiawiki-v1.dump` · 30,884바이트 · `PGDMP` 형식 · SHA-256 `c57943ac02dd71c307fcd0cc358077764996d9761c873805c72bddb2763c8b7a`. [개발 DB V5 적용 기록](https://github.com/Mi-no-Kim/LumiaWiki/blob/1dc6fa18a22c795f0cb984bee4f4fb4b3a294b48/work/records/phase-001/issue-43/artifacts/task-003-execution.md#development-db-v5)에 이전 격리 복원의 V1 이력·소유·앱 권한·제품 8개 표의 0행 확인과 개발 DB V5 적용 결과가 남아 있다.
