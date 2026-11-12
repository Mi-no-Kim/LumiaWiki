# Git 작업 기준

<a id="current"></a>

## 적용

Git 작업의 공통 기준과 상황별 상세 기준을 안내한다. 실행 흐름은 [Git 작업 절차](<../harness/Git 작업 절차.md#entry>), 제목·본문 양식은 [PR 템플릿](../harness/templates/pr.md)을 따른다.

공통 [권한](<details/operations/권한과 실행 범위.md>)·[검증과 완료](<details/operations/검증과 완료.md>), [기록 소유·상태](<작업 기록 체계.md#current>)·[작성 시점](<작업 기록 작성 기준.md#minimum>)은 기존 기준을 적용한다.

## 필요한 기준 선택

| 판단 상황                                                                        | 담당 기준                                                              |
| -------------------------------------------------------------------------------- | ---------------------------------------------------------------------- |
| 브랜치 계층·이름·상위 변경 반영·정리·재개                                        | [브랜치 관리 기준](<details/git/브랜치 관리 기준.md#current>)          |
| <a id="independent-issues"></a>독립 Issue·하네스 정비·긴급 수정의 분기·통합 경로 | [독립 작업 경로](<details/git/브랜치 관리 기준.md#independent-issues>) |
| 작업 커밋의 단위·완료 시 반영 사항·메시지                                        | [작업 커밋 기준](<details/git/작업 커밋 기준.md#current>)              |
| PR 작성·검수·병합 방식·통합 메시지·병합 후 확인                                  | [PR과 병합 기준](<details/git/PR과 병합 기준.md#current>)              |
| GitHub 저장소 옵션·기능 지원                                                     | [저장소 설정 기준](<GitHub 저장소 설정 기준.md#current>)               |

<a id="github-closing"></a>

### GitHub 참조와 닫기

Task·Issue·Phase와 독립 Issue에 공통으로 병합에 따른 자동 닫기를 사용하지 않는다. PR 본문과 작업·squash·merge 커밋에서 `Closes`·`Fixes`·`Resolves` 등 같은 기능의 표현을 사용하지 않고, 연결은 `Refs #실제번호`나 일반 링크로 한다. GitHub `Development`의 자동 닫기용 연결도 만들지 않는다. 자동 생성된 통합 메시지도 같은 기준으로 확인한다.

PR의 닫기 키워드는 기본 브랜치 대상일 때 작동하고, 커밋의 키워드는 나중에 기본 브랜치에 들어갈 때 작동할 수 있어 단계별 완료 시점과 일치하지 않는다. 동작은 [GitHub 공식 설명](https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/linking-a-pull-request-to-an-issue)을 참고한다.

닫기·재개는 [로컬 상태 대응](<작업 기록 체계.md#github-state>)을 원천으로 [GitHub 반영 절차](<../harness/문서 관리.md#github-update>)에서 허용된 범위의 명시적 갱신으로 처리한다. PR 병합이나 미병합 종료만으로 해당 작업의 완료·취소를 판단하지 않는다.
