# Task 95-002 수행 기록

- Task: [Task 95-002](../task-002.md#summary)
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

<a id="work-trace"></a>

## 파일 유입·사용자 발언·현재 영향 대조

- 할 일: [Phase와 #43의 변경 출처와 승인 증거 대조](../task-002.md#work-trace)
- 조치·판단: [42-001 당사자 기록](https://github.com/Mi-no-Kim/LumiaWiki/blob/3ffeb6dcdb4f9de099bb7d42b754a0d3f401d64e/work/records/phase-001/issue-42/task-001.md)과 [Find next work item](codex://threads/01a1cb3b-9270-7913-8ea1-99ee016bf830)의 사용자 발언 및 당시 명령 출력을 먼저 읽었다. 단계별 Git diff와 PR을 대조하고 사용자 제공, 변경 수행, 과제 수준 지시, 배포·DB 승인 및 파일별 직접 승인 근거를 구분했다.
- 확인: 두 기준에서 검토 대상의 유입과 수정 이력을 아래 표로 확인했다. 초기 파일 3개의 당시 내용 출력은 찾았으며 별도 원본 파일·바이트 지문과 일부 직접 승인 근거는 미확인으로 표시했다.
- 검수: `3140abb` 기준 두 제출 파일의 인덱스를 자체·별도 검수했다. 별도 검토자는 파일 이력 93행, 참조 21개와 Java 포맷 차이를 확인했다. 지적받은 Git 제출본의 출처 표현과 백엔드 CI 호출 경로를 보완하고 변경 부분을 다시 별도 검수했다. 주석·기록·공백 검사를 통과했다.
- 잔여: Phase 파일의 처리는 95-003에서 사용자가 결정한다. #43 전용 코드는 인계에 필요한 영향 조사까지 수행했다.

<a id="user-source"></a>

### 42-001 당시 사용자 발언과 파일 제공

- 같은 [Find next work item 대화](codex://threads/01a1cb3b-9270-7913-8ea1-99ee016bf830)의 구현 턴 `01a1cb78-5bb5-7e21-a29f-9340873f796a`에서 사용자는 “그럼 확정한 내용대로 task 1 구현해.”라고 했고 이어 “spring boot 파일은 내가 넣을게”라고 지시했다. 제공 완료 확인 질문에 “모두 넣었음”이라고 답했다. 이 뒤 대화에서 Phase의 각 Spring 파일을 다시 쓰는 데 대한 사용자 직접 응답은 미확인이다.
- AI가 앞서 Spring Initializr 출력에서 일곱 파일을 추출했다. 사용자 제공 완료 직후의 당시 읽기 출력 `exec-9de39b5c-93cc-41bc-b882-9932fe1af255`는 `build.gradle`, Wrapper properties, `application.yaml`, `HELP.md`, 기본 Java 테스트의 존재를 보여준다. settings·Wrapper 실행 파일 2개·JAR·애플리케이션 클래스는 AI가 이전 보관본에서 복원한 다섯 파일이다. `exec-2f417c22-1242-44ed-895a-04cadacd6575`에서 복원 다섯 건 이후 두 프로필 설정 파일 중 첫 번째에서 원본 부재로 중단됐고, 후속 명령 `exec-9374182f-4b48-4272-8229-0614995b6b7a`가 두 프로필을 작성하고 제공 파일을 변경했다.
- `build.gradle` 당시 출력에는 description과 SQL 패키징 작업이 없고 Flyway PostgreSQL 모듈은 `implementation`이었다. [#54](https://github.com/Mi-no-Kim/LumiaWiki/pull/54)는 description·`processResources`를 추가하고 모듈을 `runtimeOnly`로 바꿨다. 사용자 제공 Wrapper 출력은 Gradle 9.8.2, #54는 9.9.1이다. 당시 `application.yaml`은 앱 이름만 포함했고 #54에서 JPA validate, open-in-view 비활성, Flyway 위치, SQL init 비활성, 일반 로그를 추가했다.
- 같은 출력에 사용자 제공 기본 테스트의 파일명은 있다. 내용 당시 출력·유입 당시 원본 바이트는 미확인이다. 추적 가능한 가장 이른 형태는 `3ffeb6d`의 빈 `contextLoads`다. 이후 #59가 테스트 연결, 태그, 트랜잭션 검사를 추가했고 #63이 포맷을 적용했다. `HELP.md`는 제출에서 제외됐다. 두 backend dotfile의 정확한 작성 주체와 유입 당시 원본 구분은 미확인이다.
- 42-001에 기록된 임시 Initializr ZIP과 `server-before-user/`는 정리 기록 및 현재 부재를 대조했다. 초기 파일 세 개는 당시 읽기 출력으로 내용 복원을 검토할 수 있다. 제거된 원본과 바이트 단위로 동일함을 확인할 별도 사본 또는 해당 시점 지문은 미확인이다. 스냅샷에 대한 지문과 사용자 제공 이전 AI 후보 지문은 각각의 시점에만 적용한다.
- 사용자는 이후 “task 1 구현한 내용 검수하고 커밋해.”, “task 1 push하고 PR 만들어서 부모 issue에 병합해.”라고 말했다. 이는 제출·부모 반영 지시 근거다. 화면 표시 확인과 기존 개발 볼륨 재생성 허용도 각각의 묻고 답한 범위로 기록한다.

<a id="phase-changes"></a>

### Phase 공통 변경과 영향

| 판단 단위                  | 최초·후속 변경과 사용자 발언                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  | 현재 영향과 남은 판단                                                                                                                                                                                                                |
| -------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| A. 사용자 제공 파일의 변경 | 위 세 파일의 AI 변경은 #54이며 #59·#62·#63이 같은 설정 일부를 후속 수정했다. 최초 계획에 Wrapper 9.9.1과 SQL·JPA 기준이 있으나 제공 완료 이후 각 수정의 직접 승인 원문은 미확인이다.                                                                                                                                                                                                                                                                                                                                                                          | Wrapper는 빌드 경로다. Gradle의 SQL 포함과 공통 YAML의 Flyway/JPA/SQL init은 후속 #43의 V1–V5와 테스트가 사용한다. 제공 직후 형태로 복원할 경우 후속 추가분과 분리해야 한다.                                                         |
| B. AI 보관본 복원과 프로필 | #54의 settings·Wrapper 실행 파일 2개·JAR·앱 클래스 다섯 개 복원, local/test YAML 추가. 앱 클래스는 #63, local/test는 #59·#62가 후속 변경했다. 이를 구체적으로 허용한 사용자 발언은 미확인이다.                                                                                                                                                                                                                                                                                                                                                                | settings·Wrapper·앱 클래스는 빌드·기동 진입점이다. local은 환경변수 DB 연결, test는 기본적으로 127.0.0.1:1 실패 및 격리 Testcontainers 사용의 일부다.                                                                                |
| C. 테스트 환경             | [#59](https://github.com/Mi-no-Kim/LumiaWiki/pull/59)에서 Testcontainers, integrationTest, test 프로필, 사용자 제공 테스트 수정 및 별도 Java/SQL 테스트 추가. 사용자는 “그럼 확정한 내용대로 task 2 구현해.”, 이후 “Task 42-002 브랜치를 push하고 … PR을 만들어줘. … PR CI에 문제가 없으면 squash 병합”을 요청했다. [초기 대화](codex://threads/01a1cb3b-9270-7913-8ea1-99ee016bf830) · [후속 대화](codex://threads/01a1cddb-7ec4-7200-847e-e1435024d49d)                                                                                                     | Task 수준에서 테스트 환경 구현 지시는 확인됐다. 제공 테스트의 수정 방식과 새 Java 파일 각각에 대한 직접 합의는 미확인이다. 제거·복원 시 공급자 테스트와 Testcontainers의 연결 방식, 기존 격리 DB 테스트를 함께 점검해야 한다.        |
| D. API·프로필·UI 연동      | [#62](https://github.com/Mi-no-Kim/LumiaWiki/pull/62)의 Spring `common/api`, `dev`, `FoundationApiTests`, ProblemDetail·SpringDoc·로그 설정. 사용자는 “Task 42-003을 진행해줘. 확인 화면부터 준비해줘.”와 “PR #62를 검토하고, 문제없으면 … 병합해줘.”라고 했다. [현재 진행 작업 확인](codex://threads/01a1cf50-69cc-7f30-8b56-5e6d2473a719)                                                                                                                                                                                                                   | 화면 선행과 Task·PR 지시는 확인됐다. 사용자 직접 화면 확인/Java 파일별 변경 허용은 미확인이다. 제거 시 현재 Vite 프록시·개발 확인 화면이 요청하는 `/api/v1/_dev/foundation`과 #43이 사용하는 공통 `ApiFailure` 영향을 보고해야 한다. |
| E. 실행·Compose·검증·품질  | #54의 `.env.example`, Compose, dev 실행기와 Node 테스트, bootstrap 검증, 빈 SQL 위치 및 안내. [#63](https://github.com/Mi-no-Kim/LumiaWiki/pull/63)은 Spotless와 10개 Java 파일 포맷, 실행·검증 스크립트 보강, 품질 CI·Compose 표현 변경을 반영했다. “Task 42-004를 정해진 절차와 결정 사항에 따라 구현하고 검증까지 진행해줘.” 이후 PostToolUse 신뢰·실제 자동 포맷 검증과 #42 완료·Phase 통합을 별도로 요청했다. [Task 42-004 진행 절차 확인](codex://threads/01a1cf82-959c-75d1-8ba4-bf05c39e3569) · [#66](https://github.com/Mi-no-Kim/LumiaWiki/pull/66) | 실행 명령·개발 볼륨 경계·CI에 직접 연결된다. #63의 Java 변경은 줄바꿈·공백 변화와 세 파일의 import 순서만 바뀐 것으로 확인했다. 작업 수행·자동 포맷 확인·통합 지시를 Java 기능 구현 승인으로 확대하지 않는다.                        |
| F. 초기 프런트 유입        | #54의 `index.html`, `package.json`·lock, `src/main.tsx`·`style.css`, `tsconfig.json`, `vite.config.mjs`는 AI가 Task 1에서 작성했다. Spring 파일을 사용자가 직접 넣는다는 지시 뒤에도 AI가 웹 작업을 별도로 진행했고 사용자 시작 화면 응답이 남아 있다.                                                                                                                                                                                                                                                                                                        | 최초 프런트 일곱 파일은 사용자 Spring 제공 범위에 포함된 근거가 없다. #59·#62·#63이 후속 변경했다. 이번 범위는 최초 유입 확인이며 API 제거·이동 시 화면의 직접 영향을 보고한다.                                                      |

- #42의 Phase 병합 `0239caa` 이후 지정 Phase `cc7338c`까지 위 제품 파일·설정의 차이는 없고, 연결된 `.github/workflows/harness-inventory.yml`에는 Ubuntu 러너 고정, PR 트리거·체크아웃·자동 닫기 검사 변경이 있다. 최신 원격 Phase는 조사 기준과 일치했다.

<a id="issue-43-only"></a>

### #43 전용 변경과 인계 조건

| 변경                                                                                | 증거와 승인 범위                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       | Phase 정정 뒤 확인할 영향                                                                                                                                                                                        |
| ----------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 43-001 [#71](https://github.com/Mi-no-Kim/LumiaWiki/pull/71) `8fe8329`              | V1 공통 8개 표, catalog 공통 엔티티·서비스·저장소, 역할 bootstrap, 별도 Flyway 접속 환경, 격리 테스트. [실제 적용 범위](https://github.com/Mi-no-Kim/LumiaWiki/blob/1dc6fa1/work/records/phase-001/issue-43/artifacts/task-001-creation.md). [다음 작업 찾기](codex://threads/01a1d02e-47e3-7351-bbd1-e7d8524af660)에서 “Task 43-001의 구현 파일 생성 보류는 해제하고, 합의한 DDL·Java 매핑·저장/조회 코드와 DB 없는 테스트를 작성해줘”라고 지정했다(턴 `01a1d46c-c6df-7ee0-b6af-6af2f0b85f1b`). 당시 합의 범주의 구현 지시가 확인됐으며 개별 구현 상세·파일 전부의 승인으로 확장하지 않는다. 후속 메시지는 격리 우선 검증과 기존 DB의 여덟 표, 별도 역할·권한 준비를 한정해 허용했다. | `.env.example`·Compose·dev 실행기·local YAML 및 Gradle SQL 리소스·JPA validate와 겹친다. 역할 분리·앱 접속과 Flyway 접속, V1 내용·이력 보존을 확인한다.                                                          |
| 43-002 [#79](https://github.com/Mi-no-Kim/LumiaWiki/pull/79) `c64a809`              | V2·V3, 아이템/능력치/스킬 Java, `ApiFailure`와 V3 매핑·참조. [Task 기록](https://github.com/Mi-no-Kim/LumiaWiki/blob/1dc6fa1/work/records/phase-001/issue-43/task-002.md). 격리 DB 구조·동작 근거와 [이슈 43 재개 워크트리로 이동](codex://threads/01a1fbf8-b374-7383-b861-075d673b4e38)의 “PR #79를 Issue #43 브랜치에 병합해” 및 당시 개발 DB·실제 자료 보류 지시가 있다. 이 제출 지시만으로 개별 Spring 파일의 직접 승인을 확정할 수 없다.                                                                                                                                                                                                                                          | #42 API 오류 계약, Testcontainers, 43-001에 기대는 V1→V3 갱신과 기존 참조·행·권한 보존을 확인한다.                                                                                                               |
| 43-003 [#91](https://github.com/Mi-no-Kim/LumiaWiki/pull/91) `f21439d` 및 `1dc6fa1` | V4·V5, 제작·획득·배달 Java·테스트·적용 기록. [선행 대화](codex://threads/01a1ff28-c9b7-7843-821a-836651d140a2)의 V4·V5 별도 커밋·회귀 확인 지시와 [개발 DB 적용 기록](https://github.com/Mi-no-Kim/LumiaWiki/blob/1dc6fa1/work/records/phase-001/issue-43/artifacts/task-003-execution.md#development-db-v5)이 있다. [원래 대화](codex://threads/01a20764-c112-72f3-9e64-9b461020cf7a)의 후속 사용자는 스프링 설계·구현으로 확대하지 말라고 명시했다.                                                                                                                                                                                                                                  | 기존 V1 백업으로 격리 V2~V5 업그레이드 시 이력·checksum·역할·기존 행, 새 설치 V1~V5와 앱 시작을 확인한다. 필요한 승인과 실제 사용자 발언은 #43 재개 때 파일별로 이어서 조사한다.                                 |
| 철회한 일괄 저장 로컬 후보                                                          | [보존 기록](task-001-execution.md#work-preserve)에 패치·지문을 남겼다. 원래 대화의 “같은 저장 요청에서는 전체를 거부하고, 별도 동시 요청은 어쩔 수 없겠네”와 이번 사용자의 저장 결과를 근거로 기록을 정정한다.                                                                                                                                                                                                                                                                                                                                                                                                                                                                         | 요청 내부 신규 행 중복·겹침 또는 기존 행 충돌 시 신규 행 전부를 저장하지 않고 기존 행은 보존한다. 별도 동시 요청은 먼저 커밋된 행 보존과 충돌 요청 거부다. 이 결과의 Spring 설계·구현 및 #69 수용·종료는 보류다. |

<a id="file-map"></a>

### 파일별 Git 변경 출처

표의 A는 추가, M은 수정이다. Phase 열의 #54·#59·#62·#63은 AI가 조립·수정한 제출본의 Git 이력이다. #54에는 사용자 제공 파일, AI 복원·작성 파일, 작성 주체가 미확인인 파일이 함께 들어 있다. Git 작성자·커미터는 실제 편집 주체나 승인 범위를 입증하지 않는다. #43 열도 같은 원칙을 적용한다. 프런트는 위 F 행이 최초 유입 근거다. Phase 열이 있는 파일은 Phase 공통이며 #43 열만 있는 파일은 #43 전용이다. 변경 의미와 사용자 발언은 위 항목을 참조한다.

| 파일                                                                                           | Phase 공통                                            | #43의 추가·수정                         |
| ---------------------------------------------------------------------------------------------- | ----------------------------------------------------- | --------------------------------------- |
| `backend/.gitattributes`                                                                       | `A 3ffeb6d`                                           | —                                       |
| `backend/.gitignore`                                                                           | `A 3ffeb6d`                                           | —                                       |
| `backend/build.gradle`                                                                         | `A 3ffeb6d` · `M 2ca4efd` · `M 355b9db`               | —                                       |
| `backend/gradle/wrapper/gradle-wrapper.jar`                                                    | `A 3ffeb6d`                                           | —                                       |
| `backend/gradle/wrapper/gradle-wrapper.properties`                                             | `A 3ffeb6d`                                           | —                                       |
| `backend/gradlew`                                                                              | `A 3ffeb6d`                                           | —                                       |
| `backend/gradlew.bat`                                                                          | `A 3ffeb6d`                                           | —                                       |
| `backend/settings.gradle`                                                                      | `A 3ffeb6d`                                           | —                                       |
| `backend/src/main/java/io/github/minokim/lumiawiki/catalog/AcquisitionMethod.java`             | —                                                     | `A f21439d`                             |
| `backend/src/main/java/io/github/minokim/lumiawiki/catalog/CatalogErrors.java`                 | —                                                     | `A 8fe8329` · `M c64a809` · `M f21439d` |
| `backend/src/main/java/io/github/minokim/lumiawiki/catalog/CatalogReferenceCheck.java`         | —                                                     | `A 8fe8329` · `M c64a809`               |
| `backend/src/main/java/io/github/minokim/lumiawiki/catalog/CatalogRow.java`                    | —                                                     | `A 8fe8329`                             |
| `backend/src/main/java/io/github/minokim/lumiawiki/catalog/CatalogViews.java`                  | —                                                     | `A 8fe8329`                             |
| `backend/src/main/java/io/github/minokim/lumiawiki/catalog/CommonCatalogService.java`          | —                                                     | `A 8fe8329`                             |
| `backend/src/main/java/io/github/minokim/lumiawiki/catalog/CommonCatalogStore.java`            | —                                                     | `A 8fe8329` · `M c64a809` · `M f21439d` |
| `backend/src/main/java/io/github/minokim/lumiawiki/catalog/EquipmentCategoryRole.java`         | —                                                     | `A f21439d`                             |
| `backend/src/main/java/io/github/minokim/lumiawiki/catalog/EquipmentSlot.java`                 | —                                                     | `A c64a809`                             |
| `backend/src/main/java/io/github/minokim/lumiawiki/catalog/GamePatch.java`                     | —                                                     | `A 8fe8329`                             |
| `backend/src/main/java/io/github/minokim/lumiawiki/catalog/HuntingAcquisitionCheck.java`       | —                                                     | `A f21439d`                             |
| `backend/src/main/java/io/github/minokim/lumiawiki/catalog/Item.java`                          | —                                                     | `A c64a809`                             |
| `backend/src/main/java/io/github/minokim/lumiawiki/catalog/ItemAcquisition.java`               | —                                                     | `A f21439d`                             |
| `backend/src/main/java/io/github/minokim/lumiawiki/catalog/ItemAcquisitionReferenceCheck.java` | —                                                     | `A f21439d`                             |
| `backend/src/main/java/io/github/minokim/lumiawiki/catalog/ItemCatalogService.java`            | —                                                     | `A c64a809` · `M f21439d`               |
| `backend/src/main/java/io/github/minokim/lumiawiki/catalog/ItemCategory.java`                  | —                                                     | `A 8fe8329` · `M f21439d`               |
| `backend/src/main/java/io/github/minokim/lumiawiki/catalog/ItemGrade.java`                     | —                                                     | `A 8fe8329`                             |
| `backend/src/main/java/io/github/minokim/lumiawiki/catalog/ItemPatchPlan.java`                 | —                                                     | `A f21439d`                             |
| `backend/src/main/java/io/github/minokim/lumiawiki/catalog/ItemSkillDefinition.java`           | —                                                     | `A c64a809`                             |
| `backend/src/main/java/io/github/minokim/lumiawiki/catalog/ItemSkillDefinitionVersion.java`    | —                                                     | `A c64a809`                             |
| `backend/src/main/java/io/github/minokim/lumiawiki/catalog/ItemSkillReferenceCheck.java`       | —                                                     | `A c64a809`                             |
| `backend/src/main/java/io/github/minokim/lumiawiki/catalog/ItemStat.java`                      | —                                                     | `A c64a809`                             |
| `backend/src/main/java/io/github/minokim/lumiawiki/catalog/ItemStatCache.java`                 | —                                                     | `A c64a809`                             |
| `backend/src/main/java/io/github/minokim/lumiawiki/catalog/ItemVersion.java`                   | —                                                     | `A c64a809` · `M f21439d`               |
| `backend/src/main/java/io/github/minokim/lumiawiki/catalog/ItemVersionSkillLink.java`          | —                                                     | `A c64a809`                             |
| `backend/src/main/java/io/github/minokim/lumiawiki/catalog/Region.java`                        | —                                                     | `A 8fe8329`                             |
| `backend/src/main/java/io/github/minokim/lumiawiki/catalog/RegionMapMember.java`               | —                                                     | `A 8fe8329`                             |
| `backend/src/main/java/io/github/minokim/lumiawiki/catalog/RegionMapVersion.java`              | —                                                     | `A 8fe8329`                             |
| `backend/src/main/java/io/github/minokim/lumiawiki/catalog/Season.java`                        | —                                                     | `A 8fe8329`                             |
| `backend/src/main/java/io/github/minokim/lumiawiki/catalog/StatType.java`                      | —                                                     | `A c64a809`                             |
| `backend/src/main/java/io/github/minokim/lumiawiki/catalog/WeaponType.java`                    | —                                                     | `A 8fe8329`                             |
| `backend/src/main/java/io/github/minokim/lumiawiki/common/api/ApiExceptionAdvice.java`         | `A 8a21c74` · `M 355b9db`                             | —                                       |
| `backend/src/main/java/io/github/minokim/lumiawiki/common/api/ApiFailure.java`                 | `A 8a21c74` · `M 355b9db`                             | `M c64a809`                             |
| `backend/src/main/java/io/github/minokim/lumiawiki/common/api/RequestIdFilter.java`            | `A 8a21c74` · `M 355b9db`                             | —                                       |
| `backend/src/main/java/io/github/minokim/lumiawiki/dev/FoundationController.java`              | `A 8a21c74` · `M 355b9db`                             | —                                       |
| `backend/src/main/java/io/github/minokim/lumiawiki/dev/FoundationResponse.java`                | `A 8a21c74` · `M 355b9db`                             | —                                       |
| `backend/src/main/java/io/github/minokim/lumiawiki/dev/FoundationService.java`                 | `A 8a21c74` · `M 355b9db`                             | —                                       |
| `backend/src/main/java/io/github/minokim/lumiawiki/LumiawikiApiApplication.java`               | `A 3ffeb6d` · `M 355b9db`                             | —                                       |
| `backend/src/main/resources/application-local.yaml`                                            | `A 3ffeb6d` · `M 8a21c74`                             | `M 8fe8329`                             |
| `backend/src/main/resources/application.yaml`                                                  | `A 3ffeb6d` · `M 8a21c74`                             | —                                       |
| `backend/src/test/java/io/github/minokim/lumiawiki/BootstrapInitializationTests.java`          | —                                                     | `A 8fe8329`                             |
| `backend/src/test/java/io/github/minokim/lumiawiki/catalog/CommonCatalogIntegrationTests.java` | —                                                     | `A 8fe8329` · `M c64a809` · `M f21439d` |
| `backend/src/test/java/io/github/minokim/lumiawiki/catalog/CommonCatalogServiceTests.java`     | —                                                     | `A 8fe8329`                             |
| `backend/src/test/java/io/github/minokim/lumiawiki/catalog/CommonCatalogStoreTests.java`       | —                                                     | `A 8fe8329`                             |
| `backend/src/test/java/io/github/minokim/lumiawiki/catalog/ItemCatalogServiceTests.java`       | —                                                     | `A c64a809` · `M f21439d`               |
| `backend/src/test/java/io/github/minokim/lumiawiki/catalog/ItemStorageMigrationTests.java`     | —                                                     | `A c64a809` · `M f21439d`               |
| `backend/src/test/java/io/github/minokim/lumiawiki/fixture/FoundationTestApplication.java`     | —                                                     | `A 8fe8329`                             |
| `backend/src/test/java/io/github/minokim/lumiawiki/FoundationApiTests.java`                    | `A 8a21c74` · `M 355b9db`                             | —                                       |
| `backend/src/test/java/io/github/minokim/lumiawiki/LumiawikiApiApplicationTests.java`          | `A 3ffeb6d` · `M 2ca4efd` · `M 355b9db`               | `M 8fe8329`                             |
| `backend/src/test/java/io/github/minokim/lumiawiki/TestEnvironmentTests.java`                  | `A 2ca4efd` · `M 355b9db`                             | —                                       |
| `backend/src/test/resources/application-test.yaml`                                             | `A 3ffeb6d` · `M 2ca4efd` · `M 8a21c74`               | —                                       |
| `backend/src/test/resources/db/bootstrap-migration/V1__bootstrap_test_probe.sql`               | —                                                     | `A 8fe8329`                             |
| `backend/src/test/resources/db/test-migration/R__test_connection_probe.sql`                    | `A 2ca4efd`                                           | —                                       |
| `db/bootstrap/10-prepare-roles.sh`                                                             | —                                                     | `A 8fe8329`                             |
| `db/bootstrap/README.md`                                                                       | —                                                     | `A 8fe8329`                             |
| `db/bootstrap/sql/prepare-roles.sql`                                                           | —                                                     | `A 8fe8329`                             |
| `db/migration/.gitkeep`                                                                        | `A 3ffeb6d`                                           | —                                       |
| `db/migration/application-status.md`                                                           | —                                                     | `A 8fe8329`                             |
| `db/migration/creation-review.md`                                                              | —                                                     | `A 8fe8329`                             |
| `db/migration/README.md`                                                                       | —                                                     | `A 8fe8329`                             |
| `db/migration/V1__create_common_model.sql`                                                     | —                                                     | `A 8fe8329`                             |
| `db/migration/V2__create_item_storage.sql`                                                     | —                                                     | `A c64a809`                             |
| `db/migration/V3__complete_item_storage.sql`                                                   | —                                                     | `A c64a809`                             |
| `db/migration/V4__derive_item_equipment_slot.sql`                                              | —                                                     | `A f21439d`                             |
| `db/migration/V5__create_item_relations.sql`                                                   | —                                                     | `A f21439d`                             |
| `db/model/common-tables.md`                                                                    | —                                                     | `A 8fe8329`                             |
| `db/model/consumer-references.md`                                                              | —                                                     | `A 8fe8329`                             |
| `db/model/implementation.md`                                                                   | —                                                     | `A 8fe8329`                             |
| `db/model/names-and-dates.md`                                                                  | —                                                     | `A 8fe8329`                             |
| `db/model/permissions-and-installation.md`                                                     | —                                                     | `A 8fe8329`                             |
| `db/model/ranges-and-uniqueness.md`                                                            | —                                                     | `A 8fe8329`                             |
| `db/model/region-layout.md`                                                                    | —                                                     | `A 8fe8329`                             |
| `db/model/table-layout.md`                                                                     | —                                                     | `A 8fe8329`                             |
| `db/model/writes-and-checks.md`                                                                | —                                                     | `A 8fe8329`                             |
| `db/README.md`                                                                                 | —                                                     | `A 8fe8329`                             |
| `.env.example`                                                                                 | `A 3ffeb6d`                                           | `M 8fe8329`                             |
| `compose.yaml`                                                                                 | `A 3ffeb6d` · `M 355b9db`                             | `M 8fe8329`                             |
| `scripts/dev-api.mjs`                                                                          | `A 3ffeb6d` · `M 355b9db`                             | `M 8fe8329`                             |
| `scripts/dev-api.test.mjs`                                                                     | `A 3ffeb6d` · `M 355b9db`                             | `M 8fe8329`                             |
| `scripts/verify-bootstrap.mjs`                                                                 | `A 3ffeb6d` · `M 355b9db`                             | `M 8fe8329`                             |
| `.github/workflows/harness-inventory.yml`                                                      | `M 355b9db`                                           | —                                       |
| `.github/workflows/quality.yml`                                                                | `A 355b9db`                                           | —                                       |
| `.gitignore`                                                                                   | `M 3ffeb6d` · `M 355b9db`                             | —                                       |
| `README.md`                                                                                    | `M 3ffeb6d` · `M 2ca4efd` · `M 8a21c74` · `M 355b9db` | `M 8fe8329`                             |
| `STRUCTURE.md`                                                                                 | `M 3ffeb6d` · `M 2ca4efd` · `M 355b9db`               | `M 8fe8329`                             |

### 백엔드 검증에 직접 연결된 파일

아래 파일은 모두 #63의 `355b9db`에서 처음 추가됐다. #59의 Gradle 통합 테스트나 #63의 Spotless를 제거·복원할 때 이 호출 경로도 함께 검토한다.

| 파일                                                        | Phase 검증과의 연결                                                                                                                     |
| ----------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------- |
| `package.json` · `package-lock.json`                        | `check:backend`·포맷 진입 명령과 Java 외 설정 검사의 Prettier 버전을 정한다.                                                            |
| `scripts/quality/check.mjs`                                 | 백엔드 검사에서 `spotlessCheck test integrationTest bootJar`를 호출한다.                                                                |
| `scripts/quality/process.mjs`                               | 운영체제별 Gradle Wrapper 실행을 연결한다.                                                                                              |
| `scripts/quality/format.mjs`                                | Java 포맷을 Gradle Spotless에 연결한다.                                                                                                 |
| `scripts/quality/changes.mjs` · `scripts/quality/paths.mjs` | 실제 diff의 검사 범위와 포맷 대상을 고른다. Phase의 `72c27a1`·`cc7338c`를 반영한 뒤 분류 규칙에는 skill·hook·Git 설정 관련 차이가 있다. |

### 관련 기록의 확인 범위

- Phase 쪽은 42-001의 `#implementation`·`#verification`과 42-002~004의 확정 설계·완료·검수, #42의 전체 수용, Phase의 보유 목록과 현황을 확인했다. 후속 정정 기록은 원래 수용된 결과, 그때 확인된 검증, 직접 승인 원문의 한계를 구별한다.
- #43 쪽은 `task-001-creation.md`, `task-002.md`와 배정·검증, `task-003.md`와 배정·수행, 부모 `issue.md` 및 운영 DB 문서를 인계 대상으로 식별했다. 원래 대화의 명시적 정정과 과거 문서의 “승인” 표현 사이 차이를 검수 조건으로 전달한다.
