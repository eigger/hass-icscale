# ICOMON 주방 저울 (hass-icscale)

<!-- hass-standards:badges:start -->
[![Release](https://img.shields.io/github/v/release/eigger/hass-icscale?style=flat)](https://github.com/eigger/hass-icscale/releases)
[![HACS Custom](https://img.shields.io/badge/HACS-Custom-41BDF5?style=flat)](#설치)
[![Home Assistant minimum](https://img.shields.io/badge/HA-%E2%89%A5%202025.2.0-41BDF5?style=flat)](hacs.json)
[![Tests](https://img.shields.io/github/actions/workflow/status/eigger/hass-icscale/tests.yml?branch=main&style=flat&label=Tests)](https://github.com/eigger/hass-icscale/actions/workflows/tests.yml)
[![Validate](https://img.shields.io/github/actions/workflow/status/eigger/hass-icscale/validate.yml?branch=main&style=flat&label=Validate)](https://github.com/eigger/hass-icscale/actions/workflows/validate.yml)
[![License](https://img.shields.io/github/license/eigger/hass-icscale?style=flat)](LICENSE)
[![Downloads](https://img.shields.io/github/downloads/eigger/hass-icscale/total?style=flat&color=41BDF5&label=Downloads)](https://github.com/eigger/hass-icscale/releases)
<!-- hass-standards:badges:end -->

[English](README.md) | **한국어**

ICOMON 블루투스(BLE) 주방·커피 저울에 직접 연결해 무게를 읽는 Home Assistant용 HACS 커스텀 통합입니다. Home Assistant Core에 포함된 통합이 아닙니다.

## 지원 기기

서비스 `0000ffb0-…`를 광고하는 ICOMON BLE 주방·커피 저울(로컬 이름 `MY_SCALE*`)입니다. 두 가지 펌웨어 변형을 처리하며 [프로토콜 노트](docs/protocol.md)(영어)를 참고하세요. 자동화 테스트(모의 BLE 전송)만 검증 범위이며 개별 실물 모델·펌웨어는 검증하지 않았습니다.

## 주요 기능

- **실시간 무게 센서**: 저울 사용 중 연결을 통해 실시간 그램 값 수신
- **안정 상태**: 무게가 안정되었는지 나타내는 바이너리 센서
- **안정 무게 센서**: 안정 플래그가 켜진 동안 마지막 무게를 유지(재시작 후 복원)
- **표시 단위 센서**: 저울에 설정된 단위를 보여주는 진단 센서
- **마지막 오류 / 오류 횟수 센서**: 최근 실패한 세션과 실패 횟수를 보여주는 진단 센서(오류 횟수는 기본 비활성)
- **자동 측정 스위치**: 켜면 저울이 깨어 있는 동안 자동 연결·스트리밍하고, 끄면 스마트폰 앱이 블루투스를 쓸 수 있도록 비워 둡니다
- **유휴 자동 연결 해제**: 설정한 시간 동안 변화가 없으면 연결을 해제해 저울이 꺼질 수 있게 하고, 다시 사용하면 자동 재연결합니다
- **지금 측정 버튼**: 즉시 연결해 값을 읽습니다
- **영점 / 전원 끄기 버튼**: 무게 영점 설정 또는 저울 전원 끄기
- **자동 검색**: Home Assistant 블루투스 통합으로 자동 검색

## 요구사항

- Home Assistant 2025.2.0 이상
- 블루투스 어댑터 또는 (강력 권장) ESPHome 블루투스 프록시([중요 제한사항](#중요-제한사항) 참고)

## 설치

1. **HACS**: `eigger/hass-icscale`을 커스텀 리포지토리(*Integration*)로 추가해 설치하거나, `custom_components/icscale` 폴더를 Home Assistant의 `custom_components`에 복사합니다.
2. Home Assistant를 재시작합니다.
3. 저울 전원을 켭니다. **설정** > **기기 및 서비스**에 자동 검색되면 **구성**을 누릅니다. 검색되지 않으면 **통합 추가**에서 "ICOMON Kitchen Scale"을 검색합니다.

제거하려면 **기기 및 서비스**에서 통합 항목을 삭제한 뒤 HACS에서 제거(또는 폴더 삭제)합니다.

## 설정

통합 페이지의 **구성**에서 **유휴 연결 해제 시간(분)**을 설정합니다. 무게 변화가 없을 때 연결을 해제하기까지의 시간이며 기본값은 3분입니다. 자세한 동작은 [동작 방식](docs/how-it-works.md)(영어)을 참고하세요.

## 빠른 시작

저울을 켜고 무게 센서가 사용 가능해질 때까지 기다린 뒤 물건을 올립니다. 유휴 해제 후에도 저울이 계속 광고 중이면 **지금 측정**을 눌러 즉시 연결합니다.

## 중요 제한사항

- 가능하면 내장 어댑터보다 **블루투스 프록시**를 사용하고 `active: true`로 설정하세요.

  ```yaml
  esp32_ble_tracker:
    scan_parameters:
      active: true

  bluetooth_proxy:
    active: true
  ```

  추천 기기와 설정은 [Bluetooth 프록시 설정](https://github.com/eigger/hass-repo-standards/blob/main/docs/bluetooth.ko.md)과 [커뮤니티 보드 글](https://community.home-assistant.io/t/great-esp32-board-for-an-esphome-bluetooth-proxy/916767/31)을 참고하세요.
- 저울은 한 번에 하나의 연결만 허용하므로 스마트폰 앱과 Home Assistant를 동시에 사용할 수 없습니다.
- 검색에 저울이 보여도 GATT 연결 성공을 의미하지 않습니다.

## 문서

- [동작 방식](docs/how-it-works.md) (영어)
- [프로토콜 노트](docs/protocol.md) (영어)
- [문제 해결](docs/troubleshooting.md) (영어)
- [개발 및 테스트](docs/development.md) (영어)

## 지원

버그는 [Issues](https://github.com/eigger/hass-icscale/issues), 질문·기능 제안은 [Discussions](https://github.com/eigger/hass-icscale/discussions)를 이용하세요.

## 라이선스

[LICENSE](LICENSE)를 참고하세요.
