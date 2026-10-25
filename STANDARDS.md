# 적용한 공통 규칙

- 표준: https://github.com/eigger/hass-repo-standards/tree/1863343638014adb8a4001afc8fddc1a27dc500f
- 참조 커밋 SHA: `1863343638014adb8a4001afc8fddc1a27dc500f`
- 채택일: 2026-10-17 (PR #17, 4350ddf)
- profile: integration / ha (실제 HA fixture·통합 로딩 필수)
- 적용 점검표: [ADOPTION_CHECKLIST.md](ADOPTION_CHECKLIST.md)
- 중앙 현황표: https://github.com/eigger/hass-repo-standards/blob/main/docs/adoption-status.md
- 조율 / 구현 / 독립 리뷰·검증 담당: 구현은 Claude Code 주 에이전트, 독립 리뷰는 별도 Opus 서브 에이전트(2026-10-17, 지적 반영 후 재검증 필요)
- 중앙 현황 갱신일: 2026-10-17 (hass-repo-standards b7d7493)
- 실제 기본 브랜치: main
- 테스트 경로: tests/components/icscale/
- 변경 전 지원 최소 HA / 선언 근거: 2025.2.0 / hacs.json
- 적용 후 지원 최소 HA: 2025.2.0 (변경 없음)
- current HA 테스트 환경: HA 2026.10.2 / Python 3.14 / pytest-homeassistant-custom-component 0.13.373
- 최소 HA 검증 환경: HA 2025.2.0 / Python 3.13 / pytest-homeassistant-custom-component 0.13.210
- 최소 package 검증: blesession (manifest 하한 >=0.9.0, 공통 CI의 minimum 모드)

## 예외

| 규칙 ID | 이유 | 담당자 | 재검토 조건 |
|---|---|---|---|
| GOV-05 | 구현을 서브 에이전트에 위임하지 않고 주 에이전트가 수행(리뷰만 독립 서브 에이전트) | @eigger | 다음 채택에서 구현도 위임 |

- Reviewed release standards SHA: `1863343638014adb8a4001afc8fddc1a27dc500f`
## 2026-10-23 ZIP release and Downloads update

Base commit: `b675dd2b976666253d3aa4b5554a9496e3727cab`. HACS remains Custom. `hacs.json` now selects `icscale.zip`; publishing the next release builds and attaches that integration ZIP through the pinned central action. Analytics Usage is replaced by Downloads. The archive contains tracked integration files at its root. No existing release/tag/assets are modified.

Implementation and review: root; generated release caller reuses the independently reviewed central ZIP contract. Support minimum, manifest, code, dependencies, README body and prior adoption exceptions are preserved. Verification evidence is recorded in ADOPTION_CHECKLIST.md; this scoped update does not establish full standards compliance.

AGENTS.md is removed at the user's explicit request; its delegation instruction is superseded.

## 2026-10-25 중앙 검사기 갱신

- 검토한 중앙 main: `1863343638014adb8a4001afc8fddc1a27dc500f` (git ls-remote 확인). 이전 기본 기준 `78d242092eac732a1af48770e77e3f51e566c6c2`의 채택 이력은 위 기록을 보존합니다.
- 모든 중앙 workflow/action pin과 reusable workflow의 standards-ref를 같은 검토 SHA로 맞춥니다. HACS-04는 actions/*의 full SHA 고정을 유지하면서 SHA 값 차이를 허용합니다.
- Validate에 중앙 템플릿의 무조건 실행 standards job을 추가합니다. 기존 HACS/Hassfest와 HA test job 이름·입력은 보존하며, 기본 브랜치를 사용하는 중앙 실행 조건을 적용합니다.
- 통합 코드·런타임 의존성·지원 최소·배포 버전은 이번 변경 대상이 아닙니다. 기존 채택 범위를 전체 완료로 바꾸지 않으며 실제 검증 결과와 남은 항목은 ADOPTION_CHECKLIST.md의 같은 날짜 기록을 참조합니다.
