# aiomobile

![Flutter](https://img.shields.io/badge/Flutter-3.44-blue?logo=flutter)
![Dart](https://img.shields.io/badge/Dart-3.12-blue?logo=dart)
![Android](https://img.shields.io/badge/Android-supported-green?logo=android)
![iOS](https://img.shields.io/badge/iOS-supported-lightgrey?logo=apple)
![License](https://img.shields.io/badge/license-MIT-green)

Flutter mobile app for the **Aio platform** — targets Android and iOS.  
Part of the [Aio monorepo](../).

---

## Features

- **BLoC state management** via `flutter_bloc 9` — events, states, cubits
- **Clean Architecture** — strict domain / data / presentation separation
- **Injectable IoC DI** — `get_it` service locator wired by `injectable`
- **GoRouter navigation** — declarative, type-safe routing with guards
- **Secure JWT storage** — tokens kept in `flutter_secure_storage` (Keychain / Keystore)
- **Dio HTTP client** — with auth interceptor, token refresh, and error mapping
- **Material 3 theming** — light and dark themes, dynamic color support

---

## Tech Stack

| Concern        | Library                              |
|----------------|--------------------------------------|
| State          | flutter_bloc 9                       |
| DI             | get_it + injectable                  |
| Navigation     | go_router 15                         |
| HTTP           | Dio                                  |
| Secure storage | flutter_secure_storage               |
| Preferences    | shared_preferences                   |
| Code generation| freezed + injectable_generator       |
| Models         | freezed + Equatable                  |

---

## Architecture

aiomobile follows **Clean Architecture** split into three layers:

```
lib/
├── core/                      # Cross-cutting concerns
│   ├── di/                    # get_it + injectable setup
│   ├── network/               # Dio client, interceptors
│   ├── router/                # GoRouter configuration
│   ├── storage/               # Secure storage abstraction
│   └── theme/                 # Material 3 light/dark themes
│
└── features/
    └── auth/                  # Example feature slice
        ├── domain/
        │   ├── entities/      # Pure Dart models (freezed)
        │   ├── repositories/  # Abstract repository contracts
        │   └── usecases/      # Single-responsibility use cases
        ├── data/
        │   ├── datasources/   # Remote (Dio) + local data sources
        │   ├── models/        # DTOs with JSON serialization
        │   └── repositories/  # Repository implementations
        └── presentation/
            ├── bloc/          # BLoC events, states, bloc class
            ├── pages/         # Full-screen route widgets
            └── widgets/       # Feature-scoped reusable widgets
```

**Data flow:** UI dispatches BLoC events → BLoC calls use cases → use cases call repository contracts → data layer hits Dio or secure storage → results surface back as BLoC states.

---

## Getting Started

### Prerequisites

- Flutter 3.44 or later (`flutter --version`)
- Dart 3.12 or later
- Android SDK (for Android targets) or Xcode (for iOS targets)

### Install dependencies

```bash
flutter pub get
```

### Run code generation

```bash
dart run build_runner build --delete-conflicting-outputs
```

### Run the app

```bash
# Debug on connected device / emulator
flutter run

# With a custom API base URL
flutter run --dart-define=API_BASE_URL=https://api.example.com
```

---

## Code Generation

This project uses `build_runner` to generate:

- **freezed** — immutable value objects and sealed unions
- **injectable_generator** — `get_it` registration boilerplate (`injection.config.dart`)
- **json_serializable** — `fromJson` / `toJson` for data-layer DTOs

Re-run generation whenever you:

- Add or modify a `@injectable` / `@singleton` / `@lazySingleton` class
- Add or modify a `@freezed` model
- Add or modify a `@JsonSerializable` DTO

```bash
# One-shot (CI / fresh clone)
dart run build_runner build --delete-conflicting-outputs

# Watch mode (during development)
dart run build_runner watch --delete-conflicting-outputs
```

---

## Project Structure

```
aiomobile/
├── android/                   # Android host project
├── ios/                       # iOS host project
├── assets/                    # Fonts, images, icons
├── test/                      # Unit and widget tests
├── lib/
│   ├── main.dart              # Entry point, app bootstrap
│   ├── app.dart               # MaterialApp + GoRouter wiring
│   ├── injection.dart         # get_it configurator (generated)
│   ├── core/
│   │   ├── di/
│   │   ├── network/
│   │   ├── router/
│   │   ├── storage/
│   │   └── theme/
│   └── features/
│       └── auth/
│           ├── domain/
│           ├── data/
│           └── presentation/
├── pubspec.yaml
├── pubspec.lock               # Committed for reproducible builds
└── analysis_options.yaml
```

---

## Environment

Pass runtime configuration via `--dart-define`:

| Variable       | Default                      | Description            |
|----------------|------------------------------|------------------------|
| API_BASE_URL   | http://localhost:3000/api/v1 | Backend API base URL   |

Example:

```bash
flutter run --dart-define=API_BASE_URL=https://staging.aio.example.com/api/v1
```

For release builds, pass the same flag to `flutter build apk` / `flutter build ipa`.

---

## Running Tests

```bash
# All tests
flutter test

# With coverage
flutter test --coverage
genhtml coverage/lcov.info -o coverage/html
```

---

## License

MIT — see [LICENSE](../LICENSE).
