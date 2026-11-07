# GitHub 저장소 설정 기준

<a id="current"></a>
## 적용

개인 계정의 GitHub Free 공개 저장소를 기준으로 옵션의 기준값과 기능 지원 범위를 관리한다. 브랜치·커밋·PR·병합의 작업 규칙은 [Git 작업 기준](<Git 작업 기준.md#current>), 실행 흐름은 [Git 작업 절차](<../harness/Git 작업 절차.md#entry>)를 따른다. 실제 설정값·변경·확인 결과는 담당 작업 기록에 남긴다.

<a id="general"></a>
## 일반 설정

| 옵션 | 기준값 |
|---|---|
| Allow merge commits | 켬 |
| Allow squash merging | 켬 |
| Allow rebase merging | 끔 |
| Allow auto-merge | 끔 |
| Automatically delete head branches | 끔 |

저장소 전체에서 merge와 squash를 허용하고 [방향별 병합 규칙](<details/git/PR과 병합 기준.md#merges>)에 맞는 방식을 선택한다. 병합 후 삭제는 [정리 조건](<details/git/브랜치 관리 기준.md#branch-cleanup>)을 확인한 뒤 수행한다. 일반 옵션의 동작은 GitHub의 [병합 방식](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/configuring-pull-request-merges/about-merge-methods-on-github)·[자동 병합 지원 범위](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/configuring-pull-request-merges/managing-auto-merge-for-pull-requests-in-your-repository)·[자동 삭제](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/configuring-pull-request-merges/managing-the-automatic-deletion-of-branches)를 참고한다.

<a id="branch-protection"></a>
## 브랜치 보호

main과 작업 브랜치의 보호 옵션은 다음 값을 기준으로 한다.

| 옵션 | `main` | `phase/*`·`issue/*`·`task/*` |
|---|---|---|
| Require a pull request before merging | 켬 | 끔 |
| PR의 허용 병합 방식 | Merge commit만 | 저장소 전체 허용값 유지 |
| Block force pushes | 켬 | 켬 |
| Restrict deletions | 켬 | 끔 |
| Require conversation resolution before merging | 켬 | 끔 |

작업 브랜치 패턴에는 `-r2` 같은 재개 차수도 포함된다. 하위 브랜치 삭제는 허용하되 [정리 조건](<details/git/브랜치 관리 기준.md#branch-cleanup>)을 지킨다.

하위 브랜치는 [직계 부모의 일반 merge 반영](<details/git/브랜치 관리 기준.md#parent-updates>)과 Issue 직접 작업을 위해 직접 push를 허용한다. 하위 결과의 상위 통합에는 기존 PR 규칙을 적용한다. PR 필수를 끈 phase·issue의 방향별 병합 방식과 올바른 head·base 관계는 절차에서 확인하며, GitHub가 자동으로 강제하는 것으로 취급하지 않는다.

상시 우회 대상은 두지 않는다. Ruleset은 우회 목록을 비우고, 기존 브랜치 보호 방식을 사용하면 관리자에게도 규칙을 적용한다. 전체 갱신 제한·브랜치 생성 제한·브랜치 잠금·선형 이력·서명·배포 성공·merge queue 요구는 사용하지 않는다. 선형 이력은 상위 변경 반영과 결과 통합의 merge commit을 막으므로 강제하지 않는다.

옵션의 의미와 관리자 예외는 [Ruleset 규칙](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets)과 [브랜치 보호](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches)를 참고한다.

<a id="review-checks"></a>
## 승인과 검사

| 옵션 | 기준값 |
|---|---|
| 필수 승인 수 | 0명 |
| CODEOWNERS 승인 필수 | 끔 |
| 마지막 push에 대한 다른 사람의 승인 필수 | 끔 |
| 변경 뒤 기존 승인 무효화 | 끔 |
| 필수 상태 검사 | 지정 없음 |
| Require branches to be up to date before merging | 필수 상태 검사를 지정하지 않은 구성에서는 사용하지 않음 |

작성자는 자기 PR을 승인할 수 없으므로 필수 승인 1명을 혼자 충족할 수 없다. 승인 수와 별개로 [자체·별도 검수 기준](<details/git/PR과 병합 기준.md#pr-review>)과 로컬 필수 검증을 지킨다. 승인 제약은 [GitHub 리뷰 설명](https://docs.github.com/en/pull-requests/how-tos/review-pull-requests/reviewing-proposed-changes-in-a-pull-request)을 참고한다.

필수 상태 검사로 지정하는 검사는 고유한 이름과 실행 조건을 갖추고 실제 실행·성공·실패 판정을 확인해야 한다. main에 필수 검사를 요구하는 구성에서는 최신 base 반영도 요구한다. 하위 브랜치의 검사 강제는 정상적인 직접 push와 상위 변경 반영을 차단하지 않아야 한다. 상태 검사 동작은 [GitHub 검사 기준](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches#require-status-checks-before-merging)을 따른다.

<a id="free-public"></a>
## GitHub Free 공개 저장소의 지원 범위

브랜치 보호·브랜치 Ruleset과 PR 자동 병합을 지원한다. 기능 지원과 계정·토큰의 접근 권한은 별개이며, 기능을 사용할 수 있다는 사실을 설정이 적용됐다는 근거로 삼지 않는다. [브랜치 보호](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches)·[Ruleset 지원 범위](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/about-rulesets)를 참고한다. 자동 병합의 지원 여부와 사용할 옵션값은 [일반 설정](<#general>)에서 구별한다.

Task에 사용하는 sub-issue도 지원한다. 모든 요금제에 공통으로 부모 Issue당 최대 100개, 중첩 최대 8단계의 제한이 있으며 로컬 순번의 표기 범위와 구별한다. [Sub-issue 공식 안내](https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/adding-sub-issues)

### Actions 실행과 저장소

| 항목 | GitHub Free 공개 저장소 기준 |
|---|---|
| 표준 GitHub-hosted runner 실행 | 무료. 월 포함 연산량을 차감하지 않음 |
| Artifact 저장소 | 계정 기준 500 MB 포함. GitHub Packages 저장소와 포함량 공유 |
| Cache 저장소 | 저장소별 10 GB. Artifact와 별도 |

실행 무료를 저장 공간 무제한으로 해석하지 않는다. 표준 runner의 무료 범위는 [공개 저장소 runner 안내](https://docs.github.com/en/actions/reference/runners/github-hosted-runners#standard-github-hosted-runners-for-public-repositories), 저장소 포함량은 [Actions 제한](https://docs.github.com/en/actions/reference/limits#storage-limits-for-all-github-hosted-runners)을 따른다. 대형 runner는 공개 저장소에서도 과금 대상이며, 저장소 초과 사용의 과금 조건과 함께 [Actions 공식 청구 기준](https://docs.github.com/en/billing/concepts/product-billing/github-actions)에서 확인한다.
