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

Task·Issue·Phase와 독립 Issue에 공통으로 병합에 따른 자동 닫기를 사용하지 않는다. PR 제목·본문과 작업·squash·merge 커밋의 제목·본문에서 `close`·`closes`·`closed`·`fix`·`fixes`·`fixed`·`resolve`·`resolves`·`resolved` 뒤에 Issue 참조를 연결하지 않는다. 대소문자와 콜론은 회피 수단이 아니며 `fix: #번호`도 닫기 표현이다. 연결은 별도 `Refs #실제번호` 행이나 일반 링크로 하고 GitHub `Development`의 자동 닫기용 연결도 만들지 않는다.

`fix` 커밋 유형은 유지하되 바로 뒤에 이슈 번호를 두지 않는다. 예를 들어 제목은 `fix: 계산 오류 수정`, 본문은 빈 줄 뒤 `Refs #72`로 작성한다. 괄호·강조·인용·코드 표시로 닫기 구문을 감춰 통과시키지 않는다.

PR의 닫기 키워드는 기본 브랜치 대상일 때 작동하고, 커밋의 키워드는 나중에 기본 브랜치에 들어갈 때 작동할 수 있어 단계별 완료 시점과 일치하지 않는다. 커밋에 의한 닫힘은 PR의 닫기 연결 목록에 나타나지 않을 수 있으므로 연결 목록이 비었다는 사실로 안전을 판정하지 않는다. 최종 base에서 head로 유입되는 모든 커밋 메시지와 실제 통합 메시지를 확인한다. 동작은 [GitHub 공식 설명](https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/linking-a-pull-request-to-an-issue)을 참고한다.

[공용 검사기](../scripts/check-github-closing.py)는 아홉 키워드와 `#번호`·`소유자/저장소#번호`·Issue URL의 결합을 차단한다. URL·단순 문장부호/Markdown 포장은 예방적으로 포함하며 인용 예시는 면제하지 않는다. GitHub 파서를 완전히 재현하는 검사가 아니므로 실제 원문·연결·상태 대조를 대체하지 않는다. 로컬 설치·CI·병합 전 호출은 [Git 절차](../harness/Git%20작업%20절차.md#closing-check)를 따른다.

닫기·재개는 [로컬 상태 대응](<작업 기록 체계.md#github-state>)을 원천으로 [GitHub 반영 절차](<../harness/문서 관리.md#github-update>)에서 허용된 범위의 명시적 갱신으로 처리한다. PR 병합이나 미병합 종료만으로 해당 작업의 완료·취소를 판단하지 않는다.
