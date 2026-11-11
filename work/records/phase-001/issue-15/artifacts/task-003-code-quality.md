# Task 003 — 코드 검사·포맷팅 합의 기록

담당 기록: [Task 003](<../task-003.md#summary>).

<a id="current"></a>
## 채택·적용 상태

사용자는 Spotless·google-java-format, Prettier, TypeScript 타입 검사·ESLint·React Hooks 검사와 TS 7.0.2/6.0 호환 API 병행, 문서·일괄 포맷·생성/수정 후 자동 포맷을 확정했다. 현재 규칙 전문은 [실제 코드 품질 기준](<../../../../../docs/details/development/코드 품질.md#current>)에서 관리한다. 실제 설치·명령·hook 연결·성능 검증은 수행하지 않았다.

<a id="typescript-compatibility"></a>
### TypeScript 병행

[실제 기준](<../../../../../docs/details/development/코드 품질.md#typescript-compatibility>)을 따른다.

<a id="timing"></a>
### 검사 시점

[실제 기준](<../../../../../docs/details/development/코드 품질.md#timing>)을 따른다.

<a id="formatting"></a>
### 문서·일괄·자동 포맷

[실제 기준](<../../../../../docs/details/development/코드 품질.md#formatting>)을 따른다.

<a id="handoff"></a>
### 담당·검증 시점

[실제 기준](<../../../../../docs/details/development/코드 품질.md#handoff>)을 따른다.

## 검수·채택 확인

작성자 자체 대조와 읽기 전용 별도 검수에서 채택/미정/미구현 구분, 공식 TS 병행안, 기존 TDD 근거와의 관계, 부분 스테이징·범위·비용·후속 배정을 확인했고 필수 수정 문제를 발견하지 못했다. 관련 문서의 로컬 참조 64개와 공백 형식을 확인했다. 실제 설치·호환 실행·hook 동작·성능 검증은 수행하지 않았다. 이후 사용자가 위 병행·포맷 방식을 확정해 채택 상태·본문·담당 Task와 부모 요약·인계를 자체 대조해 갱신했다. 기검수한 방식의 의미는 유지했으며 기준 채택과 실제 도입을 구분한다.

## 근거

- [Microsoft — TypeScript 7.0과 6.0의 병행 방법](https://devblogs.microsoft.com/typescript/announcing-typescript-7-0/)
- [typescript-eslint 공식 지원 범위](https://typescript-eslint.io/users/dependency-versions/)
- [Spotless Gradle](https://github.com/diffplug/spotless/blob/main/plugin-gradle/README.md) · [Prettier 옵션](https://prettier.io/docs/options) · [Prettier 제외](https://prettier.io/docs/ignore)
- [OpenAI 공식 hooks — PostToolUse·도구 범위와 한계](https://learn.chatgpt.com/docs/hooks)
- [기존 TDD hook 기준](<task-003-tdd-hook-proposal.md#minimum>) · [TDD 근거 재사용](<task-003-tdd-hook-proposal.md#evidence>)
