class AppConfig {
  const AppConfig._();

  static const String appName = 'Aio';
  static const String apiBaseUrl = String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: 'http://localhost:8000/api/v1',
  );
  static const int connectTimeout = 30000;
  static const int receiveTimeout = 30000;
}
