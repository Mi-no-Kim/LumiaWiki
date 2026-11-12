# Issue #60 검증 근거

<a id="verification"></a>
## 확인 범위와 결과

- 기준: main `d9c2826`, Windows / Python 3.14.2. 새 기록 검사·작성 경계·기존 pre-commit 결합만 확인했다.
- 초기 무동작 스켈레톤의 테스트 10개에서 의도한 assertion 실패 9개·error 0을 확인했다. 검사기 구현과 지적 수정 후 10개가 실패/error/skip 0으로 통과했다.
- 정상 기록: 필요한 결정·승인·현재 막힘·제품 날짜·일반 API 원본 시각을 허용했다. artifacts의 원본 코드 블록·전용 실행 근거와 `issue.md`/`task-001.md` 이름도 허용했다.
- 거부: 새 평문·표·강조 표시·JSON 기록 날짜, 신규 날짜형 기록 파일명과 Task·Issue 본문의 실행 근거 전용 블록을 확인했다. 미변경 과거 날짜는 추가 위반으로 판정하지 않았다.
- 후보: 실제 index와 작업 파일의 불일치를 양방향으로 대조했고, 커밋은 첫 부모와 비교하며 작업 파일의 새 날짜에 영향받지 않았다. 미변경 긴 기록은 경고하지 않았다.
- 길이: 빈 줄 포함 100줄은 정상, 101줄은 WARNING·종료 0이다. artifacts는 길이 경고에서 제외했다.
- 기존 hook 관련 6개 테스트: 새 기록 gate, 이전 hook 보존·설치/복원, 기존 hook 뒤 정상/거부 커밋, 현황 도입 전 브랜치, 실제 선언 의존 fixture, 기록 검사 도입 전 브랜치 호환·작업 파일만 삭제한 후보 거부가 통과했다.
- 실제 설치 hook의 별도 index 확인: 정상 종료 0, 101줄 WARNING·종료 0, 강조된 기록 날짜는 `Record violation`·종료 2였다. 실제 index는 같았고 기존 TDD wrapper·metadata를 보존했다.
- CI 정의는 동일 검사기의 `--candidate HEAD`와 첫 부모 비교에 필요한 checkout 깊이 2를 사용한다. 이 근거의 실행 범위는 로컬이며 원격 CI 결과는 연결 PR의 검사에서 확인한다.
- 자체·별도 검수의 artifacts 분류와 날짜 필드 지적을 반영했다. 최종 staged 16개와 작업 파일·입력 지문·현황 범위를 대조했고 필수 미해결 지적은 없었다.

<a id="inputs"></a>
## 대응 입력과 한계

- `scripts/check-work-records.py`: SHA-256 `94590db6bb08d51e5dc0add9c8225f63ece2fb600dcca38c5becef5a0bc4690e`
- `scripts/hooks/pre-commit`: SHA-256 `3f5aa2b620ec98713efb5629ebb5b3a41a2ca8e224731a8f00cd66d80ceadcc7`
- `scripts/tests/test_work_records.py`: SHA-256 `f0847497f2623b76ef727ca2c8d6ba34b830fd8de2b719e083703b3df2818c0f`
- 기존 TDD wrapper SHA-256 `a82f6143429c4a98c3f6c3be39e73dccf9c8b56bc75075a4dc7d9229006413c7`; metadata 보존.
- 자동 검사는 명시적 형식만 판정한다. 일반 문장의 의미·본문 이력 누적과 다른 날짜 표현은 기존 문서 검수에서 확인하며 코드 블록의 원본 여부를 자동 인증하지 않는다.
- 스킬 원천·제품 코드는 변경하지 않았고 기존 스킬 검증·제품 테스트를 재실행하지 않았다.

<a id="ci-preparation"></a>
## PR CI의 비교 입력 준비

- [초기 PR CI](https://github.com/Mi-no-Kim/LumiaWiki/actions/runs/43199673154)는 두 OS에서 부모 문서 blob이 없는 partial/sparse checkout 때문에 `AGENTS.md` 비교에 실패했다. 검사기의 읽기 전용 정책은 유지했다.
- CI는 허용된 변경 문서의 부모측 blob 중 없는 객체만 한 번에 준비한다. 공개 origin을 확인했고 인증 저장·전수 checkout을 추가하지 않았다.
- 새 회귀 사례 1개가 실제 depth 2·partial·sparse clone의 동일 실패, 실제 workflow 준비 코드 뒤 통과와 무관 blob 미취득을 확인했다. 기존 10개 테스트 메서드의 AST·검사기·hook은 같아 기존 근거를 재사용했다. 자체·별도 검수는 이 변경 영향만 대조했고 필수 지적은 없었다.
- 원격 결과와 통합 상태는 [PR #61](https://github.com/Mi-no-Kim/LumiaWiki/pull/61)의 검사를 따른다.
