# 공통 규칙 적용 체크리스트

[사용법과 판정 기준](https://github.com/eigger/hass-repo-standards/blob/78d242092eac732a1af48770e77e3f51e566c6c2/docs/checklist.md). 상태: `PASS` 근거 확인, `TODO` 미확인·미충족, `EXCEPTION` 기록된 예외, `N/A` 해당 없음.

## 검토 대상

| 항목 | 값 |
|---|---|
| 통합 리포 / 기본 브랜치 | eigger/hass-icscale / main |
| domain / 구현 경로 | icscale / custom_components/icscale |
| 검토 대상 통합 커밋 / 채택 PR | 4350ddf (main) / [PR #17](https://github.com/eigger/hass-icscale/pull/17) 스쿼시 병합 |
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
| 정확한 최소 라이브러리 | 3.14 / 2026.10.2 / 0.13.373 | CI `current / Python 3.14 / ha / minimum` success (blesession 하한 0.9.0, pip check 포함) | 현재 최신도 0.9.0이라 current와 동일 값 |
| CI (main 4350ddf) | 3.14·3.13 | [Tests](https://github.com/eigger/hass-icscale/actions/runs/39036976401): current/ha/current, current/ha/minimum(blesession 0.9.0), minimum-ha/ha/current, lint 2개 모두 success. [Validate](https://github.com/eigger/hass-icscale/actions/runs/39036976389) (HACS·Hassfest) success | 설치된 HA/플러그인 버전은 job summary 확인 |

## 항목 상태

| 규칙 ID | 상태 | 근거 / 남은 작업 |
|---|---|---|
| GOV-01, GOV-02 | PASS | STANDARDS.md에 SHA 기록, workflow는 표준 SHA로 고정 |
| GOV-03 | PASS | 채택 PR #17 병합 |
| GOV-04 | PASS | 중앙 표 갱신: hass-repo-standards b7d7493 (상태 진행 중) |
| GOV-05 | EXCEPTION | 구현은 주 에이전트, 독립 리뷰는 Opus 서브 에이전트(지적 12건 중 1~5,7 반영). 구현 위임 예외는 STANDARDS.md |
| TEST-08 | PASS | tests/components/icscale/, pytest.ini testpaths 일치 |
| TEST-02, TEST-03, TEST-09 | PASS | 실제 hass fixture·config entry로 setup 실행(기존 테스트 유지) |
| TEST-04 | PASS | current와 exact-minimum 분리, 로컬 둘 다 58 passed, CI minimum-ha job success |
| TEST-01, TEST-06, TEST-07 | TODO | config_flow 테스트(hass.config_entries.flow 경유)·재설정·migration 회귀가 없음(기존 공백) |
| TEST-05, DEP-02 | PASS | CI minimum 모드 success. 현재 최신=최소=0.9.0이므로 차이가 생기면 재확인 |
| DEP-01, DEP-06 | PASS | 런타임은 manifest, 테스트/린트 requirements 분리 |
| DEP-03, DEP-08 | TODO | 이번 변경에 새 의존성 없음 — 확인 근거 필요 시 갱신 |
| DEP-07, CI-06 | PASS | ha-components 입력으로 bluetooth·bluetooth_adapters·recorder 요구사항 설치, CI pip check 포함 success |
| CI-01, CI-02 | PASS | 공통 workflow 호출, PR·main push 실행 success |
| CI-03, CI-05, CI-08 | PASS | 최소 권한·full SHA 고정. checkout 자격증명 비보존은 공통 workflow가 처리 |
| CI-04, CI-07, CI-12 | TODO | required checks 이름(Tests / Validate)은 저장소 설정 확인 필요 |
| CI-09, CI-10 | TODO | 공통 dependency-update 구성 완료, 첫 주간 실행(스케줄/수동) 결과 대기 |
| HACS-01, HACS-02 | PASS | hacs.json 최소 HA 2025.2.0 유지 |
| HACS-03, HACS-05 | PASS | brand/icon.png 존재, `ignore: brands` 제거 후 Validate(HACS·Hassfest) success |
| HACS-04, REL-01~04, HACS-06 | N/A | 적용만으로 태그·릴리스 안 함 / 권장 항목은 미검토 |
| DOC-01, DOC-02, DOC-06 | PASS | README.md(영)/README.ko.md(한) 상호 링크, 상세는 docs/(영어, 한국어 README에 표기) |
| DOC-03, DOC-04, DOC-05 | PASS | sync_badges.py --check 통과, 동적 Usage 배지 포함 |
| DOC-07, HA-12 | PASS(문서) | troubleshooting에 모델 고유 조건·진단·제보 절차. 실물 검증은 주장하지 않음 |
| HA-01 ~ HA-13 | TODO | 통합 코드 구조·생명주기 점검은 이번 채택에서 하지 않음(소스 변경은 ruff format만) |

## 남은 작업

| 항목 | 내용 |
|---|---|
| TEST-01/06/07 | config_flow(`hass.config_entries.flow` 경유)·재설정·migration 회귀 테스트 추가 |
| HA-01 ~ HA-13 | 통합 코드 구조·생명주기 점검 |
| CI-04, CI-07, CI-12 | required checks 이름(Tests / Validate) 저장소 설정 확인 |
| CI-09, CI-10 | update_dependencies 첫 실행 결과 확인 (Actions의 PR 생성 허용 설정 포함) |


## 2026-10-23 HACS ZIP and Downloads (scoped)

- Target base: `b675dd2b976666253d3aa4b5554a9496e3727cab`; reviewed release central: `fd4162c0b93fbe8e109f99c787773ae09ba157e1`.
- Scope: HACS-04/CI-11 release ZIP and DOC-03/05 Downloads replacing Analytics Usage. No release is created during this update.
- Local scoped validation: PASS — canonical badge check, no Analytics Usage, release metadata/caller contract, actionlint 1.7.12, native git diff --check, unchanged tracked integration/manifest/dependencies/tests.
- Actual archive build: PASS at `1c1b695d2d4b89a81035afdd35c0563458d1d4fa`; `icscale.zip`, 25 files, SHA256 `06226aad1689fb89acf5367fde833dde7c43665eca373838d65be0b1fdde5994`. All archive members matched checkout bytes; manifest.json and __init__.py are at ZIP root. Final documentation-only follow-up preserves this integration tree. Windows Python 3.14.6; validation WSL Python 3.14.4/PyYAML 6.0.3/packaging 26.0.
- Full central integration checker: FAIL (pre-existing or unadopted contracts outside this scoped update; not treated as PASS). Findings:

```text
DOC-01 README.md: Exactly one ordered header marker pair required
DOC-01 README.ko.md: Exactly one ordered header marker pair required
HA-02 custom_components/icscale/manifest.json: categories requires 1–3 actual product categories (HA-02 project policy)
TEST-08 tests/components/icscale/test_init.py: Required contract file is missing
TEST-08 tests/components/icscale/test_config_flow.py: Required contract file is missing
TEST-08 tests/components/icscale/test_binary_sensor.py: Required contract file is missing
TEST-08 tests/components/icscale/test_button.py: Required contract file is missing
TEST-08 tests/components/icscale/test_sensor.py: Required contract file is missing
TEST-08 tests/components/icscale/test_switch.py: Required contract file is missing
TEST-08 tests/components/icscale/test_coordinator.py: Required contract file is missing
HA-13 custom_components/__init__.py: Required contract file is missing
GOV-02 .github/workflows/tests.yml: standards-ref must equal the reviewed reusable workflow SHA
GOV-02 .github/workflows/tests.yml: standards-ref must equal the reviewed reusable workflow SHA
GOV-02 .github/workflows/update_dependencies.yml: standards-ref must equal the reviewed reusable workflow SHA
TEST-03 tests/conftest.py: must match the central template exactly
TEST-08 tests/components/icscale/conftest.py: Exactly one ordered domain-fixtures marker pair required
TEST-08 tests/components/icscale/test_init.py: real HA lifecycle tests are required
CI-01 .github/workflows/validate.yml: central standards composite action pinned to full SHA required
DOC-07 docs/troubleshooting.md: Use the central troubleshooting H2 headings in their fixed order
DOC-07 README.md: README must link to matching-language local troubleshooting and blesession proxy setup
DOC-07 docs/troubleshooting.ko.md: [Errno 2] No such file or directory: '/mnt/d/Source/Github/.hacs-custom-zip/hass-icscale/docs/troubleshooting.ko.md'
DOC-07 README.ko.md: README must link to matching-language local troubleshooting and blesession proxy setup
```

- Existing CI workflows are preserved, except hass-kocom-smarthome where matching reviewed central references are synchronized. Existing support minimum and prior exceptions remain.
- Independent review and remote CI: tracked in this branch's pull request; merge requires resolved actionable findings and successful applicable checks. No real release upload, device or new real HA runtime validation is claimed by these local packaging checks.


## 2026-10-25 중앙 검사기 부분 갱신 검증

- 검토한 중앙 SHA: `1863343638014adb8a4001afc8fddc1a27dc500f`; 적용 시작 커밋: `f69ec95bbcf094acd5090f302b29f9d4ceb4f15d`.
- 범위: 중앙 pin·standards-ref·검토 기준 기록 정합화 및 누락 standards job 추가. HA 구현·요구 버전은 유지합니다.
- 로컬: Python 3.14.5 / PyYAML 6.0.3, `python scripts/check_integration.py <target>` (검토한 중앙 source에서 실행): FAIL — 아래 미충족 항목을 확인했으며 성공으로 표시하지 않음.
- actionlint: PASS. PR CI·독립 리뷰 결과는 PR 링크와 check 결과를 확인합니다. 이 로컬 결과만으로 전체 채택 완료를 주장하지 않습니다.
- 수정 전에도 최신 검사기로 검사 시 22개 진단이 있었습니다. 이번 검사기가 드러내는 잔여 항목은 다음과 같습니다. 승인 예외나 실패 무시를 추가하지 않았습니다.

```text
DOC-01 README.md: Exactly one ordered header marker pair required
DOC-01 README.ko.md: Exactly one ordered header marker pair required
HA-02 custom_components/icscale/manifest.json: categories requires 1–3 actual product categories (HA-02 project policy)
TEST-08 tests/components/icscale/test_init.py: Required contract file is missing
TEST-08 tests/components/icscale/test_config_flow.py: Required contract file is missing
TEST-08 tests/components/icscale/test_binary_sensor.py: Required contract file is missing
TEST-08 tests/components/icscale/test_button.py: Required contract file is missing
TEST-08 tests/components/icscale/test_sensor.py: Required contract file is missing
TEST-08 tests/components/icscale/test_switch.py: Required contract file is missing
TEST-08 tests/components/icscale/test_coordinator.py: Required contract file is missing
HA-13 custom_components/__init__.py: Required contract file is missing
TEST-03 tests/conftest.py: must match the central template exactly
TEST-08 tests/components/icscale/conftest.py: Exactly one ordered domain-fixtures marker pair required
TEST-08 tests/components/icscale/test_init.py: real HA lifecycle tests are required
DOC-07 docs/troubleshooting.md: Use the central troubleshooting H2 headings in their fixed order
DOC-07 README.md: README must link to matching-language local troubleshooting and blesession proxy setup
DOC-07 docs/troubleshooting.ko.md: [Errno 2] No such file or directory: 'docs/troubleshooting.ko.md'
DOC-07 README.ko.md: README must link to matching-language local troubleshooting and blesession proxy setup
```
- 독립 리뷰: 별도 review_checker_rollout 담당자가 19개 리포의 workflow 69개·기존 job 100개를 구조 비교했습니다. 새 CI 회귀 지적 없음. 기존 job ID·입력·권한·지원 최소와 통합 코드 보존 및 새 standards job의 중앙 템플릿 일치 확인. 실행 변경 없는 이 기록 추가 전 작업 트리를 검토했습니다.
