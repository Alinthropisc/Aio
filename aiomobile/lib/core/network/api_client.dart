import 'package:dio/dio.dart';
import '../config/app_config.dart';

// Factory pattern for Dio instance creation
class ApiClient {
  ApiClient._();

  static Dio create({List<Interceptor> interceptors = const []}) {
    final dio = Dio(
      BaseOptions(
        baseUrl: AppConfig.apiBaseUrl,
        connectTimeout: const Duration(milliseconds: AppConfig.connectTimeout),
        receiveTimeout: const Duration(milliseconds: AppConfig.receiveTimeout),
        headers: {'Content-Type': 'application/json'},
      ),
    );

    dio.interceptors.addAll(interceptors);
    return dio;
  }
}
