# 공통 규칙 적용 체크리스트

[사용법과 판정 기준](https://github.com/eigger/hass-repo-standards/blob/78d242092eac732a1af48770e77e3f51e566c6c2/docs/checklist.md). 상태: `PASS` 근거 확인, `TODO` 미확인·미충족, `EXCEPTION` 기록된 예외, `N/A` 해당 없음.

## 검토 대상

| 항목 | 값 |
|---|---|
| 통합 리포 / 기본 브랜치 | eigger/hass-icscale / main |
| domain / 구현 경로 | icscale / custom_components/icscale |
| 검토 대상 통합 커밋 / 채택 PR | f3ecbbf (0.2.1) 위 작업 트리 / 미생성 |
| 검토한 표준 SHA | 78d242092eac732a1af48770e77e3f51e566c6c2 (STANDARDS.md와 일치) |
| 검토일 | 2026-10-17 |
| 변경 전 지원 최소 HA | 2025.2.0 (hacs.json) — 유지 |
| current 테스트 HA / Python·플러그인 | 2026.10.2 / 3.14 / 0.13.373 |
| 최소 테스트 HA / Python·플러그인 | 2025.2.0 / 3.13 / 0.13.210 |
| profile / 테스트 경로 | integration / ha, tests/components/icscale/ |
| 이전 검토 기록 | 최초 검토 |

## 검증 증거 (로컬)

| 검증 축 | Python / HA / 플러그인 | 명령·결과 | 범위 |
|---|---|---|---|
| 현재 환경 | 3.14 / 2026.10.2 / 0.13.373 | `pytest tests/components/icscale` — 58 passed (macOS) | blesession 최신, bluetooth·bluetooth_adapters·recorder 요구사항 설치 |
| 정확한 최소 HA | 3.13 / 2025.2.0 / 0.13.210 | 동일 명령 — 58 passed (macOS) | 동일 |
| Lint | ruff 0.17.1 | `ruff check .`, `ruff format --check .` 통과 | E/F 규칙 유지(ruff.toml) |
| 정확한 최소 라이브러리 | — | 로컬 미실행, 공통 CI `minimum` 모드에서 검증 예정 | TODO |
| CI | — | 푸시 전이라 미실행 | TODO |

## 항목 상태

| 규칙 ID | 상태 | 근거 / 남은 작업 |
|---|---|---|
| GOV-01, GOV-02 | PASS | STANDARDS.md에 SHA 기록, workflow는 표준 SHA로 고정 |
| GOV-03 | TODO | 채택 PR 생성 필요 |
| GOV-04 | TODO | 중앙 adoption-status 표 미갱신 — 반영할 내용: icscale, 테스트 구조·공통 CI·README 영/한·배지 적용, CI 결과 대기 |
| GOV-05 | EXCEPTION | 구현은 주 에이전트, 독립 리뷰는 Opus 서브 에이전트(지적 12건 중 1~5,7 반영). 구현 위임 예외는 STANDARDS.md |
| TEST-08 | PASS | tests/components/icscale/, pytest.ini testpaths 일치 |
| TEST-02, TEST-03, TEST-09 | PASS | 실제 hass fixture·config entry로 setup 실행(기존 테스트 유지) |
| TEST-04 | PASS(로컬) | current와 exact-minimum 분리, 로컬 둘 다 58 passed. CI 결과는 TODO |
| TEST-01, TEST-06, TEST-07 | TODO | config_flow 테스트(hass.config_entries.flow 경유)·재설정·migration 회귀가 없음(기존 공백) |
| TEST-05, DEP-02 | TODO | blesession minimum 모드는 CI에서 확인(현재 최신=최소=0.9.0) |
| DEP-01, DEP-06 | PASS | 런타임은 manifest, 테스트/린트 requirements 분리 |
| DEP-03, DEP-08 | TODO | 이번 변경에 새 의존성 없음 — 확인 근거 필요 시 갱신 |
| DEP-07, CI-06 | TODO | ha-components 입력 사용, CI 결과 대기 |
| CI-01, CI-02 | TODO | 공통 reusable workflow 호출 구성 완료, 실행 결과 대기 |
| CI-03, CI-05, CI-08 | PASS(구성) | 최소 권한·full SHA·checkout 자격증명 비보존은 공통 workflow가 처리, 실행 확인은 TODO |
| CI-04, CI-07, CI-12 | TODO | required checks 이름(Tests / Validate)은 저장소 설정 확인 필요 |
| CI-09, CI-10 | TODO | 공통 dependency-update 사용, 실행 결과 대기 |
| HACS-01, HACS-02 | PASS | hacs.json 최소 HA 2025.2.0 유지 |
| HACS-03, HACS-05 | TODO | brand/icon.png 존재, `ignore: brands` 제거 — HACS 실행 결과 확인 필요 |
| HACS-04, REL-01~04, HACS-06 | N/A | 적용만으로 태그·릴리스 안 함 / 권장 항목은 미검토 |
| DOC-01, DOC-02, DOC-06 | PASS | README.md(영)/README.ko.md(한) 상호 링크, 상세는 docs/(영어, 한국어 README에 표기) |
| DOC-03, DOC-04, DOC-05 | PASS | sync_badges.py --check 통과, 동적 Usage 배지 포함 |
| DOC-07, HA-12 | PASS(문서) | troubleshooting에 모델 고유 조건·진단·제보 절차. 실물 검증은 주장하지 않음 |
| HA-01 ~ HA-13 | TODO | 통합 코드 구조·생명주기 점검은 이번 채택에서 하지 않음(소스 변경은 ruff format만) |

## 남은 작업

| 항목 | 내용 |
|---|---|
| 푸시 후 CI | Tests(current/minimum blesession/minimum-ha), Validate(HACS·Hassfest) 결과를 확인해 TODO를 PASS로 갱신 |
| 중앙 표 | hass-repo-standards docs/adoption-status.md의 hass-icscale 행 갱신 |
| 저장소 설정 | Dependabot·Actions의 PR 생성 허용 설정 확인 |
