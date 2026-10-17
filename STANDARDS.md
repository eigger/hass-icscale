# 적용한 공통 규칙

- 표준: https://github.com/eigger/hass-repo-standards/tree/main
- 참조 커밋 SHA: 78d242092eac732a1af48770e77e3f51e566c6c2
- 채택일: 2026-10-17 (채택 변경은 아직 커밋/PR 전)
- profile: integration / ha (실제 HA fixture·통합 로딩 필수)
- 적용 점검표: [ADOPTION_CHECKLIST.md](ADOPTION_CHECKLIST.md)
- 중앙 현황표: https://github.com/eigger/hass-repo-standards/blob/main/docs/adoption-status.md
- 조율 / 구현 / 독립 리뷰·검증 담당: 구현은 Claude Code 주 에이전트, 독립 리뷰는 별도 Opus 서브 에이전트(2026-10-17, 지적 반영 후 재검증 필요)
- 중앙 현황 갱신일: 미등록 (외부 리포이므로 갱신하지 않음; 반영할 내용은 ADOPTION_CHECKLIST.md 참조)
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
