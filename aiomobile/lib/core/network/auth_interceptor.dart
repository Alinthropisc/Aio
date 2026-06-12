import 'package:dio/dio.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:injectable/injectable.dart';

@injectable
final class AuthInterceptor extends Interceptor {
  final FlutterSecureStorage _storage;
  // Lazy Dio reference to avoid circular dep; set by ApiClient after build.
  Dio? _dio;

  AuthInterceptor(this._storage);

  void setDio(Dio dio) => _dio = dio;

  @override
  Future<void> onRequest(
    RequestOptions options,
    RequestInterceptorHandler handler,
  ) async {
    final token = await _storage.read(key: 'access_token');
    if (token != null) {
      options.headers['Authorization'] = 'Bearer $token';
    }
    handler.next(options);
  }

  @override
  Future<void> onError(
    DioException err,
    ErrorInterceptorHandler handler,
  ) async {
    if (err.response?.statusCode == 401 && _dio != null) {
      final refreshed = await _tryRefresh();
      if (refreshed) {
        // Retry original request with new token.
        final token = await _storage.read(key: 'access_token');
        final opts = err.requestOptions
          ..headers['Authorization'] = 'Bearer $token';
        try {
          final response = await _dio!.fetch(opts);
          return handler.resolve(response);
        } catch (_) {}
      }
    }
    handler.next(err);
  }

  Future<bool> _tryRefresh() async {
    try {
      final refresh = await _storage.read(key: 'refresh_token');
      if (refresh == null) return false;
      final response = await _dio!.post(
        '/auth/refresh',
        data: {'refresh_token': refresh},
        options: Options(extra: {'skipAuth': true}),
      );
      final accessToken = response.data['access_token'] as String?;
      if (accessToken == null) return false;
      await _storage.write(key: 'access_token', value: accessToken);
      return true;
    } catch (_) {
      await _storage.deleteAll();
      return false;
    }
  }
}
