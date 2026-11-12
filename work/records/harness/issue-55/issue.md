# 스킬·hook 현황 관리와 갱신 누락 방지

<a id="summary"></a>
## 현재 요약

- GitHub: [Issue #55](https://github.com/Mi-no-Kim/LumiaWiki/issues/55)
- 상태: 완료
- 현재 진행 위치: 상세 기록 분리·기록 날짜 제거와 작성 기준·양식·현황 검사 보완을 마쳤다. 로컬 검증과 두 OS의 원격 회귀를 통과했다.
- 다음 행동: PR·main 반영은 별도 허용 후 진행한다.

<a id="goal"></a>
## 목표와 범위

프로젝트 skill·Codex/Git hook의 목록·역할·적용 조건·원천·확인 범위를 관리하고, 추가·변경·삭제 후 현황 갱신 누락을 제출 전에 발견한다. 개인·전역 설정·외부 플러그인과 보존 영역은 수집하지 않는다.

## 수용 조건

1. 실제 목록·원천·지문을 맞추고 현재 내용과 마지막 동작 확인 근거를 구분한다.
2. 추가·수정·삭제 누락, 잘못된 경로·지문과 부분 스테이징을 발견한다. 관계없는 문서 수정으로 통과하지 않는다.
3. 정상 후보는 통과하고 무관한 변경에 현황 수정을 요구하지 않는다.
4. 정의·지정 실행기·보조 파일과 미등록 관리 대상을 확인한다.
5. 검사기는 자동 수정·스테이징·설치·테스트·AI·네트워크 호출을 하지 않는다.
6. 기존 Git hook의 보존·공존·중복 설치·해제를 확인한다.
7. Windows·부분 후보·경로 경계와 기존 검수 도구 회귀를 확인한다.
8. 실제 원격 정상·실패와 변경 영향의 필요한 재검증을 확인한다. 미확인 범위를 완료로 표시하지 않는다.

## 상세 기록

| 문서 | 담당 내용 |
|---|---|
| [구현과 운영 계약](implementation.md#implementation-contract) | 관리 대상·후보·설치/복원 계약과 의존 관계 |
| [현황 검사와 hook 검증](verification.md#verification) | 로컬·원격 실행, 누락 탐지·보존/복원·문서 정리 근거 |
| [스킬 수행 검증](skill-verification.md#skill-verification) | 대표 요청 9사례, 인코딩 보완과 원천/근거 대응 |

<a id="related"></a>
## 관계와 후속

- 독립 하네스 Issue다. 브랜치는 `main → issue/55-skill-hook-inventory`이며 Phase·milestone·자식 Task는 없다.
- [관련 Task #51](https://github.com/Mi-no-Kim/LumiaWiki/issues/51)과 [관련 Task #53](https://github.com/Mi-no-Kim/LumiaWiki/issues/53)은 이 Issue의 자식이 아니다. 부모 반영 순서는 [구현과 운영 계약](implementation.md#pending)을 따른다.
- PR·main 반영은 별도 허용 후 진행한다.
